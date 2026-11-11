#!/usr/bin/env python3
import json
import os

 
def produce_storage_layout(inferred_names: dict[str, str] | None =None):
    """
      Reads 3 json files output by our datalog logic, performs minor transformations
      to produce a valid (solc-compatible) storage layout json file
    """
    if inferred_names == None:
        inferred_names = dict()

    if not os.path.exists("StorageDecls.json"):
        # identify previous analysis timeout.
        with open('inferred-storage-layout.json', 'w') as f:
            json.dump(dict(), f)
        exit(0)

    storage_decls = json.load(open('StorageDecls.json', 'r'))

    if inferred_names is not None:
        for decl in storage_decls:
            if decl["label"] in inferred_names:
                decl["label"] = inferred_names[decl["label"]]
    # print(inferred_names)
    # print(storage_decls)

    # print("Type info:")
    type_decls = json.load(open('UsedType.json', 'r'))


    struct_field_info = json.load(open('StructFieldTypeInfo.json', 'r'))
    # print("Struct field info:")
    # print(struct_field_info)

    struct_fields = dict()
    for entry in struct_field_info:
        struct_id = entry['structId']
        del entry['structId']
        if struct_id not in struct_fields:
            struct_fields[struct_id] = []
        struct_fields[struct_id].append(entry)
        # print(struct_id, entry)

    # print(struct_fields)
    # print("======================================================================")

    # print("======================================================================")


    type_decls_filtered = dict()
    for type in type_decls:
        type_id = type["typeId"]
        type_info = type["typeInfo"]
        type_kind = type_info["kind"]

        del type_info["kind"]

        if type_kind == "value":
            del type_info["base"]
            del type_info["key"]
            del type_info["value"]
        elif type_kind == "struct":
            del type_info["base"]
            del type_info["key"]
            del type_info["value"]
            type_info["members"] = struct_fields.get(type_id, [])
        elif type_kind == "dynamic_array":
            del type_info["key"]
            del type_info["value"]
        elif type_kind == "mapping":
            del type_info["base"]
        elif type_kind == "bytes":
            del type_info["base"]
            del type_info["key"]
            del type_info["value"]
        elif type_kind == "static_array":
            del type_info["key"]
            del type_info["value"]


        type_decls_filtered[type_id] = type_info

        # print(type_id, type_info)

    output = dict()
    output["storage"] = storage_decls
    output["types"] = type_decls_filtered

    with open('inferred-storage-layout.json', 'w') as f:
        json.dump(output, f)

if __name__ == "__main__":
    produce_storage_layout()