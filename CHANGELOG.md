# Changelog

All notable changes to this project will be documented in this file.

## 2026-08-07 — temporal routes

A temporal fact takes one route, determined by what the fact is: process
duration → `life:hasDuration`, entity age → `life:hasEntityAge`, observation
delay → `life:hasObservationDelay`, instrument setting → `obs:hasSetting`,
measured temporal quantity → `life:hasTemporalQuantityResult`. A temporal fact
is not a process condition. Previously the condition route was equally
available, with nothing to select between the two; extraction split across
both, and the competency queries — which read only the property route —
returned nothing for Q12 on every extraction output in the benchmark corpus.

### Removed

- **lifecycle 7.0.0 (breaking)** — temporal `obs:ConditionFactor` individuals
  `life:duration`, `life:storageDuration`, `life:agingTime`,
  `life:exposureDuration`, `life:entityAge`, `life:measurementDelayTime`.
  Observed-property individuals naming stated parameters:
  `life:storageDurationProperty`, `life:agingTimeProperty`,
  `life:entityAgeProperty`, `life:exposureDurationProperty`. Each of the latter
  carried an `rdfs:label` identical to the condition factor of the same name.
- **matsci 6.0.0 (breaking)** — condition factors `matsci:processDuration`,
  `matsci:synthesisDuration`, `matsci:assemblyDuration`. Observed-property
  individuals `processDurationProperty`, `synthesisDurationProperty`,
  `assemblyDurationProperty`, `reactionTimeProperty`,
  `solventEvaporationTimeProperty`, `dryingTimeProperty`,
  `centrifugationTimeProperty`, `measurementDelayTimeProperty`,
  `pumpProbeDelayTimeProperty`, `pulseDurationProperty`, with their temporal
  typing triples. Measured-quantity properties (`lifetimeProperty`,
  `decayTimeProperty`, `coherenceTimeProperty`, the superfluorescence and
  superradiance set, …) are unchanged.

### Changed

- **matsci 6.0.0** — `matsci:pulseDuration` retyped `obs:InstrumentSettingFactor`
  and re-parented `skos:broader obs:time`; `matsci:temporalResolution` given
  `skos:broader obs:time` (it had no broader factor).
- **observation 5.4.0** — `obs:time` narrowed to instrument settings in
  `rdfs:comment`, with a `skos:scopeNote` naming the property route.
  `obs:ConditionFactor` gains a `skos:scopeNote` and drops `"time"` from
  `skos:example`.
- **lifecycle 7.0.0** — `skos:scopeNote` on `life:hasDuration`,
  `life:hasEntityAge`, `life:hasObservationDelay` and
  `life:hasTemporalQuantityResult` stating which fact kind each takes.
  `life:hasStorageCondition` and `life:StorageAgingProcess` no longer list
  storage duration among conditions. `life:TimeConditionValue` scoped to
  instrument settings. `life:ObservableProcessTemporalProperty` declares no
  individuals and is documented as an extension point for measured process
  times.
- **Competency queries** — Q13 reads `life:hasDuration` on the step, keyed on
  method or label, replacing `matsci:solventEvaporationTimeProperty`.

### Added

- **observation-shapes 2.4.0** — `obs:NoTemporalProcessConditionConstraint`
  rejects a condition reached via `obs:hasProcessCondition` /
  `obs:hasObservationCondition` whose factor is `skos:broader*` `obs:time`.
  `obs:hasSetting` is exempt.
- **Competency queries 31 and 32** — `life:hasEntityAge` and
  `life:hasObservationDelay`, neither previously read by any query.
- **`fixtures/`, `scripts/check_competency.py`** — acceptance gate.
  `fixtures/exemplar.ttl` is a synthetic data graph covering the competency
  surface and all five temporal routes; `fixtures/negative-temporal-condition.ttl`
  states a duration as a process condition. The script asserts that all 32
  queries return rows, that the exemplar conforms, that the negative fixture is
  rejected by the named constraint, and that no condition factor shares an
  `rdfs:label` with an observable property.

## 2026-08-07

### Changed

- **qqval-shapes 2.2.0** — enforce the qqval numeric-form contract
  ("scalar → `qudt:numericValue` only", qqval scope note) that a benchmark
  run showed extraction violating: two new `sh:sparql` constraints on
  `QualifiedQuantityValueShape` reject (1) equal
  `numericLowerBound`/`numericUpperBound` (an exact scalar encoded as
  bounds) and (2) `epistemicQualifier qqval:Exact` without
  `qudt:numericValue` or with any bound property present (also catches an
  exact value asserted as a lone lower bound, which reads as "≥ x").
  Validated with pyshacl against conforming scalar/range fixtures and both
  observed failure patterns.

