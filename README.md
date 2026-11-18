# ICSE'26 DYELS Artifact

This source dependency provides the Gigahorse bytecode lifter, DYELS storage
analysis, native export adapters, signature facts and Soufflé functors used by
Remora. Source versions, attribution, licenses and requirements are documented
in [SOURCE.md](SOURCE.md).

Build the functors using the same domain width as the installed Soufflé:

```bash
make -C souffle-addon WORD_SIZE=64 libsoufflenum.so
export LD_LIBRARY_PATH="$PWD/souffle-addon${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
python gigahorse.py --help
```

Remora invokes `gigahorse.py` with `clients/gigadall/export.dl`, then runs
`clients/gigadall/storage_prototype.dl` on the exported facts. The inherited
native type and layout rules remain unchanged. Unused Docker launchers,
visualization/evaluation utilities, orphan Datalog programs and standalone
functor examples/tests are excluded from this dependency.

Compiled binaries and analysis outputs are untracked. The runtime Python code
uses the standard library. The original Gigahorse engine is described in
Grech et al., *Gigahorse: Thorough, Declarative Decompilation of Smart
Contracts*, ICSE 2019; DYELS provenance is linked in `SOURCE.md`.
