from functools import reduce
import itertools
from typing import Generator, Iterable, NamedTuple, Protocol
from collections.abc import Sized

class SupplyAtom(NamedTuple):
    identifier: str
    description: str

    # only consider the identifier field when hashing or comparing
    def __hash__(self) -> int:
        return self.identifier.__hash__()
    def __eq__(self, __o: object) -> bool:
        return self.identifier == __o.identifier

class Supplier(NamedTuple):
    name: str
    supplies: frozenset[SupplyAtom]
    
    @staticmethod
    def create(name: str, supplies: Iterable[SupplyAtom]):
        return Supplier(name, frozenset(supplies))


class Maker(NamedTuple):
    name: str
    tools: frozenset[SupplyAtom]

    @staticmethod
    def create(name: str, tools: Iterable[SupplyAtom]):
        return Maker(name, frozenset(tools))

    def compatible(self, tools: Iterable[SupplyAtom]):
        for tool in tools:
            if tool not in self.tools:
                return False
        return True

class ProductDesign(NamedTuple):
    product: SupplyAtom
    bom: frozenset[SupplyAtom]
    tools: frozenset[SupplyAtom]
    bomOutputs: frozenset[SupplyAtom]

    @staticmethod
    def create(product: SupplyAtom, bom: Iterable[SupplyAtom], tools: Iterable[SupplyAtom], bomOutput: Iterable[SupplyAtom]):
        return ProductDesign(product, frozenset(bom), frozenset(tools), frozenset(bomOutput))

class SupplyTree(Protocol):
    def getProduct() -> SupplyAtom:
        ...
    def print(indent:int):
        ...

class SupplierSupplyTree(NamedTuple):
    product: SupplyAtom
    supplier: Supplier

    def getProduct(self):
        return self.product

    def print(self, indent: int):
        buffer = ' ' * indent
        print(buffer + "Supplier: {}/{}".format(self.supplier.name, self.product.description))

class MakerSupplyTree(NamedTuple):
    product: SupplyAtom
    design: ProductDesign
    maker: Maker
    supplies: frozenset[SupplyTree]

    def getProduct(self):
        return self.product

    def print(self, indent: int):
        buffer = ' ' * indent
        print(buffer + "Maker: {}/{}".format(self.maker.name, self.design.product.description))
        for s in self.supplies:
            s.print(indent + 1)

class SupplyProblemSpace(NamedTuple):
    suppliers: frozenset[Supplier]
    makers: frozenset[Maker]
    designs: frozenset[ProductDesign]

    @staticmethod
    def create(suppliers: Iterable[Supplier], makers: Iterable[Maker], designs: Iterable[ProductDesign]):
        return SupplyProblemSpace(frozenset(suppliers), frozenset(makers), frozenset(designs))

    def query(self, product: SupplyAtom) -> Generator[SupplyTree, None, None]:
        for supplier in self.suppliers:
            for supply in supplier.supplies:
                if supply == product:
                    yield SupplierSupplyTree(product, supplier)
        for design in self.designs:
            if design.product == product:
                foo = map(lambda b: self.query(b), design.bom)
                inputs = frozenset(itertools.chain.from_iterable(foo))
                for maker in self.makers:
                    if maker.compatible(design.tools):
                        yield MakerSupplyTree(product, design, maker, inputs)


# Mask Sample

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

supplierRaw = Supplier.create("raw supplies",  [nwpp, biasTape, tinTie, pipeCleaner])
makerJames = Maker.create("James Maker Space", [sewingMachine, scissors, pins, measuringTape])
designMask = ProductDesign.create(
    fabricMask, 
    [nwpp, biasTape, tinTie, pipeCleaner], 
    [sewingMachine, scissors, pins, scissors],
    [scrapFabric])

problemSpace = SupplyProblemSpace.create([supplierRaw], [makerJames], [designMask])
for t in problemSpace.query(fabricMask):
    t.print(0)
