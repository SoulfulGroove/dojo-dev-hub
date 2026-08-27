import math
import streamlit as st

st.set_page_config(page_title="Book Design Laboratory", page_icon="📐", layout="wide")

st.title("📐 Book Design Laboratory")
st.caption("Foundry Experiment · page proportion, typography density, and vertical rhythm")

sample = (
    "The way of strategy is straight and true. Through continual practice, "
    "the structure of the whole becomes visible in the smallest parts. "
    "Form, spacing, rhythm, and proportion work together to guide the reader."
)

with st.sidebar:
    st.header("Page")
    page_width = st.number_input("Page width (in)", 4.0, 14.0, 8.5, 0.1)
    page_height = st.number_input("Page height (in)", 6.0, 20.0, 11.0, 0.1)
    top = st.number_input("Top margin (in)", 0.25, 3.0, 0.75, 0.05)
    bottom = st.number_input("Bottom margin (in)", 0.25, 3.0, 1.00, 0.05)
    inside = st.number_input("Inside margin (in)", 0.25, 3.0, 0.80, 0.05)
    outside = st.number_input("Outside margin (in)", 0.25, 3.0, 0.70, 0.05)

    st.header("Typography")
    body_size = st.slider("Body size (pt)", 8.0, 16.0, 10.5, 0.5)
    leading = st.slider("Leading (pt)", 9.0, 24.0, 14.0, 0.5)
    chars_factor = st.slider("Typeface width factor", 0.42, 0.62, 0.50, 0.01,
                             help="Approximate average character width as a fraction of body size. Narrower faces use a lower value.")
    heading_size = st.slider("Heading size (pt)", 12.0, 32.0, 18.0, 0.5)
    h_space_before = st.slider("Heading space before (pt)", 0.0, 56.0, 28.0, 1.0)
    h_space_after = st.slider("Heading space after (pt)", 0.0, 28.0, 7.0, 1.0)

text_width_in = max(0.1, page_width - inside - outside)
text_height_in = max(0.1, page_height - top - bottom)
text_width_pt = text_width_in * 72
text_height_pt = text_height_in * 72
avg_char_width = body_size * chars_factor
chars_per_line = max(1, int(text_width_pt / avg_char_width))
words_per_line = chars_per_line / 5.5
lines_per_page = max(1, int(text_height_pt / leading))
words_per_page = int(words_per_line * lines_per_page)
leading_ratio = leading / body_size
text_area_ratio = (text_width_in * text_height_in) / (page_width * page_height)

rhythm_before = h_space_before / leading if leading else 0
rhythm_after = h_space_after / leading if leading else 0
before_drift = abs(rhythm_before - round(rhythm_before))
after_half_drift = abs((rhythm_after * 2) - round(rhythm_after * 2)) / 2

m1, m2, m3, m4 = st.columns(4)
m1.metric("Text block", f"{text_width_in:.2f} × {text_height_in:.2f} in")
m2.metric("Characters / line", chars_per_line)
m3.metric("Lines / page", lines_per_page)
m4.metric("Est. words / page", words_per_page)

left, right = st.columns([1.05, 1.4], gap="large")

