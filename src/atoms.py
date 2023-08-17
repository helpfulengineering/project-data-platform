import yaml
from typing import Generator, Iterable, NamedTuple, Protocol
import urllib.request
from ghapi.all import GhApi
import base64
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


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
    inventory: frozenset[SupplyAtom]

    @staticmethod
    def create(
        name: str, 
        supplies: Iterable[SupplyAtom], 
        tools: Iterable[SupplyAtom],
        inventory: Iterable[SupplyAtom]
    ):
        return OkwParty(name, frozenset(supplies), frozenset(tools), frozenset(inventory))

    @staticmethod
    def parse(yml):
        name = yml.get("title")
        supplies = SupplyAtom.parseArray(yml.get("supply-atoms"))
        tools = SupplyAtom.parseArray(yml.get("tool-list-atoms"))
        inventory = SupplyAtom.parseArray(yml.get("inventory-atoms"))
        return OkwParty.create(name, supplies, tools, inventory)

    @staticmethod
    def load(path: str):
        with openFileOrUrl(path) as file_stream:
            yml = yaml.safe_load(file_stream)
            return OkwParty.parse(yml)

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
    def parse(yml):
        name = yml.get("title")
        product = SupplyAtom.parse(yml.get("product-atom"))
        bom = SupplyAtom.parseArray(yml.get("bom-atoms"))
        tools = SupplyAtom.parseArray(yml.get("tool-list-atoms"))
        bomOutput = []  # SupplyAtom.parseArray(yml.get("bom-output-atoms"))
        return OkhDesign(name, product, bom, tools, bomOutput)

    @staticmethod
    def load(path: str):
        with openFileOrUrl(path) as file_stream:
            yml = yaml.safe_load(file_stream)
            return OkhDesign.parse(yml)


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
    parties: list[OkwParty]
    designs: list[OkhDesign]

    @staticmethod
    def create(parties: Iterable[OkwParty], designs: Iterable[OkhDesign]):
        return SupplyProblemSpace(list(parties), list(designs))

    def query(self, product: SupplyAtom) -> Generator[SupplyTree, None, None]:
        found = False
        # first, look for a supplier of the product being queried
        for supplier in self.parties:
            if product in supplier.supplies:
                found = True
                yield SuppliedSupplyTree(product, supplier)
        # next, look for a design for  the product being queried
        for design in self.designs:
            if design.product == product:
                # for each compatible design, look for a maker with the appropriate tools
                for maker in self.parties:
                    if maker.compatible(design.tools):
                        found = True
                        supplies = []

                        # find a supply tree for each bom in the design
                        for bom in design.bom:
                            if bom in maker.inventory:
                                supplies.append(SuppliedSupplyTree(bom, maker))
                            else:
                                for tree in self.query(bom):
                                    supplies.append(tree)

                        yield MadeSupplyTree(product, design, maker, frozenset(supplies))



                # for bom in design.bom:
                #     for tree in self.query(bom):
                #         trees.append(tree)
                # for maker in self.parties:
                #     if maker.compatible(design.tools):
                #         found = True
                #         yield MadeSupplyTree(product, design, maker, frozenset(trees))
        if found == False:
            yield MissingSupplyTree(product)

okh_designs = []
okw_parties = []

account_url = "https://helpfulprojectdatatemp.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url)
library_client = blob_service_client.get_container_client("library")

okh_blobs = library_client.list_blobs(name_starts_with="beta/okh")
for okh_blob in okh_blobs:
    blob_client = blob_service_client.get_blob_client(container="library", blob=okh_blob)
    downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
    blob_text = downloader.readall()
    yml = yaml.safe_load(blob_text)
    okh = OkhDesign.parse(yml)
    okh_designs.append(okh)

okw_blobs = library_client.list_blobs(name_starts_with="beta/okw")
for okh_blob in okw_blobs:
    blob_client = blob_service_client.get_blob_client(container="library", blob=okh_blob)
    downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
    blob_text = downloader.readall()
    yml = yaml.safe_load(blob_text)
    okw = OkwParty.parse(yml)
    okw_parties.append(okw)

problemSpace = SupplyProblemSpace.create(okw_parties, okh_designs)

for t in problemSpace.query(okh_designs[0].product):
    # print(json.dumps(t.forJson()))
    t.print(0)


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
# fabricMask = SupplyAtom("QH00001", "Fabric Mask")

# # BOM atoms
# nwpp = SupplyAtom("QH00002", "Non-woven Polypropylene bag")
# biasTape = SupplyAtom("Q4902580", "Bias tape")
# tinTie = SupplyAtom("QH00003", "Coffee tin tie")
# pipeCleaner = SupplyAtom("Q3355092", "pipe cleaners")

# # Tool Atoms
# sewingMachine = SupplyAtom("Q49013", "Sewing machine")
# scissors = SupplyAtom("Q40847", "Scissors")
# pins = SupplyAtom("Q111591519", "Pins")
# measuringTape = SupplyAtom("Q107196205", "Measuring Tape")

# # BOM Output Atoms
# scrapFabric = SupplyAtom("Q1378670", "Scrap Fabric")

# # Chair sample

# # Product atoms
# chair = SupplyAtom("Q15026", "chair")
# chairLeg = SupplyAtom("QH100", "chair leg")
# chairSeat = SupplyAtom("QH101", "chair seat")
# chairBack = SupplyAtom("QH102", "chair back")

# # BOM atoms
# fabric = SupplyAtom("QH103", "fabric")
# wood = SupplyAtom("QH104", "wood")
# stuffing = SupplyAtom("QH105", "stuffing")
# upholstery = SupplyAtom("QH106", "upholstery")
# frame = SupplyAtom("QH107", "frame")
# nails = SupplyAtom("QH108", "nails")

# # Tool Atoms
# plane = SupplyAtom("Q204260", "plane")
# lathe = SupplyAtom("Q187833", "lathe")
# hammer = SupplyAtom("Q25294", "hammer")
# saw = SupplyAtom("Q125356", "saw")

# # designs

# chairDesign = OkhDesign.create(
#     "Funky Chair Design", chair, [chairLeg, chairSeat, chairBack, nails], [hammer], []
# )

# legDesign = OkhDesign.create("Leg Design", chairLeg, [wood], [lathe], [])

# seatDesign1 = OkhDesign.create("Seat Design 1", chairSeat, [fabric], [plane], [])

# seatDesign2 = OkhDesign.create(
#     "Seat Design 2", chairSeat, [frame, stuffing, upholstery], [sewingMachine], []
# )

# supplierRaw = OkwParty.create(
#     "raw supplies",
#     [nwpp, biasTape, tinTie, pipeCleaner, fabric, wood, upholstery, frame, nails],
#     [],
# )
# supplierRobert = OkwParty.create("Robert's Chair Parts", [chairBack, chairLeg], [])
# makerJames = OkwParty.create(
#     "James Maker Space", [], [sewingMachine, scissors, pins, measuringTape]
# )
# makerHarry = OkwParty.create("Devhawk Engineering", [], [hammer, lathe, plane])

# maskDesign = OkhDesign.create(
#     "Surge Mask",
#     fabricMask,
#     [nwpp, biasTape, tinTie, pipeCleaner],
#     [sewingMachine, scissors, pins, scissors],
#     [scrapFabric],
# )

# problemSpace = SupplyProblemSpace.create(
#     [supplierRaw, supplierRobert, makerJames, makerHarry],
#     [maskDesign, chairDesign, seatDesign1, seatDesign2, legDesign],
# )

# for t in problemSpace.query(chair):
#     print(json.dumps(t.forJson()))
