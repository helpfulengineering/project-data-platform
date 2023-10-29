from pydantic import BaseModel

from .validate import OKValidator


class OKH(BaseModel, extra="allow"):
    title: str
    bom: list[str]


class OKHValidator(OKValidator):
    def __init__(self):
        super().__init__(OKH)
