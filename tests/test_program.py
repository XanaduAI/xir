# pylint: disable=redefined-outer-name
"""Unit tests for the program class"""

from decimal import Decimal
from typing import Any, Dict, Iterable, List, MutableSet, Sequence

import pytest

import xir


@pytest.fixture
def program():
    """Returns an empty XIR program."""
    return xir.Program()


# pylint: disable=protected-access
def make_program(
    called_functions: MutableSet[str] = None,
    declarations: Dict[str, List[xir.Declaration]] = None,
    gates: Dict[str, Sequence] = None,
    includes: List[str] = None,
    observables: Dict[str, Sequence] = None,
    options: Dict[str, Any] = None,
    statements: List[xir.Statement] = None,
    variables: MutableSet[str] = None,
):
    """Returns an XIR program with the given attributes."""
    program = xir.Program()
    program._called_functions = called_functions or set()
    program._declarations = declarations or {"gate": [], "func": [], "out": [], "obs": []}
    program._gates = gates or {}
    program._includes = includes or []
    program._observables = observables or {}
    program._options = options or {}
    program._statements = statements or []
    program._variables = variables or set()
    return program


class TestSerialize:
    """Unit tests for the serialize method of an XIR Program."""

    def test_empty_program(self, program):
        """Tests serializing an empty program."""
        assert program.serialize() == ""

    def test_includes(self, program):
        """Tests serializing a XIR program with includes."""
        program.add_include("xstd")
        program.add_include("randomlib")
        res = program.serialize()
        assert res == "use xstd;\nuse randomlib;"

    #####################
    # Test declarations
    #####################

    @pytest.mark.parametrize(
        "params, wires, declaration_type, want_res",
        [
            (["a", "b"], (0,), "gate", "gate name(a, b)[0];"),
            ([], (0, 2, 1), "obs", "obs name[0, 2, 1];"),
            (["theta"], ("a", "b", "c"), "out", "out name(theta)[a, b, c];"),
        ],
    )
    def test_declarations(self, params, wires, declaration_type, want_res):
        """Test serializing gate, operation and output declarations"""
        decl = xir.Declaration("name", declaration_type, params, wires)

        program = xir.Program()
        program._declarations[declaration_type].append(decl)
        have_res = program.serialize()

        assert have_res == want_res

    @pytest.mark.parametrize(
        "params, want_res",
        [
            (["a", "b"], "func name(a, b);"),
            ([], "func name;"),
            (["theta"], "func name(theta);"),
        ],
    )
    def test_func_declaration(self, params, want_res):
        """Test serializing function declarations."""
        decl = xir.Declaration("name", type_="func", params=params)

        program = xir.Program()
        program._declarations["func"].append(decl)
        have_res = program.serialize()
        assert have_res == want_res

    ###################
    # Test statements
    ###################

    @pytest.mark.parametrize("name", ["ry", "toffoli"])
    @pytest.mark.parametrize("params", [[0, 3.14, -42]])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_statements_params(self, program, name, params, wires):
        """Tests serializing an XIR program with general (gate) statements."""
        stmt = xir.Statement(name, params, wires)

        program.add_statement(stmt)
        res = program.serialize()

        params_str = ", ".join(map(str, params))
        wires_str = ", ".join(map(str, wires))
        assert res == f"{name}({params_str}) | [{wires_str}];"

    @pytest.mark.parametrize("name", ["ry", "toffoli"])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_statements_no_params(self, program, name, wires):
        """Tests serializing an XIR program with general (gate) statements without parameters."""
        stmt = xir.Statement(name, [], wires)

        program.add_statement(stmt)
        res = program.serialize()

        wires_str = ", ".join(map(str, wires))
        assert res == f"{name} | [{wires_str}];"

    @pytest.mark.parametrize("pref", [42, Decimal("3.14"), "2 * a + 1"])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_observable_stmt(self, program, pref, wires):
        """Tests serializing an XIR program with observable statements."""
        xyz = "XYZ"
        factors = [xir.ObservableFactor(xyz[i], None, w) for i, w in enumerate(wires)]
        factors_str = " @ ".join(str(t) for t in factors)
        wires_str = ", ".join(wires)

        program.add_observable("H", ["a", "b"], wires, [xir.ObservableStmt(pref, factors)])

        res = program.serialize()
        assert res == f"obs H(a, b)[{wires_str}]:\n    {pref}, {factors_str};\nend;"

    #########################
    # Test gate definitions
    #########################

    @pytest.mark.parametrize("name", ["ry", "toffoli"])
    @pytest.mark.parametrize("params", [["a", "b"]])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_gates_params_and_wires(self, program, name, params, wires):
        """Tests serializing an XIR program with gates that have both parameters and wires."""
        stmts = [xir.Statement("rz", [0.13], (0,)), xir.Statement("cnot", [], (0, 1))]
        program.add_gate(name, params, wires, stmts)

        res = program.serialize()

        params_str = ", ".join(map(str, params))
        wires_str = ", ".join(map(str, wires))
        assert (
            res == f"gate {name}({params_str})[{wires_str}]:"
            "\n    rz(0.13) | [0];\n    cnot | [0, 1];\nend;"
        )

    @pytest.mark.parametrize("name", ["ry", "toffoli"])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_gates_no_params(self, program, name, wires):
        """Tests serializing an XIR program with gates that have no parameters."""
        stmts = [xir.Statement("rz", [0.13], (0,)), xir.Statement("cnot", [], (0, 1))]
        program.add_gate(name, [], wires, stmts)

        res = program.serialize()

        wires_str = ", ".join(map(str, wires))
        assert res == f"gate {name}[{wires_str}]:\n    rz(0.13) | [0];\n    cnot | [0, 1];\nend;"

    @pytest.mark.parametrize("name", ["ry", "toffoli"])
    @pytest.mark.parametrize("params", [["a", "b"]])
    def test_gates_no_wires(self, program, name, params):
        """Tests serializing an XIR program with gates that have no wires."""
        stmts = [xir.Statement("rz", [0.13], (0,)), xir.Statement("cnot", [], (0, 1))]
        program.add_gate(name, params, (), stmts)

        res = program.serialize()

        params_str = ", ".join(map(str, params))
        assert res == f"gate {name}({params_str}):\n    rz(0.13) | [0];\n    cnot | [0, 1];\nend;"

    @pytest.mark.parametrize("name", ["mygate", "a_beautiful_gate"])
    def test_gates_no_params_and_no_wires(self, program, name):
        """Tests serializing an XIR program with gates that have no parameters or wires."""
        stmts = [xir.Statement("rz", [0.13], (0,)), xir.Statement("cnot", [], (0, 1))]
        program.add_gate(name, [], (), stmts)

        res = program.serialize()
        assert res == f"gate {name}:\n    rz(0.13) | [0];\n    cnot | [0, 1];\nend;"

    ###############################
    # Test observable definitions
    ###############################

    @pytest.mark.parametrize("name", ["H", "my_op"])
    @pytest.mark.parametrize("params", [["a", "b"]])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_observables_params_and_wires(self, program, name, params, wires):
        """Tests serializing an XIR program with observables that have both parameters and wires."""
        stmts = [
            xir.ObservableStmt(
                42, [xir.ObservableFactor("X", None, [0]), xir.ObservableFactor("Y", None, [1])]
            )
        ]
        program.add_observable(name, params, wires, stmts)

        res = program.serialize()

        params_str = ", ".join(map(str, params))
        wires_str = ", ".join(map(str, wires))
        assert res == f"obs {name}({params_str})[{wires_str}]:\n    42, X[0] @ Y[1];\nend;"

    @pytest.mark.parametrize("name", ["H", "my_op"])
    @pytest.mark.parametrize("wires", [("w0", "w1"), ("w0",), ("wire0", "anotherWire", "FortyTwo")])
    def test_observables_no_params(self, program, name, wires):
        """Tests serializing an XIR program with observables that have no parameters."""
        stmts = [
            xir.ObservableStmt(
                42, [xir.ObservableFactor("X", None, [0]), xir.ObservableFactor("Y", None, [1])]
            )
        ]
        program.add_observable(name, [], wires, stmts)

        res = program.serialize()

        wires_str = ", ".join(map(str, wires))
        assert res == f"obs {name}[{wires_str}]:\n    42, X[0] @ Y[1];\nend;"

    @pytest.mark.parametrize("name", ["H", "my_op"])
    @pytest.mark.parametrize("params", [["a", "b"]])
    def test_observables_no_wires(self, program, name, params):
        """Tests serializing an XIR program with observables that have no declared wires."""
        stmts = [
            xir.ObservableStmt(
                42, [xir.ObservableFactor("X", None, [0]), xir.ObservableFactor("Y", None, [1])]
            )
        ]
        program.add_observable(name, params, (), stmts)

        res = program.serialize()

        params_str = ", ".join(map(str, params))
        assert res == f"obs {name}({params_str}):\n    42, X[0] @ Y[1];\nend;"

    @pytest.mark.parametrize("name", ["my_op", "op2"])
    def test_observables_no_params_and_no_wires(self, program, name):
        """Tests serializing an XIR program with observables that have no parameters or wires."""
        stmts = [
            xir.ObservableStmt(
                42, [xir.ObservableFactor("X", None, [0]), xir.ObservableFactor("Y", None, [1])]
            )
        ]
        program.add_observable(name, [], (), stmts)

        res = program.serialize()
        assert res == f"obs {name}:\n    42, X[0] @ Y[1];\nend;"