### Added

- **perovskitemat-shapes 1.0.0** — the module was the only authored one with
  OWL restrictions but no SHACL companion, so extracted perovskite data was
  checked open-world only. Shapes mirror the `PerovskiteSample`
  some/allValuesFrom pair on `matsci:describesMaterial`, close the
  site-component property ranges (`hasASiteComponent` /
  `hasBSiteComponent` / `hasXSiteComponent` / `hasPhase` /
  `hasSiteOccupancy`), require exactly one `occupancyComponent` and one
  `occupancyFraction` per reified `SiteOccupancy`, and bound occupancy
  fractions (nominal value and range bounds) to [0, 1]. Validated with
  pyshacl: the module's own individuals conform; missing components and
  out-of-range fractions are rejected.

## 2026-08-04

### Added

- **observation 5.3.0** — instrument-configuration pattern:
  `obs:InstrumentSettingFactor` (an `obs:ConditionFactor` specialization),
  `obs:InstrumentConfiguration`, `obs:hasInstrumentConfiguration`,
  `obs:configuredEquipment`, `obs:hasSetting`. Methods-section instrument
  settings (excitation wavelength, repetition rate, NA, resolutions,
  accelerating voltage) now have a landing zone instead of being dropped.
  Also the reported-value pattern: `obs:ReportedObservation` +
  `obs:reportedIn`, keeping literature-cited values distinct from this-work
  measurements (pairs with OntoCast's citation-metadata extraction of
  reference lists).
- **matsci 5.1.0** — material-portion pattern: `matsci:MaterialPortion`
  (subclass of `sosa:FeatureOfInterest`) with `matsci:isPortionOfMaterial`,
  `matsci:hasAmount`, `matsci:hasPurity`, `matsci:hasSupplierName`, and
  `matsci:hasInputPortion` (subproperty of `obs:hasInputEntity`) — recipe
  quantities ("2 mL oleic acid, 90%, Sigma-Aldrich") become structured.
  Seven instrument-setting factor individuals (`matsci:excitationWavelength`,
  `excitationFluence`, `repetitionRate`, `numericalAperture`,
  `spectralResolution`, `temporalResolution`, `acceleratingVoltage`).
- **matsci-qudt-units 1.1.0** — vendored `unit:KiloV` (symbol "kV",
  `scalingOf unit:V`, multiplier 1000): TEM accelerating voltages can now be
  transcribed verbatim instead of being force-converted to volts.
- **observation-shapes 2.3.0** — `obs:InstrumentConfigurationShape` (one
  equipment per configuration, settings must be reified `obs:Condition`s).
- **matsci-shapes 1.3.0** — `matsci:MaterialPortionShape` (one material kind
  per portion, quantity-typed amount/purity, string supplier).

## 2026-07-31

### Removed

- **matsci 5.0.0 (breaking)** — four `owl:imports` that `matsci` referenced no
  term from are gone: `pergres`, `matsci-units`, `matsci-qudt-units` and QUDT's
  `3.1.4/vocab/unit`. The collection now follows one rule — *a module imports
  exactly the modules whose terms it references* — so every arrow in the
  dependency graph means the same thing.

  None of the four did anything for `matsci`. `pergres` declares no terms, and
  the three it constrains (`obs:hasQuantityResult`,
  `obs:QuantitativeObservation`, `life:TimeQuantityValue`) occur nowhere in
  `matsci.ttl` — its observation classes moved to `observation` — while
  matsci's own `hasEdgeLength` / `hasThickness` keep a permissive
  `qudt:QuantityValue` range. Nothing constrains unit values' *type* either
  (`qqval`'s restriction on `qudt:unit` is `owl:minCardinality 1`, and its shape
  `sh:minCount 1` with no `sh:class`), so the unit imports bought availability
  that nothing verifies; `matsci-qudt-units` was redundant twice over, since
  `matsci-units` imports it and matsci imported QUDT's real unit vocabulary
  directly. matsci references zero `unit:` terms, so that one went too.

  Breaking for anyone resolving `owl:imports` over `matsci` alone: the
  qqval-qualification policy and the locally minted units are no longer pulled
  in, and must be loaded alongside. No effect on OntoCast, which never
  dereferences `owl:imports`, nor on the `pyshacl` recipe in the README, which
  concatenates every file in `ontologies/` and `shapes/`.

