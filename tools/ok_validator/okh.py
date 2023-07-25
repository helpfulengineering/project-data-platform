from .validate import OKValidator

__REQUIRED_FIELDS__ = [
    "bom",
    "tools",
    "title",
    "description",
    "intended-output",
    "intended-use"
]

class OKHValidator(OKValidator):

    def __int__(self):
        super().__init__(__REQUIRED_FIELDS__)
