import yaml
from typing import Generator, Iterable, NamedTuple, Protocol
import urllib.request
from ghapi.all import GhApi
import base64
import json


def openFileOrUrl(path: str):
    if path.startswith("http"):
        return urllib.request.urlopen(path)
    else:
        return open(path, "rb")


class SupplyAtom(NamedTuple):
    identifier: str
    description: str
    # link: str

    # only consider the identifier field when hashing or comparing
    def __hash__(self) -> int:
        return self.identifier.__hash__()

    def __eq__(self, __o: object) -> bool:
        return self.identifier == __o.identifier

    def forJson(self):
        return {"id": self.identifier, "desc": self.description}

    @staticmethod
    def parse(yml):
        identifier = yml.get("identifier")
        if identifier == None:
            raise ValueError("missing SupplyAtom identifier")
        description = yml.get("description")
        # link = yml.get("link")
        return SupplyAtom(identifier, description)  # , link)

    @staticmethod
    def parseArray(yml):
        atoms = []
        if yml == None:
            return atoms
        for i in range(len(yml)):
            atom = SupplyAtom.parse(yml[i])
            atoms.append(atom)
        return atoms


class OkwParty(NamedTuple):
    name: str
    supplies: frozenset[SupplyAtom]
    tools: frozenset[SupplyAtom]

    @staticmethod
    def create(name: str, supplies: Iterable[SupplyAtom], tools: Iterable[SupplyAtom]):
        return OkwParty(name, frozenset(supplies), frozenset(tools))

    @staticmethod
    def parse(path: str):
        with openFileOrUrl(path) as file_stream:
            yml = yaml.safe_load(file_stream)
            name = yml.get("title")
            supplies = SupplyAtom.parseArray(yml.get("supply-atoms"))
            tools = SupplyAtom.parseArray(yml.get("tool-list-atoms"))
            return OkwParty.create(name, supplies, tools)

    def compatible(self, tools: Iterable[SupplyAtom]):
        # assume that a party w/o tools is not a maker and therefore not compatible with any design
        if len(tools) == 0:
            return False
        for tool in tools:
            if tool not in self.tools:
                return False
        return True


class OkhDesign(NamedTuple):
    name: str
    product: SupplyAtom
    bom: frozenset[SupplyAtom]
    tools: frozenset[SupplyAtom]
    bomOutputs: frozenset[SupplyAtom]

    @staticmethod
    def create(
        name: str,
        product: SupplyAtom,
        bom: Iterable[SupplyAtom],
        tools: Iterable[SupplyAtom],
        bomOutput: Iterable[SupplyAtom],
    ):
        return OkhDesign(
            name, product, frozenset(bom), frozenset(tools), frozenset(bomOutput)
        )

    @staticmethod
    def slurp(path: str):
        with openFileOrUrl(path) as file_stream:
            yml = yaml.safe_load(file_stream)
            name = yml.get("title")
            product = SupplyAtom.parse(yml.get("product-atom"))
            bom = SupplyAtom.parseArray(yml.get("bom-atoms"))
            tools = SupplyAtom.parseArray(yml.get("tool-list-atoms"))
            bomOutput = []  # SupplyAtom.parseArray(yml.get("bom-output-atoms"))
            return OkhDesign(name, product, bom, tools, bomOutput)


class SupplyTree(Protocol):
    def getProduct() -> SupplyAtom:
        ...

    def print(indent: int):
        ...

    def forJson():
        ...


class SuppliedSupplyTree(NamedTuple):
    product: SupplyAtom
    supplier: OkwParty

    def getProduct(self):
        return self.product

    def print(self, indent: int):
        buffer = " " * indent
        print(
            buffer
            + "Supplier: {}/{}".format(self.supplier.name, self.product.description)
        )

    def forJson(self):
        return {
            "product": self.product.forJson(),
            "type": "supplied",
            "party": self.supplier.name,
        }


class MadeSupplyTree(NamedTuple):
    product: SupplyAtom
    design: OkhDesign
    maker: OkwParty
    supplies: frozenset[SupplyTree]

    def getProduct(self):
        return self.product

    def print(self, indent: int):
        buffer = " " * indent
        print(buffer + "Maker: {}/{}".format(self.maker.name, self.design.name))
        for s in self.supplies:
            s.print(indent + 4)
    def forJson(self):
        return {
            "product": self.product.forJson(),
            "type": "made",
            "party": self.maker.name,
            "design": self.design.name,
            "bom": [x.forJson() for x in self.supplies]
        }


class MissingSupplyTree(NamedTuple):
    product: SupplyAtom

    def getProduct(self):
        return self.product

    def print(self, indent: int):
        buffer = " " * indent
        print(buffer + "Missing:  {}".format(self.product.description))

    def forJson(self):
        return {"product": self.product.forJson(), "type": "missing"}


