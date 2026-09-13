"""
Pantry Tracker — HTML Rapport Generator
Kør efter pantry_tracker.py for at generere en visuel rapport.

Krav: pip install requests
Kør:  python generate_rapport.py
"""

import requests
from collections import defaultdict
from datetime import date

from config import ØNSKEDE_BUTIKKER, VARER

API_BASE = "https://squid-api.tjek.com/v2"
HEADERS = {"Accept": "application/json", "X-Token": "tjek"}

# Hvilke varer er mad vs husholdning
MAD_VARER = {
    "hakkede tomater", "tomatpuré", "kikærter", "kokosmælk", "kokosfløde",
    "linser", "kidneybønner", "sorte bønner", "røde bønner", "dåsemajs",
    "tun", "makrel", "sardiner", "soltørrede tomater", "pasta", "ris",
    "basmatiris", "couscous", "quinoa", "havregryn", "müsli", "mandler",
    "cashewnødder", "valnødder", "jordnødder", "blandede nødder", "chiafrø",
    "hørfrø", "solsikkekerner", "olivenolie", "kokosolie", "sojasauce",
    "eddike", "honning", "havremælk", "sojamælk", "mandelmælk",
    "peanutbutter", "mørk chokolade", "bouillon",
    "mælk", "skyr", "bær",
}
HUSHOLDNING_VARER = {
    "toiletpapir", "køkkenrulle", "opvaskemiddel", "vaskemiddel",
    "sæbe", "tandpasta", "shampoo", "deodorant",
}

BUTIK_FARVER = {
    "Netto":        "#FFD950",
    "REMA 1000":    "#cc0000",
    "Lidl":         "#0347a1",
    "SuperBrugsen": "#00843D",
    "Meny":         "#e8000d",
    "365discount":  "#ff6600",
}

def hent_tilbud(vare, limit=20):
    r = requests.get(
        f"{API_BASE}/offers/search",
        headers=HEADERS,
        params={"query": vare, "limit": limit, "r_locale": "da_DK"},
        timeout=10,
    )
    r.raise_for_status()
    include_kw = VARER[vare]["include"]
    exclude_kw = VARER[vare]["exclude"]
    resultater = []
    for t in r.json():
        if t["dealer"]["country"]["id"] != "DK":
            continue
        if t["branding"]["name"] not in ØNSKEDE_BUTIKKER:
            continue
        heading_lower = t["heading"].lower()
        if not any(kw in heading_lower for kw in include_kw):
            continue
        if any(kw in heading_lower for kw in exclude_kw):
            continue
        resultater.append(t)
    return resultater

def normaliseret_pris(tilbud, enhed):
    if enhed == "stk":
        return None, ""
    try:
        q = tilbud["quantity"]
        pris = tilbud["pricing"]["price"]
        størrelse = q["size"]["from"]
        factor = q["unit"]["si"]["factor"]
        norm = størrelse * factor
        if norm > 0:
            label = "kr/l" if enhed == "l" else "kr/kg"
            return round(pris / norm, 2), label
    except (KeyError, TypeError, ZeroDivisionError):
        pass
    return None, ""

def indsaml_data():
    print("Henter tilbud...")
    alle = []
    for vare in VARER:
        print(f"  {vare}...")
        try:
            tilbud = hent_tilbud(vare)
            enhed = VARER[vare].get("enhed", "kg")
            for t in tilbud:
                norm_pris, norm_label = normaliseret_pris(t, enhed)
                alle.append({
                    "vare": vare,
                    "navn": t["heading"],
                    "pris": t["pricing"]["price"],
                    "norm_pris": norm_pris,
                    "norm_label": norm_label,
                    "butik": t["branding"]["name"],
                    "gyldig_til": t.get("run_till", "")[:10],
                    "kategori": "mad" if vare in MAD_VARER else "husholdning",
                })
        except Exception as e:
            print(f"  ⚠️  Fejl: {e}")
    return alle

