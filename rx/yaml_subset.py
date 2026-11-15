"""Strict YAML subset parser for controlled RLL configuration migration.

Supported:
- indentation-based mappings;
- block sequences;
- sequence items that begin mappings;
- quoted/plain scalar strings;
- booleans/null/numbers;
- JSON-compatible flow lists.

Explicitly rejected:
anchors, aliases, tags, merge keys, tabs, block scalars, flow mappings,
custom types and arbitrary YAML features.

This is NOT a general YAML implementation.
"""
from __future__ import annotations

import json
import re

class RxYamlSubsetError(ValueError):
    pass

_FORBIDDEN_TOKENS = ("&", "*", "!", "<<:")

def _strip_comment(line):
    out=[]
    quote=None
    escaped=False
    for ch in line:
        if escaped:
            out.append(ch); escaped=False; continue
        if ch=="\\" and quote=='"':
            out.append(ch); escaped=True; continue
        if quote:
            out.append(ch)
            if ch==quote:
                quote=None
            continue
        if ch in ("'", '"'):
            quote=ch; out.append(ch); continue
        if ch=="#":
            break
        out.append(ch)
    return "".join(out).rstrip()

def _scalar(text):
    value=text.strip()
    if not value:
        raise RxYamlSubsetError("empty_scalar")
    if value.startswith("{"):
        raise RxYamlSubsetError("flow_mapping_forbidden")
    if value.startswith("["):
        try:
            parsed=json.loads(value)
        except json.JSONDecodeError as exc:
            raise RxYamlSubsetError("flow_list_must_be_json_compatible") from exc
        if not isinstance(parsed,list):
            raise RxYamlSubsetError("flow_value_not_list")
        return parsed
    if value[0:1] == value[-1:] and value.startswith(('"', "'")):
        if value.startswith('"'):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise RxYamlSubsetError("invalid_double_quoted_string") from exc
        return value[1:-1].replace("''", "'")
    low=value.lower()
    if low=="true": return True
    if low=="false": return False
    if low in {"null","~"}: return None
    if re.fullmatch(r"[-+]?\d+",value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][-+]?\d+)?",value):
        return float(value)
    return value

def _key_value(text):
    if ":" not in text:
        raise RxYamlSubsetError("mapping_colon_required")
    key,raw=text.split(":",1)
    key=key.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.+-]+",key):
        raise RxYamlSubsetError("unsupported_key:"+key)
    return key,raw.strip()

def loads(text):
    raw_lines=text.splitlines()
    tokens=[]
    for number,raw in enumerate(raw_lines,1):
        if "\t" in raw:
            raise RxYamlSubsetError("tabs_forbidden:%d"%number)
        stripped=_strip_comment(raw)
        if not stripped.strip():
            continue
        content=stripped.lstrip(" ")
        indent=len(stripped)-len(content)
        if indent % 2:
            raise RxYamlSubsetError("indent_must_be_multiple_of_2:%d"%number)
        if content.endswith("|") or content.endswith(">"):
            raise RxYamlSubsetError("block_scalars_forbidden:%d"%number)
        for tok in _FORBIDDEN_TOKENS:
            if tok in content and not (tok=="!" and "!=" in content):
                raise RxYamlSubsetError("yaml_feature_forbidden:%s:%d"%(tok,number))
        tokens.append((indent,content,number))

    if not tokens:
        return None

    def parse_block(index,indent):
        if index>=len(tokens) or tokens[index][0]!=indent:
            raise RxYamlSubsetError("unexpected_indent")
        is_seq=tokens[index][1].startswith("- ")
        container=[] if is_seq else {}

        while index<len(tokens):
            cur_indent,content,number=tokens[index]
            if cur_indent<indent:
                break
            if cur_indent>indent:
                raise RxYamlSubsetError("unexpected_deeper_indent:%d"%number)

            if is_seq:
                if not content.startswith("- "):
                    break
                item=content[2:].strip()
                if not item:
                    if index+1>=len(tokens) or tokens[index+1][0]<=indent:
                        raise RxYamlSubsetError("empty_sequence_item:%d"%number)
                    value,index=parse_block(index+1,tokens[index+1][0])
                    container.append(value)
                    continue
                if ":" in item:
                    key,raw=_key_value(item)
                    obj={}
                    if raw:
                        obj[key]=_scalar(raw)
                        index+=1
                    else:
                        if index+1>=len(tokens) or tokens[index+1][0]<=indent:
                            obj[key]={}
                            index+=1
                        else:
                            value,index=parse_block(index+1,tokens[index+1][0])
                            obj[key]=value
                    # absorb following mapping fields belonging to same sequence item
                    while index<len(tokens) and tokens[index][0]==indent+2 and not tokens[index][1].startswith("- "):
                        kcontent=tokens[index][1]
                        k,raw2=_key_value(kcontent)
                        if raw2:
                            obj[k]=_scalar(raw2); index+=1
                        else:
                            if index+1>=len(tokens) or tokens[index+1][0]<=indent+2:
                                obj[k]={}; index+=1
                            else:
                                value,index=parse_block(index+1,tokens[index+1][0])
                                obj[k]=value
                    container.append(obj)
                    continue
                container.append(_scalar(item))
                index+=1
                continue

            if content.startswith("- "):
                break
            key,raw=_key_value(content)
            if key in container:
                raise RxYamlSubsetError("duplicate_key:%s:%d"%(key,number))
            if raw:
                container[key]=_scalar(raw)
                index+=1
            else:
                if index+1>=len(tokens) or tokens[index+1][0]<=indent:
                    container[key]={}
                    index+=1
                else:
                    value,index=parse_block(index+1,tokens[index+1][0])
                    container[key]=value
        return container,index

    result,index=parse_block(0,tokens[0][0])
    if index!=len(tokens):
        raise RxYamlSubsetError("trailing_unparsed_content")
    return result

def load(path):
    return loads(path.read_text(encoding="utf-8"))
