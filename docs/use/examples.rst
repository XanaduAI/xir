Examples
========

The examples below demonstrate how the XIR can be used to model quantum circuits.

Qubit Circuits
--------------

For the sake of brevity, the following preamble is omitted from the qubit
circuit examples:

.. code-block:: text

    // Gate Declarations
    gate H [a];
    gate X [a];
    gate Z [a];
    gate SWAP [a, b];
    gate Phase(theta) [a];

    // Output Declarations
    out amplitude(state) [a, b];

    // Gate Definitions
    gate CNOT [c, t]:
        ctrl [c] X | [t];
    end;


Bell State Amplitudes
^^^^^^^^^^^^^^^^^^^^^

To return the amplitudes of a **Bell state**:

.. code-block:: text

    H | [0];
    CNOT | [0, 1];

    amplitude(state: [0, 0]) | [0, 1];
    amplitude(state: [0, 1]) | [0, 1];
    amplitude(state: [1, 0]) | [0, 1];
    amplitude(state: [1, 1]) | [0, 1];


GHZ State Preperation
^^^^^^^^^^^^^^^^^^^^^

To prepare a **Greenberger–Horne–Zeilinger state** over four qubits:

.. code-block:: text

    H | [0];
    ctrl [0] X | [1];
    ctrl [1] X | [2];
    ctrl [2] X | [3];


Qubit State Teleportation
^^^^^^^^^^^^^^^^^^^^^^^^^

To (locally) teleport a qubit state from wire ``0`` to wire ``2``:

.. code-block:: text

    H | [1];
    CNOT | [1, 2];

    CNOT | [0, 1];
    H | [0];

    ctrl [1] X | [2];
    ctrl [0] Z | [2];


Grover Diffusion Operator
^^^^^^^^^^^^^^^^^^^^^^^^^

To apply the **Grover Diffusion Operator** to three qubits:

.. code-block:: text

    gate H2:
        H | [0];
        H | [1];
    end;

    gate X2:
        X | [0];
        X | [1];
    end;

    H2 | [0, 1];
    X2 | [0, 1];

    Z | [2];
    ctrl [0, 1] X | [2];
    Z | [2];

    X2 | [0, 1];
    H2 | [0, 1];


Quantum Fourier Transform
^^^^^^^^^^^^^^^^^^^^^^^^^

To apply the **Quantum Fourier Transform** to four qubits:

.. code-block:: text

    gate P2 [w]: Phase(theta: pi / 2) | [w]; end;
    gate P3 [w]: Phase(theta: pi / 4) | [w]; end;
    gate P4 [w]: Phase(theta: pi / 8) | [w]; end;

    H | [0];
    ctrl [1] P2 | [0];
    ctrl [2] P3 | [0];
    ctrl [3] P4 | [0];

    H | [1];
    ctrl [2] P2 | [1];
    ctrl [3] P3 | [1];

    H | [2];
    ctrl [3] P2 | [2];

    H | [3];

    SWAP | [0, 3];
    SWAP | [1, 2];


Continuous Variable Circuits
----------------------------

Similar to the qubit examples, the preamble below is assumed for all continuous
variable circuits:

.. code-block:: text

    // Function Declarations
    func sqrt;

    // Gate Declarations
    gate S(z) [a];
    gate X(p) [a];
    gate Z(p) [a];
    gate BS(theta, phi) [a, b];

    // Output Declarations
    out MeasureX [a];
    out MeasureP [a];
    out MeasureFock [a, b, c];


Gaussian State Teleportation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To teleport a Gaussian state from wire ``0`` to wire ``2``:

.. code-block:: text

    S(-1.23) | [1];
    S(1.23) | [2];
    BS(theta: pi / 4, phi: pi) | [1, 2];

    BS(theta: pi / 4, phi: pi) | [0, 1];
    MeasureX | [0];
    MeasureP | [1];

    X(sqrt(2) * outs[0]) | [2];
    Z(sqrt(2) * outs[1]) | [2];


GKP State Approximation
^^^^^^^^^^^^^^^^^^^^^^^

To approximate a **Gottesman-Kitaev-Preskill state** with a Fock cutoff dimension of 4:

.. code-block:: text

    options:
        cutoff: 4;
    end;

    S(-1.38155106) | [0];
    S(-1.21699567) | [1];
    S(0.779881700) | [2];

    BS(1.04182349, 1.483536390) | [0, 1];
    BS(0.87702211, 1.696290600) | [1, 2];
    BS(0.90243916, -0.24251599) | [0, 1];

    S(0.1958) | [2];

    MeasureFock | [0, 1, 2];