"""Rx bounded HTTP read-only transport.

Stdlib only. This module is intentionally not a generic browser/client:
- HTTPS only;
- GET only;
- explicit host allowlist supplied by the caller;
- bounded response size;
- redirects may only stay inside the supplied allowlist;
- no credentials or authorization headers.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class RxHttpError(RuntimeError):
    pass


def _host(url):
    parsed = urllib.parse.urlsplit(str(url))
    if parsed.scheme != "https":
        raise RxHttpError("https_required")
    if parsed.username is not None or parsed.password is not None:
        raise RxHttpError("userinfo_forbidden")
    if not parsed.hostname:
        raise RxHttpError("host_required")
    return parsed.hostname


class _AllowlistRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hosts):
        super().__init__()
        self.allowed_hosts = set(allowed_hosts)

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = _host(newurl)
        if host not in self.allowed_hosts:
            raise urllib.error.URLError("redirect_host_not_allowlisted")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get_bytes(
    url,
    *,
    allowed_hosts,
    timeout=30,
    max_bytes=8 * 1024 * 1024,
    params=None,
    user_agent="RLL-Rx-HTTP/1.0",
):
    allowed = set(str(x) for x in allowed_hosts)
    host = _host(url)
    if host not in allowed:
        raise RxHttpError("host_not_allowlisted:" + host)

    parsed = urllib.parse.urlsplit(str(url))
    if params:
        query = urllib.parse.urlencode(params, doseq=True)
        parsed = parsed._replace(query=query)
        url = urllib.parse.urlunsplit(parsed)

    opener = urllib.request.build_opener(_AllowlistRedirect(allowed))
    request = urllib.request.Request(
        str(url),
        headers={"User-Agent": str(user_agent), "Accept-Encoding": "identity"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=float(timeout)) as response:
            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    if int(content_length) > int(max_bytes):
                        raise RxHttpError("response_too_large")
                except ValueError:
                    pass
            payload = response.read(int(max_bytes) + 1)
            if len(payload) > int(max_bytes):
                raise RxHttpError("response_too_large")
            status = int(getattr(response, "status", 200))
            if status < 200 or status >= 300:
                raise RxHttpError("http_status:%d" % status)
            return payload
    except RxHttpError:
        raise
    except Exception as exc:
        raise RxHttpError("%s:%s" % (exc.__class__.__name__, exc)) from exc


def get_json(url, **kwargs):
    payload = get_bytes(url, **kwargs)
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RxHttpError("invalid_json") from exc
