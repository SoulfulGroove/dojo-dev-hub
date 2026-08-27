import re
from collections import Counter, defaultdict

import streamlit as st
from janome.tokenizer import Tokenizer

from corpus_parser import parse_corpus, flatten_passages

st.set_page_config(page_title="Musashi Concept Atlas", page_icon="⚔️", layout="wide")

SCROLLS = ["Preface", "Earth", "Water", "Fire", "Wind", "Void"]
STOP_SURFACES = {
    "の", "に", "を", "は", "が", "と", "て", "で", "も", "へ", "や", "か", "なり", "也",
    "事", "所", "云", "云ふ", "云て", "する", "す", "なる", "有", "有り", "ある", "此", "其",
    "又", "而", "共", "より", "まで", "もの", "こと", "これ", "それ", "我", "人", "時"
}

st.title("⚔️ Musashi Concept Atlas")
st.caption("Koten Original · searchable corpus, concept distribution, context, and term browsing")

uploaded = st.sidebar.file_uploader("Load compiled Koten TXT", type=["txt"])
st.sidebar.caption("The source TXT remains authoritative; the app builds a cached research index from it.")

if uploaded is None:
    st.info("Upload the compiled Koten-original TXT file to load the Concept Atlas.")
    st.stop()

@st.cache_data(show_spinner=False)
def load_corpus(raw: bytes):
    text = raw.decode("utf-8")
    corpus = parse_corpus(text)
    rows = flatten_passages(corpus)
    return corpus, rows

@st.cache_resource(show_spinner=False)
def get_tokenizer():
    return Tokenizer()

@st.cache_data(show_spinner=False)
def build_term_index(texts):
    tokenizer = get_tokenizer()
    counts = Counter()
    passage_terms = []
    for text in texts:
        terms = []
        for token in tokenizer.tokenize(text):
            surface = token.surface.strip()
            pos = token.part_of_speech.split(",")[0]
            if not surface or re.fullmatch(r"[\s\W_]+", surface):
                continue
            if surface in STOP_SURFACES:
                continue
            if pos in {"記号", "助詞", "助動詞"}:
                continue
            if len(surface) == 1 and re.fullmatch(r"[ぁ-ゖァ-ヺ]", surface):
                continue
            terms.append(surface)
            counts[surface] += 1
        passage_terms.append(terms)
    return counts, passage_terms

corpus, rows = load_corpus(uploaded.getvalue())
term_counts, passage_terms = build_term_index(tuple(r["text"] for r in rows))
for row, terms in zip(rows, passage_terms):
    row["terms"] = terms

if "atlas_term" not in st.session_state:
    st.session_state.atlas_term = "道"

scroll_scope = st.sidebar.selectbox("Scroll scope", ["All"] + SCROLLS)
context_chars = st.sidebar.slider("Context window (characters)", 10, 80, 28, 2)
nearby_chars = st.sidebar.slider("Nearby-term window (characters)", 10, 60, 24, 2)

scope_rows = rows if scroll_scope == "All" else [r for r in rows if r["scroll"] == scroll_scope]

search_term = st.sidebar.text_input("Concept / exact string", value=st.session_state.atlas_term)
if search_term != st.session_state.atlas_term:
    st.session_state.atlas_term = search_term
term = st.session_state.atlas_term.strip()

matches = [r for r in scope_rows if term and term in r["text"]]
occurrences = sum(r["text"].count(term) for r in scope_rows) if term else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Unique browse terms", len(term_counts))
m2.metric("Corpus passages", len(rows))
m3.metric("Matching passages", len(matches))
m4.metric("Occurrences", occurrences)

atlas_tab, terms_tab, browse_tab, source_tab = st.tabs([
    "Concept Atlas", "Browse Terms", "Browse Corpus", "Source Structure"
])

