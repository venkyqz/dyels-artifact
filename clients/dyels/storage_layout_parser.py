from typing import Literal, Any
import argparse
from pydantic import BaseModel, ConfigDict, ValidationError, Field
from enum import Enum

class VarDef(BaseModel):
    astId: int
    contract: str
    label: str
    offset: int
    slot: str
    type: str

class TypeDef(BaseModel):
    encoding: str
    label: str
    numberOfBytes: str

class ValueTypeDef(TypeDef):
    encoding: Literal['inplace']

class BytesTypeDef(TypeDef):
    encoding: Literal['bytes']

class MappingTypeDef(TypeDef):
    encoding: Literal['mapping']
    key: str
    value: str

class StructTypeDef(TypeDef):
    encoding: Literal['inplace']
    members: list[VarDef]

class ArrayTypeDef(TypeDef):
    encoding: Literal['dynamic_array']
    base: str

class ConstArrayTypeDef(TypeDef):
    encoding: Literal['inplace']
    base: str

class Delivery(BaseModel):
    model_config = ConfigDict(strict=True)

    storage: list[VarDef]
    types: dict[str, ValueTypeDef | MappingTypeDef | StructTypeDef | ArrayTypeDef | BytesTypeDef | ConstArrayTypeDef] | None

class ComparisonKind(Enum):
    STRUCTURES_ONLY = 1
    WITH_ANY = 2
    STRICT = 3


def parse_storage_model(filaname: str):
    json_data = open(filaname, "r").read()
    if json_data == "{}":
        json_data = "{\"storage\": [], \"types\": {}}"

    # print(json_data)

    model = Delivery.model_validate_json(json_data)

    return model

def proccess_def_list(def_list: list[VarDef], types_defs1: dict[str, TypeDef]):
    slot_info = dict()
    for stor_var in def_list:
        slot = stor_var.slot
        type_info = types_defs1[stor_var.type]
        if type(type_info) == ValueTypeDef:
            if slot not in slot_info:
                slot_info[slot] = dict()

            if stor_var.offset in slot_info[slot]:
                # Adding it so we get a FP when 2 vars start at the same offset, instead of overwritting
                slot_info[slot][32 + stor_var.offset] = type_info
            else:
                if isinstance(slot_info[slot], ConstArrayTypeDef):
                    # conflict, fix crash and report analysis failure, will need to handle properly in the future
                    slot_info[slot] = {0: slot_info[slot]}
                slot_info[slot][stor_var.offset] = type_info
            # print(model.types[stor_var.type])
        elif type(type_info) == StructTypeDef:
            in_types = proccess_def_list(type_info.members, types_defs1)
            print(f"Slot {slot} is struct {in_types}")

            for i in in_types.keys():
                slot_info[str(int(slot) + int(i))] = in_types[i]
        else:
            slot_info[slot] = type_info

    return slot_info

def get_constant_slot_info(model: Delivery):
    print(proccess_def_list(model.storage, model.types))
    print()
    print(model.types)
    return proccess_def_list(model.storage, model.types)

def get_composite_slot_info(model: Delivery):
    slot_info = dict()
    for stor_var in model.storage:
        slot = stor_var.slot
        type = stor_var.type
        model.types[stor_var.type]
        # print(stor_var)
        type_info = model.types[type]
        if type_info.encoding != 'inplace':
            slot_info[slot] = type_info
    print(slot_info)

    return slot_info

