#!/usr/bin/env python3
"""RLL bounded private-image entropy: gated execution, encrypted-only output.

Requires an operator secret from a trusted external environment (NOT RLL GITPAT),
an independently entered read-only GitHub PAT, and an X25519 recipient public key.
Never place source images, numerical matrices or keys in a public GitHub repository.
"""
import argparse
import base64
from collections import Counter
import getpass
import hashlib
import hmac
import io
import json
import math
import os
from pathlib import Path
import sys
import urllib.request
import zlib

AUDIENCE = b"rll.joao_matheus.private.v1"
REPOSITORY = "instituto-Rafael/relativity-living-light"
MAX_IMAGE_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 16_000_000

class GateBlocked(Exception):
    """Authorization, custody, or processing prerequisite not satisfied."""


def shannon(values):
    if not values:
        return 0.0
    counts = Counter(values)
    n = len(values)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def quadrant_metrics(pixels, width, height, grid=4):
    """Bounded measurements on quantized grayscale; no inferred semantics."""
    if width < grid or height < grid or len(pixels) != width * height:
        raise GateBlocked("Invalid image geometry")
    rows = []
    for ry in range(grid):
        y0, y1 = ry * height // grid, (ry + 1) * height // grid
        for rx in range(grid):
            x0, x1 = rx * width // grid, (rx + 1) * width // grid
            region = bytes((pixels[y * width + x] >> 4) for y in range(y0, y1) for x in range(x0, x1))
            rw = x1 - x0
            residual = bytes(((region[i] - region[i-1]) & 15)
                             for i in range(len(region)) if i % rw)
            h = shannon(region) / 4.0
            hr = shannon(residual) / 4.0
            ratio = len(zlib.compress(region, level=9)) / len(region)
            ink = sum(v < 12 for v in region) / len(region)
            # Higher proxy means more local complexity. Not semantic entropy.
            score = 0.4 * h + 0.3 * hr + 0.3 * min(ratio, 1.0)
            rows.append({"quadrant": f"R{ry+1}C{rx+1}",
                         "bounds_xyxy": [x0, y0, x1, y1],
                         "entropy_4bit_normalized": round(h, 8),
                         "residual_entropy_normalized": round(hr, 8),
                         "zlib_bytes_per_quantized_pixel": round(ratio, 8),
                         "dark_pixel_fraction_proxy": round(ink, 8),
                         "complexity_proxy": round(score, 8)})
    return rows


def paired_matrices(rows):
    # Identical underlying measurements, opposite sorting; deterministic ties.
    joao = sorted(rows, key=lambda r: (r["complexity_proxy"], r["quadrant"]))
    matheus = sorted(rows, key=lambda r: (-r["complexity_proxy"], r["quadrant"]))
    return {"JOAO_low_complexity_first": joao,
            "MATHEUS_high_complexity_first": matheus}


def require_operator_secret(expected, entered):
    if not expected or len(expected) < 24 or not entered:
        raise GateBlocked("Authorization not configured")
    if not hmac.compare_digest(expected.encode("utf-8"), entered.encode("utf-8")):
        raise GateBlocked("Authorization denied")


def verify_read_only_pat(pat, *, opener=urllib.request.urlopen):
    if not pat:
        raise GateBlocked("GitHub authorization missing")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}",
        headers={"Authorization": f"Bearer {pat}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "rll-private-entropy-v1"}, method="GET")
    try:
        with opener(request, timeout=10) as response:
            data = json.loads(response.read(65536))
    except Exception:
        raise GateBlocked("GitHub authorization unavailable") from None
    if data.get("full_name") != REPOSITORY:
        raise GateBlocked("Repository identity mismatch")
    permissions = data.get("permissions")
    # A broad administrative credential is NOT accepted for this analysis.
    if not isinstance(permissions, dict) or permissions.get("pull") is not True:
        raise GateBlocked("Read permission not attested")
    if permissions.get("push") is not False or permissions.get("admin") is not False:
        raise GateBlocked("Overprivileged or unverifiable credential")


def encrypt_to_recipient(payload, recipient_hex):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    try:
        recipient = x25519.X25519PublicKey.from_public_bytes(bytes.fromhex(recipient_hex))
    except (ValueError, TypeError):
        raise GateBlocked("Recipient public key invalid") from None
    ephemeral = x25519.X25519PrivateKey.generate()
    secret = ephemeral.exchange(recipient)
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=AUDIENCE).derive(secret)
    nonce = os.urandom(12)
    sealed = AESGCM(key).encrypt(nonce, payload, AUDIENCE)
    return {"schema": "rll.private_entropy_ciphertext.v1",
            "alg": "X25519-HKDF-SHA256-AES256-GCM",
            "ephemeral_public_b64": base64.b64encode(ephemeral.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw)).decode("ascii"),
            "nonce_b64": base64.b64encode(nonce).decode("ascii"),
            "ciphertext_b64": base64.b64encode(sealed).decode("ascii")}


