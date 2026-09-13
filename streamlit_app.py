"""
Pantry Tracker — Streamlit app
Adgangskode-beskyttet webudgave af ugens tilbudsrapport.

Kør lokalt:  streamlit run streamlit_app.py
"""

from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from generate_report import indsaml_data, generer_html
from pantry_liste import generer_liste_html, generer_butik_html

try:
    ADGANGSKODE = st.secrets["adgangskode"]
except Exception:
    ADGANGSKODE = "Wyoi7"

st.set_page_config(page_title="Pantry", page_icon="🥫", layout="wide")

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    <style>
      #MainMenu, footer { visibility: hidden; }
      [data-testid="stToolbar"] { display: none; }
      .stApp { background: #EFF1EC; }
      .block-container { padding-top: 2rem; max-width: 1100px; }
      iframe { border: none !important; }

      /* Sidebar */
      [data-testid="stSidebar"] { background: #14231C !important; }
      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] span,
      [data-testid="stSidebar"] label { color: #EFF1EC !important; }
      [data-testid="stSidebar"] small,
      [data-testid="stSidebar"] .stCaption { color: #7B9A83 !important; }
      [data-testid="stSidebar"] hr { border-color: #2D4035 !important; }
      [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid #3D5244 !important;
        color: #EFF1EC !important;
        border-radius: 2px !important;
        font-family: 'Archivo', system-ui, sans-serif !important;
        letter-spacing: 0.01em;
        margin-top: 2px;
        width: 100%;
      }
      [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(239,241,236,0.07) !important;
        border-color: #7B9A83 !important;
      }
      [data-testid="stSidebar"] .stRadio > label { color: #7B9A83 !important; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; }
      [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { color: #EFF1EC !important; font-size: 14px; text-transform: none; letter-spacing: 0; }

      /* Login */
      .pantry-logo {
        font-family: 'Fraunces', Georgia, serif;
        font-size: clamp(64px, 14vw, 108px);
        font-weight: 600;
        letter-spacing: -0.055em;
        line-height: 0.82;
        color: #14231C;
        padding: 48px 0 20px;
      }
      .pantry-sub {
        color: #5F7168;
        font-family: 'Archivo', system-ui, sans-serif;
        font-size: 15px;
        margin-bottom: 28px;
      }

      /* Input */
      [data-testid="stTextInput"] input {
        background: #E4E8DF !important;
        border: 1px solid #C8D0C3 !important;
        border-radius: 2px !important;
        color: #14231C !important;
        font-family: 'Archivo', system-ui, sans-serif !important;
        font-size: 15px !important;
        padding: 11px 14px !important;
      }
      [data-testid="stTextInput"] input:focus {
        border-color: #14231C !important;
        box-shadow: none !important;
      }

      /* Primary button (login) */
      .login-btn .stButton > button {
        background: #14231C !important;
        color: #EFF1EC !important;
        border: none !important;
        border-radius: 2px !important;
        font-family: 'Archivo', system-ui, sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.03em !important;
        padding: 12px 0 !important;
        width: 100% !important;
        margin-top: 8px;
      }
      .login-btn .stButton > button:hover {
        background: #1F3328 !important;
      }

      /* Download button */
      [data-testid="stDownloadButton"] button {
        background: transparent !important;
        border: 1px solid #C8D0C3 !important;
        color: #5F7168 !important;
        border-radius: 2px !important;
        font-size: 13px !important;
        margin-top: 8px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60 * 60 * 6, show_spinner="Henter tilbud fra butikkerne…")
def hent_tilbud():
    return indsaml_data()


def login() -> bool:
    if st.session_state.get("adgang_ok"):
        return True

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="pantry-logo">Pantry</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="pantry-sub">Ugens tilbud på basisvarer</div>',
            unsafe_allow_html=True,
        )
        kode = st.text_input(
            "Adgangskode",
            type="password",
            label_visibility="collapsed",
            placeholder="Adgangskode",
        )
        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Log ind", use_container_width=True):
            if kode == ADGANGSKODE:
                st.session_state["adgang_ok"] = True
                st.rerun()
            else:
                st.error("Forkert adgangskode. Prøv igen.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False


def main():
    if not login():
        return

    uge = date.today().isocalendar().week
    år = date.today().year

    with st.sidebar:
        st.markdown(
            '<div style="font-family:\'Fraunces\',Georgia,serif;font-size:26px;'
            'font-weight:600;letter-spacing:-0.03em;color:#EFF1EC;padding:12px 0 2px">'
            "Pantry</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Uge {uge}, {år}")
        st.divider()

        visning = st.radio(
            "Visning",
            ["Vare (A–Å)", "Butik (A–Å)", "Butikskort"],
            index=0,
        )

        st.divider()

        if st.button("Opdater tilbud"):
            st.cache_data.clear()
            st.rerun()
        if st.button("Log ud"):
            st.session_state["adgang_ok"] = False
            st.rerun()

    alle = hent_tilbud()

    if not alle:
        st.warning("Ingen tilbud fundet. Prøv at opdatere.")
        return

    if visning == "Vare (A–Å)":
        html = generer_liste_html(alle)
    elif visning == "Butik (A–Å)":
        html = generer_butik_html(alle)
    else:
        html = generer_html(alle)

    components.html(html, height=960, scrolling=True)

    st.download_button(
        "Download som HTML",
        data=html,
        file_name=f"pantry_uge{uge}_{år}.html",
        mime="text/html",
    )


if __name__ == "__main__":
    main()
