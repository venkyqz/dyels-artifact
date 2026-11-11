# Inherited DYELS clients

This directory contains the four native analysis files and five Python utilities inherited from the DYELS artifact.

- types.dl: type recovery rules, included by the storage analysis and GigaDall export adapter.
- storage_eval.dl: storage analysis entry point.
- analytics_client.dl and reentrancy_guards.dl: artifact analyses.
- get_storage_layout.py and storage_layout_parser.py: storage-layout processing.
- evaluate_storage_model.py: artifact layout comparison.
- visualizeout.py: native IR rendering.
- cleanup_dyels_out.py: artifact output cleanup.

Invoke utility scripts by their full path as before; their input/output paths remain relative to the analysis working directory. The sibling import used by evaluate_storage_model.py remains within this directory. visualizeout.py resolves clientlib from the toolchain root after relocation.

Only include/import paths were edited. Original source hashes and reversible edits are recorded in env/dyels-source.json. Custom Remora naming rules live in the sibling remora/ directory.
