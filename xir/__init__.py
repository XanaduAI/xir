from lark import lark

from ._version import __version__
from .decimal_complex import DecimalComplex
from .parser import Transformer, read_lark_file
from .program import Declaration, ObservableStmt, Program, Statement, ObservableFactor
from .validator import Validator

__all__ = [
    "DecimalComplex",
    "Declaration",
    "ObservableFactor",
    "ObservableStmt",
    "Program",
    "Statement",
    "Transformer",
]


def parse_script(script: str, debug=True, **kwargs) -> Program:
    """Parses an XIR script into a structured :class:`xir.Program`."""
    if debug:
        parser = lark.Lark(
            grammar=read_lark_file(),
            maybe_placeholders=True,
            start="program",
            parser="lalr",
            debug=True
        )
        tree = parser.parse(script)
        return Transformer(**kwargs).transform(tree)
    else:
        parser = lark.Lark(
            grammar=read_lark_file(),
            maybe_placeholders=True,
            start="program",
            parser="lalr",
            transformer=Transformer(**kwargs)
        )
        return parser.parse(script)
