from ._version import __version__
from .decimal_complex import DecimalComplex
from .parser import Transformer, parser
from .program import Declaration, ObservableStmt, Program, Statement
from .validator import Validator

__all__ = ["DecimalComplex", "Declaration", "ObservableStmt", "Program", "Statement", "Transformer"]


def parse_script(script: str, **kwargs) -> Program:
    """Parses an XIR script into a structured :class:`xir.Program`."""
    tree = parser.parse(script)
    return Transformer(**kwargs).transform(tree)
