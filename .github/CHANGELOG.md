## Release 0.1.1 (development release)

### New features since last release

* A `constants` block is added to support declaring script level constants, which can then be used
  as parameters in statements.
  [(#7)](https://github.com/XanaduAI/xir/pull/7)

 ```
 constants:
     p0: [3.141592653589793, 4.71238898038469, 0];
     p1: [1, 0.5, 3.141592653589793];
     p2: [0, 0, 0];
 end;

 Sgate(0.123, 4.5) | [2];
 BSgate(p0, 0.0) | [1, 2];
 Rgate(p1) | [2];
 MeasureHomodyne(phi: p0) | [0];
 """
 ```

### Improvements

* The maximum wire value used in a statement within a definition will be the number of wires
  declared. For example, if a single statement within a definition is applied to wire 4, then the
  declared wires will be 0, 1, 2, 3, and 4.
  [(#2)](https://github.com/XanaduAI/xir/pull/2)

* `xir.Validator` now checks that parameters used in definitions are not also declared constants.
  [(#7)](https://github.com/XanaduAI/xir/pull/2)

### Bug Fixes

* Wires are implicitly added to an observable if they are not explicitly declared.
  [(#2)](https://github.com/XanaduAI/xir/pull/2)

* Validation now checks that applied wires is a subset of declared wires.
  [(#2)](https://github.com/XanaduAI/xir/pull/2)

* `decimal.Decimal` and `DecimalComplex` objects in nested lists and dictionaries are correctly
  converted to ``float`` and ``complex`` respectively when extracted.
  [(#7)](https://github.com/XanaduAI/xir/pull/7)

### Documentation

### Contributors

This release contains contributions from (in alphabetical order):

[Mikhail Andrenkov](https://github.com/Mandrenkov), [Theodor Isacsson](https://github.com/thisac).


## Release 0.1.0 (current release)

### New features since last release

* This is the initial public release.

### Contributors

This release contains contributions from (in alphabetical order):

[Mikhail Andrenkov](https://github.com/Mandrenkov), [Tom Bromley](https://github.com/trbromley), [Ant Hayes](https://github.com/anthayes92), [Theodor Isacsson](https://github.com/thisac), [Josh Izaac](https://github.com/josh146), [Nathan Killoran](https://github.com/co9olguy), [Antal Száva](https://github.com/antalszava).