def analyze_private_image(raw, source_ref):
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise GateBlocked("Input unavailable or exceeds limit")
    try:
        from PIL import Image, ImageOps
        Image.MAX_IMAGE_PIXELS = MAX_PIXELS
        with Image.open(io.BytesIO(raw)) as img:
            img = ImageOps.exif_transpose(img)
            width, height = img.size
            if width * height > MAX_PIXELS:
                raise GateBlocked("Image pixel limit exceeded")
            px = img.convert("L").tobytes()
    except GateBlocked:
        raise
    except Exception:
        raise GateBlocked("Image decoding failed") from None
    rows = quadrant_metrics(px, width, height)
    return {"schema": "rll.entropy_joao_matheus.v1",
            "source_ref": source_ref,
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "grayscale_dimensions": [width, height],
            "quantization": "L_8bit_to_4bit_high_nibble",
            "grid": "4x4",
            "units": "normalized empirical pixel entropy / proxy",
            "classification_boundary": "PATTERN_PROXY_ONLY_NOT_SEMANTICS_NOT_COSMOLOGY",
            "claim_allowed": False,
            "matrices": paired_matrices(rows)}


def run(args):
    # The key and PAT are obtained BEFORE opening even the private input file.
    required_secret = os.environ.get("RLL_ENTROPY_OPERATOR_KEY", "")
    entered = getpass.getpass("Operator key (hidden): ")
    require_operator_secret(required_secret, entered)
    pat = getpass.getpass("Scoped read-only GitHub PAT (hidden): ")
    verify_read_only_pat(pat)
    # Public key must be pinned by the private authorized recipient; not a secret.
    recipient = os.environ.get("RLL_ENTROPY_RECIPIENT_X25519_PUBLIC_HEX", "")
    if len(recipient) != 64:
        raise GateBlocked("Recipient key not configured")
    if not args.source_ref or args.source_ref == "TOKEN_VAZIO":
        raise GateBlocked("Immutable private source reference required")
    private_root_str = os.environ.get("RLL_ENTROPY_PRIVATE_ROOT", "")
    if not private_root_str or not Path(private_root_str).is_absolute():
        raise GateBlocked("Private storage root not configured")
    private_root = Path(private_root_str).resolve(strict=True)
    repository_root = Path(__file__).resolve().parents[2]
    if private_root == repository_root or private_root.is_relative_to(repository_root):
        raise GateBlocked("Private storage must remain outside public checkout")
    source_path = Path(args.input_private_image).resolve(strict=True)
    target = Path(args.out_encrypted)
    target_parent = target.parent.resolve(strict=True)
    if source_path.parent == repository_root or source_path.is_relative_to(repository_root):
        raise GateBlocked("Refuse public repository source")
    if not source_path.is_relative_to(private_root) or not target_parent.is_relative_to(private_root):
        raise GateBlocked("Private input/output must remain inside private root")
    raw = source_path.read_bytes()
    data = analyze_private_image(raw, args.source_ref)
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    envelope = encrypt_to_recipient(payload, recipient)
    serialized = (json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if target.exists():
        raise GateBlocked("Refuse overwrite; use an unused ciphertext path")
    # The only persisted result is ciphertext; output must be a private directory.
    fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(serialized)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    print("ENCRYPTED_ONLY | claim_allowed=false | ciphertext_sha256=" +
          hashlib.sha256(serialized).hexdigest())


def main():
    parser = argparse.ArgumentParser(description="Gated RLL private image entropy, no plaintext output")
    parser.add_argument("--input-private-image", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--out-encrypted", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except (GateBlocked, FileNotFoundError, PermissionError, EOFError, KeyboardInterrupt, ValueError):
        print("BLOCKED | TOKEN_VAZIO | no public scientific claim", file=sys.stderr)
        return 3
    return 0

if __name__ == "__main__":
    sys.exit(main())
