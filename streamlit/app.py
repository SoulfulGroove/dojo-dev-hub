import streamlit as st

st.set_page_config(page_title="Musashi Corpus Explorer", page_icon="⚔️", layout="wide")

st.title("⚔️ Musashi Corpus Explorer")
st.caption("Foundry Experiment 002 · Streamlit Lab")

PASSAGES = [
    {
        "scroll": "Earth",
        "jp": "三十を越えて跡をおもひ見るに兵法至極して勝つにはあらず",
        "literal": "Looking back after passing thirty, my victories were not because I had reached the ultimate of strategy.",
        "note": "Musashi reflects on earlier victories and rejects the idea that they proved complete mastery."
    },
    {
        "scroll": "Earth",
        "jp": "おのづから道の器用ありて天理を離れざるが故か",
        "literal": "Perhaps I naturally had an aptitude for the Way and did not depart from the principles of Heaven.",
        "note": "A reflective explanation rather than a claim of finished understanding."
    },
    {
        "scroll": "Earth",
        "jp": "その後猶も深き道理を得んと朝鍛夕錬して見ればおのづから兵法の道にあふこと我五十歳のころなり",
        "literal": "After that, seeking still deeper principles, training morning and evening, I naturally came to accord with the Way of strategy around the age of fifty.",
        "note": "A strong example of sustained practice leading toward deeper structural understanding."
    },
]

left, right = st.columns([1, 2])

with left:
    st.subheader("Search")
    scroll = st.selectbox("Scroll", ["All", "Earth", "Water", "Fire", "Wind", "Void"])
    term = st.text_input("Japanese term or phrase", value="道")
    show_literal = st.toggle("Show literal reading", value=True)
    show_notes = st.toggle("Show interpretive note", value=False)

filtered = [p for p in PASSAGES if scroll == "All" or p["scroll"] == scroll]
if term:
    matches = [p for p in filtered if term in p["jp"]]
else:
    matches = filtered

occurrences = sum(p["jp"].count(term) for p in filtered) if term else 0

with right:
    st.subheader("Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Matching passages", len(matches))
    c2.metric("Occurrences", occurrences)
    c3.metric("Loaded passages", len(filtered))

    if not matches:
        st.info("No matching passage in this small prototype dataset yet.")

    for i, passage in enumerate(matches, start=1):
        with st.container(border=True):
            st.caption(f"{passage['scroll']} Scroll · Match {i}")
            st.markdown(f"### {passage['jp']}")
            if show_literal:
                st.markdown(f"**Literal working reading:** {passage['literal']}")
            if show_notes:
                st.markdown(f"**Interpretive note:** {passage['note']}")

st.divider()
st.subheader("Quick term counts")
terms = ["道", "兵法", "理", "天理", "鍛", "錬"]
counts = {t: sum(p["jp"].count(t) for p in PASSAGES) for t in terms}
st.bar_chart(counts)

st.caption("Prototype only: seeded with a few Earth Scroll passages to prove the Streamlit workflow. The corpus can be expanded later without changing the basic interface.")