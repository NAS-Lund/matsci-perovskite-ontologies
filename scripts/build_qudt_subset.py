"""Generate ontologies/matsci-qudt-units.ttl: the matsci projection of QUDT.

Why this file exists
--------------------
OntoCast does not dereference ``owl:imports`` -- it treats every ``.ttl`` in the
ontology directory as an independent ontology. Declaring
``owl:imports <http://qudt.org/3.1.4/vocab/unit>`` therefore brings in *nothing*:
the extraction LLM is asked to point ``qudt:unit`` at a QUDT IRI while having seen
no QUDT IRIs at all, and invents plausible-but-wrong ones (``unit:NM`` for
nanometre, and so on). Vendoring a subset gives it real, retrievable identifiers.

The whole QUDT unit vocabulary is not vendored on purpose: 2839 units become
thousands of embedding atoms and would crowd out the domain vocabulary within
OntoCast's atom and induced-subgraph budgets. Only units this corpus actually
reports are kept, together with the quantity kinds they point at.

The selection is therefore a matsci-project decision, not a general one, which
is what the module name records: a sibling project measuring different
quantities produces its own projection rather than editing this one.

Usage
-----
No project environment is needed::

    uv run --with rdflib python scripts/build_qudt_subset.py

Pass ``--source`` to build from an already-downloaded copy instead of fetching.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import urllib.request

from rdflib import DCTERMS, OWL, RDF, RDFS, SKOS, Graph, Literal, Namespace, URIRef

QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")

# Pinned QUDT release. Unit IRIs are version-independent
# (http://qudt.org/vocab/unit/NanoM carries no version), so this pin decides only
# *which* units exist and *how* their symbols are spelled -- never the identifiers.
QUDT_VERSION = "3.1.4"
QUDT_UNITS_URL = f"https://qudt.org/{QUDT_VERSION}/vocab/unit"
QUDT_QUANTITYKIND_URL = f"https://qudt.org/{QUDT_VERSION}/vocab/quantitykind"

SUBSET_IRI = URIRef("https://growgraph.dev/ontologies/matsci-qudt-units")
SUBSET_VERSION = "1.0.0"

# Units this corpus reports. Local names are QUDT's own; a typo here surfaces as a
# "missing from QUDT" error at build time rather than as a silent omission.
CURATED_UNITS: dict[str, tuple[str, ...]] = {
    # --- length -------------------------------------------------------------
    "M": (),
    "CentiM": (),
    "MilliM": (),
    "MicroM": ("µm", "micron", "microns"),
    "NanoM": (),
    "PicoM": (),
    "ANGSTROM": ("Angstrom", "angstrom"),
    # --- time ---------------------------------------------------------------
    "SEC": (),
    "MilliSEC": (),
    "MicroSEC": ("µs", "us"),
    "NanoSEC": (),
    "PicoSEC": (),
    "FemtoSEC": (),
    "MIN": (),
    "HR": (),
    "DAY": (),
    # --- energy -------------------------------------------------------------
    "J": (),
    "MilliJ": (),
    "MicroJ": ("µJ", "uJ"),
    "EV": (),
    "KiloEV": (),
    "MegaEV": (),
    "KiloJ-PER-MOL": (),
    # --- temperature --------------------------------------------------------
    "K": (),
    "DEG_C": ("degC", "deg C", "Celsius"),
    # --- power and power density -------------------------------------------
    "W": (),
    "MilliW": (),
    "MicroW": ("µW", "uW"),
    "W-PER-CentiM2": ("W/cm2", "W·cm⁻²"),
    # --- areal energy density (fluence) ------------------------------------
    "J-PER-CentiM2": ("J/cm2",),
    # --- wavenumber ---------------------------------------------------------
    "PER-CentiM": ("cm⁻¹", "1/cm"),
    # --- frequency ----------------------------------------------------------
    "HZ": (),
    "KiloHZ": (),
    "MegaHZ": (),
    "GigaHZ": (),
    "TeraHZ": (),
    # --- electrical ---------------------------------------------------------
    "V": (),
    "MilliV": (),
    "A": (),
    "MilliA": (),
    "MicroA": ("µA", "uA"),
    "A-PER-CentiM2": ("A/cm2",),
    "OHM": ("Ohm", "ohm"),
    "OHM-CentiM": ("Ohm·cm",),
    "CentiM2-PER-V-SEC": ("cm2/(V·s)", "cm²V⁻¹s⁻¹"),
    # --- amount and concentration ------------------------------------------
    "MOL": (),
    "MOL-PER-L": ("molar",),
    "MilliMOL-PER-L": ("mM",),
    # --- mass ---------------------------------------------------------------
    "GM": (),
    "MilliGM": (),
    "MicroGM": ("µg", "ug"),
    "KiloGM": (),
    # --- volume -------------------------------------------------------------
    "L": (),
    "MilliL": (),
    "MicroL": ("µL", "uL"),
    # --- density ------------------------------------------------------------
    "GM-PER-CentiM3": ("g/cm3",),
    # --- pressure -----------------------------------------------------------
    "PA": (),
    "KiloPA": (),
    "MegaPA": (),
    "GigaPA": (),
    "BAR": (),
    "MilliBAR": (),
    "TORR": (),
    "ATM": (),
    # --- angle and solid angle ---------------------------------------------
    "DEG": ("deg",),
    "RAD": (),
    "SR": (),
    # --- magnetic and mechanical -------------------------------------------
    "T": (),
    "N": (),
    # --- dimensionless and counting ----------------------------------------
    "PERCENT": ("percent", "pct"),
    "NUM-PER-SEC": ("counts/s", "cps"),
    "REV-PER-MIN": ("rpm",),
}

# Quantity kinds kept for the curated units. QUDT maps generic units to a long
# many-to-many tail -- unit:SEC alone reaches BiodegredationHalfLife and
# BloodGlucoseLevel -- so the set is curated explicitly rather than taken whole.
# build() reports both dropped kinds and unreferenced entries, keeping the
# curation auditable instead of silent.
CURATED_QUANTITY_KINDS: frozenset[str] = frozenset(
    {
        "Length",
        "Time",
        "Energy",
        "Power",
        "PowerPerArea",
        "EnergyPerArea",
        "Temperature",
        "ThermodynamicTemperature",
        "Frequency",
        "Voltage",
        "ElectricCurrent",
        # QUDT's name for current density (mA/cm2, Jsc) is ElectricCurrentDensity.
        "ElectricCurrentDensity",
        "Resistance",
        "Resistivity",
        "Mobility",
        "AmountOfSubstance",
        # QUDT types molar concentration units (mol/L, mM) as plain Concentration.
        "Concentration",
        "Mass",
        "Volume",
        "Density",
        "MassDensity",
        # QUDT types pressure units (Pa, bar, Torr) as ForcePerArea.
        "ForcePerArea",
        "Angle",
        "PlaneAngle",
        "SolidAngle",
        "MagneticFluxDensity",
        "Force",
        "DimensionlessRatio",
        "CountRate",
        "RotationalFrequency",
        # QUDT's name for wavenumber (cm-1) is InverseLength.
        "InverseLength",
        "MolarEnergy",
    }
)

# Annotation predicates carried over from QUDT for each kept term. Conversion
# factors and dimension vectors come along so a downstream reasoner can still do
# unit algebra; the lexical forms are what the retrieval lanes consume.
#
# Deliberately excluded: dcterms:description, qudt:plainTextDescription and the
# qudt:LatexString glosses. OntoCast folds descriptions into the dense embedding,
# where QUDT's encyclopedia prose ("In geometric measurements, length most
# commonly refers to...") dilutes the vector without discriminating between
# terms, and the LaTeX forms embed markup like "$microm$". Label plus symbol
# carry the retrieval signal; this mirrors the comment policy applied to the
# hand-authored modules.
KEPT_PREDICATES: tuple[URIRef, ...] = (
    RDF.type,
    RDFS.label,
    RDFS.isDefinedBy,
    QUDT.symbol,
    QUDT.ucumCode,
    QUDT.expression,
    QUDT.conversionMultiplier,
    QUDT.conversionOffset,
    QUDT.hasQuantityKind,
    QUDT.unitForQuantityKind,
    QUDT.hasDimensionVector,
    QUDT.applicableSystem,
    QUDT.prefix,
    QUDT.scalingOf,
    SKOS.broader,
)

# QUDT publishes up to ~23 translations of a single rdfs:label. They are one
# triple each against OntoCast's induced-subgraph budget and never match English
# source text, so only English and untagged literals are vendored.
def _is_wanted_label(obj: object) -> bool:
    if not isinstance(obj, Literal):
        return True
    language = obj.language
    return not language or language.lower().startswith("en")

HEADER_COMMENT = """The matsci projection of QUDT: the units this corpus reports, vendored so \
they have real, retrievable identifiers."""

HEADER_SCOPE_NOTE = """OntoCast does not dereference owl:imports, so a declared dependency on QUDT
delivers no terms: without this file the extraction pipeline is asked to cite
QUDT unit IRIs it has never seen, and invents them. Only units this corpus
reports are vendored, together with the quantity kinds they belong to -- the
full vocabulary would swamp the atom and induced-subgraph budgets.

