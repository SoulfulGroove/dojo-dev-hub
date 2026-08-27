import streamlit as st
from corpus_parser import parse_corpus, flatten_passages

st.set_page_config(page_title="Musashi Corpus Explorer", page_icon="⚔️", layout="wide")

st.title("⚔️ Musashi Corpus Explorer")
st.caption("Koten Original · full-corpus prototype")

uploaded = st.sidebar.file_uploader("Load compiled Koten TXT", type=["txt"])
st.sidebar.caption("Uses the numbered [####] hierarchy in the compiled source.")

if uploaded is None:
    st.info("Upload the compiled Koten-original TXT file to load the full corpus.")
    st.stop()

text = uploaded.getvalue().decode("utf-8")
corpus = parse_corpus(text)
rows = flatten_passages(corpus)

scroll_options = ["All", "Preface", "Earth", "Water", "Fire", "Wind", "Void"]
scroll = st.sidebar.selectbox("Scroll", scroll_options)
term = st.sidebar.text_input("Search Japanese term or phrase", value="道")
whole_section = st.sidebar.toggle("Show section context", value=False)

scope_rows = rows if scroll == "All" else [r for r in rows if r["scroll"] == scroll]
matches = [r for r in scope_rows if (term in r["text"] if term else True)]
occurrences = sum(r["text"].count(term) for r in scope_rows) if term else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sections", sum(corpus["section_counts"].values()))
c2.metric("Passages", len(rows))
c3.metric("Matching passages", len(matches))
c4.metric("Occurrences", occurrences)

tab_search, tab_browse, tab_analysis, tab_source = st.tabs(
    ["Search", "Browse", "Analysis", "Source Structure"]
)

with tab_search:
    if not matches:
        st.info("No matching passages in the selected scope.")
    else:
        for r in matches:
            with st.container(border=True):
                corrected = ""
                if r["source_id"] != r["section_id"]:
                    corrected = f" · source marker [{r['source_id']}]"
                st.caption(f"{r['scroll']} · [{r['section_id']}] {r['heading']}{corrected}")
                st.markdown(f"### {r['text']}")
                st.caption(r["passage_id"])
                if whole_section:
                    same = [x for x in rows if x["section_id"] == r["section_id"]]
                    with st.expander("Section context"):
                        for x in same:
                            st.write(x["text"])

with tab_browse:
    browse_scroll = st.selectbox(
        "Browse scroll",
        ["Preface", "Earth", "Water", "Fire", "Wind", "Void"],
        key="browse_scroll",
    )
    section_records = [
        rec for rec in corpus["records"]
        if rec["scroll"] == browse_scroll and rec["kind"] in {"preface", "section"}
    ]
    labels = {
        f"[{rec['canonical_id']}] {rec['heading']}": rec
        for rec in section_records
    }
    if labels:
        selected = st.selectbox("Section", list(labels.keys()))
        rec = labels[selected]
        st.subheader(rec["heading"])
        st.caption(
            f"Canonical ID [{rec['canonical_id']}] · source marker [{rec['source_id']}]"
        )
        for p in rec["passages"]:
            st.markdown(p["text"])
            st.caption(p["passage_id"])

with tab_analysis:
    st.subheader("Term distribution by scroll")
    analysis_term = st.text_input("Term", value=term or "道", key="analysis_term")
    scrolls = ["Preface", "Earth", "Water", "Fire", "Wind", "Void"]
    counts = {
        s: sum(r["text"].count(analysis_term) for r in rows if r["scroll"] == s)
        for s in scrolls
    }
    st.bar_chart(counts)
    st.write(counts)

    st.subheader("Quick comparison set")
    default_terms = "道,兵法,理,拍子,心,勝"
    term_list = [
        t.strip() for t in st.text_input(
            "Comma-separated terms", default_terms
        ).split(",") if t.strip()
    ]
    table = []
    for t in term_list:
        row = {"term": t}
        for s in scrolls[1:]:
            row[s] = sum(r["text"].count(t) for r in rows if r["scroll"] == s)
        table.append(row)
    st.dataframe(table, use_container_width=True)

with tab_source:
    st.subheader("Parsed hierarchy")
    st.write(
        {
            "records": corpus["record_count"],
            "sections": corpus["section_counts"],
            "passages": len(rows),
        }
    )
    corrected = [
        rec for rec in corpus["records"]
        if rec["kind"] == "section" and rec["id_corrected"]
    ]
    if corrected:
        st.warning(
            "Canonical IDs differ from source markers where the compiled numbering "
            "contains obvious sequence typos. Source markers are retained."
        )
        st.dataframe(
            [
                {
                    "scroll": r["scroll"],
                    "canonical": r["canonical_id"],
                    "source": r["source_id"],
                    "heading": r["heading"],
                }
                for r in corrected
            ],
            use_container_width=True,
        )

st.caption(
    "Prototype scope: Koten original only. Future modern/reconstructed/translation "
    "layers can attach to the same canonical section IDs."
)