def compare_types(type1: TypeDef | dict[str, TypeDef], types_defs1: dict[str, TypeDef], type2: TypeDef | dict[str, TypeDef], types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    if type(type1) != type(type2):
        ## Special case: struct with a single field
        if type(type1) == StructTypeDef and type(type2) == ValueTypeDef and len(type1.members) == 1:
            return compare_value_types(types_defs1[type1.members[0].type], types_defs1, type2, types_defs2, comparison_kind)
        return False


    if type(type1) == dict:
        return compare_type_dicts(type1, types_defs1, type2, types_defs2, comparison_kind)
    elif type(type1) == ValueTypeDef:
        return compare_value_types(type1, types_defs1, type2, types_defs2, comparison_kind)
    elif type(type1) == ArrayTypeDef:
        return compare_arrays(type1, types_defs1, type2, types_defs2, comparison_kind)
    elif type(type1) == MappingTypeDef:
        return compare_mappings(type1, types_defs1, type2, types_defs2, comparison_kind)
    elif type(type1) == StructTypeDef:
        return compare_structs(type1, types_defs1, type2, types_defs2, comparison_kind)
    elif type(type1) == ConstArrayTypeDef:
        return compare_const_arrays(type1, types_defs1, type2, types_defs2, comparison_kind)
    else:
        return True

def compare_type_dicts(dict1: dict[str, TypeDef], types_defs1: dict[str, TypeDef], dict2: dict[str, TypeDef], types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    if len(dict1) != len(dict2):
        return False
    for offset in dict1.keys():
        if not (offset in dict2 and compare_value_types(dict1[offset], types_defs1, dict2[offset], types_defs2, comparison_kind)):
            return False
    return True

def compare_value_types(value_type1: ValueTypeDef, types_defs1: dict[str, TypeDef], value_type2: ValueTypeDef, types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    if comparison_kind == ComparisonKind.STRUCTURES_ONLY:
        return value_type1.numberOfBytes == value_type2.numberOfBytes
    # We consider address payable and address to be the same type, we may want to reconsider

    label1 = value_type1.label
    if value_type1.label.startswith("enum"):
        label1 = "uint8"
    if (value_type1.label == "address payable" or value_type1.label.startswith("contract")):
        label1 = "address"
    if comparison_kind == ComparisonKind.WITH_ANY and value_type2.label == "bytes32/(u)int256" and value_type1.label in ["bytes32", "uint256", "int256"]:
        return True
    return label1 == value_type2.label

def compare_arrays(array1: ArrayTypeDef, types_defs1: dict[str, TypeDef], array2: ArrayTypeDef, types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    if array1.base not in types_defs1 or array2.base not in types_defs2:
        return False

    return compare_types(types_defs1[array1.base], types_defs1, types_defs2[array2.base], types_defs2, comparison_kind)

def compare_mappings(map1: MappingTypeDef, types_defs1: dict[str, TypeDef], map2: MappingTypeDef, types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    if (map1.key not in types_defs1 or map2.key not in types_defs2
        or map1.value not in types_defs1 or map2.value not in types_defs2):
        print(f"NOT FOUND {map1.key} {map1.value} {types_defs1}   OR {map2.key} {map2.value} {types_defs2}")
        return False

    if not compare_types(types_defs1[map1.key], types_defs1, types_defs2[map2.key], types_defs2, comparison_kind):
        print(f"FAILED FOR {types_defs1[map1.key]}    {types_defs2[map2.key]}")
    if not compare_types(types_defs1[map1.value], types_defs1, types_defs2[map2.value], types_defs2, comparison_kind):
        print(f"FAILED for {types_defs1[map1.value]}    {types_defs2[map2.value]}")
    return (compare_types(types_defs1[map1.key], types_defs1, types_defs2[map2.key], types_defs2, comparison_kind)
            and compare_types(types_defs1[map1.value], types_defs1, types_defs2[map2.value], types_defs2, comparison_kind))


def compare_structs(struct1: StructTypeDef, types_defs1: dict[str, TypeDef], struct2: StructTypeDef, types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    processed1 = proccess_def_list(struct1.members, types_defs1)
    processed2 = proccess_def_list(struct2.members, types_defs2)

    for slot in processed1.keys():
        if slot not in processed2:
            # todo handle this, perhaps leave it like this, in the spirit of missing
            continue
        else:
            if not compare_types(processed1[slot], types_defs1, processed2[slot], types_defs2, comparison_kind):
                print(f"Failed struct type equality for fields {processed1[slot]}, {processed2[slot]}")
                return False

    return True

def compare_const_arrays(array1: ConstArrayTypeDef, types_defs1: dict[str, TypeDef], array2: ConstArrayTypeDef, types_defs2: dict[str, TypeDef], comparison_kind: ComparisonKind=ComparisonKind.STRICT):
    if array1.base not in types_defs1 or array2.base not in types_defs2:
        return False

    if array1.numberOfBytes != array2.numberOfBytes:
        return False

    return compare_types(types_defs1[array1.base], types_defs1, types_defs2[array2.base], types_defs2, comparison_kind)


def compare_storage_layouts(ground_truth_file: str, inferred_file: str):
    print("")
    print(f"====================================== GROUND TRUTH ======================================")
    ground_truth_model = parse_storage_model(ground_truth_file)
    ground_truth_slot_info = get_constant_slot_info(ground_truth_model)

    print("")
    print(f"====================================== ANALYSIS RESULT ======================================")
    inferred_model = parse_storage_model(inferred_file)
    inferred_slot_info = get_constant_slot_info(inferred_model)

    success = set()
    needs_any_type = set()
    structure_success = set()
    fail = set()
    analysis_missing = set()
    solc_missing = set(inferred_slot_info.keys() - ground_truth_slot_info.keys())

    for slot, typeOrDict in ground_truth_slot_info.items():
        if slot not in inferred_slot_info:
            analysis_missing.add(slot)
            continue
        elif compare_types(typeOrDict, ground_truth_model.types, inferred_slot_info[slot], inferred_model.types, ComparisonKind.WITH_ANY):
            success.add(slot)
            structure_success.add(slot)
            if not compare_types(typeOrDict, ground_truth_model.types, inferred_slot_info[slot], inferred_model.types, ComparisonKind.STRICT):
                needs_any_type.add(slot)
            continue
        elif compare_types(typeOrDict, ground_truth_model.types, inferred_slot_info[slot], inferred_model.types, ComparisonKind.STRUCTURES_ONLY):
            structure_success.add(slot)
            continue
        else:
            fail.add(slot)

    print(f"Success for: {success}")
    print(f"Needs any type: {needs_any_type}")
    print(f"Strict Failed for: {fail.union(structure_success - success)}")
    print(f"Partial Success for: {structure_success}")
    print(f"Partial Failed for: {fail}")
    print(f"Analysis Missing for: {analysis_missing}")
    print(f"Compiler Missing for: {solc_missing}")

    return success, structure_success, fail, analysis_missing, solc_missing, needs_any_type

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A batch analyzer for EVM bytecode programs."
    )

    parser.add_argument(
        '--parse',
        nargs=1,
        metavar='filepath',
        # help='Compares ground truth with analysis inferrences.',
    )
    parser.add_argument(
        '-c',
        '--compare',
        nargs=2,
        metavar=('ground_truth', 'inferred'),
        help='Compares ground truth with analysis inferrences.',
    )

    args = parser.parse_args()

    if args.parse:
        filepath, = args.parse
        print(filepath)
        model = parse_storage_model(filepath)
        print(model)
        slot_info = get_constant_slot_info(model)

    if args.compare:
        ground_truth, inferred = args.compare
        compare_storage_layouts(ground_truth, inferred)