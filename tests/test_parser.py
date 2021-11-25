"""Unit tests for the parser"""

import math
from decimal import Decimal

import pytest
from lark.exceptions import UnexpectedToken

from xir import DecimalComplex, parse_script


class TestParser:
    """Unit tests for the parser."""

    @pytest.mark.parametrize(
        "array, res",
        [
            ("[0, 1, 2]", [0, 1, 2]),
            ("[true, false]", [True, False]),
            ("[3+2, sin(3)]", [5, "sin(3)"]),
            ("[[0, 1], [[2], [3, 4]], [5, 6]]", [[0, 1], [[2], [3, 4]], [5, 6]]),
            ("[]", []),
        ],
    )
    def test_output_with_array(self, array, res):
        """Test outputs with arrays as parameter values."""
        circuit = f"an_output_statement(array: {array}) | [0, 1];"
        irprog = parse_script(circuit)

        assert irprog.statements[0].params["array"] == res

    @pytest.mark.parametrize(
        "key, val, expected",
        [
            ("cutoff", "5", 5),
            ("anything", "4.2", 4.2),
            ("a_number", "3 + 2.1", 5.1),
            ("a_number_with_pi", "pi / 2", math.pi / 2),
            ("a_string", "hello", "hello"),
            ("True", "False", "False"),
            ("true", "false", False),
        ],
    )
    def test_options(self, key, val, expected):
        """Test script level options."""
        irprog = parse_script(f"options:\n    {key}: {val};\nend;", use_floats=True, eval_pi=True)

        assert key in irprog.options
        assert irprog.options[key] == expected

    @pytest.mark.parametrize(
        "key, val",
        [
            ("key", ["compound", "value"]),
            ("True", [1, 2, "False"]),
            ("key", [1, [2, [3, 4]]]),
        ],
    )
    def test_options_lists(self, key, val):
        """Test script level options with lists."""
        val_str = "[" + ", ".join(str(v) for v in val) + "]"
        irprog = parse_script(f"options:\n    {key}: {val_str};\nend;")

        assert key in irprog.options
        assert irprog.options[key] == val

    @pytest.mark.parametrize(
        "key, val, expected",
        [
            ("cutoff", "5", 5),
            ("anything", "4.2", 4.2),
            ("a_number", "3 + 2.1", 5.1),
            ("a_number_with_pi", "pi / 2", math.pi / 2),
            ("a_string", "hello", "hello"),
            ("True", "False", "False"),
            ("true", "false", False),
        ],
    )
    def test_constants(self, key, val, expected):
        """Test script level constants."""
        irprog = parse_script(f"constants:\n    {key}: {val};\nend;", use_floats=True, eval_pi=True)

        assert key in irprog.constants
        assert irprog.constants[key] == expected

    @pytest.mark.parametrize(
        "key, val",
        [
            ("key", ["compound", "value"]),
            ("True", [1, 2, "False"]),
            ("key", [1, [2, [3, 4]]]),
        ],
    )
    def test_constants_lists(self, key, val):
        """Test script level constants with lists."""
        val_str = "[" + ", ".join(str(v) for v in val) + "]"
        irprog = parse_script(f"constants:\n    {key}: {val_str};\nend;")

        assert key in irprog.constants
        assert irprog.constants[key] == val

    @pytest.mark.parametrize(
        "script, inverse",
        [
            ("inv ry(2.4) | [2];", True),
            ("inv inv ry(2.4) | [2];", False),
            ("inv ctrl[0, 1] inv ry(2.4) | [2];", False),
            ("inv inv ctrl[0, 1] inv ry(2.4) | [2];", True),
            ("ry(2.4) | [2];", False),
        ],
    )
    def test_inverse_modifier(self, script, inverse):
        """Test that inverse modifier for gate statements works correctly."""
        irprog = parse_script(script)

        assert irprog.statements[0].is_inverse is inverse

    @pytest.mark.parametrize(
        "script, ctrl_wires",
        [
            ("ctrl[0, 1] ry(2.4) | [2];", (0, 1)),
            ("ctrl[0, 1] ctrl[3] rz(4.2) | [2];", (0, 1, 3)),
            ("ctrl[0, 1] inv ctrl[3] rx(3.1) | [4];", (0, 1, 3)),
            ("ry(2.4) | [2];", ()),
            ("ctrl [0, 1] ctrl [0] rx(6.2) | [2];", (0, 1)),
            ("ctrl [0, 0, 1, 2, 2] rx(6.2) | [2];", (0, 1, 2)),
        ],
    )
    def test_ctrl_modifier(self, script, ctrl_wires):
        """Test that control wires modifier for gate statements correctly sets
        the ``Statement.ctrl_wires`` property.
        """
        irprog = parse_script(script)

        assert irprog.statements[0].ctrl_wires == ctrl_wires

    @pytest.mark.parametrize("use_floats", [True, False])
    @pytest.mark.parametrize("param", [3, 4.2, 2j])
    def test_use_floats(self, use_floats, param):
        """Test the ``use_floats`` kwarg to return float and complex types."""
        if use_floats:
            t = type(param)
        else:
            if isinstance(param, complex):
                t = DecimalComplex
            elif isinstance(param, float):
                t = Decimal
            elif isinstance(param, int):
                t = int

        circuit = f"a_gate({param}) | [0, 1];"
        irprog = parse_script(circuit, use_floats=use_floats)

        assert isinstance(irprog.statements[0].params[0], t)

    @pytest.mark.parametrize("eval_pi", [True, False])
    @pytest.mark.parametrize("param, expected", [("pi", math.pi), ("pi / 2", math.pi / 2)])
    def test_eval_pi(self, eval_pi, param, expected):
        """Test the ``eval_pi`` kwarg to evaluate mathematical expressions containing pi."""
        circuit = f"a_gate({param}) | [0, 1];"
        irprog = parse_script(circuit, eval_pi=eval_pi)
        if eval_pi:
            assert irprog.statements[0].params[0] == expected
        else:
            assert irprog.statements[0].params[0] == param.upper()

    @pytest.mark.parametrize(
        "circuit",
        [
            "adjective name(a, b)[0];",
            "gate name(a, b)[];",
            "gate name(a: 3, b: 2)[0, 1];",
        ],
    )
    def test_invalid_declarations_token_error(self, circuit):
        """Test that an UnexpectedToken error is raised when using invalid declaration syntax."""
        with pytest.raises(UnexpectedToken, match=r"Unexpected token"):
            parse_script(circuit)

    @pytest.mark.parametrize(
        "include",
        [
            # Absolute
            "/",
            "/foo",
            "/foo/bar",
            "C:/foo",
            # Relative
            "foo",
            "foo/bar",
            "./foo",
            "../foo",
            # Libraries
            "<foo>",
            "<foo/bar>",
        ],
    )
    def test_include_valid(self, include):
        """Tests that an include statement with valid syntax is parsed correctly."""
        program = parse_script(f"use {include};")
        assert program.includes == [include]

    @pytest.mark.parametrize("include", ["Path With Spaces", "<NoAngleR", "NoAngleL>", "*"])
    def test_include_invalid(self, include):
        """Tests that an UnexpectedToken exception is raised when the syntax for
        including an external XIR script is invalid.
        """
        with pytest.raises(UnexpectedToken, match=r"Unexpected token"):
            parse_script(f"use {include};")

    @pytest.mark.parametrize(
        "stmt, expected_wires",
        [
            (
                "gate MultiRot(x, y, z): RX(x) | [0]; RY(y) | [0]; RZ(z) | [0]; end;",
                (0,),
            ),
            (
                "gate MultiRot(x, y, z): RX(x) | [0]; RY(y) | [1]; RZ(z) | [2]; end;",
                (0, 1, 2),
            ),
            # Reverse order of the above.
            (
                "gate MultiRot(x, y, z): RX(x) | [2]; RY(y) | [1]; RZ(z) | [0]; end;",
                (0, 1, 2),
            ),
            (
                "gate MultiRot(x, y, z): RX(x) | [0]; RY(y) | [1]; RZ(z) | [1]; end;",
                (0, 1),
            ),
            (
                "gate MultiRot(x, y, z): RX(x) | [0]; RY(y) | [0]; RZ(z) | [3]; end;",
                (0, 1, 2, 3),
            ),
            (
                "gate MultiRot(x, y, z): RX(x) | [4]; RY(y) | [4]; RZ(z) | [4]; end;",
                (0, 1, 2, 3, 4),
            ),
            (
                "gate MultiRot(x, y, z)[4]: RX(x) | [4]; RY(y) | [4]; RZ(z) | [4]; end;",
                (4,),
            ),
            (
                "gate MultiRot(x, y, z)[b, a]: RX(x) | [a]; RY(y) | [b]; RZ(z) | [a]; end;",
                ("b", "a"),
            ),
            (
                "gate MultiRot(x, y, z)[0, 1, 2, 3]: RX(x) | [0]; RY(y) | [2]; RZ(z) | [0]; end;",
                (0, 1, 2, 3),
            ),
        ],
    )
    def test_gate_definition_wires(self, stmt, expected_wires):
        """Tests that wires are correctly declared when defining a gate."""
        script = f"gate RX(x)[0];gate RY(x)[0];gate RZ(x)[0]; {stmt}"
        program = parse_script(script)

        assert program.declarations["gate"][0].name == "RX"
        assert program.declarations["gate"][1].name == "RY"
        assert program.declarations["gate"][2].name == "RZ"

        assert program.declarations["gate"][3].name == "MultiRot"
        assert program.declarations["gate"][3].wires == expected_wires

    @pytest.mark.parametrize(
        "stmt, expected_wires",
        [
            (
                "obs Orange(x, y, z): 1.2, X[0]; end;",
                (0,),
            ),
            (
                "obs Orange(x, y, z): 4.1, X[0] @ Y[1]; 1, Z[2]; end;",
                (0, 1, 2),
            ),
            (
                "obs Orange(x, y, z): 1, X[0] @ Y[1]; 1, Z[1]; end;",
                (0, 1),
            ),
            (
                "obs Orange(x, y, z): 1, X[3] @ Y[1]; 1.4, Z[0] @ Y[2]; end;",
                (0, 1, 2, 3),
            ),
            (
                "obs Orange(x, y, z): 1, X[4]; 1, Z[4]; end;",
                (0, 1, 2, 3, 4),
            ),
            (
                "obs Orange(x, y, z)[4]: 2.2, X[4]; 1, Z[4]; end;",
                (4,),
            ),
            (
                "obs Orange(x, y, z)[b, a]: 1, X[a] @ Y[b]; 1, Z[b]; end;",
                ("b", "a"),
            ),
            (
                "obs Orange(x, y, z)[0, 1, 2, 3]: 1, X[0] @ Y[2]; 0.42, Z[0]; end;",
                (0, 1, 2, 3),
            ),
        ],
    )
    def test_observable_definition_wires(self, stmt, expected_wires):
        """Tests that wires are correctly declared when defining an observable."""
        script = f"obs X[0];obs Y[0];obs Z[0]; {stmt}"
        program = parse_script(script)

        assert program.declarations["obs"][0].name == "X"
        assert program.declarations["obs"][1].name == "Y"
        assert program.declarations["obs"][2].name == "Z"

        assert program.declarations["obs"][3].name == "Orange"
        assert program.declarations["obs"][3].wires == expected_wires
