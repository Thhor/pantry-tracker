"""
Pantry Tracker — liste-visning (A-Å pr. vare)

Bygger en HTML-side hvor tilbuddene er grupperet efter vare i alfabetisk
orden, med den billigste kilo-/literpris markeret pr. vare.

Bruges af streamlit_app.py. Rører ikke generate_report.py.
"""

from collections import defaultdict
from datetime import datetime

BUTIK_FARVER = {
    "Netto": "#FFD950",
    "REMA 1000": "#CC0000",
    "Lidl": "#0347A1",
    "SuperBrugsen": "#00843D",
    "Meny": "#E8000D",
    "365discount": "#FF6600",
}

# Bogstaver der skal sorteres sidst, dansk stil
_DANSK = {"æ": "zz1", "ø": "zz2", "å": "zz3", "ä": "zz1", "ö": "zz2"}


def _sorter_nøgle(tekst: str) -> str:
    return "".join(_DANSK.get(c, c) for c in tekst.lower())


def _kort_dato(iso: str) -> str:
    """2026-09-20 -> 20.09"""
    try:
        å, m, d = iso.split("-")
        return f"{d}.{m}"
    except (ValueError, AttributeError):
        return iso or ""


def _pris(v: float) -> str:
    """Dansk prisskilt: 6,-  /  45,50"""
    if float(v).is_integer():
        return f"{int(v)},-"
    return f"{v:.2f}".replace(".", ",")


def _begyndelsesbogstav(navn: str) -> str:
    return navn[0].upper() if navn else "?"


CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --paper: #EFF1EC;
  --paper-2: #E7EAE3;
  --ink: #14231C;
  --ink-soft: #5F7168;
  --rule: #D2D9CE;
  --stamp: #7B2D4E;
  --serif: 'Fraunces', Georgia, serif;
  --sans: 'Archivo', system-ui, sans-serif;
}

html { scroll-behavior: smooth; }

body {
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.4;
  -webkit-font-smoothing: antialiased;
}

.wrap { max-width: 960px; margin: 0 auto; padding: 0 20px 80px; }

/* ── Masthead ───────────────────────────────────────── */
.masthead {
  padding: 40px 0 20px;
  border-bottom: 6px solid var(--ink);
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}
.logo {
  font-family: var(--serif);
  font-optical-sizing: auto;
  font-weight: 600;
  font-size: clamp(52px, 12vw, 104px);
  letter-spacing: -0.055em;
  line-height: 0.82;
}
.masthead-meta {
  font-size: 13px;
  color: var(--ink-soft);
  text-align: right;
  line-height: 1.7;
  font-variant-numeric: tabular-nums;
}
.masthead-meta b { color: var(--ink); font-weight: 600; }

/* ── Kontrolbjælke ──────────────────────────────────── */
.controls {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--paper);
  border-bottom: 1px solid var(--rule);
  padding: 12px 0;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.search {
  flex: 1 1 220px;
  min-width: 180px;
  background: transparent;
  border: 1px solid var(--rule);
  border-radius: 2px;
  padding: 9px 12px;
  font-family: var(--sans);
  font-size: 14px;
  color: var(--ink);
}
.search::placeholder { color: var(--ink-soft); }
.search:focus { outline: 2px solid var(--ink); outline-offset: -1px; }

.chips { display: flex; gap: 6px; }
.chip {
  border: 1px solid var(--rule);
  background: transparent;
  border-radius: 2px;
  padding: 8px 14px;
  font-family: var(--sans);
  font-size: 13px;
  color: var(--ink-soft);
  cursor: pointer;
}
.chip:hover { border-color: var(--ink-soft); color: var(--ink); }
.chip[aria-pressed="true"] {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
}
.chip:focus-visible { outline: 2px solid var(--stamp); outline-offset: 2px; }

/* ── Alfabet-index ──────────────────────────────────── */
.index {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 12px 0 4px;
  border-bottom: 1px solid var(--rule);
}
.index a {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-soft);
  text-decoration: none;
  padding: 3px 7px;
  border-radius: 2px;
}
.index a:hover { background: var(--ink); color: var(--paper); }

