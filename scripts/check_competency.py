"""Acceptance test for the ontology collection.

Four assertions:

1. **Competency.** Every query in ``queries/sparql_queries.rq`` returns at
   least one row against ``fixtures/exemplar.ttl``.

2. **Label disjointness.** No ``obs:ConditionFactor`` shares an ``rdfs:label``
   with an observable-property individual. A shared label leaves the IRI
   suffix as the only distinguishing feature, which neither the dense nor the
   lexical retrieval lane reads.

3. **Exemplar conformance.** ``fixtures/exemplar.ttl`` conforms to every
   shapes graph under RDFS inference.

4. **Negative case.** ``fixtures/negative-temporal-condition.ttl``, which
   states a duration as a process condition, is rejected by
   ``obs:NoTemporalProcessConditionConstraint``.

Run::

    uv run --with rdflib --with pyshacl python scripts/check_competency.py

Exits non-zero on any failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from rdflib import Graph, RDFS, URIRef
from rdflib.namespace import SKOS

REPO = Path(__file__).resolve().parent.parent
ONTOLOGY_DIR = REPO / "ontologies"
SHAPES_DIR = REPO / "shapes"
FIXTURE_DIR = REPO / "fixtures"
QUERY_FILE = REPO / "queries" / "sparql_queries.rq"

OBS = "https://growgraph.dev/ontologies/observation#"
CONDITION_FACTOR = URIRef(OBS + "ConditionFactor")
LIFE_OBSERVABLE_TEMPORAL = URIRef(
    "https://growgraph.dev/ontologies/lifecycle#ObservableTemporalProperty"
)
SOSA_OBSERVABLE_PROPERTY = URIRef("http://www.w3.org/ns/sosa/ObservableProperty")

# A query block starts at a "# <n>. <question>" header and runs to the next one.
QUERY_HEADER = re.compile(r"^#\s*(\d+)\.\s*(.*)$")


def load_ontologies() -> Graph:
    """Merge every ontology module into one graph."""
    graph = Graph()
    for path in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


def load_shapes() -> Graph:
    """Merge every shapes graph into one graph."""
    graph = Graph()
    for path in sorted(SHAPES_DIR.glob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


def parse_queries(text: str) -> list[tuple[str, str, str]]:
    """Split the competency-query file into (number, question, query) triples.

    Comment lines between the header and the first PREFIX are rationale, not
    query text, so they are kept in the block and ignored by the SPARQL parser.
    """
    blocks: list[tuple[str, str, str]] = []
    number = question = None
    buffer: list[str] = []

    def flush() -> None:
        if number is None:
            return
        body = "\n".join(buffer)
        if "SELECT" in body:
            blocks.append((number, question or "", body))

    for line in text.splitlines():
        header = QUERY_HEADER.match(line)
        if header:
            flush()
            number, question = header.group(1), header.group(2)
            buffer = []
        else:
            buffer.append(line)
    flush()
    return blocks


def check_competency(data: Graph) -> list[str]:
    """Every competency query must return at least one row."""
    failures = []
    blocks = parse_queries(QUERY_FILE.read_text())
    print(f"  {len(blocks)} competency queries")
    for number, question, query in blocks:
        try:
            rows = list(data.query(query))
        except Exception as exc:  # noqa: BLE001 - report, do not abort the sweep
            failures.append(f"Q{number} failed to execute: {exc}")
            continue
        if not rows:
            failures.append(f"Q{number} returned no rows -- {question}")
    return failures


def check_label_disjointness(ontologies: Graph) -> list[str]:
    """A condition factor must not share a label with an observable property."""
    factor_labels: dict[str, list[str]] = {}
    property_labels: dict[str, list[str]] = {}

    for subject in ontologies.subjects(None, CONDITION_FACTOR):
        for label in ontologies.objects(subject, RDFS.label):
            factor_labels.setdefault(str(label), []).append(str(subject))

    observable_types = {SOSA_OBSERVABLE_PROPERTY, LIFE_OBSERVABLE_TEMPORAL}
    observable_types |= set(
        ontologies.subjects(RDFS.subClassOf, LIFE_OBSERVABLE_TEMPORAL)
    )
    for observable_type in observable_types:
        for subject in ontologies.subjects(None, observable_type):
            for label in ontologies.objects(subject, RDFS.label):
                property_labels.setdefault(str(label), []).append(str(subject))

    failures = []
    for label, factors in sorted(factor_labels.items()):
        if label in property_labels:
            failures.append(
                f"label {label!r} is shared by condition factor(s) "
                f"{factors} and observable property/properties "
                f"{property_labels[label]} -- retrieval cannot separate the "
                f"two routes"
            )
    return failures


def check_negative_fixture(shapes: Graph, ontologies: Graph) -> list[str]:
    """The temporal-condition fixture must be rejected."""
    from pyshacl import validate

    data = Graph()
    data.parse(FIXTURE_DIR / "negative-temporal-condition.ttl", format="turtle")
    data += ontologies

    conforms, _, text = validate(
        data_graph=data, shacl_graph=shapes, inference="rdfs", advanced=True
    )
    if conforms:
        return [
            "negative-temporal-condition.ttl conforms, but a duration "
            "expressed as a process condition must be rejected"
        ]
    if "Temporal facts are not conditions" not in text:
        return [
            "negative-temporal-condition.ttl was rejected, but not by "
            "NoTemporalProcessConditionConstraint -- the rule may not be firing"
        ]
    return []


def check_exemplar_conforms(shapes: Graph, ontologies: Graph) -> list[str]:
    """The exemplar must pass every shape."""
    from pyshacl import validate

    data = Graph()
    data.parse(FIXTURE_DIR / "exemplar.ttl", format="turtle")
    data += ontologies

    conforms, _, text = validate(
        data_graph=data, shacl_graph=shapes, inference="rdfs", advanced=True
    )
    if not conforms:
        return ["exemplar.ttl does not conform:\n" + text]
    return []


def main() -> int:
    ontologies = load_ontologies()
    shapes = load_shapes()

    exemplar = Graph()
    exemplar.parse(FIXTURE_DIR / "exemplar.ttl", format="turtle")
    data = exemplar + ontologies

    checks: list[tuple[str, list[str]]] = [
        ("competency queries", check_competency(data)),
        ("label disjointness", check_label_disjointness(ontologies)),
        ("exemplar conformance", check_exemplar_conforms(shapes, ontologies)),
        ("negative fixture rejected", check_negative_fixture(shapes, ontologies)),
    ]

    failed = False
    for name, failures in checks:
        if failures:
            failed = True
            print(f"\nFAIL  {name}")
            for failure in failures:
                print(f"      {failure}")
        else:
            print(f"ok    {name}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