### Changed

- **pergres 1.3.0** — `skos:scopeNote` no longer names `matsci` as the module
  that imports it. States instead that nothing in the collection imports it by
  design: a module declaring no terms cannot be a vocabulary dependency, so
  loading it is a deployment choice made wherever reasoning or SHACL validation
  is configured. Axioms unchanged.

- **Change history removed from ontology and shapes annotations**, which carry
  current-state descriptions only — history belongs in this file.
  `observation-shapes` 2.1.0 → **2.2.0**, `lifecycle-shapes` 2.0.0 → **2.1.0**
  and `matsci-shapes` 1.1.0 → **1.2.0** drop the per-version rename logs from
  their `rdfs:comment`; `matsci` loses six Turtle section comments that narrated
  where classes used to live ("now lives in observation as …", "moved out of
  lifecycle 3.0.0", "that workaround is no longer needed"), restated as what the
  layering is. No axiom or term changed in any of them.

- **README dependency graph** — redrawn top-down (`graph TD`) so that arrows
  importer → importee now run downward and the base layer sits at the *bottom*,
  as the surrounding prose has always claimed; the previous `graph BT` rendered
  the collection upside-down, with `perovskitemat` at the bottom. `qqval`,
  `observation` and `matsci-qudt-units` are grouped in a `base layer` subgraph
  so they share one rank. With the imports above removed, `pergres` and
  `matsci-units` are now roots rather than dependants of `matsci`; the
  dependency-order list is restated by level to match.

### Added

- README section for the 30 competency queries in
  `queries/sparql_queries.rq`, which were previously undocumented.

- `perovskitemat` is now noted as having no shapes graph, and its transitive
  reliance on `qqval` / `sosa` through `matsci` is spelled out.

## 2026-07-30

### Added

- Initial SPARQL queries for retrieving synthesis and spectroscopy information with these queries.

- **matsci-units 3.0.0** (`ontologies/matsci-units.ttl`, was `units` 1.0.0) — a
  QUDT *gap-filler* module, not a unit vocabulary. QUDT is canonical: units it already defines are used under
  their own QUDT IRIs, with no local alias and no `owl:sameAs` bridge. The module
  holds only what QUDT lacks and shrinks as gaps are accepted upstream.

  Seven terms, each verified absent from QUDT 2.1 *and* 3.1.4. QUDT mints
  prefixed units as individuals rather than deriving them compositionally, so the
  milli/micro forms of its compound units are simply missing:
  `millielectronvolt` (meV — exciton binding and Urbach energies),
  `milliamperePerSquareCentimetre` (mA/cm² — Jsc),
  `milliwattPerSquareCentimetre` (mW/cm² — illumination intensity),
  `microjoulePerSquareCentimetre` and `millijoulePerSquareCentimetre` (excitation
  fluence), `sun` (AM1.5G multiples) and `arbitraryUnit` (a.u.; QUDT's
  `unit:UNITLESS` is not a substitute — it means dimensionless-but-absolute and
  its symbol is the CJK ideograph U+4E00). Each mirrors QUDT's own minting
  pattern, to be proposed upstream.

  No shapes graph: the module declares named individuals only, so there are no
  constraints to mirror.

- **matsci-qudt-units 1.0.0** (`ontologies/matsci-qudt-units.ttl`) — the matsci
  projection of QUDT 3.1.4: 72 units this corpus reports plus the 32 quantity kinds they
  belong to. Generated by `scripts/build_qudt_subset.py`.

  Vendoring is necessary because OntoCast does not dereference `owl:imports`, so
  a declared QUDT dependency delivers no terms and the extraction pipeline is
  asked to cite unit IRIs it has never seen. The full vocabulary (2839 units) is
  deliberately not vendored — it would swamp the retrieval budgets and drown the
  domain vocabulary.

  Terms keep their QUDT IRIs and definitions unchanged. The only additions are
  extra lexical surface forms, because QUDT's spellings do not match paper text:
  QUDT writes micro as U+03BC (GREEK SMALL LETTER MU) where papers use U+00B5
  (MICRO SIGN), and writes wavenumber as `/cm` where papers write `cm⁻¹`. These
  are extra `qudt:symbol` / `skos:notation` literals on the QUDT IRI itself,
  never a competing individual. QUDT's multilingual labels (up to 23 per term)
  and its encyclopedia/LaTeX descriptions are dropped.

- `scripts/build_qudt_subset.py` — regenerates `matsci-qudt-units.ttl` from a pinned
  QUDT release. Runs without a project environment:
  `uv run --with rdflib python scripts/build_qudt_subset.py`. Reports dropped
  quantity kinds, unreferenced allowlist entries, and any term kept without a
  label, so the curation stays auditable.

### Changed

- **Annotation predicates reworked for retrieval.** All 45 `dcterms:alternative`
  triples became `skos:altLabel`, and codes moved to `skos:notation` (60 new
  across matsci, perovskitemat and units). `dcterms:alternative` is not a label
  predicate anywhere in OntoCast, so every synonym the corpus declared — "QD",
  "IPA", "ACN", "OLA", "Cesium", "Methylammonium", "pump-probe" — reached neither
  retrieval lane nor the extraction prompt. `skos:notation` additionally feeds
  OntoCast's lexical-trigger lane, which matches raw source-text tokens directly.

- **Comment policy: `rdfs:comment` ≤ ~250 characters.** OntoCast folds comments
  into the dense embedding, where the default model truncates at 128 tokens, so
  long prose consumed the whole vector and displaced the structural clues. Term
  comments over the limit dropped from 21 to 0 and every ontology header was
  trimmed. Normative and usage prose moved to `skos:scopeNote` (never embedded);
  design rationale and module contracts moved to this README.

- **Label hygiene**: parenthetical acronyms left `rdfs:label` for the annotation
  that earns retrieval — `"photoluminescence (PL)"` → label `"photoluminescence"`
  + `skos:notation "PL"`. Affects `Photoluminescence`, `PLE`, `TA`, `TRPL`,
  `XRD`, `fwhmProperty`.

- **QUDT import pins moved from 2.1 to 3.1.4** across matsci, qqval, observation
  and lifecycle. Unit IRIs are version-independent
  (`http://qudt.org/vocab/unit/NanoM` carries no version), so the pin decides
  only which units exist and how symbols are spelled, never the identifiers.

- **matsci 4.2.0 → 4.3.0**, **perovskitemat 1.5.0 → 1.6.0**,
  **qqval 2.1.0 → 2.2.0**, **lifecycle 6.0.0 → 6.1.0**,
  **observation 5.1.0 → 5.2.0**, **pergres 1.1.0 → 1.2.0** for the annotation and
  comment rework above. matsci additionally imports both unit modules.

- **Both unit modules are project-scoped by name** (`units` → `matsci-units`,
  prefix `units:` → `matsciunits:`; the QUDT subset ships as
  `matsci-qudt-units`). Which units QUDT is missing, and which QUDT units are
  worth vendoring, are properties of what a corpus measures, not general facts —
  a sibling project adds its own pair rather than widening these. A generic
  `units:` alias would also collide in a shared catalog, since OntoCast
  registers the Turtle prefix as a catalog alias and rejects a second ontology
  claiming one already bound.

  **Breaking for IRI consumers**: every term moves from
  `.../ontologies/units#` to `.../ontologies/matsci-units#`, hence the major
  bump.

### Changed (naming — breaking for IRI consumers)

- Dropped the `-ontology` suffix from ontology file stems and IRIs
  (`qqval-ontology` → `qqval`, etc.; `perovskitemat` unchanged). Prefixes
  unchanged (`qqval:`, `obs:`, `matsci:`, …). Minor version bumps for
  path-only modules: qqval 2.0.0 → **2.1.0**, observation 5.0.0 → **5.1.0**,
  pergres 1.0.0 → **1.1.0**, matsci 4.0.0 → **4.1.0**, perovskitemat 1.4.0 →
  **1.5.0**; companion shapes bumped minor.
- Renamed module `temporal` → **`lifecycle`** (file/IRI/`rdfs:label`; prefix
  `tempo:` → **`life:`**). Selective local-name renames for lifecycle
  concepts only: `TemporalProcess` → `LifecycleProcess`,
  `EntityTemporalState` → `EntityLifecycleState`,
  `entityTemporalStateProperty` → `entityLifecycleStateProperty`,
  `QualitativeEntityTemporalObservation` →
  `QualitativeEntityLifecycleObservation` (+ shape),
  `hasEntityTemporalStateResult` → `hasEntityLifecycleStateResult`.
  Kept temporal-quantity vocabulary as `Temporal*` / `Time*`
  (`TemporalObservation`, `Observable*TemporalProperty`,
  `hasTemporalQuantityResult`, `hasTemporalReferenceProcess`, …).
  `lifecycle` 5.0.0 → **6.0.0**; `lifecycle-shapes` 1.1.0 → **2.0.0**.
  No redirects for old IRIs. Design notes: `planning/modularization.md` in the
  consuming OntoCast workspace (outside this repository).

## 2026-07

### Changed (modularization — breaking)

- Decoupled `qqval-ontology` and `observation-ontology`: observation no longer imports qqval; quantitative results are `qudt:QuantityValue`. Cross-module qqval-qualification policy moved to new `pergres-ontology` (imports qqval + observation + temporal; asserts `hasQuantityResult` range → `QualifiedQuantityValue` and `TimeQuantityValue ⊑ QualifiedQuantityValue`). `temporal-ontology` no longer imports qqval; keeps its substantive dependence on observation. Design notes: `planning/modularization.md` in the consuming OntoCast workspace (outside this repository).
- `qqval-ontology` 1.2.1 → **2.0.0**: renamed `ApproximateQuantityValue` → `QualifiedQuantityValue`; restructured `ApproximationQualifier` → `EpistemicQualifier` with only `Exact`/`Approximate` (dropped `Range`/`AtLeast`/`AtMost`/`WithUncertainty` — numeric form and uncertainty inferred from property presence); renamed `approximationQualifier` → `epistemicQualifier` (functional, cardinality 1); added `lowerBoundInclusive`/`upperBoundInclusive`; removed `owl:disjointWith` vs `QuantityRange` (SHACL `sh:not` retained).
- `observation-ontology` 4.0.1 → **5.0.0**: dropped qqval import and qqval restrictions; `hasQuantityResult` range → `qudt:QuantityValue`; `QualitativeResult ⊑ sosa:Result`; deleted `observationSource` (use `dcterms:source`); clarified Phenomenon/PhysicalPhenomenon/Process comments; kept `obs:time` in place.
- `temporal-ontology` 4.1.0 → **5.0.0**: dropped qqval import; `TimeQuantityValue ⊑ qudt:QuantityValue`; renamed `PostSynthesisProcess` → `PostCreationProcess`; renamed `hasObservationTimePoint` → `hasObservationDelay`.
- `matsci-ontology` 3.1.0 → **4.0.0**: imports `pergres-ontology`; updated qqval term references.
- `perovskitemat` 1.3.0 → **1.4.0**: `occupancyFraction` range → `QualifiedQuantityValue`.
- Shapes: `qqval-shapes` → 2.0.0 (property-presence rules); `observation-shapes` → 3.0.0 (qudt only); new `pergres-shapes` 1.0.0; `pergres-ontology` 1.0.0.
- Ontology headers now carry current-state descriptions only; history lives in this changelog.

### Changed (naming clarity -- observation classes should read as a matrix)
- Renamed `tempo:EntityTemporalObservation` -> `tempo:QualitativeEntityTemporalObservation` and `tempo:hasEntityTemporalResult` -> `tempo:hasEntityTemporalStateResult`. The class rename follows `observation-ontology`'s existing Qualitative-/Quantitative-prefix convention (`obs:QualitativeObservation`/`QuantitativeObservation`, `obs:QualitativeConditionValue`/`QuantitativeConditionValue`) instead of leaving "qualitative" only implicit in prose; the property rename follows the `hasXResult`-names-after-its-range convention (`hasTemporalQuantityResult`/`TimeQuantityValue`, `hasQualitativeResult`/`QualitativeResult`), since its range is `tempo:EntityTemporalState`. Entity-vs-process observed-property scope and quantitative-vs-qualitative result are independent axes -- the old name and its "qualitative counterpart to `tempo:TemporalObservation`" comment only surfaced the scope axis and implied a cleaner quantitative/qualitative pairing than actually exists (`tempo:ObservableEntityTemporalProperty` itself is shared by quantitative individuals like `entityAgeProperty`/`agingTimeProperty` and the qualitative `entityTemporalStateProperty`). Reworded the class comment and `tempo:ObservableEntityTemporalProperty`'s comment to state both axes explicitly. Also corrected `tempo:hasElapsedTime`'s comment, which claimed to link "an entity" even though no `rdfs:domain` is (or safely can be, given `hasObservationTimePoint`'s domain-propagating `subPropertyOf` link to it) asserted; and added a comment noting `tempo:StorageEffect`'s lack of `ExposureEffect`/`OperationalEffect` siblings is intentional, not a gap. `temporal-ontology` bumped 4.0.1 -> 4.1.0; `temporal-shapes.ttl` updated (`EntityTemporalObservationShape` -> `QualitativeEntityTemporalObservationShape`) and bumped 1.0.0 -> 1.1.0. Verified zero references to the renamed terms outside `matsci-perovskite-ontologies/`.