with atlas_tab:
    if not term:
        st.info("Choose or type a Japanese term to explore.")
    else:
        st.subheader(f"Concept: {term}")

        # 1. Frequency by scroll
        st.markdown("#### 1 · Frequency by scroll")
        scroll_counts = {
            s: sum(r["text"].count(term) for r in rows if r["scroll"] == s)
            for s in SCROLLS
        }
        st.bar_chart(scroll_counts)

        # 2. Ranked sections by concentration
        st.markdown("#### 2 · Highest-concentration sections")
        section_stats = defaultdict(lambda: {"count": 0, "chars": 0, "heading": "", "scroll": ""})
        for r in scope_rows:
            key = r["section_id"]
            section_stats[key]["count"] += r["text"].count(term)
            section_stats[key]["chars"] += len(r["text"])
            section_stats[key]["heading"] = r["heading"]
            section_stats[key]["scroll"] = r["scroll"]
        ranked = []
        for sid, data in section_stats.items():
            if data["count"]:
                density = data["count"] / max(data["chars"], 1) * 1000
                ranked.append({
                    "section": sid,
                    "scroll": data["scroll"],
                    "heading": data["heading"],
                    "occurrences": data["count"],
                    "per_1000_chars": round(density, 2),
                })
        ranked.sort(key=lambda x: (x["per_1000_chars"], x["occurrences"]), reverse=True)
        st.dataframe(ranked[:20], use_container_width=True, hide_index=True)

        # 3. All occurrences with context
        st.markdown("#### 3 · Occurrences in context")
        if not matches:
            st.info("No occurrences in the selected scope.")
        else:
            for r in matches:
                text = r["text"]
                positions = [m.start() for m in re.finditer(re.escape(term), text)]
                with st.container(border=True):
                    st.caption(f"{r['scroll']} · [{r['section_id']}] {r['heading']} · {r['passage_id']}")
                    for pos in positions:
                        left = max(0, pos - context_chars)
                        right = min(len(text), pos + len(term) + context_chars)
                        before = text[left:pos]
                        after = text[pos + len(term):right]
                        st.markdown(f"…{before}**{term}**{after}…")

        # 4. Nearby term analysis
        st.markdown("#### 4 · Nearby terms")
        nearby = Counter()
        tokenizer = get_tokenizer()
        for r in matches:
            text = r["text"]
            for m in re.finditer(re.escape(term), text):
                left = max(0, m.start() - nearby_chars)
                right = min(len(text), m.end() + nearby_chars)
                window = text[left:right]
                for tok in tokenizer.tokenize(window):
                    surface = tok.surface.strip()
                    pos = tok.part_of_speech.split(",")[0]
                    if not surface or surface == term or surface in STOP_SURFACES:
                        continue
                    if pos in {"記号", "助詞", "助動詞"}:
                        continue
                    if re.fullmatch(r"[\s\W_]+", surface):
                        continue
                    nearby[surface] += 1
        near_rows = [{"term": t, "nearby_hits": c} for t, c in nearby.most_common(30)]
        st.dataframe(near_rows, use_container_width=True, hide_index=True)
        st.caption("Nearby terms are automatic tokenizer output and should be treated as exploratory evidence, not definitive classical-Japanese lexical segmentation.")

with terms_tab:
    st.subheader("Browse corpus terms")
    st.caption("Terms are automatically segmented with Janome. Use them as navigation aids; exact-string search remains the authoritative lookup method.")

    tc1, tc2, tc3 = st.columns([1.2, 1, 1])
    with tc1:
        contains = st.text_input("Filter term list", "", key="term_filter")
    with tc2:
        min_count = st.number_input("Minimum frequency", 1, 999, 2)
    with tc3:
        sort_mode = st.selectbox("Sort", ["Frequency ↓", "Frequency ↑", "Japanese A–Z"])

    candidates = [(t, c) for t, c in term_counts.items() if c >= min_count and (contains in t if contains else True)]
    if sort_mode == "Frequency ↓":
        candidates.sort(key=lambda x: (-x[1], x[0]))
    elif sort_mode == "Frequency ↑":
        candidates.sort(key=lambda x: (x[1], x[0]))
    else:
        candidates.sort(key=lambda x: x[0])

    st.write(f"**{len(candidates):,} terms shown** of {len(term_counts):,} unique automatically segmented terms")

    page_size = st.select_slider("Terms per page", options=[25, 50, 100, 200], value=50)
    pages = max(1, (len(candidates) + page_size - 1) // page_size)
    page = st.number_input("Page", 1, pages, 1)
    shown = candidates[(page - 1) * page_size: page * page_size]

    cols = st.columns(4)
    for i, (browse_term, count) in enumerate(shown):
        with cols[i % 4]:
            if st.button(f"{browse_term} · {count}", key=f"term_{page}_{i}_{browse_term}", use_container_width=True):
                st.session_state.atlas_term = browse_term
                st.rerun()

with browse_tab:
    browse_scroll = st.selectbox("Browse scroll", SCROLLS, key="browse_scroll")
    section_records = [
        rec for rec in corpus["records"]
        if rec["scroll"] == browse_scroll and rec["kind"] in {"preface", "section"}
    ]
    labels = {f"[{rec['canonical_id']}] {rec['heading']}": rec for rec in section_records}
    if labels:
        selected = st.selectbox("Section", list(labels.keys()))
        rec = labels[selected]
        st.subheader(rec["heading"])
        st.caption(f"Canonical ID [{rec['canonical_id']}] · source marker [{rec['source_id']}]")
        for p in rec["passages"]:
            st.markdown(p["text"])
            st.caption(p["passage_id"])

with source_tab:
    st.subheader("Parsed hierarchy")
    st.write({
        "records": corpus["record_count"],
        "sections": corpus["section_counts"],
        "passages": len(rows),
        "unique_browse_terms": len(term_counts),
    })
    corrected = [r for r in corpus["records"] if r["kind"] == "section" and r["id_corrected"]]
    if corrected:
        st.warning("Canonical IDs correct obvious sequence typos while retaining the source marker for provenance.")
        st.dataframe([
            {"scroll": r["scroll"], "canonical": r["canonical_id"], "source": r["source_id"], "heading": r["heading"]}
            for r in corrected
        ], use_container_width=True, hide_index=True)

st.caption("Prototype scope: Koten original only. Future textual layers can attach to the same canonical section IDs.")
