"""
Pantry Tracker — Streamlit app
Adgangskode-beskyttet webudgave af ugens tilbudsrapport.

Kør lokalt:  streamlit run streamlit_app.py
"""

from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from generate_report import indsaml_data, generer_html
from pantry_liste import generer_liste_html

# ── Adgangskode ──────────────────────────────────────────────
# Bruger Streamlit secrets hvis de findes, ellers fallback herunder.
try:
    ADGANGSKODE = st.secrets["adgangskode"]
except Exception:
    ADGANGSKODE = "Wyoi7"

st.set_page_config(page_title="Pantry", page_icon="🥫", layout="wide")

st.markdown(
    """
    <style>
      #MainMenu, footer {visibility: hidden;}
      .block-container {padding-top: 2rem; max-width: 1100px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60 * 60 * 6, show_spinner="Henter tilbud fra butikkerne…")
def hent_tilbud():
    """Henter alle tilbud. Caches i 6 timer, så API'et ikke spammes."""
    return indsaml_data()


def login() -> bool:
    if st.session_state.get("adgang_ok"):
        return True

    st.title("Pantry")
    st.caption("Ugens tilbud på basisvarer. Indtast adgangskode for at se listen.")

    kode = st.text_input("Adgangskode", type="password")
    if st.button("Log ind"):
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
        st.subheader("Pantry")
        st.caption(f"Uge {uge}, {år}")
        visning = st.radio("Visning", ["Liste (A–Å)", "Butikskort"], index=0)
        if st.button("Hent tilbud igen"):
            st.cache_data.clear()
            st.rerun()
        if st.button("Log ud"):
            st.session_state["adgang_ok"] = False
            st.rerun()

    alle = hent_tilbud()

    if not alle:
        st.warning("Ingen tilbud fundet lige nu. Prøv at hente igen om lidt.")
        return

    if visning.startswith("Liste"):
        html = generer_liste_html(alle)
    else:
        html = generer_html(alle)

    components.html(html, height=900, scrolling=True)

    st.download_button(
        "Download som HTML",
        data=html,
        file_name=f"pantry_uge{uge}_{år}.html",
        mime="text/html",
    )


if __name__ == "__main__":
    main()
