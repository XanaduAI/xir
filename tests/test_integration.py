"""Integration tests for the XIR"""

import pytest

import xir
from xir.utils import is_equal

photonics_script = """
gate Sgate(a, b)[0];
gate BSgate(theta, phi)[0, 1];
gate Rgate(p0)[a];
func cos(a);
out MeasureHomodyne(phi)[0];

Sgate(cos(0.7), 0) | [1];
BSgate(0.1, 0.0) | [0, 2];
Rgate(0.2) | [1];

MeasureHomodyne(phi: 3) | [0];
"""

photonics_script_no_decl = """
use photonics_gates;

Sgate(0.7, 0) | [1];
BSgate(0.1, 0.0) | [0, 1];
Rgate(0.2) | [1];

MeasureHomodyne(phi: 3) | [0];
"""

qubit_script = """
// this file works with the current parser
use <qubit>;

gate h(x)[a, b, c]:
    rz(-2.3932854391951004) | [a];
    rz(sin(3)) | [b];
    ctrl[a] inv rz(x) | [c];
    // rx(pi / sin(3 * 4 / 2 - 2)) | [b, c];
end;

obs o(a)[0, 1]:
    sin(a), X[0] @ Z[1];
    -1.6, Y[0];
    2.45, Y[0] @ X[1];
end;

g_one(pi) | [0, 1];
g_two | [2];
g_three(1, 3.3) | [2];
inv g_four(1.23) | [2];
ctrl[0, 2] g_five(3.21) | [1];

// The circuit and statistics
ry(1.23) | [0];
rot(0.1, 0.2, 0.3) | [1];
h(0.2) | [0, 1, 2];
ctrl[3] inv h(0.2) | [0, 1, 2];

// TODO: support observables as parameters
sample(observable: o(0.2), shots: 1000) | [0, 1];
"""

jet_script = """
use <xc/jet>;

options:
    cutoff: 13;
    anything: 42;
end;

obs H2[0, 1];

// declared wires are implicit, but needed for test comparison
gate H2[0, 1]:
    H | [0];
    H | [1];
end;

obs X1[0]:
    1, X[0];
end;

H2 | [0, 1];
CNOT | [0, 1];
amplitude(state: [0, 0]) | [0, 1];
amplitude(state: [0, 1]) | [0, 1];
amplitude(state: [1, 0]) | [0, 1];
amplitude(state: [1, 1]) | [0, 1];
"""

simple_script = """
gate rx(x)[0];
gate ry(x)[0];
gate rz(x)[0];
func sin(x);
obs X[0];
obs Y[0];
obs Z[0];

gate rot(x, y, z)[a]:
    rx(sin(4.3)) | [a];
    ry(y) | [a];
    rz(z) | [a];
end;

obs xyz(x, y, z)[a, b]:
    x, X[a] @ Y[b];
    y, Y[a] @ Z[b];
    sin(z), Z[a] @ X[b];
end;

rx(0) | [0];
"""


class TestParser:
    """Integration tests for parsing, and serializing, XIR scripts"""

    @pytest.mark.parametrize(
        "circuit",
        [qubit_script, photonics_script, photonics_script_no_decl, jet_script, simple_script],
    )
    def test_parse_and_serialize(self, circuit):
        """Test parsing and serializing an XIR script.

        Tests parsing, serializing as well as the ``is_equal`` utils function.
        """
        program = xir.parse_script(circuit)
        xir.Validator(program).run()
        result = program.serialize()
        assert is_equal(result, circuit)
