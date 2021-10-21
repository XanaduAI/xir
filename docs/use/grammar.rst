Grammar
=======

Overview
--------

An XIR script consists of five parts, all of which are optional. Each of these
is expanded on in detail following some initial examples:

1. **Includes.** Included XIR scripts which have been prepared to contain useful
declarations or definitions.

.. code-block:: text

    use circuit;

2. **Options.** Settings at the global scope.

.. code-block:: text

    options:
        dimension: 3;
    end;

3. **Declarations.** Declarations of gates, observables, functions, and outputs.

.. code-block:: text

    gate CNOT [control, target];
    obs ScaledZ(scalar) [wire];
    func arctan(x);
    out amplitude;


4. **Definitions.** Definitions of gates and observables.

.. code-block:: text

    // Define a custom 2-qubit Hadamard gate.
    gate H2 [a, b]:
        H | [a];  // Apply a Hadamard to the first wire.
        H | [b];  // Apply a Hadamard to the second wire.
    end;

5. **Statements.** Gate application statements and measurements.

.. code-block:: text

    H2 | [0, 1];
    amplitude(state: [0, 0]) | [0, 1];


.. note::

  All includes *must* appear at the start of an XIR script. The ordering of the
  other parts does not matter.

Includes
--------

The ``use`` directive specifies the name of an XIR script to be included in the
current XIR script. An included XIR script may contain gate or observable
declarations and definitions, mathematical function declarations, or measurement
and post-processing statistics declarations.

Here is an example of an XIR script that includes two other XIR scripts from
the local filesystem:

.. code-block:: text

    use dir/file;
    use /abs/path/to/script;

Note that the first include statement uses a *relative* path to specify the XIR
script at ``dir/file.xir`` while the second statement uses an *absolute* path to
include ``/abs/path/to/script.xir``.

.. warning::

  For security reasons, remote XIR interpreters should *not* support include
  statements that specify XIR scripts using a relative or absolute filepath.

An alternative syntax can be used to include XIR libraries offered by a cloud
provider:

.. code-block:: text

    use <xc/x8>;

This include statement references an XIR library named ``xc/x8`` which is
assumed to be known to the XIR interpreter processing the XIR script above.

.. note::

    Full support of the ``use`` directive is still a work-in-progress in the
    current release of the XIR. Specifically, includes must be manually passed
    to :meth:`xir.Program.resolve()` in order to be considered during include
    resolution.

Options
-------

The ``options`` block is a simple way to pass arbitrary metadata to an XIR
interpreter. The syntax for specifying options is analogous to that of a (flat)
JSON object or Python dictionary. Each XIR interpreter is free to define its own
set of supported options and choose their semantics.

.. code-block:: text

    options:
        dimension: 4;              // Set the Fock cutoff dimension for CV gates to 4.
        simplify: true;            // Simplify the circuit using gate identities.
        tags: [experimental, d20];  // Associate some tags with the program result.
    end;

Declarations
------------

There are no gate, observable, function, or output declarations included in the
XIR. There are also very few keywords (see :ref:`keywords`). Consequently, the following operations
must be declared within the main script or within scripts included using the ``use`` keyword:

* **Gates.** Gates are declared by writing the ``gate`` keyword followed by the
  name of the gate, the names of the gate parameters (optional), and the wire
  labels used by the gate definition.

  .. code-block:: text

    gate RX(theta) [wire];
    gate CNOT [control, target];

* **Observables.** Observables are declared similarly to gate declarations
  except the ``obs`` keyword is used instead:

  .. code-block:: text

    obs Z3 [w1, w2];

* **Functions.** Functions are declared by writing the ``func`` keyword followed
  by the name of the function and, optionally, the names of the function
  parameters.

  .. code-block:: text

    func atan(x);
    func one;

* **Outputs.** Outputs are declared the similarly to gate declarations except the
  ``out`` keyword is used instead:

  .. code-block:: text

    out amplitude(state) [...];

Note that the XIR interpreter is responsible for implementing the correct
semantics of a gate. For example, to the XIR parser, all single-qubit
non-parametrized gates are equivalent aside from their names.


Definitions
-----------

Conceptually, a gate or observable definition is composed of two parts:

#. The declaration of the gate or observable.
#. The implementation of the gate or observable.

Gates and observables which are not implemented by a device must have a
corresponding definition in an XIR script.

