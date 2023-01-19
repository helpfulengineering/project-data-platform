from functools import reduce
from typing import Iterable, NamedTuple

# Added SupplyAtom type. Defined as a NamedTuple
class SupplyAtom(NamedTuple):
    identifier: str
    description: str
    
    # only consider the identifier field when hashing or comparing
    def __hash__(self) -> int:
        return self.identifier.__hash__()
    def __eq__(self, __o: object) -> bool:
        return self.identifier == __o.identifier

# Product atoms
fabricMask = SupplyAtom("QH00001", "Fabric Mask")

# BOM atoms
nwpp = SupplyAtom("QH00002", "Non-woven Polypropylene bag")
biasTape = SupplyAtom("Q4902580", "Bias tape")
tinTie = SupplyAtom("QH00003", "Coffee tin tie")
pipeCleaner = SupplyAtom("Q3355092", "pipe cleaners")

# Tool Atoms
sewingMachine = SupplyAtom("Q49013", "Sewing machine")
scissors = SupplyAtom("Q40847", "Scissors")
pins = SupplyAtom("Q111591519", "Pins")
measuringTape = SupplyAtom("Q107196205", "Measuring Tape")

# BOM Output Atoms
scrapFabric = SupplyAtom("Q1378670", "Scrap Fabric")

# SupplyDesign maps to the original Supply and OKH types
# Note, this type currently it lacks the `eqn` field needed for cost calculation
class SupplyDesign(NamedTuple):
    product: SupplyAtom
    bom: frozenset[SupplyAtom]
    tools: frozenset[SupplyAtom]
    bomOutputs: frozenset[SupplyAtom]

    @property
    def outputs(self):
        return frozenset([self.product]).union(self.bomOutputs)

    @staticmethod
    def create(product: SupplyAtom, bom: Iterable[SupplyAtom], tools: Iterable[SupplyAtom], bomOutput: Iterable[SupplyAtom]):
        return SupplyDesign(product, frozenset(bom), frozenset(tools), frozenset(bomOutput))

maskDesign = SupplyDesign.create(
    fabricMask, 
    [nwpp, biasTape, tinTie, pipeCleaner], 
    [sewingMachine, scissors, pins, scissors],
    [scrapFabric])

# SupplyNetwork maps to the original SupplyNetwork type
# it stores supplies in a set instead of a list since we aren't tracking ammounts yet
# Also, it also stores a set of available tools as well as available supplies
class SupplyNetwork:
    def __init__(self, name: str, supplies: Iterable[SupplyAtom], tools: Iterable[SupplyAtom]) -> None:
        self.name = name
        self.supplies = set(supplies)
        self.tools = set(tools)
    def addSupply(self, item: SupplyAtom):
        self.supplies.add(item)
    def removeSupply(self, item: SupplyAtom):
        self.supplies.remove(item)
    def addTool(self, item: SupplyAtom):
        self.tools.add(item)
    def removeSupply(self, item: SupplyAtom):
        self.tools.remove(item)

    @staticmethod
    def union(a: 'SupplyNetwork', b: 'SupplyNetwork'):
        return SupplyNetwork(
            a.name + "|" + b.name,
            a.supplies.union(b.supplies),
            a.tools.union(b.tools)) 
    
    # goodTypes - not sure what to do with this
    # oneSUpply - doesn't appear to be used yet
    # allSupplies - doesn't appear to be used yet

jamesSpace = SupplyNetwork("James Maker Space", 
    [nwpp, biasTape, tinTie, pipeCleaner], 
    [sewingMachine, scissors, pins, measuringTape])
