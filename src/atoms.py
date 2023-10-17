import yaml
from typing import Generator, Iterable, NamedTuple, Protocol
import urllib.request
import json
import boto3
import botocore


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
        inventory: Iterable[SupplyAtom],
    ):
        return OkwParty(
            name, frozenset(supplies), frozenset(tools), frozenset(inventory)
        )

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

class InventorySupplyTree(NamedTuple):
    product: SupplyAtom
    maker: OkwParty

    def getProduct(self):
        return self.product

    def print(self, indent: int):
        buffer = " " * indent
        print(
            buffer
            + "Maker Inventory: {}/{}".format(self.supplier.name, self.product.description)
        )

    def forJson(self):
        return {
            "product": self.product.forJson(),
            "type": "inventory",
            # "party": self.maker.name,
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
            "bom": [x.forJson() for x in self.supplies],
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
                                supplies.append(InventorySupplyTree(bom, maker))
                            else:
                                for tree in self.query(bom):
                                    supplies.append(tree)

                        yield MadeSupplyTree(
                            product, design, maker, frozenset(supplies)
                        )
        if found == False:
            yield MissingSupplyTree(product)


config = botocore.client.Config(signature_version=botocore.UNSIGNED)
s3Client = boto3.client("s3", config=config)


def readBucketFolder(bucket: str, prefix: str, parseYaml):
    collection = []
    paginator = s3Client.get_paginator("list_objects_v2")
    iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    for page in iterator:
        for object in page["Contents"]:
            obj = s3Client.get_object(Bucket=bucket, Key=object["Key"])
            text = obj["Body"].read()
            yml = yaml.safe_load(text)
            collection.append(parseYaml(yml))
    return collection


bucket = "github-helpfulengineering-library"
okh_designs = readBucketFolder(bucket, "beta/okh", OkhDesign.parse)
okw_parties = readBucketFolder(bucket, "beta/okw", OkwParty.parse)

problemSpace = SupplyProblemSpace.create(okw_parties, okh_designs)

results = []
for supplyTree in problemSpace.query(okh_designs[0].product):
    results.append(supplyTree.forJson())

print(json.dumps(results))
