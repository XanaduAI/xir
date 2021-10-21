<p align="center">
  <img height=65 alt="XIR" src="https://raw.githubusercontent.com/XanaduAI/xir/main/docs/_static/xir_title.svg">
</p>


<p align="center">
  <b>XIR</b> is an intermediate representation language for quantum circuits.
</p>

## Features

- *Simple*. Easy to learn, write, and understand.

- *Modular*. Compose observables, gates, and entire XIR programs.

- *Flexible*. Declare or define your own gates and observables.

## Installation

XIR requires Python version 3.7 or above. Installation of XIR, as well as all
dependencies, can be done using pip:

```console
pip install quantum-xir
```

## Examples

A curated selection of XIR scripts can be found in the [Examples](docs/use/examples.rst) page of the Sphinx documentation; however, the example below demonstrates a general overview of the syntax:

```
// Include additional script
use my_declarations;

// Declare custom gates
gate RX(theta) [w1];
gate RY(theta) [w1];
gate RZ(theta) [w1];
gate Toffoli [w1, w2, w3];

// Declare a function
func sin(x);

// Declare observables
obs X [w1]; obs Y [w1]; obs Z [w1];

// Declare outputs
out sample(shots) [0..8];
out expval(observable) [w1, w2];
out amplitude(state) [0..8];

// Define a composite gate.
gate R3T(theta)[a, b, c, d]:
    RX(theta: -2.3932854391951004) | [a];
    RY(theta) | [b];
    RZ(pi / sin(3 * 4 / 2 - 2)) | [c];
    Toffoli | [b, c, d];
end;

// Define an observable.
obs XYZ [w1, w2]:
    -1.6, X[w1];
    0.73, Y[w1] @ Z[w2];
end;

// Apply the gate twice.
R3T(1.23) | [0, 1, 2, 3];
R3T(theta: 3.21) | [4..8];

// Compute various outputs.
sample(shots: 1000) | [0..8];
expval(observable: XYZ) | [0, 3];
amplitude(state: [0, 1, 0, 1, 0, 0, 1, 1]) | [0..8];
```

## Contributing to XIR

We welcome contributions - simply fork the XIR repository, and then make a [pull
request](https://help.github.com/articles/about-pull-requests/) containing your
contribution. All contributors to XIR will be listed as authors on the releases.
See our [changelog](.github/CHANGELOG.md) for more details.

We also encourage bug reports, suggestions for new features and enhancements,
and even links to cool projects or applications built on XIR. Visit the [contributions
page](.github/CONTRIBUTING.md) to learn more about sharing your ideas with the
XIR team.

## Support

- **Source Code:** https://github.com/XanaduAI/xir
- **Issue Tracker:** https://github.com/XanaduAI/xir/issues

If you are having issues, please let us know by posting the issue on our GitHub issue tracker.

## Authors

XIR is the work of [many contributors](https://github.com/XanaduAI/xir/graphs/contributors).

## License

XIR is **free** and **open source**, released under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
