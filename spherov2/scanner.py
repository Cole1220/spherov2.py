import importlib
from functools import partial
from typing import List, Type

from spherov2.toy.core import Toy
from spherov2.toy.r2d2 import R2D2
from spherov2.toy.r2q5 import R2Q5


class ToyNotFoundError(Exception):
    ...


def all_toys(cls=Toy):
    subtypes = cls.__subclasses__()
    yield cls
    for sub in subtypes:
        yield from all_toys(sub)


def find_toys(timeout=5.0, toy_types: List[Type[Toy]] = None, adapter=None):
    if adapter is None:
        adapter = importlib.import_module('spherov2.adapter.bleak').BleakAdaptor
    toys = adapter.scan_toys(timeout)
    if toy_types is None:
        toy_types = all_toys()
    ret = []
    for toy_cls in toy_types:
        for toy in toys:
            toy_type = toy_cls.toy_type
            if toy.name.startswith(toy_type.filter_prefix) and \
                    (toy_type.prefix is None or toy.name.startswith(toy_type.prefix)):
                ret.append(toy_cls(toy.address, adapter))
    return ret


def find_toy(*args, **kwargs):
    toys = find_toys(*args, **kwargs)
    if not toys:
        raise ToyNotFoundError
    return toys[0]


find_R2D2 = partial(find_toy, toy_types=[R2D2])
find_R2Q5 = partial(find_toy, toy_types=[R2Q5])