class SupplyProblemSpace(NamedTuple):
    parties: frozenset[OkwParty]
    designs: frozenset[OkhDesign]

    @staticmethod
    def create(parties: Iterable[OkwParty], designs: Iterable[OkhDesign]):
        return SupplyProblemSpace(frozenset(parties), frozenset(designs))

    def query(self, product: SupplyAtom) -> Generator[SupplyTree, None, None]:
        found = False
        for supplier in self.parties:
            for supply in supplier.supplies:
                if supply == product:
                    found = True
                    yield SuppliedSupplyTree(product, supplier)
        for design in self.designs:
            if design.product == product:
                trees = []
                for bom in design.bom:
                    for tree in self.query(bom):
                        trees.append(tree)
                for maker in self.parties:
                    if maker.compatible(design.tools):
                        found = True
                        yield MadeSupplyTree(product, design, maker, frozenset(trees))
        if found == False:
            yield MissingSupplyTree(product)


# # Sample code that demonstrates how to use the GhApi library to read files from GitHub

# # create a ghapi client for the helpfulengineering/library repo
# api = GhApi(owner='helpfulengineering', repo='library')
# # get the main branch
# ref = api.git.get_ref('heads/main')
# # get the commit for the main branch
# commit = api.git.get_commit(ref.object.sha)
# # get the tree for the commit
# tree = api.git.get_tree(commit.tree.sha)
# # find the root README.md blob ref
# readmeItem = next(filter(lambda x: x.path == "README.md", tree.tree.items))
# # get the blob for the README.md
# readmeBlob = api.git.get_blob(readmeItem.sha)
# # decode the blob's base64 encoded content
# readmeContent = base64.b64decode(readmeBlob.content)

# # todo:
# #  get a list of all the .yaml files in the beta/okw and beta/okh folders
# #  and slurp each of them a the appropriate type


# #Slurp Sample
# helpfulChair = OkhDesign.slurp("https://raw.githubusercontent.com/helpfulengineering/library/main/alpha/okh/okh-chair-helpful.yml")
# devhawkMaker = slurpOKW("https://raw.githubusercontent.com/helpfulengineering/library/main/alpha/okw/DevhawkEngineering.okw.yml")
# chairPartSupplier = slurpOKW("https://raw.githubusercontent.com/helpfulengineering/library/main/alpha/okw/ChairParts.okw.yml")

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

# Chair sample

# Product atoms
chair = SupplyAtom("Q15026", "chair")
chairLeg = SupplyAtom("QH100", "chair leg")
chairSeat = SupplyAtom("QH101", "chair seat")
chairBack = SupplyAtom("QH102", "chair back")

# BOM atoms
fabric = SupplyAtom("QH103", "fabric")
wood = SupplyAtom("QH104", "wood")
stuffing = SupplyAtom("QH105", "stuffing")
upholstery = SupplyAtom("QH106", "upholstery")
frame = SupplyAtom("QH107", "frame")
nails = SupplyAtom("QH108", "nails")

# Tool Atoms
plane = SupplyAtom("Q204260", "plane")
lathe = SupplyAtom("Q187833", "lathe")
hammer = SupplyAtom("Q25294", "hammer")
saw = SupplyAtom("Q125356", "saw")

# designs

chairDesign = OkhDesign.create(
    "Funky Chair Design", chair, [chairLeg, chairSeat, chairBack, nails], [hammer], []
)

legDesign = OkhDesign.create("Leg Design", chairLeg, [wood], [lathe], [])

seatDesign1 = OkhDesign.create("Seat Design 1", chairSeat, [fabric], [plane], [])

seatDesign2 = OkhDesign.create(
    "Seat Design 2", chairSeat, [frame, stuffing, upholstery], [sewingMachine], []
)

supplierRaw = OkwParty.create(
    "raw supplies",
    [nwpp, biasTape, tinTie, pipeCleaner, fabric, wood, upholstery, frame, nails],
    [],
)
supplierRobert = OkwParty.create("Robert's Chair Parts", [chairBack, chairLeg], [])
makerJames = OkwParty.create(
    "James Maker Space", [], [sewingMachine, scissors, pins, measuringTape]
)
makerHarry = OkwParty.create("Devhawk Engineering", [], [hammer, lathe, plane])

maskDesign = OkhDesign.create(
    "Surge Mask",
    fabricMask,
    [nwpp, biasTape, tinTie, pipeCleaner],
    [sewingMachine, scissors, pins, scissors],
    [scrapFabric],
)

problemSpace = SupplyProblemSpace.create(
    [supplierRaw, supplierRobert, makerJames, makerHarry],
    [maskDesign, chairDesign, seatDesign1, seatDesign2, legDesign],
)

for t in problemSpace.query(chair):
    print(json.dumps(t.forJson()))
