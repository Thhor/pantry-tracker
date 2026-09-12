"""
Pantry Tracker - eTilbudsavis
Søger efter dåsevarer på tilbud og sender en ugentlig mail-oversigt.

Krav: pip install requests
"""

import requests
import json
from datetime import date

# --- Konfiguration ---
VARER = [
    "hakkede tomater",
    "kikærter",
    "kokosmælk",
    "linser",
    "kidneybønner",
    "tun",
]

API_BASE = "https://squid-api.tjek.com/v2"
HEADERS = {
    "Accept": "application/json",
    "X-Token": "tjek",  # Offentlig token brugt af eTilbudsavis-appen
}


def søg_tilbud(vare: str, limit: int = 20) -> list[dict]:
    """Søg efter en vare og returnér aktuelle tilbud."""
    url = f"{API_BASE}/offers"
    params = {
        "query": vare,
        "limit": limit,
        "order_by": "price",
    }
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def find_bedste_tilbud(tilbud: list[dict]) -> list[dict]:
    """Filtrér og sorter tilbud — kun dem med pris og navn."""
    relevante = []
    for t in tilbud:
        if t.get("pricing") and t.get("heading"):
            relevante.append({
                "navn": t["heading"],
                "butik": t.get("branding", {}).get("name", "Ukendt"),
                "pris": t["pricing"].get("price", 0),
                "beskrivelse": t.get("description", ""),
                "gyldig_til": t.get("run_till", ""),
            })
    # Sorter efter pris
    relevante.sort(key=lambda x: x["pris"])
    return relevante[:3]  # Top 3 billigste


def generer_rapport() -> str:
    """Generér en tekstrapport over ugens bedste dåsetilbud."""
    rapport_linjer = [
        f"🛒 PANTRY TRACKER — Uge {date.today().isocalendar().week}, {date.today().year}",
        "=" * 55,
        "",
    ]

    alle_tilbud = {}

    for vare in VARER:
        print(f"Søger efter: {vare}...")
        try:
            tilbud = søg_tilbud(vare)
            bedste = find_bedste_tilbud(tilbud)
            alle_tilbud[vare] = bedste

            rapport_linjer.append(f"📦 {vare.upper()}")
            if bedste:
                for t in bedste:
                    rapport_linjer.append(
                        f"   {t['butik']:<15} {t['pris']:>6.2f} kr  —  {t['navn']}"
                    )
            else:
                rapport_linjer.append("   Ingen tilbud fundet denne uge")
            rapport_linjer.append("")

        except requests.RequestException as e:
            rapport_linjer.append(f"   ⚠️  Fejl ved søgning: {e}")
            rapport_linjer.append("")

    # Opsummering: hvilken butik har flest tilbud?
    butik_tæller: dict[str, int] = {}
    for vare_tilbud in alle_tilbud.values():
        for t in vare_tilbud:
            butik = t["butik"]
            butik_tæller[butik] = butik_tæller.get(butik, 0) + 1

    if butik_tæller:
        bedste_butik = max(butik_tæller, key=butik_tæller.__getitem__)
        rapport_linjer += [
            "=" * 55,
            f"🏆 BEDSTE BUTIK DENNE UGE: {bedste_butik}",
            f"   ({butik_tæller[bedste_butik]} af dine pantry-varer på tilbud)",
            "",
        ]

    return "\n".join(rapport_linjer)


def send_mail(rapport: str, til: str, fra: str, adgangskode: str):
    """Send rapporten som mail via Gmail SMTP."""
    import smtplib
    from email.mime.text import MIMEText

    besked = MIMEText(rapport, "plain", "utf-8")
    besked["Subject"] = f"🛒 Pantry Tracker — Uge {date.today().isocalendar().week}"
    besked["From"] = fra
    besked["To"] = til

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(fra, adgangskode)
        server.sendmail(fra, til, besked.as_string())
    print(f"Mail sendt til {til} ✅")


if __name__ == "__main__":
    # 1. Generer rapport
    rapport = generer_rapport()
    print(rapport)

    # 2. Gem rapport til fil
    #filnavn = f"pantry_rapport_uge{date.today().isocalendar().week}.txt"
    #with open(filnavn, "w", encoding="utf-8") as f:
    #    f.write(rapport)
    #print(f"\nRapport gemt som: {filnavn}")

    # 3. Send mail (kommenter ud hvis du ikke vil sende endnu)
    # send_mail(
    #     rapport=rapport,
    #     til="din@email.dk",
    #     fra="din.gmail@gmail.com",
    #     adgangskode="dit-app-password",  # Gmail App Password, ikke dit normale password
    # )