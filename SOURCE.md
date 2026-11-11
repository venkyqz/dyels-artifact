# Standalone DYELS analysis dependency

This repository contains the native DYELS/Gigahorse analysis engine, its
signature facts, inherited clients, and source for its Soufflé functors. It has
no Gigadall Python package, Remora implementation, TypeScript frontend, model
client, experiment results, or compiled binaries.

## Source provenance

- Published DYELS artifact: https://doi.org/10.5281/zenodo.17709265
- Artifact image: `sha256:ec574745d97a837537eb370e6598ed23493af574d4ffa291e85794987b7ca61b`
- Gigahorse engine: `4bcaa26c43a6c9444e2d0e7c098d4f0d4b49bdcb`
- Soufflé addon: `992145cd85da891dd28322cd16460f5e23e6dee4`
- Extraction source: `venkyqz/gigadall` commit
  `bf0ffbd4f3eb716fc72978d31c87ba105e6d37a7`, directory
  `core/gigahorse-dyels`; original provenance was recorded in
  `env/dyels-source.json` in that repository.

The addon is vendored source, with its own license, and is not a nested Git
submodule. Its inherited `.gitmodules` declaration has been omitted.

`clients/dyels/` contains the artifact clients relocated from the engine root
client directory, with relative Datalog include paths adjusted. The native
extensions in `clients/gigadall/` come from the extraction-source commit:
`export.dl`, `storage_facts.dl`, and `storage_prototype.dl`. They expose completed
native analysis facts and storage reconstruction to Remora. They are retained
byte-for-byte to preserve the facts consumed by existing runs; they are
integration extensions, not original DYELS algorithms. The engine, type rules,
and functor sources are copied without algorithm changes.

Gigahorse and the addon carry their BSD 3-Clause license texts in `LICENSE` and
`souffle-addon/LICENSE`. Individual file notices, including the Keccak source
notices, remain in place. Extension attribution is recorded above; no separate
upstream Gigadall license was present at the extraction commit.

## Native requirements and execution

Use Python 3.10 or newer, Soufflé 2.4.1 built with a 64-bit domain, a C/C++
compiler supporting C++17 and OpenMP, Boost headers, Z3 headers/library, GNU
Make, and the standard Unix preprocessing/build utilities. The source-only
engine runner uses Python's standard library. Some optional inherited client
utilities have their own Python imports.

The Soufflé development headers must be on the C++ include search path. For a
non-system installation, set `CPLUS_INCLUDE_PATH` to its `include` directory
before running Make, and put its `bin` directory on `PATH`.

Build the source functors with the same domain width as Soufflé:

```bash
make -C souffle-addon WORD_SIZE=64 libsoufflenum.so
export LD_LIBRARY_PATH="$PWD/souffle-addon${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
python gigahorse.py --help
```

The recorded host configuration used Soufflé 2.4.1 and `WORD_SIZE=64`; the
Makefile's default is 32, so specify the width explicitly. Compilation outputs,
shared libraries, caches, and analysis results are intentionally untracked.
The inherited README documents the engine's analysis command-line arguments.