### Added (layering hygiene and extraction readiness)
- Added domain-agnostic **specificity rule** to ontocast extraction prompts (`facts_guidelines.py`, `criticise_facts.py`) and a smoke test (`ontocast/test/test_facts_guidelines.py`): when ancestor and descendant terms co-appear in ontology context, prefer the most specific applicable descendant.
- Added `matsci:derivedFromSample` to `matsci-ontology` for sample lineage/provenance across processing stages and time points. `matsci-ontology` bumped 3.0.0 -> 3.1.0.
- Added `perovmat:SiteOccupancy` (+ `hasSiteOccupancy`, `occupancyComponent`, `occupancyFraction`) to `perovskitemat` for qqval-qualified fractional site occupancy (mixed halides, doping levels). `perovskitemat` bumped 1.2.4 -> 1.3.0.

### Changed (layering hygiene -- documentation only)
- Removed downstream ontology name-drops from live guidance in upstream layers: `observation-ontology` extension-contract paragraph, `obs:hasInputEntity`/`hasOutputEntity` comments, and the `obs:time` section banner; `temporal-ontology` extension-contract paragraph, `tempo:EntityTemporalState` `skos:example`, and section banners. No vocabulary changes. `observation-ontology` bumped 4.0.0 -> 4.0.1; `temporal-ontology` bumped 4.0.0 -> 4.0.1.

