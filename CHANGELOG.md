# Changelog

All notable changes to this project will be documented in this file.

## 2026-07

### Added
- Added `qqval-shapes.ttl` and `observation-shapes.ttl`, SHACL shapes graphs mirroring the OWL cardinality/qualifier restrictions already declared in `qqval-ontology` (`ApproximateQuantityValue`, `QuantityRange`) and `observation-ontology` (`EnvironmentCondition`, `QuantitativeObservation`, `QualitativeObservation`), so an extraction pipeline can reject non-conforming data outright instead of relying on OWL's open-world semantics. Validated against hand-written pass/fail fixtures with `pyshacl`.
- Added optional `qqval:confidenceLevel` and `qqval:distributionAssumption` (with a small open `qqval:DistributionAssumption` vocabulary, seeded with `qqval:Gaussian` / `qqval:Unspecified`) to `qqval-ontology`, so a reported uncertainty is never silently assumed to be a symmetric 1-sigma Gaussian.
- Documented an explicit "extraction convention" in `qqval-ontology` and `observation-ontology`: absence of a result triple (not a placeholder value or individual) is the intended way to express "not extracted from source". `qqval-ontology` bumped 1.1.1 -> 1.2.0.
- Added an explicit default-qualifier rule to `qqval:ApproximateQuantityValue`'s documentation: prefer it over `qqval:QuantityRange` unless bounds carry independently-tracked provenance or units.

### Changed
- Renamed `core-ontology` (prefix `core:`) to `experiment-ontology` (prefix `exp:`) for a more descriptive name; no vocabulary changes. `temporal-ontology` (2.0.0 -> 2.1.0) and `matsci-ontology` (2.0.0 -> 2.1.0) updated their imports and term usages accordingly.
- Consistency pass across all ontology files: aligned `@prefix` blocks, standardized ontology-header field order (`versionIRI` before `owl:imports`), standardized `rdfs:label` to a bare short name, switched `perovskitemat` section banners from ALL CAPS to Title Case, and dropped stray `@en` tags from `dcterms:alternative` literals in `perovskitemat` to match the rest of the collection. `qqval-ontology` bumped 1.1.0 -> 1.1.1; `perovskitemat` bumped 1.2.3 -> 1.2.4.
- Universality pass (part 1 of a multi-phase effort to make the observation/temporal scaffolding domain-neutral, not just materials-science-tolerant):
  - Tightened `obs:hasQuantityResult`'s range from `qudt:QuantityValue` to `qqval:ApproximateQuantityValue`, and reworded its comment, to match the mandatory (not merely "preferred") restriction already present on `obs:QuantitativeObservation`. `observation-ontology` bumped 3.0.0 -> 3.1.0.
  - Moved materials-science illustrations (`atmosphere`, `humidity`, `temperature`, `pressure`, `illumination`, `biasing`, ...) out of `rdfs:comment` prose and into `skos:example` on `obs:EnvironmentFactor`, `tempo:OperationProcess`, `tempo:StorageAgingProcess`, `tempo:ExposureAgingProcess`, `tempo:OperationalAgingProcess`, and `tempo:SampleTemporalState`, so illustrations read as examples rather than scope boundaries. Added the `skos:` prefix to `observation-ontology` and `temporal-ontology` for this.
- Moved `tempo:airAgedSampleState` and `tempo:vacuumAgedSampleState` from `temporal-ontology` to `matsci-ontology` (as `matsci:airAgedSampleState` / `matsci:vacuumAgedSampleState`) -- "air" and "vacuum" are materials-science storage conditions that had been missed in the 3.0.0 pass that moved the rest of the domain-specific temporal vocabulary out of `temporal-ontology`. `temporal-ontology` bumped 3.0.0 -> 3.1.0; `matsci-ontology` bumped 2.2.0 -> 2.3.0.

## 2026-05

### Added
- Added a qqval ontology, developed to express quantitative values whose reported numeric component carries an epistemic qualifier: approximations, ranges, bounds...

### Changed
- All quantity qualifiers were refactored in a new qqval ontology