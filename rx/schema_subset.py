"""Strict JSON-Schema subset validator for controlled RLL contracts.

Supported keywords:
type, required, properties, enum, items, minItems, additionalProperties,
format=date, plus annotation/meta keys ($schema, $id, title, description).

No claim of general JSON Schema conformance.
"""
from __future__ import annotations

from datetime import date

class RxSchemaSubsetError(ValueError):
    pass

_ALLOWED_KEYS={
    "$schema","$id","title","description",
    "type","required","properties","enum","items","minItems",
    "additionalProperties","format",
}

def _type_ok(value, expected):
    if expected=="object": return isinstance(value,dict)
    if expected=="array": return isinstance(value,list)
    if expected=="string": return isinstance(value,str)
    if expected=="boolean": return isinstance(value,bool)
    if expected=="null": return value is None
    if expected=="integer": return isinstance(value,int) and not isinstance(value,bool)
    if expected=="number": return isinstance(value,(int,float)) and not isinstance(value,bool)
    raise RxSchemaSubsetError("unsupported_type:"+str(expected))

def validate(instance,schema,path="$"):
    if not isinstance(schema,dict):
        raise RxSchemaSubsetError("schema_node_must_be_object:"+path)
    unknown=set(schema)-_ALLOWED_KEYS
    if unknown:
        raise RxSchemaSubsetError("unsupported_schema_keywords:%s:%s"%(path,",".join(sorted(unknown))))

    expected=schema.get("type")
    if expected is not None:
        types=expected if isinstance(expected,list) else [expected]
        if not any(_type_ok(instance,item) for item in types):
            raise RxSchemaSubsetError("type_mismatch:%s:expected=%s"%(path,types))

    if "enum" in schema and instance not in schema["enum"]:
        raise RxSchemaSubsetError("enum_mismatch:"+path)

    if schema.get("format")=="date":
        if not isinstance(instance,str):
            raise RxSchemaSubsetError("date_requires_string:"+path)
        try:
            date.fromisoformat(instance)
        except ValueError as exc:
            raise RxSchemaSubsetError("invalid_date:"+path) from exc
    elif "format" in schema:
        raise RxSchemaSubsetError("unsupported_format:%s:%s"%(path,schema["format"]))

    if isinstance(instance,dict):
        required=schema.get("required",[])
        if not isinstance(required,list) or not all(isinstance(x,str) for x in required):
            raise RxSchemaSubsetError("invalid_required:"+path)
        missing=[name for name in required if name not in instance]
        if missing:
            raise RxSchemaSubsetError("missing_required:%s:%s"%(path,",".join(missing)))

        properties=schema.get("properties",{})
        if not isinstance(properties,dict):
            raise RxSchemaSubsetError("properties_must_be_object:"+path)
        additional=schema.get("additionalProperties",True)
        for key,value in instance.items():
            if key in properties:
                validate(value,properties[key],path+"."+str(key))
            elif additional is False:
                raise RxSchemaSubsetError("additional_property_forbidden:%s.%s"%(path,key))
            elif isinstance(additional,dict):
                validate(value,additional,path+"."+str(key))
            elif additional is not True:
                raise RxSchemaSubsetError("unsupported_additionalProperties:"+path)

    if isinstance(instance,list):
        minimum=schema.get("minItems")
        if minimum is not None:
            if not isinstance(minimum,int) or minimum<0:
                raise RxSchemaSubsetError("invalid_minItems:"+path)
            if len(instance)<minimum:
                raise RxSchemaSubsetError("minItems_violation:"+path)
        item_schema=schema.get("items")
        if item_schema is not None:
            for index,value in enumerate(instance):
                validate(value,item_schema,"%s[%d]"%(path,index))

    return True