class TestProgram:
    """Unit tests for the xir.Program class."""

    def test_init(self):
        """Tests that an (empty) XIR program can be constructed."""
        program = xir.Program(version="1.2.3", use_floats=False)

        assert program.version == "1.2.3"
        assert program.use_floats is False

        assert list(program.wires) == []

        assert set(program.called_functions) == set()
        assert dict(program.declarations) == {"gate": [], "func": [], "out": [], "obs": []}
        assert dict(program.gates) == {}
        assert list(program.includes) == []
        assert dict(program.observables) == {}
        assert list(program.options) == []
        assert list(program.statements) == []
        assert set(program.variables) == set()

    def test_repr(self):
        """Test that the string representation of an XIR program has the correct format."""
        program = xir.Program(version="1.2.3")
        assert repr(program) == "<Program: version=1.2.3>"

    def test_search(self, program):
        """Tests that an XIR program can be searched for the wires or parameters
        of a declaration.
        """
        decl1 = xir.Declaration("spin", type_="gate", params=["x", "y", "z"], wires=(0, 1))
        program.add_declaration(decl1)

        decl2 = xir.Declaration("spin", type_="func", params=["t", "p", "o"])
        program.add_declaration(decl2)

        assert program.search(decl_type="gate", attr_type="wires", name="spin") == (0, 1)
        assert program.search(decl_type="gate", attr_type="params", name="spin") == ["x", "y", "z"]
        assert program.search(decl_type="func", attr_type="params", name="spin") == ["t", "p", "o"]

    def test_search_for_invalid_declaration_type(self, program):
        """Tests that a ValueError is raised when an XIR prorgram is searched
        for an invalid declaration type.
        """
        with pytest.raises(ValueError, match=r"Declaration type 'invalid' must be one of \{.*\}"):
            program.search(decl_type="invalid", attr_type="wires", name="name")

    def test_search_for_invalid_attribute_type(self, program):
        """Tests that a ValueError is raised when an XIR prorgram is searched
        for an invalid attribute type.
        """
        with pytest.raises(ValueError, match=r"Attribute type 'invalid' must be one of \{.*\}"):
            program.search(decl_type="gate", attr_type="invalid", name="name")

    def test_search_for_missing_declaration(self, program):
        """Tests that a ValueError is raised when an XIR prorgram is searched
        for a declaration which does not exist.
        """
        with pytest.raises(ValueError, match=r"No obs declarations with the name 'pos' were found"):
            program.search(decl_type="obs", attr_type="wires", name="pos")

    def test_add_called_function(self, program):
        """Tests that called functions can be added to an XIR program."""
        program.add_called_function("cos")
        assert set(program.called_functions) == {"cos"}

        program.add_called_function("sin")
        assert set(program.called_functions) == {"cos", "sin"}

        program.add_called_function("cos")
        assert set(program.called_functions) == {"cos", "sin"}

    def test_add_declaration(self, program):
        """Tests that declarations can be added to an XIR program."""
        tan = xir.Declaration("tan", type_="func", params=["x"])
        program.add_declaration(tan)
        assert program.declarations == {"func": [tan], "gate": [], "obs": [], "out": []}

        u2 = xir.Declaration("U2", type_="gate", params=["a", "b"], wires=(0,))
        program.add_declaration(u2)
        assert program.declarations == {"func": [tan], "gate": [u2], "obs": [], "out": []}

        z3 = xir.Declaration("Z3", type_="obs", wires=(0, 1, 2))
        program.add_declaration(z3)
        assert program.declarations == {"func": [tan], "gate": [u2], "obs": [z3], "out": []}

    def test_add_declaration_with_same_key(self, program):
        """Tests that multiple declarations with the same key can be added to an XIR program."""
        amplitude = xir.Declaration("amplitude", type_="out")
        program.add_declaration(amplitude)

        probabilities = xir.Declaration("probabilities", type_="out")
        program.add_declaration(probabilities)

        assert program.declarations["out"] == [amplitude, probabilities]

    def test_add_declaration_with_same_name(self, program):
        """Tests that a warning is issued when two declarations with the same
        name are added to an XIR program.
        """
        atan1 = xir.Declaration("atan", type_="func", params=["x"])
        program.add_declaration(atan1)

        with pytest.warns(UserWarning, match=r"Func 'atan' already declared"):
            atan2 = xir.Declaration("atan", type_="func", params=["x", "y"])
            program.add_declaration(atan2)

        assert program.declarations["func"] == [atan2]

    def test_add_gate(self, program):
        """Tests that gates can be added to an XIR program."""
        crx = {
            "params": ["theta"],
            "wires": (0, 1),
            "statements": [
                xir.Statement(name="X", params=[], wires=[0]),
                xir.Statement(name="X", params=[], wires=[0]),
                xir.Statement(name="CRX", params=["theta"], wires=[0, 1]),
            ],
        }
        program.add_gate("CRX", **crx)
        assert program.declarations["gate"][0] == xir.Declaration("CRX", "gate", ["theta"], (0, 1))
        assert program.gates == {"CRX": crx["statements"]}

        u3 = {
            "params": ["theta", "phi", "lam"],
            "wires": [1],
            "statements": [xir.Statement(name="U3", params=["theta", "phi", "lam"], wires=[1])],
        }
        program.add_gate("U3", **u3)
        assert program.declarations["gate"][1] == xir.Declaration(
            "U3", "gate", ["theta", "phi", "lam"], [1]
        )
        assert program.gates == {"CRX": crx["statements"], "U3": u3["statements"]}

    def test_add_gate_with_same_name(self, program):
        """Tests that a warning is issued when two gates with the same name are
        added to an XIR program.
        """
        phi = {"params": ["phi"], "wires": [0, 1], "statements": []}
        psi = {"params": ["psi"], "wires": [0, 1], "statements": []}

        program.add_gate("CRX", **phi)
        assert program.declarations["gate"][0] == xir.Declaration("CRX", "gate", ["phi"], [0, 1])
        assert program.gates == {"CRX": phi["statements"]}

        with pytest.warns(Warning, match=r"Gate 'CRX' already defined"):
            program.add_gate("CRX", **psi)

        assert program.declarations["gate"] == [xir.Declaration("CRX", "gate", ["psi"], [0, 1])]
        assert program.gates == {"CRX": psi["statements"]}

    def test_add_include(self, program):
        """Tests that includes can be added to an XIR program."""
        program.add_include("complex")
        assert list(program.includes) == ["complex"]

        program.add_include("algorithm")
        assert list(program.includes) == ["complex", "algorithm"]

    def test_add_include_with_same_name(self, program):
        """Tests that a warning is issued when two identical includes are added
        to an XIR program.
        """
        program.add_include("memory")

        with pytest.warns(Warning, match=r"Module 'memory' is already included"):
            program.add_include("memory")

        assert list(program.includes) == ["memory"]

    def test_add_observable(self, program):
        """Tests that observables can be added to an XIR program."""
        x = {
            "params": [],
            "wires": [0],
            "statements": [xir.ObservableStmt(pref=1, factors=[("X", 0)])],
        }
        program.add_observable("X", **x)

        assert program.declarations["obs"][0] == xir.Declaration("X", "obs", [], [0])
        assert program.observables == {"X": x["statements"]}

        y = {
            "params": [],
            "wires": [1],
            "statements": [xir.ObservableStmt(pref=2, factors=[("Y", 0)])],
        }
        program.add_observable("Y", **y)

        assert program.declarations["obs"][1] == xir.Declaration("Y", "obs", [], [1])
        assert program.observables == {"X": x["statements"], "Y": y["statements"]}

    def test_add_observable_with_same_name(self, program):
        """Tests that a warning is issued when two observables with the same name
        are added to an XIR program.
        """
        degrees = {"params": ["degrees"], "wires": (0, 1), "statements": []}
        radians = {"params": ["radians"], "wires": (0, 1), "statements": []}

        program.add_observable("angle", **degrees)

        assert program.declarations["obs"][0] == xir.Declaration(
            "angle", "obs", ["degrees"], (0, 1)
        )
        assert program.observables == {"angle": degrees["statements"]}

        with pytest.warns(Warning, match=r"Observable 'angle' already defined"):
            program.add_observable("angle", **radians)

        assert program.declarations["obs"] == [xir.Declaration("angle", "obs", ["radians"], (0, 1))]
        assert program.observables == {"angle": radians["statements"]}

    def test_add_option(self, program):
        """Tests that options can be added to an XIR program."""
        program.add_option("cutoff", 3)
        assert program.options == {"cutoff": 3}

        program.add_option("speed", "fast")
        assert program.options == {"cutoff": 3, "speed": "fast"}

    def test_add_option_with_same_key(self, program):
        """Tests that a warning is issued when two options with the same key
        are added to an XIR program.
        """
        program.add_option("precision", "float")
        assert program.options == {"precision": "float"}

        with pytest.warns(Warning, match=r"Option 'precision' already set"):
            program.add_option("precision", "double")

        assert program.options == {"precision": "double"}

    def test_add_constant(self, program):
        """Tests that constants can be added to an XIR program."""
        program.add_constant("p0", [1, 2, 3])
        assert program.constants == {"p0": [1, 2, 3]}

        program.add_constant("golden_ratio", 1.618)
        assert program.constants == {"p0": [1, 2, 3], "golden_ratio": 1.618}

    def test_add_constant_with_same_key(self, program):
        """Tests that a warning is issued when two constants with the same key
        are added to an XIR program.
        """
        program.add_constant("p1", [4, 2])
        assert program.constants == {"p1": [4, 2]}

        with pytest.warns(Warning, match=r"Constant 'p1' already set"):
            program.add_constant("p1", [3, 14])

        assert program.constants == {"p1": [3, 14]}

    def test_add_statement(self, program):
        """Tests that statements can be added to an XIR program."""
        program.add_statement(xir.Statement("X", {}, [0]))
        assert [stmt.name for stmt in program.statements] == ["X"]

        program.add_statement(xir.Statement("Y", {}, [0]))
        assert [stmt.name for stmt in program.statements] == ["X", "Y"]

        program.add_statement(xir.Statement("X", {}, [0]))
        assert [stmt.name for stmt in program.statements] == ["X", "Y", "X"]

    def test_add_variable(self, program):
        """Tests that variables can be added to an XIR program."""
        program.add_variable("theta")
        assert set(program.variables) == {"theta"}

        program.add_variable("phi")
        assert set(program.variables) == {"theta", "phi"}

        program.add_variable("theta")
        assert set(program.variables) == {"theta", "phi"}

    def test_clear_includes(self, program):
        """Tests that includes can be cleared from an XIR program."""
        program.clear_includes()
        assert len(program.includes) == 0

        program.add_include("bitset")
        program.clear_includes()
        assert len(program.includes) == 0

        program.add_include("stack")
        program.add_include("queue")
        program.clear_includes()
        assert len(program.includes) == 0

    def test_merge_zero_programs(self):
        """Test that a ValueError is raised when zero XIR programs are merged."""
        with pytest.raises(ValueError, match=r"Merging requires at least one XIR program"):
            xir.Program.merge()

    def test_merge_programs_with_different_versions(self):
        """Test that a ValueError is raised when two XIR programs with different
        versions are merged.
        """
        p1 = xir.Program(version="0.0.1")
        p2 = xir.Program(version="0.0.2")

        match = r"XIR programs with different versions cannot be merged"

        with pytest.raises(ValueError, match=match):
            xir.Program.merge(p1, p2)

    def test_merge_programs_with_different_float_settings(self):
        """Test that a warning is issued when two XIR programs with different
        float settings are merged.
        """
        p1 = xir.Program(use_floats=True)
        p2 = xir.Program(use_floats=False)

        match = r"XIR programs with different float settings are being merged"

        with pytest.warns(UserWarning, match=match):
            assert xir.Program.merge(p1, p2).use_floats is True

    @pytest.mark.parametrize(
        ["programs", "want_result"],
        [
            pytest.param(
                [
                    make_program(
                        called_functions={"tanh"},
                        declarations={
                            "func": [],
                            "gate": [
                                xir.Declaration(
                                    "U2", type_="gate", params=["phi", "lam"], wires=(0,)
                                )
                            ],
                            "obs": [xir.Declaration("Z", type_="obs", wires=(1,))],
                            "out": [],
                        },
                        gates={"U2": []},
                        includes=["xstd"],
                        observables={"Z": []},
                        options={"cutoff": 3},
                        statements=[xir.Statement("U1", {"phi": 1}, [0])],
                        variables={"angle"},
                    ),
                ],
                make_program(
                    called_functions={"tanh"},
                    declarations={
                        "func": [],
                        "gate": [
                            xir.Declaration("U2", type_="gate", params=["phi", "lam"], wires=(0,))
                        ],
                        "obs": [xir.Declaration("Z", type_="obs", wires=(1,))],
                        "out": [],
                    },
                    gates={"U2": []},
                    includes=["xstd"],
                    observables={"Z": []},
                    options={"cutoff": 3},
                    statements=[xir.Statement("U1", {"phi": 1}, [0])],
                    variables={"angle"},
                ),
                id="One XIR program",
            ),
            pytest.param(
                [
                    make_program(
                        called_functions={"cos"},
                        declarations={
                            "func": [xir.Declaration("cos", type_="func", params=["x"])],
                            "gate": [xir.Declaration("H", type_="gate", wires=(0,))],
                            "obs": [xir.Declaration("X", type_="obs", wires=(0,))],
                            "out": [],
                        },
                        gates={"H": []},
                        includes=[],
                        observables={"X": []},
                        options={"cutoff": 2},
                        statements=[xir.Statement("S", [], [0])],
                        variables={"theta"},
                    ),
                    make_program(
                        called_functions={"sin"},
                        declarations={
                            "func": [xir.Declaration("sin", type_="func", params=["x"])],
                            "gate": [
                                xir.Declaration("D", type_="gate", params=["r", "phi"], wires=(1,))
                            ],
                            "obs": [xir.Declaration("Y", type_="obs", wires=(1,))],
                            "out": [],
                        },
                        gates={"D": []},
                        includes=["xstd"],
                        observables={"Y": []},
                        options={"cutoff": 4},
                        statements=[xir.Statement("T", [], [0])],
                        variables=set(),
                    ),
                ],
                make_program(
                    called_functions={"cos", "sin"},
                    declarations={
                        "func": [
                            xir.Declaration("cos", type_="func", params=["x"]),
                            xir.Declaration("sin", type_="func", params=["x"]),
                        ],
                        "gate": [
                            xir.Declaration("H", type_="gate", wires=(0,)),
                            xir.Declaration("D", type_="gate", params=["r", "phi"], wires=(1,)),
                        ],
                        "obs": [
                            xir.Declaration("X", type_="obs", wires=(0,)),
                            xir.Declaration("Y", type_="obs", wires=(1,)),
                        ],
                        "out": [],
                    },
                    gates={
                        "H": [],
                        "D": [],
                    },
                    includes=["xstd"],
                    observables={
                        "X": [],
                        "Y": [],
                    },
                    options={"cutoff": 4},
                    statements=[xir.Statement("S", [], [0]), xir.Statement("T", [], [0])],
                    variables={"theta"},
                ),
                id="Two XIR programs",
            ),
        ],
    )
    def test_merge_programs(self, programs, want_result):
        """Test that one or more XIR programs can be merged."""
        have_result = xir.Program.merge(*programs)

        assert have_result.called_functions == want_result.called_functions
        assert have_result.variables == want_result.variables
        assert have_result.includes == want_result.includes
        assert have_result.options == want_result.options

        def serialize(mapping: Dict[str, Iterable[Any]]) -> Dict[str, List[str]]:
            """Partially serializes a dictionary with sequence values by casting
            each item of each sequence into a string.
            """
            return {k: list(map(str, v)) for k, v in mapping.items()}

        have_declarations = serialize(have_result.declarations)
        want_declarations = serialize(want_result.declarations)
        assert have_declarations == want_declarations

        assert serialize(have_result.gates) == serialize(want_result.gates)

        assert serialize(have_result.observables) == serialize(want_result.observables)

        have_statements = list(map(str, have_result.statements))
        want_statements = list(map(str, want_result.statements))
        assert have_statements == want_statements

    @pytest.mark.parametrize(
        "name, library, want_program",
        [
            pytest.param(
                "empty",
                {
                    "empty": xir.Program(),
                },
                xir.Program(),
                id="Empty",
            ),
            pytest.param(
                "play",
                {
                    "play": xir.parse_script("func Play;"),
                    "loop": xir.parse_script("use loop; func Loop;"),
                },
                xir.parse_script("func Play;"),
                id="Lazy",
            ),
            pytest.param(
                "coffee",
                {
                    "coffee": xir.parse_script(
                        """
                        use cream;
                        use sugar;
                        use water;
                        func Coffee;
                        """
                    ),
                    "cream": xir.parse_script("func Cream;"),
                    "sugar": xir.parse_script("func Sugar;"),
                    "water": xir.parse_script("func Water;"),
                },
                xir.parse_script(
                    """
                    func Cream;
                    func Sugar;
                    func Water;
                    func Coffee;
                    """
                ),
                id="Flat",
            ),
            pytest.param(
                "bot",
                {
                    "bot": xir.parse_script("use mid; func Bot;"),
                    "mid": xir.parse_script("use top; func Mid;"),
                    "top": xir.parse_script("func Top;"),
                },
                xir.parse_script(
                    """
                    func Top;
                    func Mid;
                    func Bot;
                    """
                ),
                id="Linear",
            ),
            pytest.param(
                "salad",
                {
                    "salad": xir.parse_script("use lettuce; use spinach; func Salad;"),
                    "lettuce": xir.parse_script("use spinach; func Lettuce;"),
                    "spinach": xir.parse_script("func Spinach;"),
                },
                xir.parse_script(
                    """
                    func Spinach;
                    func Lettuce;
                    func Salad;
                    """
                ),
                id="Acyclic",
            ),
            pytest.param(
                "Z",
                {
                    "Z": xir.parse_script("use K1; use K2; use K3; func Z;"),
                    "K1": xir.parse_script("use A; use B; use C; func K1;"),
                    "K2": xir.parse_script("use B; use D; use E; func K2;"),
                    "K3": xir.parse_script("use A; use D; func K3;"),
                    "A": xir.parse_script("use O; func A;"),
                    "B": xir.parse_script("use O; func B;"),
                    "C": xir.parse_script("use O; func C;"),
                    "D": xir.parse_script("use O; func D;"),
                    "E": xir.parse_script("use O; func E;"),
                    "O": xir.parse_script("func O;"),
                },
                xir.parse_script(
                    """
                    func O;
                    func A;
                    func B;
                    func C;
                    func K1;
                    func D;
                    func E;
                    func K2;
                    func K3;
                    func Z;
                    """
                ),
                id="Wikipedia",
            ),
        ],
    )
    def test_resolve_programs(self, name, library, want_program):
        """Test that a valid XIR program include hierarchy can be resolved."""
        have_program = xir.Program.resolve(library=library, name=name)
        assert have_program.serialize() == want_program.serialize()

    @pytest.mark.parametrize(
        "name, library",
        [
            ("null", {}),
            ("init", {"init": make_program(includes=["stop"])}),
        ],
    )
    def test_resolve_unknown_program(self, name, library):
        """Test that a KeyError is raised when an XIR program that is missing
        from the passed XIR library is resolved.
        """
        with pytest.raises(KeyError, match=r"XIR program '[^']+' cannot be found"):
            xir.Program.resolve(library=library, name=name)

    @pytest.mark.parametrize(
        "name, library",
        [
            ("self", {"self": make_program(includes=["self"])}),
            (
                "tick",
                {
                    "tick": make_program(includes=["tock"]),
                    "tock": make_program(includes=["tick"]),
                },
            ),
        ],
    )
    def test_resolve_program_with_circular_dependency(self, name, library):
        """Test that a ValueError is raised when an XIR program that (transitively)
        includes itself is resolved.
        """
        with pytest.raises(ValueError, match=r"XIR program '[^']+' has a circular dependency"):
            xir.Program.resolve(library=library, name=name)

    @pytest.mark.parametrize(
        "name, library",
        [
            (
                "client",
                {
                    "client": make_program(includes=["server"]),
                    "server": make_program(statements=[xir.Statement("Water", [], [0])]),
                },
            ),
            (
                "private",
                {
                    "private": make_program(includes=["colonel"]),
                    "colonel": make_program(includes=["captain"]),
                    "captain": make_program(statements=[xir.Statement("Command", [], [0])]),
                },
            ),
        ],
    )
    def test_resolve_program_with_included_statements(self, name, library):
        """Test that a ValueError is raised when an XIR program that (transitively)
        includes another XIR program with a statement is resolved.
        """
        with pytest.raises(ValueError, match=r"XIR program '[^']+' contains a statement"):
            xir.Program.resolve(library=library, name=name)

    # pylint: disable=protected-access
    @pytest.mark.parametrize("version", ["4.2.0", "0.3.0"])
    def test_validate_version(self, version):
        """Test that a correct version passes validation."""
        xir.Program._validate_version(version)

    # pylint: disable=protected-access
    @pytest.mark.parametrize("version", [42, 0.2, True, object()])
    def test_validate_version_with_wrong_type(self, version):
        """Test that an exception is raised when a version has the wrong type."""
        with pytest.raises(TypeError, match=r"Version '[^']*' must be a string"):
            xir.Program._validate_version(version)

    # pylint: disable=protected-access
    @pytest.mark.parametrize("version", ["", "abc", "4.2", "1.2.3-alpha", "0.1.2.3"])
    def test_validate_version_with_wrong_format(self, version):
        """Test that an exception is raised when a version has the wrong format."""
        with pytest.raises(ValueError, match=r"Version '[^']*' must be a semantic version"):
            xir.Program._validate_version(version)
