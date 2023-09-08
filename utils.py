from typing import Sequence, Callable

def filter(seq: Sequence, predicate: Callable):
    matched = []
    for item in Sequence:
        if predicate(item):
            matched.append(item)
    return matched

def map(seq: Sequence, func: Callable):
    mapped = []
    for item in seq:
        mapped.append(func(item))
    return mapped

def unit_to_quantity(literal: str, ratio_dict: dict[str, float]) -> float:
    quantity, unit, *leftover = literal.split(" ")
    quantity = float(quantity)
    if unit not in ratio_dict:
        return quantity
    return quantity * ratio_dict[unit]

quantity_ratio = {
    "nghìn": 1e3,
    "triệu": 1e6,
    "tỷ": 1e9
}

area_ratio = {
    "cm2": 1e-4,
    "dm2": 1e-2,
    "m2": 1,
    "km2": 1e6
}