### Investigated (Phase 3 -- audit only, no ontology changes)
- BFO/QUDT "lite" import audit: grepped every `obo:`/`qudt:`/`unit:`/`om:` term actually used across all five ontology files. Only 4 BFO classes (`BFO_0000015/0000016/0000019/0000023`) and 3 QUDT schema terms (`qudt:QuantityValue`/`unit`/`numericValue`) are used anywhere; the full QUDT unit vocabulary (`http://qudt.org/2.1/vocab/unit`, imported by `qqval-ontology` and `matsci-ontology`) has zero uses in any ontology axiom (`matsci-ontology` even declares an unused `@prefix unit:`), and `om:Measure` is used as a superclass without `om-2` ever being formally `owl:imports`-ed. Decision: document only for now -- no lite stub files created, no `owl:imports` changed.
- Asymmetric-uncertainty / combined-bound-plus-uncertainty extension: checked the three real extraction outputs in `aux/results/` for evidence of need. Every uncertainty found is a plain symmetric `±` value; the two `hasLowerBound`/`hasUpperBound` occurrences found both pointed at the same node (an extraction artifact, not a genuine asymmetric bound). No signal yet -- staying deferred per the original data-gated recommendation.

### Added (Phase 2 -- structural genericization)
- Added `temporal-shapes.ttl` and `matsci-shapes.ttl` SHACL shapes graphs, mirroring `temporal-ontology`'s `TemporalObservation`/`EntityTemporalObservation` restrictions and `matsci-ontology`'s one real OWL disjointness axiom plus a curated closed-world type-sanity net for `MorphologyState`'s value properties and the new `hasInputSample`/`hasOutputSample` convenience subproperties. Smoke-tested with `pyshacl` against hand-written pass/fail fixtures; found and documented that validating `tempo:TemporalObservation`/`EntityTemporalObservation` instances requires `pyshacl -i rdfs` (RDFS inference), since `tempo:hasTemporalQuantityResult`/`hasEntityTemporalResult` are `rdfs:subPropertyOf` `observation-shapes.ttl`'s checked properties and SHACL Core does not follow `rdfs:subPropertyOf` on its own -- updated the README's validation example accordingly.
- Added `tempo:precedes`/`tempo:follows` (native, mutually inverse, transitive object properties on `obs:Process`, with `rdfs:seeAlso` hooks to OWL-Time's `time:before`/`time:after`) so `tempo:TemporalProcess`'s "temporal order... is explicitly relevant" claim is backed by vocabulary.
- Added `tempo:EntityTemporalObservation` (+ `tempo:hasEntityTemporalResult`) as the qualitative counterpart to `tempo:TemporalObservation`, mirroring its restriction pattern.
- Added `matsci:hasInputSample`/`matsci:hasOutputSample` as `sosa:Sample`-narrowed convenience subproperties of `obs:hasInputEntity`/`obs:hasOutputEntity`.
- Added an "Extension contract" section to each of the four ontology headers (`qqval`, `observation`, `temporal`, `matsci`), documenting which classes/properties are extension points vs. closed/open controlled vocabularies. `qqval-ontology` bumped 1.2.0 -> 1.2.1 (documentation only).

### Changed (Phase 2 -- structural genericization, breaking)
- Generalized the `sosa:Sample`-coupled parts of the domain-neutral scaffolding to `sosa:FeatureOfInterest`, using "Entity" as the generic replacement word (re-scrutinized mid-implementation: the first draft used "Feature", but that reads as software/product/ML jargon to most readers -- a worse wrong-domain signal than "Sample" was; "Entity" echoes BFO's own top class and has a much milder wrong-domain risk):
  - `observation-ontology`: `obs:hasInputSample`/`hasOutputSample` -> `obs:hasInputEntity`/`hasOutputEntity` (range now `sosa:FeatureOfInterest`); `obs:hasObservation`/`producedByProcess` domain/range widened from `sosa:Sample` to `sosa:FeatureOfInterest`. Bumped 3.1.0 -> 4.0.0.
  - `temporal-ontology`: `tempo:SampleTemporalState` -> `EntityTemporalState`, `tempo:ObservableSampleTemporalProperty` -> `ObservableEntityTemporalProperty`, `tempo:hasSampleAge` -> `hasEntityAge` (domain widened to `sosa:FeatureOfInterest`), `tempo:sampleAge`/`sampleAgeProperty` -> `entityAge`/`entityAgeProperty`, `tempo:freshSampleState`/`agedSampleState`/`storedSampleState` -> `freshEntityState`/`agedEntityState`/`storedEntityState`, `tempo:sampleTemporalStateProperty` -> `entityTemporalStateProperty`. Swapped "sample" for "entity" throughout domain-neutral `rdfs:comment` prose (`PostSynthesisProcess`, `StorageProcess`, `ExposureProcess`, `AgingProcess`, `AgingEffect`, `StorageEffect`, `ObservableTemporalProperty`, `TimeConditionValue`, `hasTemporalReferenceProcess`). Bumped 3.1.0 -> 4.0.0.
  - `matsci-ontology`: renamed `matsci:airAgedSampleState`/`vacuumAgedSampleState` to `matsci:airAgedEntityState`/`vacuumAgedEntityState` to match; updated `hasInputMaterial`/`hasOutputMaterial` cross-references to point at the new `matsci:hasInputSample`/`hasOutputSample` convenience properties. Bumped 2.3.0 -> 3.0.0.
- Renamed `obs:EnvironmentCondition` -> `obs:Condition` and `obs:EnvironmentFactor` -> `obs:ConditionFactor` across `observation-ontology`, `temporal-ontology`, and `matsci-ontology` -- "environment" implied physical/atmospheric conditions specifically, which this reified factor+value pattern never actually required. Retyped every affected individual (`obs:time`, `tempo:duration`/`storageDuration`/`agingTime`/`exposureDuration`/`entityAge`/`measurementDelayTime`, `matsci:atmosphere`/`humidity`/`temperature`/`processDuration`/`synthesisDuration`/`assemblyDuration`/`pulseDuration`) accordingly.
- Retired `obs:broaderEnvironmentFactor` in favor of `skos:broader`, consistent with how `qqval:ApproximationQualifier` individuals already use `skos:broader`/`skos:narrower`. Updated every affected triple in `temporal-ontology` and `matsci-ontology`.
- Updated `observation-shapes.ttl`'s `obs:EnvironmentConditionShape` to `obs:ConditionShape`, retargeted at the renamed classes. Bumped 1.0.0 -> 2.0.0.
- Verified zero hardcoded references to any renamed term in `ontocast/` and `ontocast-validation/` before merging (see plan verification notes); `perovskitemat.ttl` needed no changes (imports `matsci-ontology` unversioned and does not reference any renamed identifier directly).

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