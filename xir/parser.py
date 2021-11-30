"""This module contains the :class:`xir.Transformer` class and the XIR parser."""
import math
from decimal import Decimal
from pathlib import Path

import lark

from .decimal_complex import DecimalComplex
from .program import Declaration, ObservableStmt, Program, Statement
from .utils import simplify_math


def _read_lark_file() -> str:
    """Reads the contents of the XIR Lark grammar file."""
    path = Path(__file__).parent / "xir.lark"
    with path.open("r") as file:
        return file.read()


parser = lark.Lark(grammar=_read_lark_file(), start="program", parser="lalr")


class Transformer(lark.Transformer):
    """Transformer for processing the Lark parse tree.

    Transformers visit each node of the tree, and run the appropriate method on it according to the
    node's data. All method names mirror the corresponding symbols from the grammar.

    Keyword args:
        eval_pi (bool): Whether pi should be evaluated and stored as a float
            instead of symbolically as a string. Defaults to ``False``.
        use_floats (bool): Whether floats and complex types are returned instead of ``Decimal``
            and ``DecimalComplex`` objects. Defaults to ``True``.
    """

    def __init__(self, *args, **kwargs):
        self._eval_pi = kwargs.pop("eval_pi", False)
        self._use_floats = kwargs.pop("use_floats", True)

        self._program = Program()
        super().__init__(*args, **kwargs)

    @property
    def eval_pi(self) -> bool:  # pylint: disable=used-before-assignment
        """Reports whether pi is evaluated and stored as a float."""
        return self._eval_pi

    @property
    def use_floats(self) -> bool:
        """Reports whether floats and complex types are used."""
        return self._use_floats

    def program(self, args):
        """Root of AST containing include statements and the main circuit.

        Returns:
            Program: program containing all parsed data
        """
        # assert all stmts are handled
        assert all(a is None for a in args)
        return self._program

    def circuit(self, args):
        """Any statement that is not an include. Appends gate and output
        statements to the program.
        """
        for stmt in args:
            if isinstance(stmt, Statement):
                self._program.add_statement(stmt)

    def script_options(self, args):
        """Script-level options. Adds any options to the program."""
        for name, value in args:
            self._program.add_option(name, value)

    def constants(self, args):
        """Script-level constants. Adds any constant to the program."""
        for name, value in args:
            self._program.add_constant(name, value)

    ###############
    # basic types
    ###############

    def int_(self, n):
        """Signed integers"""
        return int(n[0])

    def uint(self, n):
        """Unsigned integers"""
        return int(n[0])

    def float_(self, d):
        """Floating point numbers"""
        return Decimal(d[0])

    def imag_(self, c):
        """Imaginary numbers"""
        return DecimalComplex("0.0", c[0])

    def bool_(self, b):
        """Boolean expressions"""
        return bool(b[0])

    def wires(self, w):
        """Tuple with wires and identifier"""
        unraveled_w = []
        for i in w:
            if isinstance(i, range):
                unraveled_w.extend(i)
            else:
                unraveled_w.append(i)
        return "wires", tuple(unraveled_w)

    def params_list(self, p):
        """Tuple with list of params and identifier"""
        return "params", list(p)

    def params_dict(self, p):
        """Tuple with dictionary of params and identifier"""
        return "params", dict(p)

    option = tuple
    array = list

    INVERSE = str
    CTRL = str

    ANGLE_L = str
    ANGLE_R = str

    def FALSE_(self, _):
        """Returns False"""
        return False

    def TRUE_(self, _):
        """Returns True"""
        return True

    #############################
    # includes
    #############################

    def include(self, args):
        """Includes an external XIR script."""
        include = "".join(map(str, args))
        self._program.add_include(include)

    def path(self, args):
        """Path to an included XIR script."""
        return str(args[0])

    #############################
    # variables and expressions
    #############################

    def var(self, v):
        """String expressions that can be substituted by values at a later stage."""
        self._program.add_variable(v[0])
        return str(v[0])

    def range_(self, args):
        """Range between two signed integers"""
        return range(int(args[0]), int(args[1]))

    def name(self, n):
        """Name of variable, gate, observable, measurement type, option, external
        file, observable, wire, mathematical operation, etc."""
        return str(n[0])

    def expr(self, args):
        """Catch-all for expressions"""
        if len(args) == 1:
            return args[0]
        # if not a single value, it's a set of string expressions
        return "".join(map(str, args))

    ##############################
    # definitions and statements
    ##############################

    def gate_def(self, args):
        """Gate definition. Starts with keyword 'gate'. Adds gate to program."""
        name = args.pop(0)
        wires = ()
        params = []
        stmts = []

        max_wire = 0
        has_declared_wires = False
        for i, arg in enumerate(args):
            if is_param(arg):
                params = arg[1]
            elif is_wire(arg):
                has_declared_wires = True
                wires = arg[1]
            elif isinstance(arg, Statement):
                if has_declared_wires:
                    stmts = args[i:]
                    break
                stmts.append(arg)

                int_wires = [w for w in arg.wires if isinstance(w, int)]
                if int_wires and max(int_wires) > max_wire:
                    max_wire = max(int_wires)

            if not has_declared_wires:
                wires = tuple(range(max_wire + 1))
            else:
                # remove duplicate wires while maintaining order
                wires = tuple(dict.fromkeys(wires))

        self._program.add_gate(name, params, wires, stmts)

    def obs_def(self, args):
        """Observable definition. Starts with keyword 'obs'. Adds observable to program."""
        name = args.pop(0)
        wires = ()
        params = []
        stmts = []

        max_wire = 0
        has_declared_wires = False
        for i, arg in enumerate(args):
            if is_param(arg):
                params = arg[1]
            elif is_wire(arg):
                wires = arg[1]
                has_declared_wires = True
            elif isinstance(arg, ObservableStmt):
                if has_declared_wires:
                    stmts = args[i:]
                    break
                stmts.append(arg)

                int_wires = [w for w in arg.wires if isinstance(w, int)]
                if int_wires and max(int_wires) > max_wire:
                    max_wire = max(int_wires)

            if not has_declared_wires:
                wires = tuple(range(max_wire + 1))
            else:
                wires = tuple(dict.fromkeys(wires))

        self._program.add_observable(name, params, wires, stmts)

    def application_stmt(self, args):
        """Application statement. Can be either a gate statement or an output statement and is
        defined either directly in the circuit or inside a gate definition.

        Returns:
            Statement: statement with the given data
        """
        inverse = False
        ctrl_wires = set()

        while args[0] in ("inv", "ctrl"):
            a = args.pop(0)
            if a == "inv":
                inverse = not inverse
            elif a == "ctrl":
                ctrl_wires.update(args.pop(0)[1])

        name = args.pop(0)
        if is_param(args[0]):
            if isinstance(args[0][1], list):
                params = list(map(simplify_math, args[0][1]))
                wires = args[1][1]
            else:  # if dict
                params = {str(k): simplify_math(v) for k, v in args[0][1].items()}
                wires = args[1][1]
        else:
            params = []
            wires = args[0][1]

        stmt_options = {
            "ctrl_wires": tuple(sorted(ctrl_wires, key=hash)),
            "inverse": inverse,
            "use_floats": self.use_floats,
        }
        return Statement(name, params, wires, **stmt_options)

    def obs_stmt(self, args):
        """Observable statement. Defined inside an observable definition.

        Returns:
            ObservableStmt: object containing statement data
        """
        pref = simplify_math(args[0])
        terms = args[1]
        return ObservableStmt(pref, terms, use_floats=self.use_floats)

    def obs_group(self, args):
        """Group of observables used to define an observable statement.

        Returns:
            list[tuple]: each observable with corresponding wires as tuples
        """
        return [(args[i], args[i + 1]) for i in range(0, len(args) - 1, 2)]

    ################
    # declarations
    ################

    def gate_decl(self, args):
        """Gate declaration. Adds declaration to program."""
        if len(args) == 3:
            name, params, wires = args[0], args[1][1], args[2][1]
        else:
            name, wires = args[0], args[1][1]
            params = []

        decl = Declaration(name, type_="gate", params=params, wires=wires)
        self._program.add_declaration(decl)

    def obs_decl(self, args):
        """Observable declaration. Adds declaration to program."""
        if len(args) == 3:
            name, params, wires = args[0], args[1][1], args[2][1]
        else:
            name, wires = args[0], args[1][1]
            params = []

        decl = Declaration(name, type_="obs", params=params, wires=wires)
        self._program.add_declaration(decl)

    def func_decl(self, args):
        """Function declaration. Adds declaration to program."""
        if len(args) == 2:
            name, params = args[0], args[1][1]
        else:
            name = args[0]
            params = []

        decl = Declaration(name, type_="func", params=params)
        self._program.add_declaration(decl)

    def out_decl(self, args):
        """Output declaration. Adds declaration to program."""
        if len(args) == 3:
            name, params, wires = args[0], args[1][1], args[2][1]
        else:
            name, wires = args[0], args[1][1]
            params = []

        decl = Declaration(name, type_="out", params=params, wires=wires)
        self._program.add_declaration(decl)

    ###############
    # mathematics
    ###############

    def math_op(self, args):
        """Mathemetical operation. Adds operation to the program.

        Returns:
            str: string representation of operation
        """
        self._program.add_called_function(args[0])
        return str(args[0]) + "(" + str(args[1]) + ")"

    def add(self, args):
        """Addition operation.

        Returns:
            Union[number, str]: resulting value after applied operation or string representation
            of operation if expression contains string variables
        """
        if all(isinstance(a, (int, Decimal, DecimalComplex)) for a in args):
            return args[0] + args[1]
        return "(" + " + ".join(map(str, args)) + ")"

    def sub(self, args):
        """Subtraction operation.

        Returns:
            Union[number, str]: resulting value after applied operation or string representation
            of operation if expression contains string variables
        """
        if all(isinstance(a, (int, Decimal, DecimalComplex)) for a in args):
            return args[0] - args[1]
        return "(" + " + ".join(map(str, args)) + ")"

    def prod(self, args):
        """Product operation.

        Returns:
            Union[number, str]: resulting value after applied operation or string representation
            of operation if expression contains string variables
        """
        if all(isinstance(a, (int, Decimal, DecimalComplex)) for a in args):
            return args[0] * args[1]
        return " * ".join(map(str, args))

    def div(self, args):
        """Division operation.

        Returns:
            Union[number, str]: resulting value after applied operation or string representation
            of operation if expression contains string variables
        """
        if all(isinstance(a, (int, Decimal, DecimalComplex)) for a in args):
            # if numerator and denominator are ints, then cast numerator to
            # Decimal so that no floats are being returned
            if all(isinstance(a, int) for a in args):
                return Decimal(args[0]) / args[1]
            return args[0] / args[1]
        return " / ".join(map(str, args))

    def neg(self, args):
        """Negation operation.

        Returns:
            Union[number, str]: resulting value after applied operation or string representation
            of operation if expression contains string variables
        """
        if isinstance(args[0], (int, Decimal, DecimalComplex)):
            return -args[0]
        return "-" + str(args[0])

    def PI(self, _):
        """Mathematical constant pi.

        Returns:
            Union[Decimal, str]: value of pi or string 'PI'
        """
        return "PI" if not self._eval_pi else Decimal(str(math.pi))


def is_wire(arg):
    """Returns whether the passed argument is a tuple of wires."""
    return isinstance(arg, tuple) and arg[0] == "wires"


def is_param(arg):
    """Returns whether the passed argument is a list or dictionary of params."""
    return isinstance(arg, tuple) and arg[0] == "params"
