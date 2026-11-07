"""Acceptance test for the ontology collection.

Six assertions:

1. **Competency.** Every query in ``queries/sparql_queries.rq`` returns at
   least one row against ``fixtures/exemplar.ttl``.

2. **Label uniqueness.** No two terms share an ``rdfs:label``, and no two
   members of one value list share a name or synonym.

3. **Lexical hazards.** No single-character ``rdfs:label`` or
   ``skos:notation``.

4. **Layering.** A module, its shapes and its annotations refer only to
   itself and to the modules it imports.

5. **Exemplar conformance.** ``fixtures/exemplar.ttl`` conforms to every
   shapes graph under RDFS inference.

6. **Negative case.** ``fixtures/negative-temporal-condition.ttl``, which
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

from rdflib import RDF, RDFS, Graph, Literal, URIRef
from rdflib.namespace import OWL, SKOS

REPO = Path(__file__).resolve().parent.parent
ONTOLOGY_DIR = REPO / "ontologies"
SHAPES_DIR = REPO / "shapes"
FIXTURE_DIR = REPO / "fixtures"
QUERY_FILE = REPO / "queries" / "sparql_queries.rq"

PROJECT_BASE = "https://growgraph.dev/ontologies/"

# Module names that are not also ordinary English words, so a mention in prose
# is a reference to the module ("lifecycle" and "observation" are not here).
DISTINCTIVE_MODULE_NAMES = ("qqval", "pergres", "matsci", "perovskitemat")

# A vocabulary describes itself, not the software that consumes it.
TOOL_NAMES = ("OntoCast",)

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


def _local_terms(graph: Graph) -> set[URIRef]:
    """Terms minted by this collection: fragment IRIs under the project base."""
    return {
        term
        for term in graph.subjects(RDF.type, None)
        if isinstance(term, URIRef)
        and str(term).startswith(PROJECT_BASE)
        and "#" in str(term)
    }


def _short(term: URIRef) -> str:
    module, _, name = str(term)[len(PROJECT_BASE) :].partition("#")
    return f"{module}#{name}"


def check_label_uniqueness(ontologies: Graph) -> list[str]:
    """No two terms share an ``rdfs:label``; no two members of one value list
    share a synonym.

    A shared label leaves the IRI suffix as the only distinguishing feature,
    which neither the dense nor the lexical retrieval lane reads.
    """
    terms = _local_terms(ontologies)
    by_label: dict[str, set[URIRef]] = {}
    for term in terms:
        for label in ontologies.objects(term, RDFS.label):
            by_label.setdefault(" ".join(str(label).lower().split()), set()).add(term)

    failures = [
        f"label {label!r} is shared by {sorted(_short(t) for t in owners)}"
        for label, owners in sorted(by_label.items())
        if len(owners) > 1
    ]

    # Members of one value list (individuals of the same class) must not share
    # a synonym, nor use another member's label as one.
    members: dict[URIRef, set[URIRef]] = {}
    for term in terms:
        for cls in ontologies.objects(term, RDF.type):
            if isinstance(cls, URIRef) and cls != OWL.NamedIndividual:
                members.setdefault(cls, set()).add(term)
    for cls, group in sorted(members.items()):
        names: dict[str, set[URIRef]] = {}
        for term in group:
            for predicate in (RDFS.label, SKOS.altLabel):
                for name in ontologies.objects(term, predicate):
                    names.setdefault(" ".join(str(name).lower().split()), set()).add(
                        term
                    )
        for name, owners in sorted(names.items()):
            if len(owners) > 1:
                failures.append(
                    f"members of {cls.n3(ontologies.namespace_manager)} share the "
                    f"name {name!r}: {sorted(_short(t) for t in owners)}"
                )
    return sorted(set(failures))


def check_lexical_hazards(ontologies: Graph) -> list[str]:
    """No single-character ``rdfs:label`` or ``skos:notation``.

    Lexical matching is case-sensitive against raw text, so a one-character
    token ("I", "1") fires on pronouns, roman numerals and every digit.
    """
    failures = []
    for term in sorted(_local_terms(ontologies)):
        for predicate in (RDFS.label, SKOS.notation):
            for value in ontologies.objects(term, predicate):
                if len(str(value).strip()) == 1:
                    failures.append(
                        f"{_short(term)} has single-character "
                        f"{predicate.n3(ontologies.namespace_manager)} {str(value)!r}"
                    )
    return failures


class Module:
    """One ontology file, or a shapes file attached to its ontology."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.graph = Graph()
        self.graph.parse(path, format="turtle")
        headers = [
            str(s)
            for s in self.graph.subjects(RDF.type, OWL.Ontology)
            if str(s).startswith(PROJECT_BASE)
        ]
        if len(headers) != 1:
            raise ValueError(f"{path.name}: expected one owl:Ontology header")
        self.name = headers[0][len(PROJECT_BASE) :]
        self.imports = {
            _module_of(str(o))
            for o in self.graph.objects(URIRef(headers[0]), OWL.imports)
            if _module_of(str(o))
        }


