# Native export adapter

`export.dl` includes `../dyels/types.dl`, runs the inherited type analysis,
and exports GD/GDR facts and DYELS type/layout products. `storage_facts.dl`
exports completed storage and contextual facts. `storage_prototype.dl`
includes the inherited storage reconstruction client.

These integration extensions retain the directory name used by their source
repository. See `../../SOURCE.md` for provenance. Inherited DYELS clients are
in `../dyels/`.