with left:
    st.subheader("Page proportion")
    page_css_w = 320
    page_css_h = int(page_css_w * page_height / page_width)
    scale_x = page_css_w / page_width
    scale_y = page_css_h / page_height
    x = inside * scale_x
    y = top * scale_y
    w = text_width_in * scale_x
    h = text_height_in * scale_y

    svg = f'''
    <svg viewBox="0 0 {page_css_w} {page_css_h}" width="100%" style="max-width:420px; background:#f4f0e6; border:1px solid #8b8478;">
      <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="#444" stroke-width="1.4"/>
      <line x1="{x:.1f}" y1="{max(8,y-14):.1f}" x2="{x+w:.1f}" y2="{max(8,y-14):.1f}" stroke="#999" stroke-width="1"/>
      <text x="{x:.1f}" y="{max(16,y-18):.1f}" font-size="8" fill="#666">running head</text>
      <text x="{x+w-18:.1f}" y="{min(page_css_h-8,y+h+18):.1f}" font-size="9" fill="#666">folio</text>
    </svg>
    '''
    st.markdown(svg, unsafe_allow_html=True)

    st.caption(f"Text occupies {text_area_ratio*100:.1f}% of total page area.")
    st.write(f"**Leading / type ratio:** {leading_ratio:.2f}")
    if 1.2 <= leading_ratio <= 1.5:
        st.success("Leading is in a broadly comfortable text-setting range.")
    elif leading_ratio < 1.2:
        st.warning("Leading is relatively tight for the selected body size.")
    else:
        st.info("Leading is relatively open for the selected body size.")

with right:
    st.subheader("Typography preview")
    preview_width_px = max(260, min(760, int(text_width_in * 92)))
    body_px = body_size * 1.333
    leading_px = leading * 1.333
    heading_px = heading_size * 1.333
    before_px = h_space_before * 1.333
    after_px = h_space_after * 1.333

    html = f'''
    <div style="max-width:{preview_width_px}px; padding:28px 34px; background:#fbfaf6; color:#24211c; border:1px solid #d5d0c5;">
      <div style="font: 11px Georgia, serif; letter-spacing:.08em; text-transform:uppercase; color:#777; margin-bottom:18px;">WATER SCROLL</div>
      <div style="font-family:Georgia, 'Times New Roman', serif; font-size:{heading_px}px; line-height:1.08; margin-top:{before_px}px; margin-bottom:{after_px}px;">On Katsu Totsu</div>
      <p style="font-family:Georgia, 'Times New Roman', serif; font-size:{body_px}px; line-height:{leading_px}px; margin:0; text-align:left;">{sample}</p>
      <p style="font-family:Georgia, 'Times New Roman', serif; font-size:{body_px}px; line-height:{leading_px}px; margin:{leading_px}px 0 0 0; text-align:left;">{sample}</p>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
    st.caption("Preview uses a browser serif fallback, so it is for proportion/density judgment rather than exact production typography.")

st.divider()
st.subheader("Vertical rhythm")
r1, r2, r3 = st.columns(3)
r1.metric("Heading before", f"{rhythm_before:.2f} body lines")
r2.metric("Heading after", f"{rhythm_after:.2f} body lines")
r3.metric("Heading/body size ratio", f"{heading_size/body_size:.2f}×")

if before_drift < 0.06:
    st.success("Space-before lands very close to a whole baseline multiple.")
else:
    st.info(f"Space-before is {rhythm_before:.2f} baseline units; consider testing {round(rhythm_before) * leading:.1f} pt for exact whole-line rhythm.")

if after_half_drift < 0.06:
    st.success("Space-after lands very close to a half-line baseline multiple.")
else:
    nearest_half = round(rhythm_after * 2) / 2
    st.info(f"Space-after is {rhythm_after:.2f} baseline units; nearest half-line value is {nearest_half * leading:.1f} pt.")

st.divider()
st.subheader("Density notes")
if chars_per_line < 45:
    st.warning("Short measure: the text may feel choppy depending on the face and prose.")
elif chars_per_line > 80:
    st.warning("Long measure: sustained reading may become harder without compensating leading or type size.")
else:
    st.success("Estimated line length sits in a conventional reading range.")

if text_area_ratio > 0.70:
    st.info("The text block is relatively large compared with the page; the page will likely read as dense/economical.")
elif text_area_ratio < 0.45:
    st.info("The text block is relatively small compared with the page; the page will likely feel spacious/formal.")
else:
    st.info("The text block/page relationship is moderate and leaves meaningful margin structure.")

st.caption("Prototype purpose: make relationships visible. Final font metrics, kerning, line breaking, hyphenation, and print proofing still belong in a production layout application.")