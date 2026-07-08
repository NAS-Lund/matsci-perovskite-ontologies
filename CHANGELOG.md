# Changelog

All notable changes to this project will be documented in this file.

## 2026-07

### Changed
- Renamed `core-ontology` (prefix `core:`) to `experiment-ontology` (prefix `exp:`) for a more descriptive name; no vocabulary changes. `temporal-ontology` (2.0.0 -> 2.1.0) and `matsci-ontology` (2.0.0 -> 2.1.0) updated their imports and term usages accordingly.
- Consistency pass across all ontology files: aligned `@prefix` blocks, standardized ontology-header field order (`versionIRI` before `owl:imports`), standardized `rdfs:label` to a bare short name, switched `perovskitemat` section banners from ALL CAPS to Title Case, and dropped stray `@en` tags from `dcterms:alternative` literals in `perovskitemat` to match the rest of the collection. `qqval-ontology` bumped 1.1.0 -> 1.1.1; `perovskitemat` bumped 1.2.3 -> 1.2.4.

## 2026-05

### Added
- Added a qqval ontology, developed to express quantitative values whose reported numeric component carries an epistemic qualifier: approximations, ranges, bounds...

### Changed
- All quantity qualifiers were refactored in a new qqval ontology