def _module_of(iri: str) -> str | None:
    """The collection module an IRI belongs to, or None for an external IRI."""
    if not iri.startswith(PROJECT_BASE):
        return None
    return re.split(r"[#/]", iri[len(PROJECT_BASE) :])[0] or None


def check_layering() -> list[str]:
    """A module knows only itself and what it imports.

    * every collection IRI an ontology uses belongs to itself or a module it
      imports directly (no reliance on transitive imports);
    * every collection IRI a shapes file uses belongs to its ontology or that
      ontology's import closure;
    * no annotation names a collection prefix (``life:``) or a distinctive
      module name (``pergres``) outside that closure, nor a consuming tool.
    """
    ontologies = {m.name: m for m in map(Module, sorted(ONTOLOGY_DIR.glob("*.ttl")))}

    def closure(name: str) -> set[str]:
        seen: set[str] = set()
        stack = [name]
        while stack:
            for imported in ontologies[stack.pop()].imports:
                if imported in ontologies and imported not in seen:
                    seen.add(imported)
                    stack.append(imported)
        return seen

    prefix_owner: dict[str, str] = {}
    for module in ontologies.values():
        for prefix, namespace in module.graph.namespace_manager.namespaces():
            owner = _module_of(str(namespace))
            if prefix and owner in ontologies:
                prefix_owner[prefix] = owner

    failures = []
    checked = [(m, m.name, {m.name} | m.imports) for m in ontologies.values()]
    for path in sorted(SHAPES_DIR.glob("*.ttl")):
        shapes = Module(path)
        target = shapes.name.removesuffix("-shapes")
        if target not in ontologies:
            failures.append(f"{path.name}: no ontology named {target!r}")
            continue
        checked.append((shapes, target, {target} | closure(target)))

    for module, owner, allowed in checked:
        label = module.path.name
        known = allowed | closure(owner)
        used: set[str] = set()
        for triple in module.graph:
            for node in triple:
                if isinstance(node, URIRef) and (found := _module_of(str(node))):
                    used.add(found)
        for found in sorted(used - allowed - {module.name}):
            failures.append(
                f"{label}: uses {found} terms but does not import {found}"
                if found in known
                else f"{label}: uses {found} terms outside its import closure"
            )
        for subject, predicate, value in module.graph:
            if not isinstance(value, Literal):
                continue
            text = str(value)
            names = {
                owner_of
                for prefix, owner_of in prefix_owner.items()
                if re.search(rf"(?<![\w-]){re.escape(prefix)}:\w", text)
            }
            names |= {
                name
                for name in DISTINCTIVE_MODULE_NAMES
                if re.search(rf"(?<![\w-]){name}(?![\w-])", text)
            }
            for name in sorted(names - known - {module.name}):
                failures.append(
                    f"{label}: {_describe(subject, module.graph)} names {name}, "
                    f"which is outside its import closure"
                )
            for tool in TOOL_NAMES:
                if tool in text:
                    failures.append(
                        f"{label}: {_describe(subject, module.graph)} names the "
                        f"tool {tool}"
                    )
    return failures


def _describe(subject: object, graph: Graph) -> str:
    if isinstance(subject, URIRef):
        return subject.n3(graph.namespace_manager)
    return "an anonymous node"


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
        ("label uniqueness", check_label_uniqueness(ontologies)),
        ("lexical hazards", check_lexical_hazards(ontologies)),
        ("layering", check_layering()),
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