def generer_html(alle_tilbud):
    uge = date.today().isocalendar().week
    år = date.today().year

    def lav_sektion(tilbud_liste, kategori_id):
        butik_data = defaultdict(list)
        for t in tilbud_liste:
            butik_data[t["butik"]].append(t)

        kort_html = ""
        for butik in ØNSKEDE_BUTIKKER:
            if butik not in butik_data:
                continue
            farve = BUTIK_FARVER.get(butik, "#888")
            items = butik_data[butik]
            antal = len(items)
            rækker = ""
            for item in items:
                norm = f'<span class="norm">{item["norm_pris"]} {item["norm_label"]}</span>' if item["norm_pris"] else ""
                udløb = f'<span class="udlob">til {item["gyldig_til"]}</span>' if item["gyldig_til"] else ""
                rækker += f"""
                <div class="item-row">
                    <span class="item-vare">{item['vare']}</span>
                    <span class="item-navn">{item['navn']}</span>
                    <span class="item-pris">{item['pris']} kr {norm}</span>
                    {udløb}
                </div>"""

            kort_html += f"""
            <div class="butik-kort" style="--butik-farve: {farve}">
                <div class="kort-header">
                    <div class="butik-navn">{butik}</div>
                    <div class="antal-badge">{antal} tilbud</div>
                </div>
                <div class="kort-items">{rækker}</div>
            </div>"""

        # Scoreboard data til bar chart
        score_data = {b: len(butik_data[b]) for b in ØNSKEDE_BUTIKKER if b in butik_data}
        max_antal = max(score_data.values()) if score_data else 1
        bars = ""
        for butik, antal in sorted(score_data.items(), key=lambda x: -x[1]):
            farve = BUTIK_FARVER.get(butik, "#888")
            pct = (antal / max_antal) * 100
            bars += f"""
            <div class="bar-row">
                <span class="bar-label">{butik}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{pct}%; background:{farve}"></div>
                </div>
                <span class="bar-antal">{antal}</span>
            </div>"""

        return f"""
        <div class="sektion" id="{kategori_id}">
            <div class="scoreboard">
                <h2 class="score-titel">Tilbud per butik</h2>
                <div class="bars">{bars}</div>
            </div>
            <div class="kort-grid">{kort_html}</div>
        </div>"""

    mad_tilbud = [t for t in alle_tilbud if t["kategori"] == "mad"]
    hus_tilbud = [t for t in alle_tilbud if t["kategori"] == "husholdning"]

    mad_html = lav_sektion(mad_tilbud, "mad")
    hus_html = lav_sektion(hus_tilbud, "husholdning")

    return f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pantry Tracker — Uge {uge}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: #0f0f0f;
    --surface: #1a1a1a;
    --surface2: #222;
    --border: #2e2e2e;
    --text: #f0f0f0;
    --muted: #888;
    --accent: #e8ff47;
    --font-display: 'Syne', sans-serif;
    --font-mono: 'DM Mono', monospace;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-mono);
    min-height: 100vh;
  }}

  /* ── Header ── */
  .header {{
    padding: 3rem 2rem 2rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
  }}
  .header-titel {{
    font-family: var(--font-display);
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.02em;
  }}
  .header-titel span {{ color: var(--accent); }}
  .header-meta {{
    font-size: 0.8rem;
    color: var(--muted);
    text-align: right;
  }}

  /* ── Tabs ── */
  .tabs {{
    display: flex;
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
  }}
  .tab {{
    padding: 1rem 1.5rem;
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--muted);
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
  .tab:hover {{ color: var(--text); }}
  .tab.aktiv {{
    color: var(--accent);
    border-bottom-color: var(--accent);
  }}

  /* ── Sektioner ── */
  .sektion {{ display: none; padding: 2rem; }}
  .sektion.vis {{ display: block; }}

  /* ── Scoreboard ── */
  .scoreboard {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    max-width: 600px;
  }}
  .score-titel {{
    font-family: var(--font-display);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 1.2rem;
  }}
  .bar-row {{
    display: grid;
    grid-template-columns: 130px 1fr 40px;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.6rem;
  }}
  .bar-label {{ font-size: 0.8rem; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .bar-track {{ background: var(--border); border-radius: 4px; height: 8px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }}
  .bar-antal {{ font-size: 0.85rem; font-weight: 500; color: var(--text); text-align: right; }}

  /* ── Butik kort grid ── */
  .kort-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.25rem;
  }}
  .butik-kort {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--butik-farve);
    border-radius: 12px;
    overflow: hidden;
  }}
  .kort-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
  }}
  .butik-navn {{
    font-family: var(--font-display);
    font-size: 1.05rem;
    font-weight: 700;
  }}
  .antal-badge {{
    background: var(--surface2);
    color: var(--accent);
    font-size: 0.75rem;
    padding: 0.25rem 0.6rem;
    border-radius: 99px;
    font-weight: 500;
  }}
  .kort-items {{ padding: 0.5rem 0; }}
  .item-row {{
    display: grid;
    grid-template-columns: 1fr;
    padding: 0.6rem 1.25rem;
    border-bottom: 1px solid var(--border);
    gap: 0.15rem;
  }}
  .item-row:last-child {{ border-bottom: none; }}
  .item-vare {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
  }}
  .item-navn {{ font-size: 0.88rem; color: var(--text); }}
  .item-pris {{
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--accent);
  }}
  .norm {{ font-size: 0.75rem; color: var(--muted); font-weight: 400; }}
  .udlob {{ font-size: 0.7rem; color: var(--muted); }}

  /* ── Ingen data ── */
  .ingen {{ color: var(--muted); font-size: 0.9rem; padding: 2rem; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="header-titel">Pantry<span>.</span>dk</div>
  </div>
  <div class="header-meta">
    Uge {uge}, {år}<br>
    {len(alle_tilbud)} tilbud fundet
  </div>
</div>

<div class="tabs">
  <div class="tab aktiv" onclick="skiftTab('mad', this)">🥫 Madvarer</div>
  <div class="tab" onclick="skiftTab('husholdning', this)">🧴 Husholdning</div>
</div>

{mad_html}
{hus_html}

<script>
  // Vis mad som default
  document.getElementById('mad').classList.add('vis');

  function skiftTab(id, el) {{
    document.querySelectorAll('.sektion').forEach(s => s.classList.remove('vis'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('aktiv'));
    document.getElementById(id).classList.add('vis');
    el.classList.add('aktiv');
  }}
</script>
</body>
</html>"""

if __name__ == "__main__":
    alle = indsaml_data()
    html = generer_html(alle)
    filnavn = f"pantry_rapport_uge{date.today().isocalendar().week}_{date.today().year}.html"
    with open(filnavn, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ Rapport gemt som: {filnavn}")
    print("Åbn filen i din browser!")
    