* **Gates.** Gates are defined by writing their declaration (with a trailing
  ``:`` instead of a ``;``), specifying one or more gate applications,
  and then finishing with an ``end;`` token. Preferably, but not necessarily,
  the statements are written on separate lines.

  .. code-block:: text

    gate RX3(theta) [w1, w2, w3]:
        RX(theta) | [w2];
        RX(theta) | [w1];
        RX(theta) | [w3];
    end;

  .. note::

    When wire labels are specified in the declaration part of the
    definition, they must be valid *non-integer* names. Conversely, if no wire
    labels are specified in the declaration, the wire labels inside the gate
    definition must all be *integers*. In this latter case, the declaration is
    implicitly set to ``[0..n]`` where ``n`` is the largest wire label appearing
    in the gate definition. Rewriting the example above,

    .. code-block:: text

      gate RX3(theta):
          RX(theta) | [1];
          RX(theta) | [0];
          RX(theta) | [2];
      end;

  .. warning::

    It is illegal to use a wire label which does not appear in the declaration of
    a gate when at least one wire label is explicitly specified. For example,

    .. code-block:: text

      gate RX3(theta) [w1, w2]:
          RX(theta) | [w2];
          RX(theta) | [w1];
          RX(theta) | [0];   // Always illegal (not declared)
      end;

  .. note::

    Gates that have been explicitly defined do not require a preceding declaration statement.

* **Observables.** Observables are defined in a similar way except the gate
  applications are replaced with observable statements consisting of a prefactor
  term followed by the tensor product of one or more unary gates.

  .. code-block:: text

    obs Z3 [w1, w2, w3]:
        1.23, Z[x1];
        -0.4, Z[w2] @ Z[w3];
    end;


Statements
----------

There are two types of statements in an XIR script: gate application statements
and output statements.

* **Gate Applications.** A gate application statement consists of the name of
  the gate to be applied, followed by the parameter values of the gate (optional),
  a vertical pipe, and finally the wires on which the gate should be applied.
  Parameters may contain mathematical expressions which reference the usual
  arithmetic operations, any declared functions, or any variables accessible
  from the specific scope (e.g., inside a gate definition). Wires are always
  represented by either integers or names, enclosed in square brackets, and
  separated by commas.

  .. code-block:: text

    RY(1.23) | [0];
    Rot(0.1, 0.2, 0.3) | [0, 1, 2];

  .. note::

    At the global scope, wire labels are *always* integers. Specifically, they
    are ``[0..n]`` where ``n`` is the largest wire label appearing in a gate
    application statement (that is not inside a gate definition).

  There are also two modifiers which may be prepended to a gate application
  statement, namely ``ctrl`` and ``inv``. The former specifies (additional)
  control wires to be applied to a gate and ``inv`` signifies that the
  inverse of the ensuing gate should be taken.

  .. code-block:: text

    ctrl [0] RY(1.23) | [1];
    inv Y | [0];

* **Output Statements.** An output statement has the same syntax as a gate
  application statement; however, the ``ctrl`` and ``inv`` modifiers are
  disallowed.

  .. code-block:: text

    amplitude(state: [0, 1, 0]) | [0, 1, 2];
    samples(shots: 1000, approximate: false) | [0, 1, 2];


Commenting
----------

XIR uses C-style single-line comments where everything after ``//`` is ignored
by the parser.

.. code-block:: text

    RX(0.42) | [0];  // This is a comment.

Comments that span multiple lines are not explicitly supported.

.. code-block:: text

    // This line is also a comment, and
    // is spread out over multiple lines.
    CNOT | [0, 1];


Notes
-----

* An empty file is a valid XIR script.

* The XIR grammar does not enforce any whitespace constraints (with the sole
  exception of comments); it is possible to remove all indentation and line
  breaks without affecting how an XIR script is parsed.

* A "name" in an XIR script can contain letters (uppercase or lowercase), digits,
  and underscores, but must start with either a letter or an underscore.

* Names and keywords are case-sensitive.

* Basic arithmetic (used to express a parameter value) is handled by the parser
  however, more complicated mathematical expressions (such as those containing
  variables) may not be fully simplified.

* (Complex) floating-point numbers are stored as (:doc:`DecimalComplex
  </api/xir.DecimalComplex>`) `decimal.Decimal
  <https://docs.python.org/3/library/decimal.html>`_ objects to avoid losses of
  precision.

* Specifying a range of integer-valued wire labels can be achieved using the ``[a..b]`` syntax,
  which is equivalent to ``[a, a + 1, ..., b - 2, b - 1]``. For example, the gate statement
  ``QFT | [4..8];`` applies a quantum Fourier transform to wires ``[4, 5, 6, 7]``.

.. _keywords:

Keywords
--------

* ``ctrl``: Control wires modifier for statements.
* ``end``: End of a definition or options section.
* ``false``: Boolean false.
* ``func``: Declaration of mathematical functions.
* ``gate``: Gate declaration or definition.
* ``inv``: Inverse modifier for statements.
* ``obs``: Observable declaration or definition.
* ``options``: Start of script level options section.
* ``out``: Declaration of measurements and post-processing statistics.
* ``pi``: Mathematical constant pi (:math:`\pi`).
* ``true``: Boolean true.
* ``use``: Include external XIR files.
