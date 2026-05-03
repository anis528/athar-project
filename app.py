import os
import streamlit as st
import replicate
import streamlit.components.v1 as components

# الآن نضع سطر المفتاح هنا (بعد تعريف st)
os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# سطر التنظيف
st.cache_data.clear()
import requests
import base64
import urllib.parse
from PIL import Image
import io
from db import init_db, create_order, list_orders, get_order, format_order_id
st.set_page_config(
    page_title="أثر - كتاب طفلك السحري",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap');

* { font-family: 'Cairo', sans-serif !important; direction: rtl; }
html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }

.stApp {
    background: #E6E6FA;
    background-image:
        radial-gradient(circle at 12% 8%, rgba(255,255,255,0.45) 0%, transparent 40%),
        radial-gradient(circle at 88% 12%, rgba(216,191,216,0.5) 0%, transparent 38%),
        radial-gradient(circle at 50% 95%, rgba(184,158,224,0.25) 0%, transparent 50%);
}

/* === Centered wizard container === */
.block-container { max-width: 980px !important; padding-top: 1rem !important; }

/* === PROGRESS BAR === */
.progress-bar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    max-width: 720px;
    margin: 0.6rem auto 1.5rem;
    padding: 0.5rem 0.4rem;
    direction: ltr;
}
.prog-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 2;
    flex: 0 0 auto;
}
.prog-circle {
    width: 50px; height: 50px;
    border-radius: 50%;
    background: white;
    border: 3px solid #D8BFD8;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.prog-step.active .prog-circle {
    background: linear-gradient(135deg, #B57EE0, #7B3FA6);
    border-color: #7B3FA6;
    color: white;
    transform: scale(1.18);
    box-shadow: 0 6px 22px rgba(155,89,182,0.45);
}
.prog-step.done .prog-circle {
    background: linear-gradient(135deg, #88D88B, #4FA84F);
    border-color: #4FA84F;
    color: white;
    font-weight: 900;
}
.prog-label {
    margin-top: 0.5rem;
    font-size: 0.72rem;
    font-weight: 700;
    color: #7B6798;
    text-align: center;
    direction: rtl;
    max-width: 86px;
    line-height: 1.3;
}
.prog-step.active .prog-label { color: #5A3D8A; font-weight: 900; }
.prog-step.done .prog-label { color: #2D7D32; }
.prog-line {
    flex: 1 1 auto;
    height: 4px;
    background: #D8BFD8;
    margin: 23px -2px 0;
    border-radius: 2px;
    z-index: 1;
}
.prog-line.done { background: linear-gradient(90deg, #4FA84F, #88D88B); }

/* === UPSELL CARDS === */
.upsell-card {
    background: linear-gradient(135deg, #FFFFFF, #F8F0FF);
    border: 2px solid #E6D8F5;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.9rem;
    transition: all 0.25s;
}
.upsell-card.checked {
    border-color: #9B59B6;
    box-shadow: 0 6px 20px rgba(155,89,182,0.18);
    background: linear-gradient(135deg, #F8F0FF, #FFE6F5);
}
.upsell-row { display: flex; justify-content: space-between; align-items: center; gap: 0.8rem; }
.upsell-name { font-size: 1.05rem; font-weight: 800; color: #5A3D8A; }
.upsell-desc { font-size: 0.78rem; color: #8B7AA8; font-weight: 600; margin-top: 0.2rem; line-height: 1.5; }
.upsell-price { font-size: 1.1rem; font-weight: 900; color: #9B59B6; white-space: nowrap; }

/* === CHECKOUT SUMMARY === */
.checkout-summary {
    background: linear-gradient(135deg, #FFFFFF, #FAF5FF);
    border: 2px solid #D8BFD8;
    border-radius: 20px;
    padding: 1.4rem 1.5rem;
    margin-top: 1rem;
    box-shadow: 0 4px 16px rgba(155,89,182,0.1);
}
.checkout-line { display: flex; justify-content: space-between; padding: 0.4rem 0; font-weight: 700; color: #5A3D8A; font-size: 0.96rem; }
.checkout-line.total { border-top: 2px solid #D8BFD8; padding-top: 0.7rem; margin-top: 0.4rem; font-size: 1.25rem; color: #7B3FA6; font-weight: 900; }

/* === CHECKBOX styling === */
.stCheckbox label { font-weight: 700 !important; color: #5A3D8A !important; font-size: 1rem !important; }

/* === MOBILE === */
@media (max-width: 600px) {
    .prog-circle { width: 38px; height: 38px; font-size: 1.05rem; }
    .prog-label { font-size: 0.6rem; max-width: 60px; }
    .prog-line { margin-top: 17px; height: 3px; }
}

.main-header {
    text-align: center;
    padding: 1.1rem 1rem 0.9rem;
    background: linear-gradient(135deg, #B57EE0 0%, #9B59B6 55%, #7B3FA6 100%);
    border-radius: 22px;
    margin-bottom: 0.6rem;
    box-shadow: 0 8px 28px rgba(123,63,166,0.35);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events: none;
}
.main-header h1 {
    font-size: 2.4rem;
    font-weight: 900;
    color: white;
    text-shadow: 1px 3px 10px rgba(0,0,0,0.22);
    margin-bottom: 0.1rem;
    letter-spacing: 3px;
    position: relative;
}
.main-header p {
    font-size: 1rem;
    color: rgba(255,255,255,0.95);
    font-weight: 600;
    position: relative;
}

.step-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 30px rgba(155,89,182,0.08);
    border: 2px solid rgba(240,232,255,0.8);
}
.step-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #6B4A8E;
    margin-bottom: 1.2rem;
    border-bottom: 3px solid;
    border-image: linear-gradient(90deg, #FF9EC4, #C8A8FF, transparent) 1;
    padding-bottom: 0.6rem;
}

/* === BOOK SELECTION CARDS === */
.book-card {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(155,89,182,0.12), inset 0 0 0 2px rgba(255,255,255,0.6);
    background: white;
    margin-bottom: 6px;
}
.book-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 32px rgba(155,89,182,0.25), inset 0 0 0 2px rgba(255,255,255,0.8);
}
.book-card.selected {
    box-shadow: 0 8px 24px rgba(155,89,182,0.4), inset 0 0 0 3px #9B59B6;
    transform: translateY(-3px);
}
.book-card.selected::after {
    content: '✓';
    position: absolute;
    top: 6px; left: 6px;
    background: linear-gradient(135deg, #9B59B6, #6B4A8E);
    color: white;
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    font-weight: 900;
    z-index: 10;
}
.book-image-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    overflow: hidden;
}
.book-image-wrap img {
    width: 100%; height: 100%;
    object-fit: cover; display: block;
}
.book-label {
    background: linear-gradient(135deg, #FFFFFF, #FFF8FC);
    padding: 0.6rem 0.4rem;
    text-align: center;
    border-top: 2px solid rgba(200,168,255,0.3);
}
.book-name {
    font-size: 0.85rem;
    font-weight: 800;
    color: #5A3D8A;
    margin-bottom: 0.1rem;
    line-height: 1.2;
}
.book-desc {
    font-size: 0.62rem;
    color: #8C7AA8;
    font-weight: 600;
    line-height: 1.3;
}

/* === THEME SELECT BUTTONS — compact, no overlap === */
.stButton > button {
    font-family: 'Cairo', sans-serif !important;
    font-weight: 700;
    border-radius: 50px;
    padding: 0.3rem 0.4rem !important;
    font-size: clamp(0.6rem, 1.2vw, 0.75rem) !important;
    line-height: 1.2 !important;
    background: linear-gradient(135deg, #C8A8FF, #9B59B6);
    color: white;
    border: none;
    box-shadow: 0 3px 10px rgba(155,89,182,0.3);
    transition: all 0.2s;
    width: 100%;
    white-space: normal !important;
    word-break: keep-all;
    min-height: 34px;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(155,89,182,0.45);
}

/* === BOOK CARD: max-width + fluid images === */
.book-card {
    max-width: 200px;
    margin-left: auto;
    margin-right: auto;
}
.book-image-wrap img {
    max-width: 100%;
    height: auto;
}

/* === RESPONSIVE PADDING === */
@media (max-width: 900px) {
    .step-card { padding: 1.2rem; }
    .main-header h1 { font-size: 2.5rem; }
    .main-header p { font-size: 1rem; }
    .book-name { font-size: 0.75rem; }
    .book-desc { font-size: 0.55rem; }
}

/* === WHATSAPP STICKY === */
.whatsapp-sticky-wrap {
    position: sticky;
    bottom: 1rem;
    z-index: 99;
    margin-top: 1rem;
}

/* === PRICE BOX === */
.price-box {
    background: linear-gradient(135deg, #FF9EC4 0%, #C8A8FF 50%, #A8D8FF 100%);
    border-radius: 24px;
    padding: 1.8rem;
    text-align: center;
    color: white;
    box-shadow: 0 12px 40px rgba(200,168,255,0.4);
}
.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    font-size: 1rem;
    font-weight: 600;
}
.price-row span:last-child { font-weight: 800; font-size: 1.05rem; }
.price-divider { height: 2px; background: rgba(255,255,255,0.35); margin: 0.6rem 0; border-radius: 2px; }
.price-total-label { font-size: 1.05rem; opacity: 0.95; font-weight: 700; margin-top: 0.4rem; }
.price-total { font-size: 2.8rem; font-weight: 900; text-shadow: 0 2px 8px rgba(0,0,0,0.2); margin-top: 0.2rem; }
.price-currency { font-size: 1.5rem; opacity: 0.9; margin-right: 0.5rem; }

/* === INFO BOX === */
.info-box {
    background: linear-gradient(135deg, #FFF9E6, #FFFBF0);
    border: 2px solid #FFD980;
    border-radius: 20px;
    padding: 1.4rem;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(255,217,128,0.2);
}
.info-box h4 { color: #B8860B; font-size: 1.15rem; font-weight: 800; margin-bottom: 0.8rem; }
.info-box p { color: #8B6914; font-size: 0.95rem; line-height: 1.9; font-weight: 600; margin: 0; }

/* === WHATSAPP === */
.whatsapp-btn {
    background: linear-gradient(135deg, #25D366, #128C7E);
    color: white !important;
    border-radius: 50px;
    padding: 1.1rem 2.5rem;
    font-size: 1.3rem;
    font-weight: 800;
    font-family: 'Cairo', sans-serif !important;
    cursor: pointer;
    width: 100%;
    box-shadow: 0 8px 28px rgba(37,211,102,0.5);
    transition: all 0.25s;
    text-decoration: none !important;
    display: block;
    text-align: center;
    margin: 0.5rem 0;
}
.whatsapp-btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 32px rgba(37,211,102,0.6); }
.whatsapp-disabled {
    background: linear-gradient(135deg, #E8E8E8, #D0D0D0);
    color: #888;
    border-radius: 50px;
    padding: 1.1rem 2.5rem;
    text-align: center;
    font-size: 1.3rem;
    font-weight: 800;
    font-family: 'Cairo', sans-serif !important;
    margin: 0.5rem 0;
}

.success-banner {
    background: linear-gradient(135deg, #E8FFE8, #F0FFF4);
    border: 2px solid #52C41A;
    border-radius: 20px;
    padding: 1.4rem;
    text-align: center;
    color: #2D7D32;
    font-weight: 800;
    font-size: 1.2rem;
}
.divider { height: 4px; background: linear-gradient(90deg, #FF9EC4, #C8A8FF, #A8D8FF); border-radius: 4px; margin: 1.8rem 0; opacity: 0.6; }
.guarantee-box {
    background: linear-gradient(135deg, #F0FFF4, #E8F5FF);
    border: 2px solid #A8D8AA;
    border-radius: 20px;
    padding: 1.3rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(82,196,26,0.1);
}
.footer { text-align: center; padding: 2rem; color: #9B8AB8; font-size: 0.9rem; font-weight: 600; margin-top: 2rem; }

.stSelectbox > div > div { font-family: 'Cairo', sans-serif !important; border-radius: 14px; border: 2px solid #E0D0FF; font-size: 1rem; font-weight: 600; }
.stTextInput > div > div > input { font-family: 'Cairo', sans-serif !important; border-radius: 14px; border: 2px solid #E0D0FF; font-size: 1rem; text-align: right; font-weight: 600; padding: 0.6rem 1rem; }
.stTextInput > div > div > input:focus { border-color: #9B59B6; box-shadow: 0 0 0 3px rgba(155,89,182,0.15); }
label { font-family: 'Cairo', sans-serif !important; font-weight: 700 !important; color: #5A3D8A !important; font-size: 1rem !important; }

#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

/* === MAGIC PREVIEW SECTION (Step 1) === */
.magic-preview-section {
    background: linear-gradient(135deg, #2A1248 0%, #5A3D8A 100%);
    border-radius: 20px;
    padding: 1.4rem 1.2rem;
    margin-top: 1.4rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.magic-preview-section::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 15% 50%, rgba(255,255,255,0.07) 0%, transparent 55%);
    pointer-events: none;
}
.magic-preview-title {
    font-size: 1.25rem; font-weight: 900; color: #FFE6F5;
    margin-bottom: 0.25rem; position: relative;
}
.magic-preview-sub {
    font-size: 0.8rem; color: rgba(255,255,255,0.75);
    margin-bottom: 1rem; font-weight: 600; position: relative;
}
.magic-thumb-row {
    display: flex; gap: 8px; justify-content: center;
    flex-wrap: wrap; position: relative;
}
.magic-thumb-item {
    width: 100px; border-radius: 12px; overflow: hidden;
    border: 3px solid rgba(255,255,255,0.18);
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    flex-shrink: 0;
}
.magic-thumb-item img { width: 100%; height: 88px; object-fit: cover; display: block; }
.magic-thumb-label {
    background: rgba(0,0,0,0.68); color: #FFE6F5;
    font-size: 0.52rem; font-weight: 800; padding: 4px 5px;
    text-align: center; line-height: 1.3;
}

/* === VISUAL UPSELL CARDS === */
.upsell-visual-card {
    background: linear-gradient(135deg, #FFFFFF, #FAF5FF);
    border: 2px solid #E6D8F5;
    border-radius: 18px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.7rem;
    transition: all 0.25s;
}
.upsell-visual-card.checked {
    border-color: #9B59B6;
    box-shadow: 0 5px 18px rgba(155,89,182,0.2);
    background: linear-gradient(135deg, #F8F0FF, #FDF0FF);
}
.upsell-visual-row { display: flex; align-items: center; gap: 1rem; }
.upsell-thumb-box {
    width: 88px; height: 88px; border-radius: 14px;
    flex-shrink: 0; overflow: hidden;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
}
.thumb-stickers { background: linear-gradient(135deg, #FFD700, #FF8C00); }
.thumb-poster   { background: linear-gradient(135deg, #1A237E, #283593); }
.upsell-info { flex: 1; text-align: right; }
.upsell-name-v2  { font-size: 1.05rem; font-weight: 900; color: #5A3D8A; margin-bottom: 0.2rem; }
.upsell-desc-v2  { font-size: 0.78rem; color: #8B7AA8; font-weight: 600; line-height: 1.5; }
.upsell-price-v2 { font-size: 1.1rem; font-weight: 900; color: #9B59B6; margin-top: 0.25rem; }

/* === SHIPPING METHOD CARDS (Step 5) === */
.ship-method-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 0.6rem 0 0.2rem;
}
.ship-method-card {
    background: white; border: 2.5px solid #D8BFD8; border-radius: 16px;
    padding: 1rem 0.8rem; text-align: center; transition: all 0.22s;
}
.ship-method-card.active {
    border-color: #9B59B6;
    background: linear-gradient(135deg, #F5E8FF, #EDE0FF);
    box-shadow: 0 4px 18px rgba(155,89,182,0.22);
}
.ship-method-icon  { font-size: 2rem; margin-bottom: 0.25rem; }
.ship-method-label { font-size: 0.88rem; font-weight: 800; color: #5A3D8A; margin-bottom: 0.2rem; }
.ship-method-price { font-size: 1.2rem; font-weight: 900; color: #9B59B6; }
.ship-method-note  { font-size: 0.68rem; color: #8B7AA8; font-weight: 600; margin-top: 0.2rem; }

/* === LIVE TOTAL BADGE === */
.live-total-badge {
    background: linear-gradient(135deg, #9B59B6, #6B4A8E);
    color: white; border-radius: 50px;
    padding: 0.55rem 1.5rem;
    font-size: 1.2rem; font-weight: 900;
    display: inline-block;
    box-shadow: 0 4px 16px rgba(155,89,182,0.35);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Precise Algerian flag — blocks Mexico/eagle confusion ──────────────────
FLAG_DESC = (
    "the authentic ALGERIAN national flag ONLY — "
    "strictly two equal vertical bars: LEFT half is solid EMERALD GREEN, "
    "RIGHT half is pure WHITE, with a RED crescent moon opening to the right "
    "and a RED five-pointed star in the center. "
    "NOT Mexico. NOT an eagle. NO coat of arms. NO crest. NO eagle emblem. "
    "ONLY the Algerian green-white-red-crescent-star flag."
)

THEMES = {
    "بَطَلُ الْفَضَاءِ": {
        "image": "theme_space.png",
        "desc": "رَائِدُ فَضَاءٍ • عَلَمُ الْجَزَائِرِ • الْقَمَرُ",
        "costume": (
            "a brave young Algerian astronaut with authentic Algerian features — "
            "dark expressive eyes, warm North African complexion, proud Algerian heritage. "
            "Wearing a brilliant white high-tech space suit. "
            "On the left shoulder: a large embroidered patch of {flag} — "
            "green left, white right, red crescent and red star, clearly visible. "
            "On the chest: another {flag} patch stitched onto the suit."
        ),
        "landmark": (
            "standing heroically on the lunar surface. Earth rising in starry space behind. "
            "A full-size {flag} planted on the moon — green-white-red crescent-star clearly showing. "
            "Cinematic NASA-style lighting."
        ),
        "story": [
            "كَانَ يَا مَا كَانَ، فِي رَبُوعِ الْجَزَائِرِ الْحَبِيبَةِ، طِفْلٌ شُجَاعٌ اسْمُهُ {name}...",
            "كَانَ يَحْلُمُ مُنْذُ صِغَرِهِ بِالتَّحْلِيقِ بَيْنَ النُّجُومِ الْبَعِيدَةِ",
            "وَفِي يَوْمٍ مُشْرِقٍ، ارْتَدَى بَدْلَتَهُ الْفَضَائِيَّةَ وَانْطَلَقَ",
            "لِيَغْرِسَ عَلَمَ الْجَزَائِرِ فَوْقَ تُرَابِ الْقَمَرِ بِفَخْرٍ..."
        ]
    },
    "الْبَطَلُ الْمُنْقِذُ بِبُرْنُوسٍ": {
        "image": "theme_burnous.png",
        "desc": "بُرْنُسٌ أَبْيَضُ • مَقَامُ الشَّهِيدِ • الْجَزَائِرُ",
        "costume": (
            "a noble young Algerian hero with authentic Algerian features — "
            "dark expressive eyes, warm North African complexion. "
            "Wearing a flowing traditional white Algerian Burnous cloak "
            "with gold embroidery. Heroic confident pose."
        ),
        "landmark": (
            "standing in front of Maqam El Chahid (Algiers Martyrs Memorial) at golden sunset. "
            "Behind the child: a LARGE waving {flag} on a tall pole — "
            "green and white vertical bars with red crescent and star, correctly colored, "
            "NO eagle, NO Mexican colors. Warm golden sky, cinematic light."
        ),
        "story": [
            "كَانَ يَا مَا كَانَ، فِي قَرْيَةٍ جَزَائِرِيَّةٍ جَمِيلَةٍ، طِفْلٌ نَبِيلٌ اسْمُهُ {name}...",
            "كَانَ يَرْتَدِي كُلَّ يَوْمٍ بُرْنُسَهُ الأَبْيَضَ بِكُلِّ فَخْرٍ وَشُمُوخٍ",
            "وَوَقَفَ أَمَامَ مَقَامِ الشَّهِيدِ يُحَيِّي أَرْوَاحَ الأَبْطَالِ",
            "وَكَانَتْ شَجَاعَتُهُ تُلْهِمُ كُلَّ مَنْ رَآهُ مِنْ حَوْلِهِ..."
        ]
    },
    "الْأَمِيرَةُ الْجَمِيلَةُ بِالْكَارَاكُو": {
        "image": "theme_princess.png",
        "desc": "كَارَاكُو جَزَائِرِيٌّ • خَيْطُ الرُّوحِ • قَصْرٌ سِحْرِيٌّ",
        "costume": (
            "a beautiful young Algerian princess with authentic Algerian features — "
            "dark expressive eyes, warm North African complexion, graceful Algerian heritage. "
            "Wearing a deep-blue gold-embroidered Karakou velvet jacket "
            "over a white skirt, wearing a traditional golden Khait El Rouh amber necklace "
            "and ornate Algerian silver jewelry."
        ),
        "landmark": (
            "inside a magnificent magical Algerian palace with colorful arabesque archways, "
            "zellige tile floors, crystal chandeliers. "
            "Rose-gold and lavender magical glow, sparkle particles floating."
        ),
        "story": [
            "كَانَ يَا مَا كَانَ، فِي بَلَدٍ جَمِيلٍ اسْمُهُ الْجَزَائِرُ، أَمِيرَةٌ صَغِيرَةٌ اسْمُهَا {name}...",
            "كَانَتْ تَرْتَدِي كَارَاكُوهَا الأَزْرَقَ الْمُطَرَّزَ بِالذَّهَبِ",
            "وَقَلْبٌ مَلِيءٌ بِالشَّجَاعَةِ وَالْحُبِّ لِبِلَادِهَا",
            "أَمِيرَةٌ حَقِيقِيَّةٌ تَخْدُمُ شَعْبَهَا بِإِخْلَاصٍ وَوَفَاءٍ..."
        ]
    },
    "الطَّيَّارُ الشُّجَاعُ": {
        "image": "theme_pilot.png",
        "desc": "طَيَّارٌ جَزَائِرِيٌّ • جِبَالُ الأَطْلَسِ • السَّمَاءُ",
        "costume": (
            "a courageous young Algerian vintage aviator with authentic Algerian features — "
            "dark expressive eyes, warm North African complexion. "
            "Wearing a classic brown leather flight jacket "
            "and aviator goggles. On the sleeve: {flag} patch — "
            "green-white-red crescent-star, no eagle, correctly colored."
        ),
        "landmark": (
            "cockpit of a vintage biplane soaring above the snow-capped Atlas Mountains of Algeria. "
            "Lush green valleys below, golden-hour sky. "
            "The {flag} painted on the tail fin — green-white-red crescent-star clearly visible."
        ),
        "story": [
            "كَانَ يَا مَا كَانَ، فِي مَدِينَةٍ جَزَائِرِيَّةٍ، طَيَّارٌ صَغِيرٌ شُجَاعٌ اسْمُهُ {name}...",
            "حَلَّقَ فَوْقَ جِبَالِ الأَطْلَسِ الشَّامِخَةِ حَامِلًا الْعَلَمَ",
            "وَأَنْقَذَ طَائِرَةً مِنَ الْعَاصِفَةِ بِشَجَاعَتِهِ وَذَكَائِهِ",
            "حَتَّى لَمَسَتْ أَجْنِحَتُهُ قِمَمَ الأَحْلَامِ وَالنُّجُومِ..."
        ]
    },
    "الْمُخْتَرِعُ الصَّغِيرُ": {
        "image": "theme_inventor.png",
        "desc": "مُخْتَرِعٌ جَزَائِرِيٌّ • نُقُوشُ الزَّلِيجِ • الْعِلْمُ",
        "costume": (
            "a brilliant young Algerian scientist inventor with authentic Algerian features — "
            "dark expressive eyes, warm North African complexion. "
            "Wearing a white lab coat "
            "decorated with Algerian geometric arabesque border patterns in gold. "
            "Holding a glowing test tube. Safety goggles on forehead."
        ),
        "landmark": (
            "a vibrant colorful modern laboratory with glowing potions in green, blue and purple, "
            "Algerian zellige tile patterns on the walls. "
            "A small {flag} desk flag — green-white-red crescent-star — sits on the lab bench."
        ),
        "story": [
            "كَانَ يَا مَا كَانَ، فِي حَيٍّ جَزَائِرِيٍّ هَادِئٍ، مُخْتَرِعٌ صَغِيرٌ اسْمُهُ {name}...",
            "كَانَ يَخْلِطُ أَلْوَانَ الْعِلْمِ فِي مَخْتَبَرِهِ الصَّغِيرِ الْجَمِيلِ",
            "وَنُقُوشُ الزَّلِيجِ الْجَزَائِرِيِّ تُزَيِّنُ جُدْرَانَهُ الْمُلَوَّنَةَ",
            "لِيُغَيِّرَ الْعَالَمَ اخْتِرَاعًا وَاحِدًا تِلْوَ الآخَرِ..."
        ]
    }
}

WILAYA_SHIPPING = {
    # (office/stopdesk_tarif, home_delivery_tarif) in DZD
    "01 - أدرار":              ( 900, 1400), "02 - الشلف":              ( 550,  850),
    "03 - الأغواط":            ( 600,  950), "04 - أم البواقي":         ( 500,  750),
    "05 - باتنة":              ( 500,  750), "06 - بجاية":              ( 500,  750),
    "07 - بسكرة":              ( 600,  950), "08 - بشار":               ( 700, 1100),
    "09 - البليدة":            ( 400,  650), "10 - البويرة":            ( 450,  700),
    "11 - تمنراست":            (1000, 1600), "12 - تبسة":               ( 500,  800),
    "13 - تلمسان":             ( 550,  850), "14 - تيارت":              ( 550,  850),
    "15 - تيزي وزو":           ( 450,  700), "16 - الجزائر العاصمة":    ( 400,  600),
    "17 - الجلفة":             ( 600,  950), "18 - جيجل":               ( 500,  750),
    "19 - سطيف":               ( 500,  750), "20 - سعيدة":              ( 500,  800),
    "21 - سكيكدة":             ( 450,  700), "22 - سيدي بلعباس":        ( 500,  800),
    "23 - عنابة":              ( 450,  700), "24 - قالمة":              ( 450,  700),
    "25 - قسنطينة":            ( 450,  700), "26 - المدية":             ( 450,  700),
    "27 - مستغانم":            ( 500,  800), "28 - المسيلة":            ( 550,  850),
    "29 - معسكر":              ( 500,  800), "30 - ورقلة":              ( 650, 1000),
    "31 - وهران":              ( 500,  800), "32 - البيض":              ( 650, 1050),
    "33 - إليزي":              ( 950, 1500), "34 - برج بوعريريج":       ( 500,  750),
    "35 - بومرداس":            ( 400,  650), "36 - الطارف":             ( 500,  750),
    "37 - تندوف":              ( 950, 1500), "38 - تيسمسيلت":           ( 550,  850),
    "39 - الوادي":             ( 650, 1000), "40 - خنشلة":              ( 550,  850),
    "41 - سوق أهراس":          ( 500,  750), "42 - تيبازة":             ( 400,  650),
    "43 - ميلة":               ( 500,  750), "44 - عين الدفلى":         ( 500,  750),
    "45 - النعامة":            ( 650, 1000), "46 - عين تموشنت":         ( 550,  850),
    "47 - غرداية":             ( 650, 1000), "48 - غليزان":             ( 550,  850),
    "49 - تيميمون":            ( 900, 1400), "50 - برج باجي مختار":     (1000, 1600),
    "51 - أولاد جلال":         ( 600,  950), "52 - بني عباس":           ( 800, 1200),
    "53 - إن صالح":            ( 950, 1500), "54 - إن قزام":            (1000, 1600),
    "55 - تقرت":               ( 650, 1000), "56 - جانت":               (1000, 1600),
    "57 - المغير":             ( 650, 1000), "58 - المنيعة":            ( 800, 1200),
}
WILAYAS = {k: v[1] for k, v in WILAYA_SHIPPING.items()}  # backward compat

BOOK_PRICE = 2800
STICKERS_PRICE = 800
POSTER_PRICE = 1500
SHIPPING_OFFICE = 400
SHIPPING_HOME = 750
WHATSAPP_NUMBER = "213790082773"
ADMIN_PASSWORD = "Anis2026"

# 25-paragraph fully-vocalized (Tashkeel) stories × 5 themes — PDF storybook
FULL_STORIES = {
    "بَطَلُ الْفَضَاءِ": [
        "كَانَ يَا مَا كَانَ، فِي رَبُوعِ الْجَزَائِرِ الْحَبِيبَةِ، طِفْلٌ شُجَاعٌ يُحِبُّ النُّجُومَ اسْمُهُ {name}.",
        "كَانَ {name} يَجْلِسُ كُلَّ لَيْلَةٍ عَلَى سَطْحِ الْبَيْتِ يُحَدِّقُ فِي السَّمَاءِ الزَّرْقَاءِ اللَّامِعَةِ.",
        "وَكَانَ يَقُولُ لِأُمِّهِ: يَا أُمِّي، سَأَطِيرُ يَوْمًا مَا إِلَى تِلْكَ النُّجُومِ الْبَعِيدَةِ!",
        "ابْتَسَمَتْ أُمُّهُ وَضَمَّتْهُ إِلَى صَدْرِهَا قَائِلَةً: أُؤْمِنُ بِكَ يَا {name}، أَنْتَ قَادِرٌ عَلَى كُلِّ شَيْءٍ!",
        "فِي صَبَاحٍ مُشْرِقٍ مِنْ صَبَاحَاتِ الْجَزَائِرِ الذَّهَبِيَّةِ، وَصَلَتْ رِسَالَةٌ سِحْرِيَّةٌ مُذَهَّبَةُ الْأَطْرَافِ.",
        "كَتَبَتْ فِيهَا وَكَالَةُ الْفَضَاءِ: أَيُّهَا الْبَطَلُ {name}، لَقَدِ اخْتَرْنَاكَ لِمُهِمَّةٍ فِي الْفَضَاءِ!",
        "قَفَزَ {name} مِنَ الْفَرَحِ وَارْتَدَى بَدْلَتَهُ الْفَضَائِيَّةَ الْبَيْضَاءَ اللَّامِعَةَ بِسُرْعَةٍ وَحَمَاسٍ.",
        "عَلَى كَتِفِهِ الْأَيْسَرِ، زَيَّنَ الْبَدْلَةَ عَلَمُ الْجَزَائِرِ الْأَخْضَرُ وَالْأَبْيَضُ الْمَرْفُوعُ بِفَخْرٍ.",
        "صَعِدَ {name} إِلَى الصَّارُوخِ الْعِمْلَاقِ وَالنِّيرَانُ الْحَمْرَاءُ تَشْتَعِلُ تَحْتَهُ بِبَهَاءٍ وَجَلَالٍ.",
        "انْطَلَقَ الصَّارُوخُ نَحْوَ السَّمَاءِ كَالنَّجْمَةِ الذَّهَبِيَّةِ وَالنَّاسُ يُصَفِّقُونَ وَيَهْتِفُونَ بِالْفَرَحِ.",
        "مَرَّ {name} بِالسُّحُبِ الْبَيْضَاءِ النَّاعِمَةِ كَالْقُطْنِ، ثُمَّ خَرَجَ إِلَى الْفَضَاءِ الْوَاسِعِ الْعَجِيبِ.",
        "رَأَى الأَرْضَ مِنْ بَعِيدٍ كَجَوْهَرَةٍ زَرْقَاءَ لَامِعَةٍ تَطْفُو فِي بَحْرٍ مِنَ الظَّلَامِ اللَّجِيِّ.",
        "وَمَيَّزَ {name} مِنَ الأَعْلَى بِلَادَ الْجَزَائِرِ الْحَبِيبَةِ وَقَلْبُهُ يَنْبِضُ بِالْحُبِّ وَالِاشْتِيَاقِ.",
        "هَبَطَ عَلَى سَطْحِ الْقَمَرِ بِخُطُوَاتٍ خَفِيفَةٍ كَأَنَّهُ يَمْشِي عَلَى الْغُيُومِ الْحَرِيرِيَّةِ الْبَيْضَاءِ.",
        "غَرَسَ {name} عَلَمَ الْجَزَائِرِ فَوْقَ تُرَابِ الْقَمَرِ الْفِضِّيِّ وَصَرَخَ بِفَرَحٍ: تَحْيَا الْجَزَائِرُ!",
        "الْتَقَطَتْ كَامِيرَاتُ الْمَرْكَبَةِ أَجْمَلَ صُورَةٍ: {name} يَقِفُ بَطَلًا فَوْقَ الْقَمَرِ حَامِلًا الْعَلَمَ.",
        "عَادَ {name} إِلَى الأَرْضِ وَالنَّاسُ يَسْتَقْبِلُونَهُ بِالزُّهُورِ وَالأَغَانِي وَالأَعْلَامِ الْخَفَّاقَةِ.",
        "قَالَ لَهُ رَئِيسُ الْوُزَرَاءِ: لَقَدْ رَفَعْتَ اسْمَ الْجَزَائِرِ فِي كُلِّ بِقَاعِ الْكَوْنِ يَا {name}!",
        "وَقَفَ {name} أَمَامَ أَطْفَالِ الْجَزَائِرِ وَقَالَ: كُلُّ وَاحِدٍ مِنْكُمْ يَسْتَطِيعُ بُلُوغَ النُّجُومِ!",
        "عَادَ إِلَى بَيْتِهِ وَأُمُّهُ تَنْتَظِرُهُ بِدُمُوعِ الْفَرَحِ وَذِرَاعَيْنِ مَفْتُوحَتَيْنِ بِالْحُبِّ وَالِاشْتِيَاقِ.",
        "جَلَسَ {name} مَعَ أُسْرَتِهِ وَحَكَى لَهُمْ عَنْ جَمَالِ الْفَضَاءِ وَعَظَمَةِ الْكَوْنِ اللَّامُتَنَاهِي.",
        "نَامَ {name} تِلْكَ اللَّيْلَةَ نَوْمَ الأَبْطَالِ وَالنُّجُومُ تُنَاجِيهِ مِنَ النَّافِذَةِ الصَّغِيرَةِ بِلُطْفٍ.",
        "فِي الصَّبَاحِ، كَتَبَ {name} رِسَالَةً إِلَى كُلِّ أَطْفَالِ الْجَزَائِرِ: آمِنُوا بِأَحْلَامِكُمْ دَائِمًا!",
        "عَرَفَ {name} أَنَّ الْحُلُمَ يَبْدَأُ بِخُطْوَةٍ صَغِيرَةٍ وَيَنْتَهِي بِفَتْحِ أَبْوَابِ الْمُسْتَحِيلِ الْعَظِيمِ.",
        "وَمُنْذُ ذَلِكَ الْيَوْمِ أَصْبَحَ {name} نَجْمًا يُضِيءُ سَمَاءَ الْجَزَائِرِ وَيُلْهِمُ كُلَّ طِفْلٍ صَغِيرٍ.",
    ],
    "الْبَطَلُ الْمُنْقِذُ بِبُرْنُوسٍ": [
        "كَانَ يَا مَا كَانَ، فِي قَرْيَةٍ جَزَائِرِيَّةٍ جَمِيلَةٍ، طِفْلٌ نَبِيلٌ اسْمُهُ {name}.",
        "كَانَ {name} يَرْتَدِي كُلَّ يَوْمٍ بُرْنُسَهُ الْأَبْيَضَ الْمَطْرُوزَ بِخُيُوطٍ ذَهَبِيَّةٍ بَدِيعَةٍ.",
        "وَكَانَ يَقُولُ: الْبُرْنُسُ لِبَاسُ الأَجْدَادِ، وَأَنَا فَخُورٌ بِهِ كُلَّ يَوْمٍ وَفِي كُلِّ مَكَانٍ.",
        "وَرِثَ {name} مِنْ جَدِّهِ الشَّجَاعَةَ، وَمِنْ أُمِّهِ الطَّيِّبَةِ الْحَنَانَ وَالرَّحْمَةَ الْوَاسِعَةَ.",
        "فِي يَوْمٍ مِنَ الأَيَّامِ، سَمِعَ {name} صُرَاخًا يَأْتِي مِنَ الْبُسْتَانِ الْكَبِيرِ الْمُلَاصِقِ لِلْقَرْيَةِ.",
        "رَكَضَ {name} بِسُرْعَةِ الرِّيحِ وَبُرْنُسُهُ يَرْفْرِفُ وَرَاءَهُ كَجَنَاحَيْ طَائِرٍ حُرٍّ أَبْيَضَ.",
        "وَجَدَ طِفْلًا صَغِيرًا مَحَاصَرًا بِجَانِبِ بِئْرٍ عَمِيقَةٍ وَالدُّمُوعُ تَنْهَمِرُ مِنْ عَيْنَيْهِ الْكَبِيرَتَيْنِ.",
        "مَدَّ {name} يَدَهُ لِلطِّفْلِ الصَّغِيرِ وَقَالَ بِصَوْتٍ هَادِئٍ مُطَمْئِنٍ: لَا تَخَفْ، أَنَا مَعَكَ!",
        "أَنْقَذَ {name} الطِّفْلَ بِحِكْمَةٍ وَشَجَاعَةٍ وَأَخَذَهُ بِأَمَانٍ إِلَى أَهْلِهِ الَّذِينَ كَانُوا يَبْحَثُونَ عَنْهُ.",
        "بَكَى أَبُو الطِّفْلِ مِنَ الْفَرَحِ وَقَالَ: أَنْتَ يَا {name} بَطَلٌ حَقِيقِيٌّ مِنْ أَبْطَالِ الْجَزَائِرِ!",
        "مَشَى {name} إِلَى سَاحَةِ الشُّهَدَاءِ وَبُرْنُسُهُ الأَبْيَضُ يَتَلَأْلَأُ تَحْتَ أَشِعَّةِ الشَّمْسِ الذَّهَبِيَّةِ.",
        "وَقَفَ أَمَامَ مَقَامِ الشَّهِيدِ الْعَظِيمِ وَرَفَعَ يَدَهُ تَحِيَّةً لِأَرْوَاحِ الأَبْطَالِ الْخَالِدِينَ.",
        "قَالَ بِقَلْبٍ مَلِيءٍ بِالإِيمَانِ: يَا أَجْدَادِي الشُّهَدَاءَ، أَعِدُكُمْ أَنْ أَكُونَ أَهْلًا لِتَضْحِيَاتِكُمْ!",
        "سَمِعَهُ شَيْخٌ طَاعِنٌ فِي السِّنِّ كَانَ يَجْلِسُ قُرْبَهُ فَابْتَسَمَ وَدَعَا لَهُ بِالتَّوْفِيقِ وَالنَّجَاحِ.",
        "أَعْطَاهُ الشَّيْخُ تَمِيمَةً جَزَائِرِيَّةً قَدِيمَةً وَقَالَ: هَذِهِ وِرَاثَةُ الأَجْدَادِ الأَشَاوِسِ يَا {name}!",
        "عَادَ {name} إِلَى قَرْيَتِهِ وَالأَهْلُ يَنْتَظِرُونَهُ بِالزَّغَارِيدِ وَأَلْوَانِ الْفَرَحِ الْجَزَائِرِيِّ الأَصِيلِ.",
        "بَدَأَ {name} يُعَلِّمُ أَطْفَالَ الْقَرْيَةِ أَهَمِّيَّةَ التُّرَاثِ وَالزِّيِّ الْجَزَائِرِيِّ الْأَصِيلِ الْجَمِيلِ.",
        "وَكَانَ يُخْبِرُهُمْ عَنِ الشُّهَدَاءِ الَّذِينَ ضَحَّوْا بِأَرْوَاحِهِمُ الثَّمِينَةِ لِأَجْلِ تَحْرِيرِ الْجَزَائِرِ.",
        "أَحَبَّهُ أَهْلُ الْقَرْيَةِ جَمِيعًا وَقَالُوا: {name} لَيْسَ طِفْلًا عَادِيًّا، إِنَّهُ فَخْرُنَا وَأَمَلُنَا!",
        "كَتَبَتْ عَنْهُ الصُّحُفُ الْجَزَائِرِيَّةُ وَنَشَرَتْ صُورَتَهُ بِالْبُرْنُسِ الأَبْيَضِ عَلَى صَفَحَاتِهَا الأُولَى.",
        "وَقَفَ {name} أَمَامَ طُلَّابِ مَدْرَسَتِهِ وَقَالَ: كُلُّ وَاحِدٍ مِنْكُمْ يَسْتَطِيعُ أَنْ يَكُونَ بَطَلًا!",
        "الْبُطُولَةُ لَيْسَتْ فِي الْقُوَّةِ وَحْدَهَا، بَلْ فِي حُبِّ الْوَطَنِ وَخِدْمَةِ الْجِيرَانِ وَمُسَاعَدَةِ الضُّعَفَاءِ.",
        "نَامَ {name} تِلْكَ اللَّيْلَةَ سَعِيدًا وَقَلْبُهُ مَلِيءٌ بِحُبِّ الْجَزَائِرِ وَحُبِّ الْخَيْرِ وَالْعَطَاءِ.",
        "فِي الْمَنَامِ رَأَى أَجْدَادَهُ الشُّهَدَاءَ يَبْتَسِمُونَ وَيَقُولُونَ: بَارَكَ اللَّهُ فِيكَ يَا {name}!",
        "وَمُنْذُ ذَلِكَ الْيَوْمِ أَصْبَحَ {name} حَارِسًا لِلذَّاكِرَةِ وَمَشْعَلَ أَمَلٍ لِكُلِّ أَطْفَالِ الْجَزَائِرِ.",
    ],
    "الْأَمِيرَةُ الْجَمِيلَةُ بِالْكَارَاكُو": [
        "كَانَ يَا مَا كَانَ، فِي بَلَدٍ جَمِيلٍ اسْمُهُ الْجَزَائِرُ، أَمِيرَةٌ صَغِيرَةٌ اسْمُهَا {name}.",
        "كَانَتْ {name} تَرْتَدِي كُلَّ يَوْمٍ كَارَاكُوهَا الْأَزْرَقَ الْمُطَرَّزَ بِخُيُوطٍ ذَهَبِيَّةٍ رَائِعَةٍ.",
        "وَكَانَتْ تَضَعُ عَلَى عُنُقِهَا خَيْطَ الرُّوحِ الأَصِيلَ وَعَلَى رَأْسِهَا تَاجًا مِنَ الزُّهُورِ الْبِيضِ.",
        "كَانَتْ تَسْكُنُ فِي قَصْرٍ مُزَخْرَفٍ بِالزَّلِيجِ الأَزْرَقِ وَالأَقْوَاسِ الأَرَبِسْكِيَّةِ الرَّائِعَةِ.",
        "أَحَبَّتِ {name} شَعْبَهَا مِنْ كُلِّ قَلْبِهَا وَكَانَتْ تَزُورُ الْفُقَرَاءَ وَتَمُدُّ لَهُمْ يَدَ الْعَوْنِ.",
        "فِي يَوْمٍ رَبِيعِيٍّ جَمِيلٍ، خَرَجَتْ {name} مِنَ الْقَصْرِ تَحْمِلُ سَلَّةً مَلِيئَةً بِالْهَدَايَا وَالطَّعَامِ.",
        "مَشَتْ بَيْنَ أَزِقَّةِ الْمَدِينَةِ الْقَدِيمَةِ وَوَزَّعَتِ الْوُرُودَ وَالِابْتِسَامَاتِ عَلَى كُلِّ مَنْ لَقِيَتْهُ.",
        "فَجَأَةً، سَمِعَتْ {name} صَوْتَ طِفْلَةٍ صَغِيرَةٍ تَبْكِي فِي زَاوِيَةٍ مُظْلِمَةٍ مِنَ الشَّارِعِ.",
        "اقْتَرَبَتِ {name} وَوَجَدَتِ الطِّفْلَةَ ضَائِعَةً خَائِفَةً فَأَخَذَتْهَا بِحَنَانٍ وَطَمْأَنَتْهَا بِكَلِمَاتٍ دَافِئَةٍ.",
        "أَرْشَدَتْهَا {name} إِلَى أَهْلِهَا وَالطِّفْلَةُ تَمْسَحُ دُمُوعَهَا وَتَبْتَسِمُ مِنَ الْفَرَحِ وَالأَمَانِ.",
        "لَكِنَّ يَوْمًا مِنَ الأَيَّامِ، قَدِمَتْ سَاحِرَةٌ شِرِّيرَةٌ تُرِيدُ أَنْ تَسْرِقَ بَهْجَةَ الْقَرْيَةِ.",
        "وَقَفَتِ {name} أَمَامَهَا بِثَبَاتٍ وَشَجَاعَةٍ وَقَالَتْ: لَنْ تَصِلِي إِلَى أَطْفَالِ بَلَدِي!",
        "قَالَتِ السَّاحِرَةُ: مَنْ أَنْتِ؟ فَرَدَّتْ {name}: أَنَا ابْنَةُ هَذِهِ الأَرْضِ الطَّيِّبَةِ الْجَزَائِرِيَّةِ!",
        "أَضَاءَ نُورٌ ذَهَبِيٌّ مِنْ خَيْطِ الرُّوحِ الَّذِي تَرْتَدِيهِ {name} وَأَحَاطَ بِهَا كَدِرْعٍ مِنَ الضَّوْءِ.",
        "ارْتَعَدَتِ السَّاحِرَةُ الشِّرِّيرَةُ خَوْفًا مِنْ نُورِ قَلْبِ الأَمِيرَةِ الطَّاهِرِ الصَّادِقِ الْجَمِيلِ.",
        "وَهَرَبَتِ السَّاحِرَةُ بَعِيدًا وَلَمْ تَعُدْ إِلَى أَرْضِ الْجَزَائِرِ الطَّيِّبَةِ إِلَى الأَبَدِ.",
        "احْتَفَلَ أَهْلُ الْقَرْيَةِ بِأَمِيرَتِهِمُ الشُّجَاعَةِ وَرَقَصُوا بِالأَهَازِيجِ الْجَزَائِرِيَّةِ الأَصِيلَةِ.",
        "قَدَّمَتْ لَهَا النِّسَاءُ قُفْطَانًا مُطَرَّزًا جَدِيدًا وَقُلْنَ: أَنْتِ مُزَيَّنَةٌ بِكَرَمِ جَزَائِرِنَا يَا {name}!",
        "جَلَسَتْ {name} وَسَطَ الأَطْفَالِ وَحَكَتْ لَهُمْ قِصَصَ الأَجْدَادِ وَتَارِيخَ الزِّيِّ الْجَزَائِرِيِّ.",
        "وَعَلَّمَتِ الْبَنَاتِ الصَّغِيرَاتِ طَرِيقَةَ التَّطْرِيزِ الْجَزَائِرِيِّ الأَصِيلِ بِيَدَيْهَا الرَّقِيقَتَيْنِ.",
        "قَالَتْ {name}: جَمَالُنَا فِي تُرَاثِنَا وَأَصَالَتِنَا وَفِي حُبِّنَا لِأَرْضِنَا الْجَزَائِرِيَّةِ الطَّيِّبَةِ!",
        "نَامَتْ {name} تِلْكَ اللَّيْلَةَ وَعَيْنَاهَا تَبْتَسِمَانِ وَقَلْبُهَا مَلِيءٌ بِالسَّعَادَةِ وَالسَّلَامِ.",
        "فِي الصَّبَاحِ، وَجَدَتْ أَمَامَ بَابِهَا بَاقَةَ وُرُودٍ مِنَ الأَطْفَالِ شُكْرًا لَهَا عَلَى شَجَاعَتِهَا.",
        "عَرَفَتْ {name} أَنَّ الأَمِيرَةَ الْحَقِيقِيَّةَ هِيَ مَنْ تُحِبُّ شَعْبَهَا وَتَخْدُمُهُ بِإِخْلَاصٍ وَوَفَاءٍ.",
        "وَمُنْذُ ذَلِكَ الْيَوْمِ أَصْبَحَتْ {name} قُدْوَةً لِكُلِّ بَنَاتِ الْجَزَائِرِ وَرَمْزًا لِلْجَمَالِ وَالشَّجَاعَةِ.",
    ],
    "الطَّيَّارُ الشُّجَاعُ": [
        "كَانَ يَا مَا كَانَ، فِي مَدِينَةٍ جَزَائِرِيَّةٍ تُطِلُّ عَلَى الْبَحْرِ، طِفْلٌ يُحِبُّ السَّمَاءَ اسْمُهُ {name}.",
        "كَانَ {name} يَنْظُرُ إِلَى الطَّائِرَاتِ الَّتِي تَمُرُّ فَوْقَ بَيْتِهِ وَيَقُولُ: سَأَطِيرُ يَوْمًا مِثْلَهَا!",
        "دَرَسَ {name} بِجِدٍّ وَمُثَابَرَةٍ حَتَّى أَصْبَحَ أَذْكَى طُلَّابِ فَصْلِهِ فِي عُلُومِ الطَّيَرَانِ.",
        "فِي يَوْمٍ مُشْرِقٍ، مَنَحَهُ أَبُوهُ جَاكِيتَ الطَّيَرَانِ الْبُنِّيَّ اللَّامِعَ وَعَلَيْهِ عَلَمُ الْجَزَائِرِ الشَّامِخُ.",
        "ارْتَدَاهُ {name} بِفَخْرٍ وَاصْطَحَبَهُ أَبُوهُ إِلَى مَطَارِ الْجَزَائِرِ لِأَوَّلِ رِحْلَةٍ فِي حَيَاتِهِ.",
        "صَعِدَ {name} إِلَى قِمْرَةِ الْقِيَادَةِ وَعَيْنَاهُ تَلْمَعَانِ كَالنُّجُومِ مِنَ الدَّهْشَةِ وَالإِثَارَةِ.",
        "أَقْلَعَتِ الطَّائِرَةُ وَرُسِمَ عَلَى ذَيْلِهَا عَلَمُ الْجَزَائِرِ بِأَلْوَانِهِ الأَخْضَرِ وَالأَبْيَضِ الزَّاهِيَةِ.",
        "حَلَّقَ {name} فَوْقَ السُّحُبِ الْبَيْضَاءِ وَرَأَى الْجَزَائِرَ مِنَ الأَعْلَى كَلَوْحَةٍ فَنِّيَّةٍ رَائِعَةٍ.",
        "مَرَّ فَوْقَ جِبَالِ الأَطْلَسِ الشَّامِخَةِ الْمُكَسَّاةِ بِالثَّلْجِ الأَبْيَضِ كَالْقُطْنِ النَّاعِمِ.",
        "وَرَأَى الأَوْدِيَةَ الْخَضْرَاءَ تَمْتَدُّ كَبِسَاطٍ سِحْرِيٍّ مَنْسُوجٍ بِأَيْدِي النِّسَاءِ الْجَزَائِرِيَّاتِ.",
        "حَلَّقَ فَوْقَ الصَّحْرَاءِ الذَّهَبِيَّةِ وَرَأَى الْكُثُبَانَ الرَّمْلِيَّةَ تَتَمَوَّجُ كَأَمْوَاجِ الْبَحْرِ الهَادِئِ.",
        "رَأَى مِنَ الأَعْلَى مَدِينَةَ وَهْرَانَ الْجَمِيلَةَ وَالْجَزَائِرَ الْعَاصِمَةَ تَسْتَحِمُّ فِي نُورِ الشَّمْسِ.",
        "وَفَجْأَةً نَظَرَ {name} إِلَى الرَّادَارِ وَرَأَى عَاصِفَةً قَادِمَةً وَطَائِرَةُ رَكَّابٍ عَلَيْهَا خَطَرٌ.",
        "أَسْرَعَ {name} وَأَرْسَلَ رِسَالَةَ تَحْذِيرٍ إِلَى الطَّائِرَةِ وَأَرْشَدَهَا إِلَى طَرِيقٍ أَكْثَرَ أَمَانًا.",
        "هَبَطَتِ الطَّائِرَةُ بِسَلَامَةٍ وَالرَّكَّابُ يَشْكُرُونَ الطَّيَّارَ الصَّغِيرَ الشُّجَاعَ {name} مِنْ قُلُوبِهِمْ.",
        "كَافَأَهُ الْمَطَارُ بِمِيدَالِيَّةِ الشَّجَاعَةِ وَقَالَ الْمُدِيرُ: أَنْتَ فَخْرُ الطَّيَرَانِ الْجَزَائِرِيِّ يَا {name}!",
        "وَكَتَبَتِ الصُّحُفُ عَنِ الطَّيَّارِ الصَّغِيرِ الشُّجَاعِ الَّذِي أَنْقَذَ الأَرْوَاحَ بِذَكَائِهِ وَشَجَاعَتِهِ.",
        "قَالَ {name} لِلصُّحُفِيِّينَ: تَعَلَّمْتُ مِنَ الْجَزَائِرِ أَنَّ الشَّجَاعَةَ وَاجِبٌ لَا خِيَارٌ!",
        "رَجَعَ {name} إِلَى بَيْتِهِ وَأُمُّهُ وَأَبُوهُ يَحْتَضِنَانِهِ بِالدُّمُوعِ وَالأَدْعِيَةِ الطَّيِّبَةِ.",
        "جَلَسَ {name} مَعَ أَصْدِقَائِهِ وَحَكَى لَهُمْ عَنْ جَمَالِ الْجَزَائِرِ كَمَا رَآهَا مِنَ السَّمَاءِ.",
        "قَالَ لَهُمْ: رَأَيْتُ الْجَزَائِرَ مِنَ الأَعْلَى فَعَرَفْتُ لِمَاذَا يُحِبُّهَا كُلُّ جَزَائِرِيٍّ بِكُلِّ جَوَارِحِهِ!",
        "عَزَمَ {name} أَنْ يُعَلِّمَ أَطْفَالَ الْجَزَائِرِ فُنُونَ الطَّيَرَانِ لِيَكُونُوا طَيَّارِينَ عُظَمَاءَ.",
        "وَوَعَدَ نَفْسَهُ أَنْ يَحْمِلَ عَلَمَ الْجَزَائِرِ فِي كُلِّ سَمَاوَاتِ الدُّنْيَا الأَرْبَعِ الْجَمِيلَةِ.",
        "عَرَفَ {name} أَنَّ السَّمَاءَ لَيْسَتْ حَدًّا لِلأَحْلَامِ، بَلْ هِيَ بِدَايَةُ طَرِيقٍ طَوِيلٍ نَحْوَ الْعَظَمَةِ.",
        "وَمُنْذُ ذَلِكَ الْيَوْمِ أَصْبَحَ {name} رَمْزًا لِطُمُوحِ كُلِّ طِفْلٍ جَزَائِرِيٍّ يَحْلُمُ بِالسَّمَاءِ.",
    ],
    "الْمُخْتَرِعُ الصَّغِيرُ": [
        "كَانَ يَا مَا كَانَ، فِي حَيٍّ جَزَائِرِيٍّ هَادِئٍ، طِفْلٌ لَا يَمَلُّ مِنَ الأَسْئِلَةِ اسْمُهُ {name}.",
        "كَانَ {name} يُفَكِّكُ الأَشْيَاءَ لِيَفْهَمَ كَيْفَ تَعْمَلُ، وَيُرَكِّبُهَا مَرَّةً أُخْرَى بِإِبْدَاعٍ جَدِيدٍ.",
        "كَانَ مَخْتَبَرُهُ الصَّغِيرُ مَلِيئًا بِالأَنَابِيبِ وَالأَدَوَاتِ وَالرُّسُومَاتِ وَالأَفْكَارِ الْمُلَوَّنَةِ.",
        "وَكَانَتْ جُدْرَانُ مَخْتَبَرِهِ مُزَيَّنَةً بِنُقُوشِ الزَّلِيجِ الْجَزَائِرِيِّ الأَصِيلِ مِنْ رَسْمِ يَدَيْهِ.",
        "فِي يَوْمٍ مِنَ الأَيَّامِ، خَرَجَ {name} إِلَى الشَّارِعِ وَرَأَى جَدَّتَهُ تَحْمِلُ أَكْيَاسًا ثَقِيلَةً.",
        "فَكَّرَ {name}: يَجِبُ أَنْ أَخْتَرِعَ شَيْئًا يُسَاعِدُ جَدَّتِي وَكُلَّ الْجَدَّاتِ فِي حَيِّنَا الْجَمِيلِ!",
        "عَادَ إِلَى مَخْتَبَرِهِ وَجَلَسَ يُفَكِّرُ وَيَرْسُمُ لِسَاعَاتٍ طَوِيلَةٍ حَتَّى ظَهَرَتِ الأَفْكَارُ الرَّائِعَةُ.",
        "بَدَأَ {name} يَخْلِطُ الأَلْوَانَ فِي أَنَابِيبِهِ الزُّجَاجِيَّةِ: أَحْمَرُ كَشَفَقِ الْجَزَائِرِ وَأَخْضَرُ كَحَدَائِقِهَا.",
        "وَأَزْرَقُ كَأَمْوَاجِ الْبَحْرِ الأَبْيَضِ الْمُتَوَسِّطِ الَّذِي تَحْتَضِنُهُ شَوَاطِئُ الْجَزَائِرِ الْجَمِيلَةِ.",
        "فَجَأَةً! لَمَعَ ضَوْءٌ سَاطِعٌ فِي الْمَخْتَبَرِ وَاخْتَرَعَ {name} عَرَبَةً صَغِيرَةً تَعْمَلُ بِالطَّاقَةِ الشَّمْسِيَّةِ!",
        "جَرَّبَ {name} الْعَرَبَةَ الصَّغِيرَةَ مَعَ جَدَّتِهِ فَحَمَلَتِ الأَكْيَاسَ الثَّقِيلَةَ بِسُهُولَةٍ وَخِفَّةٍ.",
        "فَرِحَتِ الْجَدَّةُ وَضَمَّتْ {name} إِلَى صَدْرِهَا وَقَالَتْ: أَنْتَ عَقْلٌ كَبِيرٌ فِي جِسْمٍ صَغِيرٍ!",
        "عَرَفَ أَهْلُ الْحَيِّ بِاخْتِرَاعِ {name} فَجَاؤُوا جَمِيعًا لِيَرَوْا الْعَرَبَةَ الشَّمْسِيَّةَ الرَّائِعَةَ.",
        "أَرْسَلَ {name} اخْتِرَاعَهُ إِلَى مُسَابَقَةٍ وَطَنِيَّةٍ وَانْتَظَرَ النَّتِيجَةَ بِقَلْبٍ يَنْبِضُ بِالأَمَلِ.",
        "جَاءَ الْخَبَرُ: فَازَ {name} بِالْجَائِزَةِ الأُولَى فِي مُسَابَقَةِ الِاخْتِرَاعَاتِ الصَّغِيرَةِ لِلْجَزَائِرِ!",
        "تَوَجَّهَ {name} إِلَى الْعَاصِمَةِ وَعَلَى صَدْرِهِ مِيدَالِيَّةٌ ذَهَبِيَّةٌ تَلْمَعُ بِنُورِ الشَّمْسِ الْجَزَائِرِيَّةِ.",
        "قَالَ لَهُ الْوَزِيرُ: بَارَكَ اللَّهُ فِيكَ يَا {name}، اخْتِرَاعُكَ سَيُغَيِّرُ حَيَاةَ كَثِيرٍ مِنَ النَّاسِ!",
        "عَادَ {name} إِلَى حَيِّهِ وَالأَهْلُ يَسْتَقْبِلُونَهُ بِالزَّغَارِيدِ وَالأَعْلَامِ الْجَزَائِرِيَّةِ الْخَفَّاقَةِ.",
        "وَقَفَ {name} أَمَامَ أَطْفَالِ الْحَيِّ وَقَالَ: الِاخْتِرَاعُ لَيْسَ صَعْبًا، كُلُّكُمْ تَسْتَطِيعُونَ ذَلِكَ!",
        "انْظُرُوا إِلَى الْمُشْكِلَاتِ مِنْ حَوْلِكُمْ وَفَكِّرُوا كَيْفَ تَحُلُّونَهَا بِالْعِلْمِ وَالإِبْدَاعِ وَالصَّبْرِ.",
        "بَدَأَ {name} يُعَلِّمُ أَطْفَالَ الْحَيِّ فِي نَادٍ صَغِيرٍ كَيْفَ يَبْنُونَ الأَشْيَاءَ بِأَيْدِيهِمُ الصَّغِيرَةِ.",
        "وَكَانَ يَقُولُ لَهُمْ: الْجَزَائِرُ تَحْتَاجُكُمْ مُخْتَرِعِينَ وَعُلَمَاءَ لِبِنَاءِ مُسْتَقْبَلِهَا الزَّاهِرِ!",
        "نَامَ {name} كُلَّ لَيْلَةٍ وَفِي رَأْسِهِ أَفْكَارٌ جَدِيدَةٌ لِاخْتِرَاعَاتٍ أُخْرَى تُفِيدُ الْجَزَائِرَ.",
        "عَرَفَ {name} أَنَّ الْعِلْمَ نُورٌ لَا يَنْطَفِئُ وَأَنَّ عَقْلَ الطِّفْلِ الْجَزَائِرِيِّ كَنْزٌ لَا يُقَدَّرُ.",
        "وَمُنْذُ ذَلِكَ الْيَوْمِ أَصْبَحَ {name} مُلْهِمًا لِكُلِّ مُخْتَرِعٍ صَغِيرٍ فِي رُبُوعِ الْجَزَائِرِ الْحَبِيبَةِ.",
    ],
}


@st.cache_data
def load_image_b64(path: str) -> str:
    abs_path = os.path.join(os.path.dirname(__file__), path)
    with open(abs_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def fetch_image_b64(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=25)
        return base64.b64encode(r.content).decode("utf-8")
    except Exception:
        return None


def render_book_mockup(img_url: str, child_name: str, theme_key: str) -> str:
    """Realistic 3D open book mockup — self-contained HTML rendered via components.html().
    LEFT page = story text printed on paper. RIGHT page = full-bleed AI image."""
    theme = THEMES[theme_key]
    story_lines = theme["story"]
    display_name = child_name.strip() if child_name and child_name.strip() else "طفلك"

    lines_html = ""
    for line in story_lines:
        rendered = line.replace("{name}", f'<strong class="name-hl">{display_name}</strong>')
        lines_html += f'<div class="sline">{rendered}</div>'

    return f"""<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Scheherazade+New:wght@400;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
    font-family: 'Cairo', sans-serif;
    background: transparent;
    width: 100%;
    min-height: 100%;
    overflow-x: hidden;
}}

/* ─── Outer scene ─── */
.scene {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 10px 12px;
    perspective: 2000px;
}}

/* ─── Stacked page edges (behind the book) ─── */
.pages-under {{
    width: min(820px, 96%);
    position: relative;
    margin-bottom: -6px;
    z-index: 0;
}}
.pu {{
    height: 7px;
    border-radius: 0 0 4px 4px;
    margin: 0 auto;
}}
.pu1 {{ background: #E8E2D6; width: 98%; }}
.pu2 {{ background: #DDD7CB; width: 95%; margin-top: 2px; }}
.pu3 {{ background: #D2CCBf; width: 92%; margin-top: 2px; }}

/* ─── The Open Book ─── */
.book {{
    display: flex;
    width: min(820px, 96%);
    min-height: 440px;
    position: relative;
    z-index: 1;
    transform: perspective(2000px) rotateX(3deg);
    transform-origin: center bottom;
    filter: drop-shadow(0 32px 48px rgba(0,0,0,0.28))
            drop-shadow(0 6px 12px rgba(0,0,0,0.18));
}}

/* ─── LEFT page — Story text ─── */
.page-left {{
    flex: 1 1 48%;
    position: relative;
    overflow: hidden;
    border-radius: 3px 0 0 3px;

    /* Warm cream paper */
    background:
        /* Ruled-line simulation */
        repeating-linear-gradient(
            to bottom,
            transparent 0px,
            transparent 27px,
            rgba(180,160,200,0.13) 27px,
            rgba(180,160,200,0.13) 28px
        ),
        /* Paper warmth gradient */
        linear-gradient(175deg, #FFFDF4 0%, #FFF8E6 40%, #FFFAF0 100%);
}}

/* Left spine shadow (where left page meets centre) */
.page-left::after {{
    content: '';
    position: absolute;
    top: 0; right: 0; bottom: 0;
    width: 28px;
    background: linear-gradient(to right,
        transparent 0%,
        rgba(80,40,120,0.06) 60%,
        rgba(60,20,100,0.18) 100%
    );
    pointer-events: none;
    z-index: 3;
}}

.page-left-inner {{
    padding: clamp(1rem, 3vw, 1.8rem) clamp(0.8rem, 2.5vw, 1.5rem) 1rem;
    display: flex;
    flex-direction: column;
    height: 100%;
    direction: rtl;
    position: relative;
    z-index: 2;
}}

/* Decorative ornament at top */
.ornament {{
    text-align: center;
    font-size: clamp(0.8rem, 2vw, 1.1rem);
    color: rgba(155,89,182,0.55);
    margin-bottom: clamp(0.4rem, 1.5vw, 0.8rem);
    letter-spacing: 4px;
    font-family: 'Scheherazade New', serif;
}}

/* Story title — printed directly on paper */
.story-title {{
    font-size: clamp(0.88rem, 2.2vw, 1.15rem);
    font-weight: 900;
    color: #4A2E7A;
    margin-bottom: clamp(0.5rem, 1.8vw, 0.9rem);
    line-height: 1.4;
    text-align: center;
    /* No background, no box — printed on paper */
}}

/* Decorative divider under title */
.divider {{
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: clamp(0.5rem, 1.8vw, 0.85rem);
}}
.divider-line {{
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(155,89,182,0.4), transparent);
}}
.divider-gem {{
    color: rgba(155,89,182,0.6);
    font-size: 0.7rem;
}}

/* Story text lines — directly on the paper */
.slines {{
    position: relative;
    flex: 1;
    overflow: hidden;
}}
.sline {{
    font-size: clamp(0.74rem, 1.7vw, 0.92rem);
    font-weight: 600;
    color: #2C1A4A;
    line-height: 2.15;
    padding: 0 0.1rem;
    /* no border, no background — ink on paper feel */
}}
.sline:first-child {{
    font-weight: 800;
    color: #4A2E7A;
    font-size: clamp(0.76rem, 1.75vw, 0.94rem);
}}
.name-hl {{ color: #8B35C8; }}

/* Fade-out + paywall area */
.story-fade {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: clamp(60px, 18%, 90px);
    background: linear-gradient(to bottom,
        transparent 0%,
        rgba(255,252,238,0.85) 55%,
        #FFFAEB 100%
    );
    pointer-events: none;
}}

/* Paywall — inked on paper, no box border */
.paywall {{
    flex-shrink: 0;
    margin-top: 0.5rem;
    text-align: center;
    padding: clamp(0.6rem, 1.5vw, 0.85rem) 0.5rem;
    /* Subtle paper stamp look */
    border-top: 1.5px dashed rgba(155,89,182,0.35);
    border-bottom: 1.5px dashed rgba(155,89,182,0.35);
}}
.paywall-icon {{ font-size: clamp(1rem, 2.5vw, 1.3rem); margin-bottom: 0.15rem; }}
.paywall p {{
    font-size: clamp(0.62rem, 1.3vw, 0.78rem);
    font-weight: 700;
    color: #7B3FA6;
    line-height: 1.7;
    margin: 0;
}}

/* Page number */
.pgnum {{
    position: absolute;
    bottom: 0.4rem;
    right: 0.6rem;
    font-size: 0.62rem;
    color: rgba(120,80,160,0.45);
    font-weight: 700;
    font-family: 'Scheherazade New', serif;
}}

/* ─── SPINE / GUTTER ─── */
.spine {{
    width: clamp(14px, 2.5vw, 22px);
    flex-shrink: 0;
    position: relative;
    z-index: 4;
    background:
        linear-gradient(to right,
            rgba(60,20,100,0.22) 0%,
            rgba(120,80,180,0.10) 25%,
            rgba(255,255,255,0.18) 50%,
            rgba(120,80,180,0.10) 75%,
            rgba(60,20,100,0.24) 100%
        );
    /* Spine top/bottom caps */
    box-shadow: 0 0 8px rgba(0,0,0,0.12);
}}

/* ─── RIGHT page — Full-bleed image ─── */
.page-right {{
    flex: 1 1 48%;
    position: relative;
    overflow: hidden;
    border-radius: 0 3px 3px 0;
    background: #1a0a2e;
}}

/* Right spine shadow (where right page meets centre) */
.page-right::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 28px;
    background: linear-gradient(to left,
        transparent 0%,
        rgba(80,40,120,0.06) 60%,
        rgba(60,20,100,0.20) 100%
    );
    pointer-events: none;
    z-index: 3;
}}

/* Page curl top-right corner */
.page-right::after {{
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 0; height: 0;
    border-style: solid;
    border-width: 0 28px 28px 0;
    border-color: transparent rgba(200,168,255,0.25) transparent transparent;
    z-index: 4;
    filter: drop-shadow(-2px 2px 3px rgba(0,0,0,0.15));
}}

.page-right img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    position: absolute;
    top: 0; left: 0;
}}

/* "Page 3" watermark on image page */
.pgnum-right {{
    position: absolute;
    bottom: 0.4rem;
    left: 0.6rem;
    font-size: 0.62rem;
    color: rgba(255,255,255,0.5);
    font-weight: 700;
    font-family: 'Scheherazade New', serif;
    z-index: 5;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}}

/* ─── MOBILE: stack vertically ─── */
@media (max-width: 520px) {{
    .book {{
        flex-direction: column-reverse;  /* image first (top), story below */
        transform: none;
        min-height: auto;
    }}
    .page-left  {{ border-radius: 0 0 3px 3px; min-height: 300px; }}
    .page-right {{ border-radius: 3px 3px 0 0; min-height: 260px; }}
    .page-right img {{ position: relative; height: 260px; object-fit: cover; }}
    .page-right::after {{ display: none; }}
    .page-left::after {{ display: none; }}
    .spine {{
        width: 100%;
        height: clamp(12px, 2vh, 18px);
        background: linear-gradient(to bottom,
            rgba(60,20,100,0.2) 0%,
            rgba(255,255,255,0.15) 50%,
            rgba(60,20,100,0.22) 100%
        );
    }}
    .pages-under {{ display: none; }}
    .scene {{ padding: 10px 6px 8px; }}
}}
</style>
</head>
<body>
<div class="scene">

  <!-- Stacked page edges beneath the book -->
  <div class="pages-under">
    <div class="pu pu1"></div>
    <div class="pu pu2"></div>
    <div class="pu pu3"></div>
  </div>

  <!-- The open book -->
  <div class="book">

    <!-- LEFT PAGE: story text, printed on warm paper -->
    <div class="page-left">
      <div class="page-left-inner">

        <div class="ornament">✦ ✦ ✦</div>

<div class="story-title">{'بطلة' if 'الأميرة' in theme_key else 'بطل'} من قلب الجزائر</div>
<div class="divider">
          <div class="divider-line"></div>
          <div class="divider-gem">◆</div>
          <div class="divider-line"></div>
        </div>

        <div class="slines">
          {lines_html}
          <div class="story-fade"></div>
        </div>

        <div class="paywall">
          <div class="paywall-icon">🔒 📖</div>
          <p>
            <strong>لإكمال بقية القصة المخصصة لطفلك،</strong><br>
            يرجى إتمام الطلب للطباعة الفاخرة
          </p>
        </div>

      </div>
      <span class="pgnum">٢</span>
    </div>

    <!-- SPINE gutter -->
    <div class="spine"></div>

    <!-- RIGHT PAGE: full-bleed AI image -->
    <div class="page-right">
      <img src="{img_url}"
           alt="صورة طفلك السحرية"
           loading="eager"
           onerror="this.style.display='none'" />
      <span class="pgnum-right">٣</span>
    </div>

  </div>
</div>
</body>
</html>"""


def generate_image(uploaded_image_bytes: bytes, theme_key: str) -> str | None:
    theme = THEMES[theme_key]

    costume = theme["costume"].replace("{flag}", FLAG_DESC)
    landmark = theme["landmark"].replace("{flag}", FLAG_DESC)

    prompt = (
        f"3D Pixar Disney cinematic illustration, vibrant colors, 8K resolution. "
        f"FLAG REQUIREMENT — strictly show {FLAG_DESC} "
        f"(NOT Mexico, NOT eagle, NOT coat of arms, ONLY Algerian flag). "
        f"Character: {costume} "
        f"Background scene: {landmark} "
        f"Style: Pixar/Disney 3D render, cinematic dramatic lighting, "
        f"vibrant saturated colors, highly detailed, masterpiece quality."
    )

    negative_prompt = (
        "Mexico, Mexican flag, eagle, coat of arms, crest, shield, "
        "eagle emblem, wrong flag, blue flag, red flag, tri-color flag, "
        "French flag, Italian flag, flag without crescent, flag without star, "
        "bad anatomy, blurry, low quality, watermark, signature, deformed face, extra limbs"
    )

    try:
        client = replicate.Client(api_token=os.environ.get("REPLICATE_API_TOKEN"))

        img_buffer = io.BytesIO(uploaded_image_bytes)
        uploaded_file = client.files.create(img_buffer, filename="child_face.jpg")
        if hasattr(uploaded_file, "urls") and isinstance(uploaded_file.urls, dict):
            face_url = uploaded_file.urls.get("get", "")
        else:
            face_url = str(uploaded_file.urls)

        if not face_url:
            st.error("❌ فشل رفع الصورة. حاول مرة أخرى.")
            return None

        output = client.run(
            "bytedance/flux-pulid:8baa7ef2255075b46f4d91cd238c21d31181b3e6a864463f967960bb0112525b",
            input={
                "main_face_image": face_url,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "id_weight": 0.9,
                "guidance_scale": 5.5,
                "num_steps": 20,
                "true_cfg": 1,
                "width": 896,
                "height": 1152,
                "num_outputs": 1,
                "output_format": "webp",
                "output_quality": 90,
                "start_step": 0,
                "max_sequence_length": 512,
            }
        )

        if output:
            result = output[0] if isinstance(output, list) else output
            if hasattr(result, "url"):
                return result.url() if callable(result.url) else result.url
            return str(result)
        return None

    except replicate.exceptions.ModelError as e:
        err = str(e)
        if "align face fail" in err or "no face" in err.lower():
            st.error("❌ لم يتعرّف النظام على الوجه. يرجى رفع صورة أمامية واضحة للوجه بإضاءة جيدة.")
        else:
            st.error(f"❌ خطأ في التوليد: {err}")
        return None
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")
        return None


def make_watermarked_preview(image_url: str) -> bytes | None:
    """Download AI image, add diagonal watermark + bottom banner, return JPEG bytes.

    The high-res Replicate URL is never sent to the browser — only this
    watermarked downscaled preview. Page-source inspection won't reveal the
    original AI image URL."""
    try:
        from PIL import ImageDraw, ImageFont

        r = requests.get(image_url, timeout=30)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert('RGBA')

        # Downscale to a small preview to save bandwidth and discourage misuse
        max_w = 720
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize(
                (max_w, int(img.height * ratio)),
                Image.Resampling.LANCZOS
            )

        font_path = os.path.join(os.path.dirname(__file__), 'Amiri-Bold.ttf')
        try:
            font_main = ImageFont.truetype(font_path, size=int(img.width * 0.06))
            font_band = ImageFont.truetype(font_path, size=20)
        except Exception:
            font_main = ImageFont.load_default()
            font_band = ImageFont.load_default()

        # Build a tile-able rotated watermark canvas (oversized so rotation doesn't crop)
        diag = int((img.width ** 2 + img.height ** 2) ** 0.5) + 80
        wm_canvas = Image.new('RGBA', (diag, diag), (0, 0, 0, 0))
        wd = ImageDraw.Draw(wm_canvas)

        watermark_text = "PREVIEW  •  ATHAR  •  PREVIEW  •  ATHAR"
        spacing_y = max(1, int(img.width * 0.18))
        for i, y in enumerate(range(0, diag, spacing_y)):
            offset_x = (i % 2) * int(img.width * 0.18)
            wd.text((-offset_x, y), watermark_text, font=font_main,
                    fill=(155, 89, 182, 110))

        rotated = wm_canvas.rotate(28, resample=Image.BICUBIC, expand=False)
        ox = (rotated.width - img.width) // 2
        oy = (rotated.height - img.height) // 2
        cropped = rotated.crop((ox, oy, ox + img.width, oy + img.height))

        composed = Image.alpha_composite(img, cropped)

        # Branded bottom banner
        banner_h = 38
        banner = Image.new('RGBA', (img.width, banner_h), (123, 63, 166, 230))
        bd = ImageDraw.Draw(banner)
        try:
            from arabic_reshaper import reshape
            from bidi.algorithm import get_display
            banner_text = get_display(reshape("✦  معاينة • أَثَر  ✦"))
        except Exception:
            banner_text = "✦  PREVIEW • ATHAR  ✦"
        try:
            tw = bd.textlength(banner_text, font=font_band)
        except Exception:
            tw = len(banner_text) * 8
        bd.text(((img.width - tw) / 2, 8), banner_text,
                fill=(255, 255, 255, 255), font=font_band)
        composed.alpha_composite(banner, (0, img.height - banner_h))

        out = io.BytesIO()
        composed.convert('RGB').save(out, format='JPEG', quality=80, optimize=True)
        return out.getvalue()
    except Exception:
        return None


# Note: the legacy build_whatsapp_message() below is intentionally kept as a
# helper for future reuse but is NOT called in the current order flow — the
# Step-5 confirmation builds its own minimal message (child name + order ID).
def build_whatsapp_message(name: str, phone: str, wilaya: str, address: str,
                            theme: str, items: list, total: int,
                            img_url: str | None, has_pdf: bool) -> str:
    items_block = "\n".join([f"   • {it}" for it in items])
    msg = (
        f"🌟 *طلب جديد - أَثَر* 🌟\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👶 *اسم الطفل:* {name}\n"
        f"📞 *رقم الهاتف:* {phone}\n"
        f"📍 *الولاية:* {wilaya}\n"
        f"🏠 *العنوان:* {address}\n"
        f"🎨 *الثيمة المختارة:* {theme}\n\n"
        f"🛍️ *المنتجات المطلوبة:*\n{items_block}\n\n"
        f"💰 *المبلغ الإجمالي:* {total:,} دج\n"
    )
    if img_url:
        msg += f"\n🖼️ *رابط الصورة المولّدة:*\n{img_url}\n"
    if has_pdf:
        msg += "\n📕 *كتاب القصة (PDF):* تم تحضير الكتاب الكامل — سيُرسل مع تأكيد الطلب\n"
    msg += "\n━━━━━━━━━━━━━━━\n✨ شكراً لاختياركم *أَثَر*!\nسيتم التواصل معكم قريباً 💜"
    return msg


# ═══════════════════════ PDF GENERATION ═══════════════════════

ARABIC_NUMS = {'0':'٠','1':'١','2':'٢','3':'٣','4':'٤','5':'٥','6':'٦','7':'٧','8':'٨','9':'٩'}

def to_arabic_num(n) -> str:
    return ''.join(ARABIC_NUMS.get(c, c) for c in str(n))

_PDF_FONTS_REGISTERED = False

def _register_pdf_fonts():
    global _PDF_FONTS_REGISTERED
    if _PDF_FONTS_REGISTERED:
        return
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    base = os.path.dirname(__file__)
    pdfmetrics.registerFont(TTFont('Amiri',     os.path.join(base, 'fonts/Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('AmiriBold', os.path.join(base, 'fonts/Amiri-Bold.ttf')))
    _PDF_FONTS_REGISTERED = True


def _ar(text: str) -> str:
    """Reshape Arabic text for proper PDF rendering (ligatures + RTL)."""
    import arabic_reshaper
    from bidi.algorithm import get_display
    return get_display(arabic_reshaper.reshape(text))


def _draw_spread_page(c, W, H, *, image_reader, story_lines, page_num):
    """Render one landscape spread page: full-bleed image (cover-fill) + bottom text band.

    The image is scaled to cover the entire W×H spread (CSS cover behaviour —
    portrait AI images are centre-cropped to fill the wider landscape canvas).
    Arabic story text is placed inside a semi-transparent band at the bottom,
    centred horizontally across the full spread width.
    """
    from reportlab.lib.colors import HexColor

    def _split_para(shaped_text: str, max_w: float, font_name: str, fsize: float) -> list:
        """Word-wrap a pre-shaped Arabic string into lines that fit max_w."""
        words = shaped_text.split()
        if not words:
            return ['']
        result, current = [], words[0]
        for w in words[1:]:
            candidate = current + ' ' + w
            if c.stringWidth(candidate, font_name, fsize) <= max_w:
                current = candidate
            else:
                result.append(current)
                current = w
        result.append(current)
        return result

    def _cover_fill(reader, page_w, page_h):
        """Draw image scaled to *cover* the full page (crop rather than letterbox)."""
        if reader is None:
            return
        try:
            iw, ih = reader.getSize()
            scale = max(page_w / iw, page_h / ih)
            dw, dh = iw * scale, ih * scale
            dx, dy = (page_w - dw) / 2, (page_h - dh) / 2
            c.drawImage(reader, dx, dy, dw, dh, mask='auto')
        except Exception:
            pass

    # ── Dark background fallback ──
    c.setFillColor(HexColor('#1A0A2E'))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Full-bleed image spanning the entire spread ──
    _cover_fill(image_reader, W, H)

    # ── Build word-wrapped display lines ──
    font_name = 'Amiri'
    font_size = 21
    h_margin = 60          # left / right margin inside the band
    usable_w  = W - 2 * h_margin

    all_lines = []
    for idx, para in enumerate(story_lines):
        if not para.strip():
            continue
        shaped  = _ar(para)
        wrapped = _split_para(shaped, usable_w, font_name, font_size)
        all_lines.extend(wrapped)
        if idx < len(story_lines) - 1:
            all_lines.append('')   # blank row between paragraphs

    while all_lines and not all_lines[-1]:
        all_lines.pop()
    if not all_lines:
        all_lines = ['']

    line_h       = 30
    v_pad        = 26
    text_block_h = len(all_lines) * line_h
    band_h       = max(text_block_h + v_pad * 2, H * 0.30)
    band_h       = min(band_h, H * 0.48)

    # ── Bottom full-width overlay band ──
    c.saveState()
    c.setFillColor(HexColor('#1A0A2E'))
    c.setFillAlpha(0.87)
    c.rect(0, 0, W, band_h, fill=1, stroke=0)
    c.restoreState()

    # Decorative accent line at top of band
    c.setFillColor(HexColor('#B57EE0'))
    c.rect(0, band_h - 4, W, 4, fill=1, stroke=0)

    # ── Text — centred across the full spread ──
    c.setFont(font_name, font_size)
    c.setFillColor(HexColor('#FFFFFF'))
    y = band_h - v_pad - font_size * 0.25
    for line in all_lines:
        if y < 14:
            break
        if line:
            c.drawCentredString(W / 2, y, line)
        y -= line_h

    # Page number
    c.setFont('Amiri', 12)
    c.setFillColor(HexColor('#C8A8FF'))
    c.drawCentredString(W / 2, 7, _ar(to_arabic_num(page_num)))

    c.showPage()


def generate_storybook_pdf(child_name: str, theme_key: str, ai_image_url: str) -> bytes | None:
    """Build the personalised 20-page PDF storybook — full landscape spread layout.

    Every page is A4 landscape (841 × 595 pt) representing an open two-page spread:
      - Page  1 : Cover spread   — theme illustration full-bleed + title overlay
      - Pages 2–19 : 18 content spreads — AI portrait full-bleed (cover-crop) + text band
      - Page 20 : Closing spread — AI portrait full-bleed + النهاية overlay

    The AI image is scaled to *cover* the entire landscape canvas (portrait image
    is centre-cropped), giving a truly immersive cinematic spread. Fully-vocalized
    Arabic text is placed in a semi-transparent band across the bottom.
    """
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.colors import HexColor
        from reportlab.lib.utils import ImageReader

        _register_pdf_fonts()

        base_dir   = os.path.dirname(__file__)
        theme      = THEMES[theme_key]
        illust_path = os.path.join(base_dir, theme['image'])

        # Download AI image once — fallback to static illustration if unavailable
        ai_bytes = None
        try:
            r = requests.get(ai_image_url, timeout=30)
            r.raise_for_status()
            ai_bytes = r.content
        except Exception:
            ai_bytes = None

        def fresh_ai_reader():
            if ai_bytes is None:
                return None
            try:
                return ImageReader(io.BytesIO(ai_bytes))
            except Exception:
                return None

        def fresh_static_reader():
            try:
                return ImageReader(illust_path)
            except Exception:
                return None

        def best_reader():
            """Return AI reader if available, else static."""
            return fresh_ai_reader() or fresh_static_reader()

        def cover_fill(c_obj, reader, page_w, page_h):
            """Scale image to cover page_w × page_h (CSS cover — centre crop)."""
            if reader is None:
                return
            try:
                iw, ih = reader.getSize()
                scale   = max(page_w / iw, page_h / ih)
                dw, dh  = iw * scale, ih * scale
                dx, dy  = (page_w - dw) / 2, (page_h - dh) / 2
                c_obj.drawImage(reader, dx, dy, dw, dh, mask='auto')
            except Exception:
                pass

        # Prepare 25 paragraphs (pad / trim to exactly 25)
        full_story = [ln.replace('{name}', child_name)
                      for ln in FULL_STORIES[theme_key]]
        while len(full_story) < 25:
            full_story.append('')
        full_story = full_story[:25]

        # Distribute 25 paragraphs across 12 content spreads
        # Pattern: 11 × 2 + 1 × 3 = 25 paragraphs
        # Alternating layout: even index = static illustration, odd index = AI portrait
        # → 6 static spreads + 6 AI spreads = 12 content spreads (API cost optimised)
        p = full_story
        chunks = [
            p[0:2],   p[2:4],   p[4:6],   p[6:8],
            p[8:10],  p[10:12], p[12:14], p[14:16],
            p[16:18], p[18:20], p[20:22], p[22:25],
        ]
        # Pages at even indices (0,2,4,6,8,10) → static theme illustration
        # Pages at odd  indices (1,3,5,7,9,11) → AI child portrait
        if ai_bytes is None:
            is_ai_seq = [False] * 12
        else:
            is_ai_seq = [False, True] * 6   # 6 static + 6 AI

        # Landscape A4 — the two-page spread canvas
        SPREAD = landscape(A4)
        W, H   = SPREAD

        pdf_buf = io.BytesIO()
        c = rl_canvas.Canvas(pdf_buf, pagesize=SPREAD)

        # ══════════════════════════════════════════════
        # PAGE 1 — COVER SPREAD
        # ══════════════════════════════════════════════
        c.setFillColor(HexColor('#1A0A2E'))
        c.rect(0, 0, W, H, fill=1, stroke=0)
        cover_fill(c, fresh_static_reader(), W, H)

        # Top overlay band (title area)
        c.saveState()
        c.setFillColor(HexColor('#1A0A2E'))
        c.setFillAlpha(0.78)
        c.rect(0, H * 0.68, W, H * 0.32, fill=1, stroke=0)
        c.restoreState()

        # Bottom thin overlay (subtitle)
        c.saveState()
        c.setFillColor(HexColor('#1A0A2E'))
        c.setFillAlpha(0.82)
        c.rect(0, 0, W, H * 0.20, fill=1, stroke=0)
        c.restoreState()

        # Accent lines
        c.setFillColor(HexColor('#B57EE0'))
        c.rect(0, H * 0.68 - 4, W, 4, fill=1, stroke=0)
        c.setFillColor(HexColor('#B57EE0'))
        c.rect(0, H * 0.20, W, 4, fill=1, stroke=0)

        c.setFont('AmiriBold', 64)
        c.setFillColor(HexColor('#FFFFFF'))
        c.drawCentredString(W / 2, H * 0.80, _ar('أَثَر'))

        c.setFont('AmiriBold', 38)
        c.setFillColor(HexColor('#FFE6F5'))
        c.drawCentredString(W / 2, H * 0.72, _ar(f'قِصَّةُ {child_name}'))

        c.setFont('Amiri', 26)
        c.setFillColor(HexColor('#C8A8FF'))
        c.drawCentredString(W / 2, H * 0.13, _ar(theme_key))

        c.setFont('Amiri', 17)
        c.setFillColor(HexColor('#9B8AB8'))
        c.drawCentredString(W / 2, H * 0.06,
                            _ar('أَثَر — كُتُبُ الأَطْفَالِ الْجَزَائِرِيَّةُ السِّحْرِيَّةُ'))
        c.showPage()

        # ══════════════════════════════════════════════
        # PAGES 2–13 — 12 immersive full-spread content pages
        # Even-index spreads → static theme illustration (6 pages, no API call)
        # Odd-index  spreads → AI child portrait          (6 pages, personalised)
        # ══════════════════════════════════════════════
        for i, (lines, is_ai) in enumerate(zip(chunks, is_ai_seq)):
            reader = fresh_ai_reader() if is_ai else fresh_static_reader()
            _draw_spread_page(c, W, H,
                              image_reader=reader,
                              story_lines=lines,
                              page_num=i + 2)

        # ══════════════════════════════════════════════
        # PAGE 20 — CLOSING SPREAD
        # ══════════════════════════════════════════════
        c.setFillColor(HexColor('#1A0A2E'))
        c.rect(0, 0, W, H, fill=1, stroke=0)
        cover_fill(c, best_reader(), W, H)

        # Bottom overlay
        c.saveState()
        c.setFillColor(HexColor('#1A0A2E'))
        c.setFillAlpha(0.88)
        c.rect(0, 0, W, H * 0.36, fill=1, stroke=0)
        c.restoreState()

        c.setFillColor(HexColor('#B57EE0'))
        c.rect(0, H * 0.36 - 4, W, 4, fill=1, stroke=0)

        c.setFont('AmiriBold', 40)
        c.setFillColor(HexColor('#FFFFFF'))
        c.drawCentredString(W / 2, H * 0.27, _ar('— النِّهَايَةُ —'))

        c.setFont('AmiriBold', 30)
        c.setFillColor(HexColor('#FFE6F5'))
        c.drawCentredString(W / 2, H * 0.17, _ar(f'شُكْرًا يَا {child_name}'))

        c.setFont('Amiri', 22)
        c.setFillColor(HexColor('#C8A8FF'))
        c.drawCentredString(W / 2, H * 0.08,
                            _ar('عَلَى رِحْلَتِكَ الْجَمِيلَةِ مَعَنَا'))

        c.setFont('Amiri', 14)
        c.setFillColor(HexColor('#7B6798'))
        c.drawCentredString(W / 2, H * 0.03,
                            _ar('أَثَر • صُنِعَ بِحُبٍّ فِي الْجَزَائِرِ'))
        c.showPage()

        c.save()
        return pdf_buf.getvalue()

    except Exception as e:
        st.error(f"❌ خطأ في إنشاء ملف PDF: {e}")
        return None


# ═══════════════════════ PROGRESS BAR ═══════════════════════

def render_progress_bar(current: int) -> str:
    steps = [
        ('👤', 'المعلومات'),
        ('🎨', 'المغامرة'),
        ('✨', 'المعاينة'),
        ('🎁', 'الإضافات'),
        ('🚚', 'التوصيل'),
    ]
    parts = ['<div class="progress-bar">']
    for i, (icon, label) in enumerate(steps, 1):
        cls = 'active' if i == current else ('done' if i < current else '')
        ic = '✓' if i < current else icon
        parts.append(
            f'<div class="prog-step {cls}">'
            f'<div class="prog-circle">{ic}</div>'
            f'<div class="prog-label">{label}</div></div>'
        )
        if i < len(steps):
            line_cls = 'prog-line done' if i < current else 'prog-line'
            parts.append(f'<div class="{line_cls}"></div>')
    parts.append('</div>')
    return ''.join(parts)


# ═══════════════════════ DATABASE & ADMIN PORTAL ═══════════════════════

init_db()


def render_admin_portal():
    """Hidden admin dashboard at ?view=admin-athar-portal — password gated."""
    st.markdown(
        '<div class="step-card" style="max-width:1100px;margin:2rem auto;">',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="step-title">🔐 لوحة تحكم أَثَر — البوابة الإدارية</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.get('admin_unlocked', False):
        st.markdown('أدخل كلمة السر للوصول إلى لوحة الطلبات:')
        pw = st.text_input('كلمة السر', type='password', key='admin_pw',
                           label_visibility='collapsed')
        if st.button('🔓 دخول', key='admin_login', width='stretch'):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.error('❌ كلمة سر خاطئة')
        st.markdown('</div>', unsafe_allow_html=True)
        return

    orders = list_orders()

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(f"### 📊 إجمالي الطلبات: {len(orders)}")
    with top_r:
        if st.button('🚪 تسجيل الخروج', key='admin_logout', width='stretch'):
            st.session_state.admin_unlocked = False
            st.rerun()

    if not orders:
        st.info('لا توجد طلبات حتى الآن.')
        st.markdown('</div>', unsafe_allow_html=True)
        return

    for o in orders:
        oid_label = format_order_id(o['id'])
        ship_label = '🏢 مكتب' if o['shipping_type'] == 'office' else '🏠 منزل'
        with st.expander(
            f"{oid_label} — {o['child_name']} — {o['theme']} — "
            f"{o['total_dzd']:,} دج — {o['created_at']}"
        ):
            cols = st.columns([3, 2])
            with cols[0]:
                st.markdown(f"""
- **الطفل:** {o['child_name']}
- **الثيمة:** {o['theme']}
- **الهاتف:** `{o['phone']}`
- **الولاية:** {o['wilaya']}
- **العنوان:** {o['address']}
- **التوصيل:** {ship_label} ({o['shipping_cost']:,} دج)
- **المنتجات:** {o['items_json']}
- **الإجمالي:** **{o['total_dzd']:,} دج**
- **التاريخ:** {o['created_at']}
                """)
            with cols[1]:
                if o['ai_image_url']:
                    st.markdown('**🖼️ الصورة عالية الدقة:**')
                    st.markdown(
                        f'[فتح الصورة في تبويب جديد ↗]({o["ai_image_url"]})'
                    )
                if o['pdf_size'] > 0:
                    full = get_order(o['id'])
                    if full and full['pdf_blob']:
                        st.download_button(
                            label=f'⬇️ تحميل PDF ({o["pdf_size"] // 1024:,} KB)',
                            data=full['pdf_blob'],
                            file_name=(
                                f'athar_order_{oid_label.lstrip("#")}_'
                                f'{o["child_name"]}.pdf'
                            ),
                            mime='application/pdf',
                            key=f'dl_{o["id"]}'
                        )

    st.markdown('</div>', unsafe_allow_html=True)


# Hidden admin route — short-circuit normal wizard if matched
_qparams = st.query_params
if _qparams.get('view') == 'admin-athar-portal':
    render_admin_portal()
    st.stop()


# ═══════════════════════ WIZARD UI ═══════════════════════

# Compact header
st.markdown("""
<div class="main-header">
    <h1>أَثَـر</h1>
    <p>كتاب طفلك السحري — ٥ خطوات لصنع تحفةٍ شخصية 💜</p>
</div>
""", unsafe_allow_html=True)


def _init_state():
    defaults = {
        'step': 1,
        'child_name': '',
        'uploaded_file_bytes': None,
        'uploaded_file_id': None,
        'selected_theme': list(THEMES.keys())[0],
        'generated_url': None,
        'generated_for_theme': None,
        'generated_for_photo': None,
        'preview_bytes': None,
        'preview_for_url': None,
        'want_stickers': False,
        'want_poster': False,
        'shipping_type': 'office',
        'wilaya': "16 - الجزائر العاصمة",
        'address': '',
        'phone': '',
        'order_id': None,
        'admin_unlocked': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()
current_step = st.session_state.step

# Progress bar at the top
st.markdown(render_progress_bar(current_step), unsafe_allow_html=True)


def go_next():
    st.session_state.step = min(5, st.session_state.step + 1)
    st.rerun()

def go_back():
    st.session_state.step = max(1, st.session_state.step - 1)
    st.rerun()


# ── STEP 1: IDENTITY ──
if current_step == 1:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">👤 الخطوة الأولى: هويّة البطل</div>', unsafe_allow_html=True)
    st.markdown('أدخل اسم طفلك وارفع صورةً واضحةً لوجهه — يُفضّل صورةً أمامية بإضاءةٍ جيدة.')

    child_name = st.text_input(
        '🌟 اسم الطفل',
        value=st.session_state.child_name,
        placeholder='مثال: محمد، ليلى، يوسف...',
        key='input_child_name'
    )

    uploaded_file = st.file_uploader(
        '📸 صورة طفلك',
        type=['jpg', 'jpeg', 'png', 'webp'],
        key='input_photo'
    )

    if uploaded_file is not None:
        photo_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.uploaded_file_id != photo_id:
            uploaded_file.seek(0)
            st.session_state.uploaded_file_bytes = uploaded_file.read()
            st.session_state.uploaded_file_id = photo_id
            # Invalidate any old AI generation tied to a previous photo
            st.session_state.generated_url = None
            st.session_state.preview_bytes = None
            st.session_state.preview_for_url = None

        c1, c2 = st.columns([1, 1])
        with c1:
            st.image(uploaded_file, caption='✨ صورة طفلك', width='stretch')
        with c2:
            st.success('✅ تم رفع الصورة بنجاح!')
            st.info('💡 تأكد أن الوجه واضح وبإضاءةٍ جيدةٍ لأفضل نتيجة')

    # ── Magic Preview: "See your child as a hero" gallery ──
    thumb_items = ''
    for tn, td in THEMES.items():
        try:
            b64 = load_image_b64(td['image'])
            img_src = f"data:image/png;base64,{b64}"
        except Exception:
            img_src = ''
        thumb_items += (
            f'<div class="magic-thumb-item">'
            f'<img src="{img_src}" alt="{tn}" />'
            f'<div class="magic-thumb-label">{tn}</div>'
            f'</div>'
        )
    st.markdown(f"""
    <div class="magic-preview-section">
        <div class="magic-preview-title">✨ شاهد كيف سيبدو ابنك كبطلٍ في القصة</div>
        <div class="magic-preview-sub">
            الذكاء الاصطناعي يُحوّل صورة طفلك إلى بطلٍ حقيقيٍّ في العالم الذي تختاره
        </div>
        <div class="magic-thumb-row">
            {thumb_items}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    has_name = bool(child_name and child_name.strip())
    has_photo = st.session_state.uploaded_file_bytes is not None

    if not has_name:
        st.warning('⚠️ يرجى كتابة اسم الطفل للمتابعة')
    if not has_photo:
        st.warning('⚠️ يرجى رفع صورة الطفل للمتابعة')

    nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
    with nav_r:
        if st.button('التالي ←', key='n1', disabled=not (has_name and has_photo), width='stretch'):
            st.session_state.child_name = child_name.strip()
            go_next()


# ── STEP 2: ADVENTURE ──
elif current_step == 2:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🎨 الخطوة الثانية: اختر المغامرة</div>', unsafe_allow_html=True)
    st.markdown(
        f'مرحباً <strong style="color:#7B3FA6">{st.session_state.child_name}</strong>! اختر القصة التي ستجعلك بطل المغامرة:',
        unsafe_allow_html=True
    )
    st.markdown('<br>', unsafe_allow_html=True)

    book_cols = st.columns(5)
    for i, (tn, td) in enumerate(THEMES.items()):
        with book_cols[i]:
            is_sel = st.session_state.selected_theme == tn
            cls = 'book-card selected' if is_sel else 'book-card'
            try:
                img_b64 = load_image_b64(td['image'])
                src = f"data:image/png;base64,{img_b64}"
            except Exception:
                src = ''
            st.markdown(f"""
            <div class="{cls}">
              <div class="book-image-wrap"><img src="{src}" alt="{tn}"/></div>
              <div class="book-label">
                <div class="book-name">{tn}</div>
                <div class="book-desc">{td['desc']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            label = '✓ مختار' if is_sel else 'اختر ✨'
            if st.button(label, key=f'theme_{i}'):
                if st.session_state.selected_theme != tn:
                    st.session_state.selected_theme = tn
                    st.session_state.generated_url = None
                    st.session_state.preview_bytes = None
                    st.session_state.preview_for_url = None
                st.rerun()

    sel = st.session_state.selected_theme
    st.markdown(
        f'<div style="text-align:center;margin-top:1rem;padding:0.8rem;'
        f'background:linear-gradient(135deg,#F5E6FF,#E6F0FF);border-radius:14px;'
        f'font-weight:800;color:#5A3D8A;font-size:1.05rem;">'
        f'🎨 المغامرة المختارة: <span style="color:#9B59B6;">{sel}</span></div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
    with nav_l:
        if st.button('→ السابق', key='b2', width='stretch'):
            go_back()
    with nav_r:
        if st.button('التالي ←', key='n2', width='stretch'):
            go_next()


# ── STEP 3: MAGIC PREVIEW ──
elif current_step == 3:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">✨ الخطوة الثالثة: المعاينة السحرية</div>', unsafe_allow_html=True)

    # Defensive prereq guards
    if not (st.session_state.child_name and st.session_state.child_name.strip()) \
       or st.session_state.uploaded_file_bytes is None:
        st.warning('⚠️ يجب إكمال الخطوة الأولى (الاسم + الصورة) أوّلاً')
        if st.button('← العودة إلى الخطوة الأولى', key='guard3_back', width='stretch'):
            st.session_state.step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    if not st.session_state.selected_theme:
        st.warning('⚠️ يجب اختيار مغامرة في الخطوة الثانية أوّلاً')
        if st.button('← العودة إلى الخطوة الثانية', key='guard3_back2', width='stretch'):
            st.session_state.step = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    sel = st.session_state.selected_theme
    needs_gen = (
        st.session_state.generated_url is None
        or st.session_state.generated_for_theme != sel
        or st.session_state.generated_for_photo != st.session_state.uploaded_file_id
    )

    if needs_gen:
        st.markdown('انقر لتوليد صورة طفلك في المغامرة المختارة (يستغرق دقيقة أو دقيقتين):')
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('🪄 ولّد الصورة السحرية الآن!', key='gen_btn'):
            with st.spinner('⏳ جاري إنشاء صورة طفلك السحرية...'):
                result_url = generate_image(st.session_state.uploaded_file_bytes, sel)
                if result_url:
                    st.session_state.generated_url = result_url
                    st.session_state.generated_for_theme = sel
                    st.session_state.generated_for_photo = st.session_state.uploaded_file_id
                    st.session_state.preview_bytes = None
                    st.session_state.preview_for_url = None
                    st.rerun()
    else:
        st.markdown('<div class="success-banner">🎉 تم توليد صورة طفلك السحرية! إليك معاينة الكتاب:</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

        # Cache watermarked preview bytes (avoid re-downloading on rerun)
        if (st.session_state.preview_bytes is None
                or st.session_state.preview_for_url != st.session_state.generated_url):
            with st.spinner('🎨 جاري تحضير المعاينة...'):
                st.session_state.preview_bytes = make_watermarked_preview(
                    st.session_state.generated_url
                )
                st.session_state.preview_for_url = st.session_state.generated_url

        if st.session_state.preview_bytes:
            data_uri = (
                "data:image/jpeg;base64,"
                + base64.b64encode(st.session_state.preview_bytes).decode('ascii')
            )
        else:
            data_uri = ''

        book_html = render_book_mockup(data_uri, st.session_state.child_name, sel)
        components.html(book_html, height=560, scrolling=False)

        st.info(
            '💡 هذه معاينة بعلامة مائية — ستحصلون على الكتاب الكامل عالي الجودة '
            '(١٢ صفحة) بعد تأكيد الطلب.'
        )

        if st.button('🔄 توليد صورة جديدة', key='regen'):
            st.session_state.generated_url = None
            st.session_state.preview_bytes = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
    with nav_l:
        if st.button('→ السابق', key='b3', width='stretch'):
            go_back()
    with nav_r:
        next_disabled = st.session_state.generated_url is None
        if st.button('التالي ←', key='n3', disabled=next_disabled, width='stretch'):
            go_next()


# ── STEP 4: CUSTOMIZATION & UPSELL ──
elif current_step == 4:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🎁 الخطوة الرابعة: التخصيص والإضافات</div>', unsafe_allow_html=True)

    # Defensive prereq guard
    if st.session_state.generated_url is None:
        st.warning('⚠️ يجب توليد صورة طفلك السحرية في الخطوة الثالثة أوّلاً')
        if st.button('← العودة إلى الخطوة الثالثة', key='guard4_back', width='stretch'):
            st.session_state.step = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    st.markdown('اختر الإضافات التي تريدها لجعل هديّتك أكثر إبهاراً:')
    st.markdown('<br>', unsafe_allow_html=True)

    # ── Main book (always included) ──
    st.markdown(f"""
    <div class="upsell-visual-card checked">
      <div class="upsell-visual-row">
        <div class="upsell-thumb-box"
             style="background:linear-gradient(135deg,#9B59B6,#5A3D8A);font-size:2.6rem;">
          📕
        </div>
        <div class="upsell-info">
          <div class="upsell-name-v2">📕 الكتاب المخصّص</div>
          <div class="upsell-desc-v2">٢٠ صفحة فاخرة مخصّصة باسم وصورة طفلك — قصة كاملة بصور سحرية من الذكاء الاصطناعي</div>
          <div class="upsell-price-v2">{BOOK_PRICE:,} دج &nbsp;✅ مضمّن دائماً</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stickers upsell with visual thumbnail ──
    stickers_cls = 'checked' if st.session_state.want_stickers else ''
    st.markdown(f"""
    <div class="upsell-visual-card {stickers_cls}">
      <div class="upsell-visual-row">
        <div class="upsell-thumb-box thumb-stickers">
          <div style="display:flex;flex-wrap:wrap;width:88px;height:88px;
                      align-items:center;justify-content:center;
                      gap:2px;padding:8px;font-size:1.5rem;line-height:1;">
            ⭐🌟💫<br>✨🎀🌈
          </div>
        </div>
        <div class="upsell-info">
          <div class="upsell-name-v2">🌟 ملصقات الشخصية</div>
          <div class="upsell-desc-v2">
            مجموعة من ١٢ ملصقاً مُخصَّصاً بصورة طفلك البطل —
            مثالية للكراسة والحقيبة والغرفة
          </div>
          <div class="upsell-price-v2">+ {STICKERS_PRICE:,} دج</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    want_stickers = st.checkbox(
        f'✅ أضف ملصقات الشخصية (+{STICKERS_PRICE:,} دج)',
        value=st.session_state.want_stickers,
        key='cb_stickers'
    )
    st.session_state.want_stickers = want_stickers

    # ── Poster upsell with visual thumbnail ──
    poster_cls = 'checked' if st.session_state.want_poster else ''
    st.markdown(f"""
    <div class="upsell-visual-card {poster_cls}">
      <div class="upsell-visual-row">
        <div class="upsell-thumb-box thumb-poster">
          <div style="display:flex;align-items:center;justify-content:center;
                      width:88px;height:88px;padding:8px;">
            <div style="border:4px solid #C8A060;border-radius:6px;padding:4px;
                        width:68px;height:68px;display:flex;align-items:center;
                        justify-content:center;background:rgba(255,255,255,0.1);">
              <span style="font-size:2.2rem;">🖼️</span>
            </div>
          </div>
        </div>
        <div class="upsell-info">
          <div class="upsell-name-v2">🖼️ بوستر حائطي فائق الجودة A3</div>
          <div class="upsell-desc-v2">
            صورة طفلك بطلاً في المغامرة — مطبوعة بجودة فائقة بحجم A3 للتعليق على الجدار
          </div>
          <div class="upsell-price-v2">+ {POSTER_PRICE:,} دج</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    want_poster = st.checkbox(
        f'✅ أضف بوستر حائطي فائق الجودة A3 (+{POSTER_PRICE:,} دج)',
        value=st.session_state.want_poster,
        key='cb_poster'
    )
    st.session_state.want_poster = want_poster

    # ── Live add-ons subtotal (shipping added in Step 5) ──
    items_total_4 = BOOK_PRICE
    if want_stickers:
        items_total_4 += STICKERS_PRICE
    if want_poster:
        items_total_4 += POSTER_PRICE

    st.markdown(f"""
    <div style="text-align:center;margin-top:1.2rem;padding:1rem;
                background:linear-gradient(135deg,#F5E8FF,#E8F0FF);border-radius:16px;">
      <div style="font-size:0.85rem;color:#8B7AA8;font-weight:700;margin-bottom:0.4rem;">
        💰 إجمالي المنتجات المختارة
      </div>
      <div class="live-total-badge">{items_total_4:,} دج</div>
      <div style="font-size:0.73rem;color:#9B8AB8;margin-top:0.4rem;font-weight:600;">
        تكلفة الشحن تُحسب في الخطوة التالية حسب ولايتك
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
    with nav_l:
        if st.button('→ السابق', key='b4', width='stretch'):
            go_back()
    with nav_r:
        if st.button('التالي ←', key='n4', width='stretch'):
            go_next()


# ── STEP 5: DELIVERY ──
elif current_step == 5:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🚚 الخطوة الخامسة: بيانات التوصيل</div>', unsafe_allow_html=True)

    # Defensive prereq guard
    if st.session_state.generated_url is None:
        st.warning('⚠️ يجب توليد صورة طفلك السحرية في الخطوة الثالثة أوّلاً')
        if st.button('← العودة إلى الخطوة الثالثة', key='guard5_back', width='stretch'):
            st.session_state.step = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ── Already-placed: show confirmation screen ──
    if st.session_state.order_id is not None:
        oid_label = format_order_id(st.session_state.order_id)
        st.markdown(f"""
        <div class="success-banner" style="text-align:center;padding:1.8rem;">
          <div style="font-size:2.4rem;margin-bottom:0.5rem;">🎉</div>
          <div style="font-size:1.4rem;font-weight:800;color:#2C1A4A;">شكراً لطلبكم!</div>
          <div style="font-size:1.8rem;font-weight:900;color:#7B3FA6;margin:0.6rem 0;">رقم طلبكم: {oid_label}</div>
          <div style="color:#5A3D8A;">احتفظوا برقم الطلب — سيتمّ التواصل معكم على واتساب لتأكيد الدفع والتوصيل 💜</div>
        </div>
        """, unsafe_allow_html=True)

        # Simple WhatsApp message: ONLY Order ID + Child Name
        wa_msg = (
            f"السلام عليكم ✨\n"
            f"أودّ تأكيد طلبي على منصّة *أَثَر*:\n\n"
            f"👶 *اسم الطفل:* {st.session_state.child_name}\n"
            f"📦 *رقم الطلب:* {oid_label}\n\n"
            f"شكراً!"
        )
        wa_link = f'https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(wa_msg)}'

        st.markdown(
            f'<div style="margin-top:1rem;text-align:center;">'
            f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">'
            f'📲 إرسال تأكيد الطلب عبر واتساب</a></div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="info-box" style="margin-top:1.5rem;">
          <h4>💳 طرق الدفع</h4>
          <p>
            📮 <strong>CCP:</strong> 0023456789 / مفتاح 47<br>
            📱 <strong>BaridiMob:</strong> 00799999001234567890<br>
            ⚠️ يُرسل إيصال الدفع عبر واتساب مع رقم الطلب
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('🔁 إنشاء طلب جديد', key='new_order', width='stretch'):
            for k in ['step', 'child_name', 'uploaded_file_bytes', 'uploaded_file_id',
                      'generated_url', 'generated_for_theme', 'generated_for_photo',
                      'preview_bytes', 'preview_for_url', 'want_stickers', 'want_poster',
                      'shipping_type', 'address', 'phone', 'order_id']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ── Pre-order: collect delivery details ──

    # 1) Wilaya selector (drives shipping price)
    wilaya_keys = list(WILAYA_SHIPPING.keys())
    try:
        w_idx = wilaya_keys.index(st.session_state.wilaya)
    except ValueError:
        w_idx = 15
    wilaya = st.selectbox('📍 الولاية', options=wilaya_keys, index=w_idx, key='inp_wilaya')
    st.session_state.wilaya = wilaya

    # 2) Dynamic shipping costs for the selected wilaya
    ship_off_cost, ship_home_cost = WILAYA_SHIPPING.get(wilaya, (500, 800))

    # 3) Shipping method — visual cards + radio
    st.markdown(
        '<div style="font-weight:800;color:#5A3D8A;font-size:1.05rem;'
        'margin:0.9rem 0 0.3rem;">🚚 طريقة التوصيل</div>',
        unsafe_allow_html=True
    )
    cur_ship = st.session_state.get('shipping_type', 'office')
    off_cls  = 'active' if cur_ship == 'office' else ''
    home_cls = 'active' if cur_ship == 'home'   else ''
    st.markdown(f"""
    <div class="ship-method-grid">
      <div class="ship-method-card {off_cls}">
        <div class="ship-method-icon">🏢</div>
        <div class="ship-method-label">توصيل للمكتب (ستوب ديسك)</div>
        <div class="ship-method-price">{ship_off_cost:,} دج</div>
        <div class="ship-method-note">اسحب الطرد من أقرب مكتب • الأسرع والأرخص</div>
      </div>
      <div class="ship-method-card {home_cls}">
        <div class="ship-method-icon">🏠</div>
        <div class="ship-method-label">توصيل للمنزل</div>
        <div class="ship-method-price">{ship_home_cost:,} دج</div>
        <div class="ship-method-note">يصل إلى باب البيت • راحة أكبر</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    shipping_choice = st.radio(
        'shipping_method',
        options=['office', 'home'],
        format_func=lambda v: (
            f'🏢 مكتب (ستوب ديسك) — {ship_off_cost:,} دج'
            if v == 'office' else
            f'🏠 توصيل للمنزل — {ship_home_cost:,} دج'
        ),
        index=0 if cur_ship == 'office' else 1,
        key='radio_shipping',
        label_visibility='collapsed',
        horizontal=True,
    )
    st.session_state.shipping_type = shipping_choice
    shipping_cost = ship_off_cost if shipping_choice == 'office' else ship_home_cost
    ship_label = '🏢 توصيل للمكتب (ستوب ديسك)' if shipping_choice == 'office' else '🏠 توصيل للمنزل'

    st.markdown('<br>', unsafe_allow_html=True)

    # 4) Phone & address
    cf1, cf2 = st.columns(2)
    with cf1:
        phone = st.text_input(
            '📞 رقم الهاتف',
            value=st.session_state.phone,
            placeholder='06xxxxxxxx',
            key='inp_phone'
        )
    with cf2:
        address = st.text_input(
            '🏠 العنوان التفصيلي',
            value=st.session_state.address,
            placeholder='الحي، الشارع، رقم المبنى...',
            key='inp_addr'
        )

    st.session_state.phone   = phone
    st.session_state.address = address

    # 5) Live total — updates instantly on any selection change
    items_lines = ['📕 الكتاب المخصّص']
    items_total = BOOK_PRICE
    if st.session_state.want_stickers:
        items_total += STICKERS_PRICE
        items_lines.append('🌟 ملصقات الشخصية')
    if st.session_state.want_poster:
        items_total += POSTER_PRICE
        items_lines.append('🖼️ بوستر حائطي فائق الجودة A3')
    grand_total = items_total + shipping_cost

    rows_html = ''.join(
        f'<div class="checkout-line"><span>{n}</span><span>{p:,} دج</span></div>'
        for n, p in [('📚 المنتجات', items_total), (ship_label, shipping_cost)]
    )
    st.markdown(f"""
    <div class="checkout-summary">
      <div style="font-weight:900;color:#5A3D8A;font-size:1.1rem;margin-bottom:0.5rem;">💰 ملخص الطلب النهائي</div>
      {rows_html}
      <div class="checkout-line total">
        <span>الإجمالي الكلي</span>
        <span>{grand_total:,} دج</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    can_order = bool(phone.strip() and address.strip() and wilaya)
    if not can_order:
        missing = []
        if not phone.strip():
            missing.append('الهاتف')
        if not address.strip():
            missing.append('العنوان')
        st.warning(f'⚠️ يرجى إكمال: **{" • ".join(missing)}**')

    st.markdown('</div>', unsafe_allow_html=True)

    nav_l, _, nav_r = st.columns([1, 2, 1])
    with nav_l:
        if st.button('→ السابق', key='b5', width='stretch'):
            go_back()
    with nav_r:
        if st.button('✅ تأكيد الطلب', key='place_order', width='stretch',
                     disabled=not can_order, type='primary'):
            with st.spinner('⏳ جاري تجهيز كتاب طفلك وحفظ الطلب...'):
                pdf = generate_storybook_pdf(
                    st.session_state.child_name,
                    st.session_state.selected_theme,
                    st.session_state.generated_url,
                )
                try:
                    new_id = create_order(
                        child_name=st.session_state.child_name,
                        theme=st.session_state.selected_theme,
                        phone=phone.strip(),
                        wilaya=wilaya,
                        address=address.strip(),
                        shipping_type=shipping_choice,
                        shipping_cost=shipping_cost,
                        items_json=json.dumps(items_lines, ensure_ascii=False),
                        total_dzd=grand_total,
                        ai_image_url=st.session_state.generated_url,
                        pdf_blob=pdf,
                    )
                    st.session_state.order_id = new_id
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ تعذّر حفظ الطلب: {e}")


# ── FOOTER ──
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <div style="font-size:1.5rem;margin-bottom:0.3rem;">⭐ أَثَـر ⭐</div>
    <div>نصنع ذكريات لا تُنسى لأطفالكم 💜</div>
    <div style="margin-top:0.4rem;opacity:0.7;font-size:0.8rem;">جميع الحقوق محفوظة © 2026</div>
</div>
""", unsafe_allow_html=True)
