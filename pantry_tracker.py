"""
Pantry Tracker
Finder dagligvarer og husholdningsartikler på tilbud i udvalgte danske butikker.

Krav: pip install requests
Kør:  python pantry_tracker.py
"""

import requests
import smtplib
from collections import defaultdict
from datetime import date
from email.mime.text import MIMEText

from config import ØNSKEDE_BUTIKKER, VARER, MAIL_TIL, MAIL_FRA, MAIL_ADGANGSKODE

API_BASE = "https://squid-api.tjek.com/v2"
HEADERS = {
    "Accept": "application/json",
    "X-Token": "tjek",
}


# ── API ──────────────────────────────────────────────────────────────────────

def hent_tilbud(vare: str, limit: int = 20) -> list[dict]:
    """Henter tilbud fra eTilbudsavis API og filtrerer på land, butik og keywords."""
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


# ── Beregninger ──────────────────────────────────────────────────────────────

def normaliseret_pris(tilbud: dict, enhed: str) -> tuple[float | None, str]:
    """
    Returnerer (normaliseret pris, enhedslabel).
    - kg/l: beregner pris per kg eller liter
    - stk:  returnerer bare stykkpris uden normalisering
    """
    if enhed == "stk":
        return None, "stk"

    try:
        q = tilbud["quantity"]
        pris = tilbud["pricing"]["price"]
        størrelse = q["size"]["from"]
        factor = q["unit"]["si"]["factor"]  # g->kg: 0.001, kg->kg: 1, ml->l: 0.001, l->l: 1
        normaliseret = størrelse * factor
        if normaliseret > 0:
            label = "kr/l" if enhed == "l" else "kr/kg"
            return round(pris / normaliseret, 2), label
    except (KeyError, TypeError, ZeroDivisionError):
        pass

    return None, ""


# ── Data-indsamling ───────────────────────────────────────────────────────────

def indsaml_data() -> dict[str, list[dict]]:
    """Henter alle tilbud og grupperer dem per butik."""
    butik_data: dict[str, list[dict]] = defaultdict(list)

    for vare in VARER:
        print(f"  Søger: {vare}...")
        try:
            tilbud = hent_tilbud(vare)
            enhed = VARER[vare].get("enhed", "kg")
            for t in tilbud:
                norm_pris, label = normaliseret_pris(t, enhed)
                butik_data[t["branding"]["name"]].append({
                    "vare": vare,
                    "navn": t["heading"],
                    "pris": t["pricing"]["price"],
                    "norm_pris": norm_pris,
                    "norm_label": label,
                    "gyldig_til": t.get("run_till", "")[:10],
                })
        except requests.RequestException as e:
            print(f"  ⚠️  Fejl ved '{vare}': {e}")

    return butik_data


# ── Formatering ───────────────────────────────────────────────────────────────

def formater_rapport(butik_data: dict[str, list[dict]]) -> str:
    """Genererer en læsbar tekstrapport grupperet per butik."""
    uge = date.today().isocalendar().week
    år = date.today().year
    linjer = [
        f"🛒 PANTRY TRACKER — Uge {uge}, {år}",
        "=" * 60,
        "",
    ]

    hvis_ingen = True
    for butik in ØNSKEDE_BUTIKKER:
        if butik not in butik_data:
            continue
        hvis_ingen = False
        linjer.append(f"🏪 {butik}")
        linjer.append("-" * 55)
        for item in butik_data[butik]:
            if item["norm_pris"]:
                norm_str = f"({item['norm_pris']} {item['norm_label']})"
            else:
                norm_str = ""
            linjer.append(
                f"  {item['vare']:<22} {item['pris']:>6} kr  "
                f"{norm_str:<20}  —  {item['navn']}"
            )
        linjer.append("")

    if hvis_ingen:
        linjer.append("Ingen tilbud fundet denne uge.")
        linjer.append("")

    # Scoreboard
    tæller = {b: len(v) for b, v in butik_data.items() if b in ØNSKEDE_BUTIKKER}
    linjer += [
        "=" * 60,
        "🏆 TILBUD PER BUTIK DENNE UGE:",
    ]
    for butik, antal in sorted(tæller.items(), key=lambda x: -x[1]):
        bar = "█" * antal
        linjer.append(f"  {butik:<20} {bar} {antal}")

    return "\n".join(linjer)


# ── Mail ──────────────────────────────────────────────────────────────────────

def send_mail(rapport: str):
    """Sender rapporten som mail via Gmail SMTP."""
    if not MAIL_ADGANGSKODE:
        print("Mail ikke konfigureret — springer over.")
        return

    uge = date.today().isocalendar().week
    besked = MIMEText(rapport, "plain", "utf-8")
    besked["Subject"] = f"🛒 Pantry Tracker — Uge {uge}"
    besked["From"] = MAIL_FRA
    besked["To"] = MAIL_TIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(MAIL_FRA, MAIL_ADGANGSKODE)
        server.sendmail(MAIL_FRA, MAIL_TIL, besked.as_string())
    print(f"✅ Mail sendt til {MAIL_TIL}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔍 Henter tilbud...\n")
    butik_data = indsaml_data()

    rapport = formater_rapport(butik_data)
    print("\n" + rapport)

    filnavn = f"pantry_uge{date.today().isocalendar().week}_{date.today().year}.txt"
    with open(filnavn, "w", encoding="utf-8") as f:
        f.write(rapport)
    print(f"\n💾 Gemt som: {filnavn}")

    send_mail(rapport)