/* ── Vare-blok ──────────────────────────────────────── */
.vare { border-bottom: 1px solid var(--rule); padding: 22px 0 18px; }
.vare-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 10px;
}
.vare-navn {
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(21px, 3vw, 27px);
  letter-spacing: -0.015em;
}
.vare-antal {
  font-size: 12px;
  color: var(--ink-soft);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.tilbud {
  display: grid;
  grid-template-columns: 14px 132px 1fr 64px 78px 84px 62px;
  gap: 14px;
  align-items: baseline;
  padding: 7px 0;
}
.tilbud + .tilbud { border-top: 1px dotted var(--rule); }

.flag { width: 4px; height: 15px; border-radius: 1px; align-self: center; }
.butik { font-size: 13px; font-weight: 600; }
.navn { font-size: 13px; color: var(--ink-soft); }
.pris {
  font-size: 17px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  text-align: right;
}
.stamp-celle { text-align: right; }
.norm {
  font-size: 12px;
  color: var(--ink-soft);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  min-width: 78px;
  text-align: right;
}
.bedst .norm { color: var(--stamp); font-weight: 600; }
.stamp {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--stamp);
  border: 1px solid var(--stamp);
  border-radius: 2px;
  padding: 1px 5px;
  vertical-align: 1px;
}
.udlob {
  font-size: 11px;
  color: var(--ink-soft);
  white-space: nowrap;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.tom {
  padding: 60px 0;
  text-align: center;
  color: var(--ink-soft);
  font-size: 14px;
}

@media (max-width: 620px) {
  .tilbud {
    grid-template-columns: 14px auto 1fr auto;
    grid-template-areas:
      "flag butik butik pris"
      "flag navn  navn  navn"
      "flag stamp norm  dato";
    column-gap: 10px;
    row-gap: 3px;
    padding: 10px 0;
  }
  .flag  { grid-area: flag; height: 100%; }
  .butik { grid-area: butik; }
  .pris  { grid-area: pris; }
  .navn  { grid-area: navn; }
  .stamp-celle { grid-area: stamp; text-align: left; }
  .norm  { grid-area: norm; text-align: left; min-width: 0; }
  .udlob { grid-area: dato; text-align: right; }
  .masthead { padding-top: 26px; }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}

/* ── Butik-visning ──────────────────────────────────── */
.butik-sektion { border-bottom: 2px solid var(--ink); padding: 28px 0 20px; }
.butik-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  padding-left: 18px;
  border-left: 5px solid;
  margin-bottom: 14px;
}
.butik-title {
  font-family: var(--serif);
  font-weight: 600;
  font-size: clamp(22px, 3.5vw, 32px);
  letter-spacing: -0.02em;
}
.tilbud-butik {
  display: grid;
  grid-template-columns: 160px 1fr 78px 84px 62px;
  gap: 14px;
  align-items: baseline;
  padding: 7px 0;
}
.tilbud-butik + .tilbud-butik { border-top: 1px dotted var(--rule); }
.vare-cat {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
@media (max-width: 620px) {
  .tilbud-butik {
    grid-template-columns: 1fr auto;
    grid-template-areas: "cat pris" "navn norm" "blank dato";
    row-gap: 2px;
  }
  .vare-cat  { grid-area: cat; }
  .tilbud-butik .pris  { grid-area: pris; }
  .tilbud-butik .navn  { grid-area: navn; }
  .tilbud-butik .norm  { grid-area: norm; text-align: left; min-width: 0; }
  .tilbud-butik .udlob { grid-area: dato; }
}
"""

JS = """
const søg = document.getElementById('soeg');
const chips = document.querySelectorAll('.chip');
const varer = document.querySelectorAll('.vare');
const tom = document.getElementById('tom');
let kategori = 'alle';

function filtrer() {
  const q = (søg.value || '').toLowerCase().trim();
  let synlige = 0;
  varer.forEach(v => {
    const matchKat = kategori === 'alle' || v.dataset.kategori === kategori;
    const matchSøg = !q || v.dataset.soeg.includes(q);
    const vis = matchKat && matchSøg;
    v.style.display = vis ? '' : 'none';
    if (vis) synlige++;
  });
  tom.style.display = synlige ? 'none' : 'block';
}

søg.addEventListener('input', filtrer);
chips.forEach(c => c.addEventListener('click', () => {
  chips.forEach(x => x.setAttribute('aria-pressed', 'false'));
  c.setAttribute('aria-pressed', 'true');
  kategori = c.dataset.kat;
  filtrer();
}));
"""


def generer_butik_html(alle_tilbud: list) -> str:
    """Bygger HTML-siden med tilbud grupperet pr. butik, varer sorteret A-Å."""

    pr_butik = defaultdict(list)
    for t in alle_tilbud:
        pr_butik[t["butik"]].append(t)

    butiksnavne = sorted(pr_butik.keys(), key=_sorter_nøgle)

    blokke = []
    for butik in butiksnavne:
        tilbud = sorted(pr_butik[butik], key=lambda t: _sorter_nøgle(t["vare"]))
        farve = BUTIK_FARVER.get(butik, "#8A9A90")

        rækker = []
        for t in tilbud:
            norm = (
                f'{t["norm_pris"]:.2f} {t["norm_label"]}'.replace(".", ",")
                if t.get("norm_pris")
                else ""
            )
            udlob = (
                f'<span class="udlob">{_kort_dato(t["gyldig_til"])}</span>'
                if t.get("gyldig_til")
                else '<span class="udlob"></span>'
            )
            rækker.append(
                f'<div class="tilbud-butik">'
                f'<span class="vare-cat">{t["vare"]}</span>'
                f'<span class="navn">{t["navn"]}</span>'
                f'<span class="pris">{_pris(t["pris"])}</span>'
                f'<span class="norm">{norm}</span>'
                f'{udlob}'
                f'</div>'
            )

        antal = len(tilbud)
        blokke.append(
            f'<section class="butik-sektion">'
            f'<div class="butik-head" style="border-left-color:{farve}">'
            f'<h2 class="butik-title">{butik}</h2>'
            f'<span class="vare-antal">{antal} tilbud</span>'
            f'</div>'
            f'{"".join(rækker)}'
            f'</section>'
        )

    nu = datetime.now()
    uge = nu.isocalendar().week
    antal_butikker = len(butiksnavne)
    antal_tilbud = len(alle_tilbud)

    return f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pantry — uge {uge}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header class="masthead">
    <div class="logo">Pantry</div>
    <div class="masthead-meta">
      Uge {uge}, {nu.year}<br>
      <b>{antal_tilbud}</b> tilbud i <b>{antal_butikker}</b> butikker<br>
      Hentet {nu.strftime("%d.%m kl. %H:%M")}
    </div>
  </header>
  {"".join(blokke)}
</div>
</body>
</html>"""


def generer_liste_html(alle_tilbud: list) -> str:
    """Bygger HTML-siden med tilbud grupperet pr. vare, sorteret A-Å."""

    pr_vare = defaultdict(list)
    for t in alle_tilbud:
        pr_vare[t["vare"]].append(t)

    varenavne = sorted(pr_vare.keys(), key=_sorter_nøgle)

    # Alfabet-index over de bogstaver der faktisk findes
    bogstaver = []
    for navn in varenavne:
        b = _begyndelsesbogstav(navn)
        if b not in bogstaver:
            bogstaver.append(b)

    index_html = "".join(
        f'<a href="#bogstav-{b}">{b}</a>' for b in bogstaver
    )

    blokke = []
    set_bogstav = set()

    for navn in varenavne:
        tilbud = pr_vare[navn]

        # Billigste normaliserede pris markeres
        med_norm = [t for t in tilbud if t.get("norm_pris")]
        bedste = min((t["norm_pris"] for t in med_norm), default=None)

        # Sorter: normaliseret pris først (billigst øverst), derefter stykpris
        tilbud.sort(
            key=lambda t: (t.get("norm_pris") is None, t.get("norm_pris") or t["pris"])
        )

        rækker = []
        for t in tilbud:
            farve = BUTIK_FARVER.get(t["butik"], "#8A9A90")
            er_bedst = bedste is not None and t.get("norm_pris") == bedste

            stamp = (
                '<span class="stamp-celle"><span class="stamp">billigst</span></span>'
                if er_bedst
                else '<span class="stamp-celle"></span>'
            )
            norm = (
                f'{t["norm_pris"]:.2f} {t["norm_label"]}'.replace(".", ",")
                if t.get("norm_pris")
                else ""
            )
            udlob = (
                f'<span class="udlob">{_kort_dato(t["gyldig_til"])}</span>'
                if t.get("gyldig_til")
                else '<span class="udlob"></span>'
            )
            pris_txt = _pris(t["pris"])

            rækker.append(
                f'<div class="tilbud{" bedst" if er_bedst else ""}">'
                f'<span class="flag" style="background:{farve}"></span>'
                f'<span class="butik">{t["butik"]}</span>'
                f'<span class="navn">{t["navn"]}</span>'
                f"{stamp}"
                f'<span class="pris">{pris_txt}</span>'
                f'<span class="norm">{norm}</span>'
                f"{udlob}"
                f"</div>"
            )

        b = _begyndelsesbogstav(navn)
        anker = ""
        if b not in set_bogstav:
            set_bogstav.add(b)
            anker = f' id="bogstav-{b}"'

        søgetekst = (navn + " " + " ".join(t["butik"] + " " + t["navn"] for t in tilbud)).lower()
        kategori = tilbud[0].get("kategori", "mad")
        antal = len(tilbud)

        blokke.append(
            f'<section class="vare"{anker} data-kategori="{kategori}" '
            f'data-soeg="{søgetekst}">'
            f'<div class="vare-head">'
            f'<h2 class="vare-navn">{navn}</h2>'
            f'<span class="vare-antal">{antal} {"tilbud" if antal != 1 else "tilbud"}</span>'
            f"</div>"
            f'{"".join(rækker)}'
            f"</section>"
        )

    nu = datetime.now()
    uge = nu.isocalendar().week
    antal_varer = len(varenavne)
    antal_tilbud = len(alle_tilbud)

    return f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pantry — uge {uge}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <div class="logo">Pantry</div>
    <div class="masthead-meta">
      Uge {uge}, {nu.year}<br>
      <b>{antal_tilbud}</b> tilbud på <b>{antal_varer}</b> varer<br>
      Hentet {nu.strftime("%d.%m kl. %H:%M")}
    </div>
  </header>

  <div class="controls">
    <input id="soeg" class="search" type="search" placeholder="Søg vare eller butik">
    <div class="chips">
      <button class="chip" data-kat="alle" aria-pressed="true">Alle</button>
      <button class="chip" data-kat="mad" aria-pressed="false">Mad</button>
      <button class="chip" data-kat="husholdning" aria-pressed="false">Husholdning</button>
    </div>
  </div>

  <nav class="index">{index_html}</nav>

  {"".join(blokke)}

  <div class="tom" id="tom" style="display:none">Ingen varer matcher søgningen.</div>

</div>
<script>{JS}</script>
</body>
</html>"""
