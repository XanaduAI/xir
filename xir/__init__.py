from pathlib import Path

from lark import lark

from ._version import __version__
from .decimal_complex import DecimalComplex
from .parser import Transformer
from .program import Declaration, ObservableFactor, ObservableStmt, Program, Statement
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


def _read_lark_file() -> str:
    """Reads the contents of the XIR Lark grammar file."""
    path = Path(__file__).parent / "xir.lark"
    with path.open("r") as file:
        return file.read()


def parse_script(script: str, debug: bool = False, **kwargs) -> Program:
    """
    Parses an XIR script into a structured :class:`xir.Program`.

    Args:
        script (str): xir script as a string.
        debug (bool): if false lark tree building will be skipped, and lark rule collisions will not be
        given a warning.
        kwargs: options to be passed to the transformer.
    """

    if debug:
        parser = lark.Lark(
            grammar=_read_lark_file(),
            maybe_placeholders=True,
            start="program",
            parser="lalr",
            debug=True,
        )
        tree = parser.parse(script)
        return Transformer(**kwargs).transform(tree)
    else:
        parser = lark.Lark(
            grammar=_read_lark_file(),
            maybe_placeholders=True,
            start="program",
            parser="lalr",
            debug=False,
            transformer=Transformer(**kwargs),
        )
        return parser.parse(script)
