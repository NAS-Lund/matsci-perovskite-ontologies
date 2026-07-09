# Domain Ontologies

OWL vocabularies for materials-science and perovskite research, factored into
reusable layers. Domain-independent scaffolding (observation, temporal,
qualified quantities) sits below the materials-science and perovskite-specific
layers.

## Ontology graph

`owl:imports` between the ontologies in this collection (arrows point from
importer → importee). External dependencies (SOSA, BFO, QUDT, SSN, unit
vocabularies) are omitted.

```mermaid
graph BT
    perov["perovskitemat<br/>1.2.4"]
    matsci["matsci-ontology<br/>2.3.0"]
    tempo["temporal-ontology<br/>3.1.0"]
    obs["observation-ontology<br/>3.1.0"]
    qqval["qqval-ontology<br/>1.2.0"]

    perov --> matsci
    matsci --> tempo
    matsci --> obs
    matsci --> qqval
    tempo --> obs
    tempo --> qqval
    obs --> qqval
```

**Dependency order** (load or reason over ontologies in this sequence):

1. `qqval-ontology`
2. `observation-ontology`
3. `temporal-ontology`
4. `matsci-ontology`
5. `perovskitemat`

`temporal-ontology` and `matsci-ontology` are siblings: temporal depends only on
observation (and qqval), not on matsci, so the graph stays acyclic.

## Ontologies

### Qualified Quantity Value (`qqval-ontology`)

| | |
|---|---|
| **File** | [`qqval-ontology.ttl`](qqval-ontology.ttl) |
| **Shapes** | [`qqval-shapes.ttl`](qqval-shapes.ttl) |
| **Prefix** | `qqval:` → `https://growgraph.dev/ontologies/qqval-ontology#` |
| **Version** | 1.2.0 |

Reusable vocabulary for quantitative values whose numeric component carries an
epistemic qualifier (exact, approximate, range, one-sided bound, uncertainty).
Imported by every other ontology in this collection that reports quantities.
`qqval:confidenceLevel` / `qqval:distributionAssumption` optionally record the
confidence level and distribution behind a reported uncertainty, so it is
never silently assumed to be a 1-sigma Gaussian. `qqval-shapes.ttl` provides
SHACL shapes that mirror the OWL cardinality/qualifier restrictions in a
closed-world-checkable form, for validating extracted data before it is
persisted.

### Observation (`observation-ontology`)

| | |
|---|---|
| **File** | [`observation-ontology.ttl`](observation-ontology.ttl) |
| **Shapes** | [`observation-shapes.ttl`](observation-shapes.ttl) |
| **Prefix** | `obs:` → `https://growgraph.dev/ontologies/observation-ontology#` |
| **Version** | 3.1.0 |

Domain-independent scaffolding for processes, observations, phenomena, and
environment conditions. Grounded in SOSA/BFO. Nucleated out of
`matsci-ontology`; formerly named `experiment-ontology` (`exp:`), before that
`core-ontology` (`core:`).

### Temporal (`temporal-ontology`)

| | |
|---|---|
| **File** | [`temporal-ontology.ttl`](temporal-ontology.ttl) |
| **Prefix** | `tempo:` → `https://growgraph.dev/ontologies/temporal-ontology#` |
| **Version** | 3.1.0 |

Domain-independent vocabulary for process duration, sample aging, storage,
exposure, and time-resolved characterization. Specializes
`observation-ontology`; does not import `matsci-ontology`.
Matsci/spectroscopy-specific temporal terms live in `matsci-ontology`.

### Material Science (`matsci-ontology`)

| | |
|---|---|
| **File** | [`matsci-ontology.ttl`](matsci-ontology.ttl) |
| **Prefix** | `matsci:` → `https://growgraph.dev/ontologies/matsci-ontology#` |
| **Version** | 2.3.0 |

General materials-science vocabulary (materials, samples, synthesis,
characterization, morphology, properties). Split from the original perovskite
ontology; layers on top of `observation-ontology` and imports
`temporal-ontology` for temporal typing of matsci-native terms.

### Perovskite (`perovskitemat`)

| | |
|---|---|
| **File** | [`perovskitemat.ttl`](perovskitemat.ttl) |
| **Prefix** | `perovmat:` → `https://growgraph.dev/ontologies/perovskitemat#` |
| **Version** | 1.2.4 |

Perovskite-specific classes and individuals (composition sites, halide
perovskites, named compounds). Imports `matsci-ontology` only.

## Validation

`qqval-shapes.ttl` and `observation-shapes.ttl` are SHACL shapes graphs that
mirror the OWL cardinality/qualifier restrictions declared in
`qqval-ontology.ttl` and `observation-ontology.ttl`, for closed-world
validation of extracted data (OWL restrictions are open-world and cannot, by
themselves, reject missing or malformed data). Validate a data graph with,
e.g., [`pyshacl`](https://github.com/RDFLib/pySHACL):

```bash
pyshacl -s qqval-shapes.ttl -s observation-shapes.ttl \
        -d qqval-ontology.ttl -d observation-ontology.ttl -d <data.ttl> \
        -a
```

(the `-d qqval-ontology.ttl -d observation-ontology.ttl` inputs give the
validator the named-individual typing -- e.g. `qqval:Exact a
qqval:ApproximationQualifier` -- that `sh:class` constraints rely on.)

## Contributing

Bump `owl:versionInfo` (and `owl:versionIRI` when present) in the ontology
header when you change a vocabulary. Update this README and
[`CHANGELOG.md`](CHANGELOG.md) for notable releases.
