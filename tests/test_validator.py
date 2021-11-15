"""Tests for the validator class"""

import inspect
import re

import pytest

import xir


@pytest.mark.parametrize(
    "val, expected",
    [
        ("sin(4.2)", "sin"),
        ("cos()", "cos"),
        ("constant", "constant"),
        ("rotate(1, 2, 3)", "rotate"),
        ("pivot (1, 2) ", "pivot"),
        ("outside(inside())", "outside"),
    ],
)
def test_stem_function(val, expected):
    """Tests that the ``stem`` function correctly removes parentheses."""
    res = xir.validator.stem(val)
    assert res == expected


class TestValidationError:
    """Unit tests for the ValidationError exception."""

    @pytest.mark.parametrize(
        "msg, match",
        [
            ("a very random error message", r"a very random error message"),
            (
                ["issue_1", "issue_2"],
                r"the following issues have been detected:\n\t\-\> issue\_1\n\t\-\> issue\_2",
            ),
            ([], r"XIR program is invalid."),
            (None, r"XIR program is invalid."),
        ],
    )
    def test_default_error(self, msg, match):
        """Tests that the ValidationError exception produces the correct error messages."""
        with pytest.raises(xir.validator.ValidationError, match=match):
            raise xir.validator.ValidationError(msg)


class TestValidatorIntegration:
    """Integration tests for the Validator class."""

    @staticmethod
    def _create_full_match(matches):
        """Create the full match based on a list of matching validations. This makes
        sure that only the specified validation error messages are being raised."""
        return (
            re.escape(
                "XIR program is invalid: the following issues have been detected:\n\t-> "
                + "\n\t-> ".join(matches)
            )
            + r"$"  # match no more matches
        )

    @pytest.mark.parametrize(
        "decl, matches",
        [
            (
                "gate cnot[0, 0];",
                [
                    "Declaration 'gate cnot[0, 0]' has duplicate wires labels.",
                ],
            ),
        ],
    )
    def test_message_reset(self, decl, matches):
        """Tests that validator messages are reset between different runs."""

        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(decl)
            xir.Validator(program).run()

        # run it again to make sure the issue messages don't "pile up"
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(decl)
            xir.Validator(program).run()

    @pytest.mark.parametrize(
        "decl, matches",
        [
            (
                "gate cnot[0, 0];",
                [
                    "Declaration 'gate cnot[0, 0]' has duplicate wires labels.",
                ],
            ),
            (
                "gate Sgate(a, a)[0];",
                [
                    "Declaration 'gate Sgate(a, a)[0]' has duplicate parameter names.",
                ],
            ),
            (
                "gate Sgate(4.2)[1];",
                [
                    "Declaration 'gate Sgate(4.2)[1]' has parameters which are not strings.",
                ],
            ),
        ],
    )
    def test_check_declarations(self, decl, matches):
        """Test that incorrect declarations raise the correct exceptions."""

        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(decl)
            xir.Validator(program).run()

    @pytest.mark.parametrize(
        "stmt, matches",
        [
            (
                "S2gate(c: 3) | [0]",
                [
                    "Statement 'S2gate(c: 3) | [0]' passes the wrong parameters. Expected 'a, b'.",
                ],
            ),
            (
                "S2gate(4, 1, 2) | [0]",
                ["Statement 'S2gate(4, 1, 2) | [0]' has 3 parameter(s). Expected 2."],
            ),
            (
                "S2gate(4, 2) | [0, 1]",
                ["Statement 'S2gate(4, 2) | [0, 1]' has 2 wire(s). Expected 1."],
            ),
            (
                "S2gate(4, 2) | [0, 0, 2]",
                [
                    "Statement 'S2gate(4, 2) | [0, 0, 2]' has 3 wire(s). Expected 1.",
                    "Statement 'S2gate(4, 2) | [0, 0, 2]' is applied to duplicate wires.",
                ],
            ),
            (
                "cnot | [1, 1]",
                ["Statement 'cnot | [1, 1]' is applied to duplicate wires."],
            ),
            (
                "ctrl[0] Sample | [1, 2]",
                [
                    (
                        "Statement 'ctrl[0] Sample | [1, 2]' is an output statement but has 'ctrl' "
                        "or 'inv' modifiers."
                    )
                ],
            ),
            (
                "inv Sample | [1, 2]",
                [
                    (
                        "Statement 'inv Sample | [1, 2]' is an output statement but has 'ctrl' "
                        "or 'inv' modifiers."
                    )
                ],
            ),
            (
                "inv ctrl[0, 3] inv Sample | [1, 2]",
                [
                    (
                        "Statement 'ctrl[0, 3] Sample | [1, 2]' is an output statement but has "
                        "'ctrl' or 'inv' modifiers."
                    )
                ],
            ),
            (
                "Sample | [x, y]",
                [
                    (
                        "Statement 'Sample | [x, y]' is applied to named wires. Only integer wire "
                        "labels are allowed at a script level."
                    )
                ],
            ),
            (
                "ctrl[0, 1] S2gate(0.3, 0.4) | [0]",
                [
                    (
                        "Statement 'ctrl[0, 1] S2gate(0.3, 0.4) | [0]' has control wires "
                        "{0} which are also applied."
                    )
                ],
            ),
            ("MyGate | [0]", ["Name 'MyGate' has not been declared."]),
        ],
    )
    def test_check_statements(self, stmt, matches):
        """Test that incorrectly defined statements raise the correct exceptions."""

        script = f"gate S2gate(a, b)[0];gate cnot[0, 1];out Sample[0, 1];{stmt};"

        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(script)
            xir.Validator(program).run()

    def test_check_recursive_defs(self):
        """Test that recursively defined definitions raise the correct exceptions."""

        script = inspect.cleandoc(
            """
            gate MooGate:
                MyGate | [0, 1];
            end;

            gate MyGate:
                MooGate | [0, 1];
            end;
            """
        )

        matches = [
            "Gate definition 'MooGate' has a circular dependency.",
            "Gate definition 'MyGate' has a circular dependency.",
        ]

        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(script)
            xir.Validator(program).run()

    @pytest.mark.parametrize(
        "stmt, matches",
        [
            (
                "gate MyGate[a, b]: BSgate(0.1, 0.2) | [0, a]; end;",
                [
                    (
                        "Definition 'MyGate' is invalid. Only named wires can be applied when "
                        "declaring named wires."
                    ),
                    (
                        "Definition 'MyGate' is invalid. Applied wires [0, a] differ from "
                        "declared wires [a, b]."
                    ),
                ],
            ),
            (
                "gate MyGate(a)[a, b]: BSgate(0.1, 0.2) | [a, b]; end;",
                ["Definition 'MyGate' is invalid. Wire and parameter names must differ."],
            ),
            (
                "gate MyGate[a, b]: BSgate(0.1, 0.2) | [c, d]; end;",
                [
                    (
                        "Definition 'MyGate' is invalid. Applied wires [c, d] differ from "
                        "declared wires [a, b]."
                    )
                ],
            ),
            (
                "gate MyGate: BSgate(0.1, 0.2) | [2, a]; end;",
                [
                    (
                        "Definition 'MyGate' is invalid. Applied wires [2, a] differ from "
                        "declared wires [0, 1, 2]."
                    )
                ],
            ),
        ],
    )
    def test_check_gate_definitions(self, stmt, matches):
        """Test that incorrectly defined definitions raise the correct exceptions."""

        script = f"gate BSgate(theta, phi)[0, 1]; {stmt}"

        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(script)
            xir.Validator(program).run()

    @pytest.mark.parametrize(
        "stmt, matches",
        [
            (
                "obs MyObs[a, b]: 3.4, X[0] @ Y[a]; end;",
                [
                    (
                        "Definition 'MyObs' is invalid. Only named wires can be applied when "
                        "declaring named wires."
                    ),
                    (
                        "Definition 'MyObs' is invalid. Applied wires [0, a] differ from "
                        "declared wires [a, b]."
                    ),
                ],
            ),
            (
                "obs MyObs(a)[a, b]: a, X[a] @ Y[b]; end;",
                ["Definition 'MyObs' is invalid. Wire and parameter names must differ."],
            ),
            (
                "obs MyObs(x)[a, b]: x, X[c] @ Y[d]; end;",
                [
                    (
                        "Definition 'MyObs' is invalid. Applied wires [c, d] differ from "
                        "declared wires [a, b]."
                    )
                ],
            ),
            (
                "obs MyObs: 4.2, X[a] @ Y[0]; end;",
                [
                    (
                        "Definition 'MyObs' is invalid. Applied wires [a, 0] differ from declared "
                        "wires [0]."
                    )
                ],
            ),
            (
                "obs MyObs: apple, X[0] @ Y[1]; end;",
                [("Statement 'apple, X[0] @ Y[1]' has an undeclared prefactor variable 'apple'.")],
            ),
            (
                "obs MyObs: 2, p[0] @ Y[1]; end;",
                [
                    (
                        "Observable statement '2, p[0] @ Y[1]' is invalid. Observable(s) ['p'] "
                        "have not been declared."
                    )
                ],
            ),
            (
                "obs MyObs: 2, X[0] @ Y[0]; end;",
                [
                    (
                        "Observable statement '2, X[0] @ Y[0]' is invalid. Products of observables "
                        "cannot be applied to the same wires."
                    )
                ],
            ),
        ],
    )
    def test_check_observable_definitions(self, stmt, matches):
        """Test that incorrectly defined obs definitions raise the correct exceptions."""
        stmt = "obs X[0];obs Y[0];obs Z[0];" + stmt
        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(stmt)
            xir.Validator(program).run()

    @pytest.mark.parametrize(
        "validators, matches",
        [
            (
                {
                    "statements": True,
                    "definitions": True,
                },
                [
                    "Statement 'Sgate(c: 3) | [0]' passes the wrong parameters. Expected 'a, b'.",
                    (
                        "Statement 'ctrl[1] MeasureHomodyne(phi: 3) | [0]' is an output statement "
                        "but has 'ctrl' or 'inv' modifiers."
                    ),
                    "Gate definition 'MyGate' has a circular dependency.",
                    "Gate definition 'MooGate' has a circular dependency.",
                    "Name 'Rgate' has not been declared.",
                    "Statement 'MyGate | [0, 2]' has 2 wire(s). Expected 3.",
                ],
            ),
            (
                {
                    "statements": False,
                    "definitions": True,
                },
                [
                    "Gate definition 'MyGate' has a circular dependency.",
                    "Gate definition 'MooGate' has a circular dependency.",
                    "Name 'Rgate' has not been declared.",
                    "Statement 'MyGate | [0, 2]' has 2 wire(s). Expected 3.",
                ],
            ),
            (
                {
                    "statements": True,
                    "definitions": False,
                },
                [
                    "Statement 'Sgate(c: 3) | [0]' passes the wrong parameters. Expected 'a, b'.",
                    (
                        "Statement 'ctrl[1] MeasureHomodyne(phi: 3) | [0]' is an output statement "
                        "but has 'ctrl' or 'inv' modifiers."
                    ),
                ],
            ),
        ],
    )
    def test_set_validators(self, validators, matches):
        """Test that switching on and off validators works as expected."""
        script = inspect.cleandoc(
            """
            gate Sgate(a, b)[0];
            gate BSgate(theta, phi)[0, 1];
            out MeasureHomodyne(phi)[0];

            Sgate(c: 3) | [0];
            ctrl[1] BSgate(0.1, 0.0) | [0, 2];

            gate MyGate:
                Sgate(0.7, 0) | [1];
                BSgate(0.1, 0.0) | [0, 1];
                ctrl[1,1] Rgate(0.2) | [0];
                MooGate | [0, 2];
            end;

            gate MooGate[0, 2]:
                MyGate | [0, 2];  // circular dependency
            end;

            ctrl[1] MeasureHomodyne(phi: 3) | [0];
            """
        )

        match = self._create_full_match(matches)
        with pytest.raises(xir.validator.ValidationError, match=match):
            program = xir.parse_script(script)

            val = xir.Validator(program)
            val._validators.update(validators)  # pylint: disable=protected-access
            val.run()
