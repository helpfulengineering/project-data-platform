from .validate import OKValidator

__REQUIRED_FIELDS__ = [
    "bom",
    "title",
]


class OKHValidator(OKValidator):
    def __init__(self):
        super().__init__(__REQUIRED_FIELDS__)
