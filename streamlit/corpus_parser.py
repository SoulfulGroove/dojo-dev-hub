import re
from collections import defaultdict

SCROLL_NAMES = {
    "01": "Earth",
    "02": "Water",
    "03": "Fire",
    "04": "Wind",
    "05": "Void",
}

SCROLL_HEADINGS = {
    "0100": "地の巻 (Scroll of Earth)",
    "0200": "水の巻",
    "0300": "火の巻",
    "0400": "風の巻",
    "0500": "空の巻",
}

MARKER_RE = re.compile(r"^(?P<prefix>.*?)[ ]*\[(?P<id>\d{4})\][ ]*$")


def _clean_heading(raw, source_id):
    heading = raw.strip().lstrip("`").strip()
    if source_id == "0000":
        marker = "序 (Preface)"
        return marker if marker in heading else heading
    if source_id.endswith("00"):
        return SCROLL_HEADINGS.get(source_id, heading)
    return heading


def parse_corpus(text):
    """Parse the compiled Koten-original TXT into deterministic scroll/section/passage records.

    Canonical section IDs are assigned by actual section order inside each scroll.
    The original marker is retained as source_id, so obvious numbering typos can be
    corrected for navigation without erasing provenance.
    """
    lines = text.splitlines()
    markers = []

    for index, line in enumerate(lines):
        match = MARKER_RE.match(line.strip())
        if match:
            markers.append({
                "line_index": index,
                "source_line": index + 1,
                "source_id": match.group("id"),
                "raw_heading": match.group("prefix"),
            })

    section_counts = defaultdict(int)
    records = []

    for i, marker in enumerate(markers):
        source_id = marker["source_id"]
        start = marker["line_index"] + 1
        stop = markers[i + 1]["line_index"] if i + 1 < len(markers) else len(lines)
        body = "\n".join(lines[start:stop]).strip()

        if source_id == "0000":
            canonical_id = "0000"
            kind = "preface"
            scroll = "Preface"
        elif source_id.endswith("00"):
            canonical_id = source_id
            kind = "scroll"
            scroll = SCROLL_NAMES.get(source_id[:2], source_id[:2])
        else:
            prefix = source_id[:2]
            section_counts[prefix] += 1
            canonical_id = f"{prefix}{section_counts[prefix]:02d}"
            kind = "section"
            scroll = SCROLL_NAMES.get(prefix, prefix)

        chunks = []
        if body:
            raw_chunks = body.split("`") if "`" in body else re.split(r"\n\s*\n", body)
            for chunk in raw_chunks:
                cleaned = re.sub(r"\s*\n\s*", " ", chunk).strip()
                if cleaned:
                    chunks.append(cleaned)

        passages = [
            {
                "passage_id": f"{canonical_id}-{n:03d}",
                "text": passage,
            }
            for n, passage in enumerate(chunks, start=1)
        ]

        records.append({
            "canonical_id": canonical_id,
            "source_id": source_id,
            "id_corrected": canonical_id != source_id,
            "kind": kind,
            "scroll": scroll,
            "heading": _clean_heading(marker["raw_heading"], source_id),
            "source_line": marker["source_line"],
            "passages": passages,
        })

    return {
        "source_layer": "Koten original",
        "record_count": len(records),
        "section_counts": dict(section_counts),
        "records": records,
    }


def flatten_passages(corpus):
    rows = []
    for record in corpus["records"]:
        if record["kind"] not in {"preface", "section"}:
            continue
        for passage in record["passages"]:
            rows.append({
                "scroll": record["scroll"],
                "section_id": record["canonical_id"],
                "source_id": record["source_id"],
                "heading": record["heading"],
                "passage_id": passage["passage_id"],
                "text": passage["text"],
            })
    return rows
