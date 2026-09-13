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

# Minimal single-line CSS to avoid Streamlit's multiline style rendering bug
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&display=swap" rel="stylesheet">'
    '<style>'
    '#MainMenu,footer{visibility:hidden}'
    '[data-testid="stToolbar"]{display:none}'
    '.block-container{padding-top:2rem;max-width:1100px}'
    'iframe{border:none!important}'
    '[data-testid="stSidebar"]{background:#14231C!important}'
    '[data-testid="stSidebar"] *{color:#EFF1EC!important}'
    '[data-testid="stSidebar"] .stCaption p{color:#7B9A83!important}'
    '[data-testid="stSidebar"] hr{border-color:#2D4035!important}'
    '[data-testid="stSidebar"] button{background:transparent!important;border:1px solid #3D5244!important;border-radius:2px!important}'
    '[data-testid="stSidebar"] button:hover{background:rgba(239,241,236,.07)!important;border-color:#7B9A83!important}'
    '</style>',
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
        st.markdown(
            '<p style="font-family:\'Fraunces\',Georgia,serif;font-size:96px;font-weight:600;'
            'letter-spacing:-.055em;line-height:.82;color:#14231C;padding:48px 0 16px 0">'
            "Pantry</p>"
            '<p style="color:#5F7168;font-size:14px;margin-bottom:24px">'
            "Ugens tilbud på basisvarer</p>",
            unsafe_allow_html=True,
        )
        kode = st.text_input(
            "Adgangskode",
            type="password",
            label_visibility="collapsed",
            placeholder="Adgangskode",
        )
        if st.button("Log ind", use_container_width=True):
            if kode == ADGANGSKODE:
                st.session_state["adgang_ok"] = True
                st.rerun()
            else:
                st.error("Forkert adgangskode. Prøv igen.")
    return False


def main():
    if not login():
        return

    uge = date.today().isocalendar().week
    år = date.today().year

    with st.sidebar:
        st.markdown(
            '<p style="font-family:\'Fraunces\',Georgia,serif;font-size:26px;'
            'font-weight:600;letter-spacing:-.03em;padding:10px 0 2px">Pantry</p>',
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

        if st.button("Opdater tilbud", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        if st.button("Log ud", use_container_width=True):
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