Canonical, not authored: every term keeps its QUDT IRI and QUDT definition.
Nothing is aliased, renamed or re-minted. The one addition is extra lexical
surface forms, because QUDT's spellings do not match paper text -- QUDT writes
micro as U+03BC (GREEK SMALL LETTER MU) where papers use U+00B5 (MICRO SIGN),
and writes wavenumber as "/cm" where papers write cm with a superscript minus
one. Those are extra qudt:symbol / skos:notation literals on the QUDT IRI
itself, never a competing individual.

Units genuinely absent from QUDT are minted locally in matsci-units.ttl.

Which units belong here is a property of what the matsci corpus reports, so the
module is project-scoped by name: another project vendors its own projection
instead of widening this one.

Generated by scripts/build_qudt_subset.py; edit that script, not this file."""


def _load(url: str, source: pathlib.Path | None) -> Graph:
    graph = Graph()
    if source is not None:
        graph.parse(source, format="turtle")
        return graph
    request = urllib.request.Request(url, headers={"Accept": "text/turtle"})
    with urllib.request.urlopen(request, timeout=300) as response:
        graph.parse(data=response.read(), format="turtle")
    return graph


def fetch_qudt(
    source: pathlib.Path | None, quantitykind_source: pathlib.Path | None
) -> Graph:
    """Load the pinned QUDT unit and quantity-kind vocabularies as one graph.

    The unit vocabulary references quantity kinds but does not define them, so
    both documents are needed for a kept quantity kind to carry a label rather
    than arrive as a bare identifier.
    """
    graph = _load(QUDT_UNITS_URL, source)
    graph += _load(QUDT_QUANTITYKIND_URL, quantitykind_source)
    return graph


def collect_quantity_kinds(
    qudt: Graph, units: list[URIRef]
) -> tuple[list[URIRef], list[str], list[str]]:
    """Curated quantity kinds for the units, plus dropped and unused names."""
    referenced: set[URIRef] = set()
    for unit in units:
        for predicate in (QUDT.hasQuantityKind, QUDT.unitForQuantityKind):
            for obj in qudt.objects(unit, predicate):
                if isinstance(obj, URIRef):
                    referenced.add(obj)

    kept: set[URIRef] = set()
    dropped: set[str] = set()
    for kind in referenced:
        name = str(kind).rsplit("/", 1)[-1]
        if name in CURATED_QUANTITY_KINDS:
            kept.add(kind)
        else:
            dropped.add(name)

    unused = sorted(
        CURATED_QUANTITY_KINDS - {str(k).rsplit("/", 1)[-1] for k in kept}
    )
    return sorted(kept, key=str), sorted(dropped), unused


def copy_term(qudt: Graph, out: Graph, term: URIRef) -> int:
    """Copy the kept predicates of one term, returning how many triples landed."""
    count = 0
    for predicate in KEPT_PREDICATES:
        for obj in sorted(qudt.objects(term, predicate), key=str):
            if predicate == RDFS.label and not _is_wanted_label(obj):
                continue
            out.add((term, predicate, obj))
            count += 1
    return count


def add_corpus_symbols(out: Graph, unit: URIRef, extra: tuple[str, ...]) -> None:
    """Attach corpus-idiomatic spellings as additional lexical forms."""
    for value in extra:
        out.add((unit, QUDT.symbol, Literal(value)))
        out.add((unit, SKOS.notation, Literal(value)))


def build(
    source: pathlib.Path | None,
    quantitykind_source: pathlib.Path | None,
    target: pathlib.Path,
) -> None:
    qudt = fetch_qudt(source, quantitykind_source)

    units = [UNIT[name] for name in CURATED_UNITS]
    missing = [str(u) for u in units if (u, RDF.type, None) not in qudt]
    if missing:
        raise SystemExit(
            "Not present in QUDT "
            f"{QUDT_VERSION} -- fix CURATED_UNITS or mint locally in units.ttl:\n  "
            + "\n  ".join(missing)
        )

    out = Graph()
    out.bind("qudt", QUDT)
    out.bind("unit", UNIT)
    out.bind("quantitykind", Namespace("http://qudt.org/vocab/quantitykind/"))
    out.bind("prefix", Namespace("http://qudt.org/vocab/prefix/"))
    out.bind("sou", Namespace("http://qudt.org/vocab/sou/"))
    out.bind("dimension", Namespace("http://qudt.org/vocab/dimensionvector/"))
    # No binding for the module's own namespace: it mints no terms, so the
    # namespace is never used and a serializer would drop the declaration
    # anyway. The module is addressed by its ontology id, matsci-qudt-units.
    out.bind("skos", SKOS)
    out.bind("dcterms", DCTERMS)
    out.bind("owl", OWL)
    out.bind("rdfs", RDFS)

    out.add((SUBSET_IRI, RDF.type, OWL.Ontology))
    out.add(
        (
            SUBSET_IRI,
            RDFS.label,
            Literal("matsci-qudt-units (QUDT projection for matsci)", lang="en"),
        )
    )
    out.add((SUBSET_IRI, RDFS.comment, Literal(HEADER_COMMENT, lang="en")))
    out.add((SUBSET_IRI, SKOS.scopeNote, Literal(HEADER_SCOPE_NOTE, lang="en")))
    out.add((SUBSET_IRI, DCTERMS.creator, Literal("growgraph.dev")))
    out.add((SUBSET_IRI, DCTERMS.source, URIRef(QUDT_UNITS_URL)))
    out.add(
        (
            SUBSET_IRI,
            OWL.versionIRI,
            URIRef(f"{SUBSET_IRI}/{SUBSET_VERSION}"),
        )
    )
    out.add((SUBSET_IRI, OWL.versionInfo, Literal(SUBSET_VERSION)))
    out.add(
        (
            SUBSET_IRI,
            DCTERMS.license,
            URIRef("https://creativecommons.org/licenses/by/4.0/"),
        )
    )

    for name, extra in CURATED_UNITS.items():
        unit = UNIT[name]
        copy_term(qudt, out, unit)
        add_corpus_symbols(out, unit, extra)

    kinds, dropped, unused = collect_quantity_kinds(qudt, units)
    unlabelled: list[str] = []
    for kind in kinds:
        copy_term(qudt, out, kind)
        out.add((kind, RDF.type, QUDT.QuantityKind))
        if not any(out.objects(kind, RDFS.label)):
            unlabelled.append(str(kind).rsplit("/", 1)[-1])

    target.parent.mkdir(parents=True, exist_ok=True)
    out.serialize(destination=target, format="turtle")
    print(
        f"QUDT {QUDT_VERSION}: {len(CURATED_UNITS)} units, {len(kinds)} quantity kinds, "
        f"{len(out)} triples -> {target}"
    )
    if dropped:
        print(f"  dropped {len(dropped)} uncurated quantity kinds: {', '.join(dropped)}")
    if unused:
        print(f"  CURATED_QUANTITY_KINDS entries never referenced: {', '.join(unused)}")
    if unlabelled:
        print(
            "  WARNING -- kept without any label (would embed as a bare identifier): "
            + ", ".join(unlabelled)
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=None,
        help="Local QUDT unit vocabulary Turtle file (default: fetch the pinned release).",
    )
    parser.add_argument(
        "--quantitykind-source",
        type=pathlib.Path,
        default=None,
        help="Local QUDT quantity-kind vocabulary Turtle file (default: fetch).",
    )
    parser.add_argument(
        "--target",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent.parent
        / "ontologies"
        / "matsci-qudt-units.ttl",
        help="Output path (default: ontologies/matsci-qudt-units.ttl).",
    )
    args = parser.parse_args(argv)
    build(args.source, args.quantitykind_source, args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
