# ============================================================
# PANTRY TRACKER — Konfiguration
# Tilføj/fjern varer og butikker her
# ============================================================

ØNSKEDE_BUTIKKER = [
    "Netto",
    "REMA 1000",
    "Lidl",
    "SuperBrugsen",
    "Meny",
    "365discount",
]

# enhed: "kg" (standard), "l" (liter), "stk" (stykpris — ingen normalisering)
VARER = {
    # ── Dåsevarer ────────────────────────────────────────────
    "hakkede tomater": {
        "include": ["tomat", "tomater"],
        "exclude": ["ketchup", "puré", "pure", "passata", "saft", "juice"],
        "enhed": "kg",
    },
    "tomatpuré": {
        "include": ["tomatpuré", "tomat puré"],
        "exclude": ["ketchup", "sauce", "hakkede"],
        "enhed": "kg",
    },
    "kikærter": {
        "include": ["kikært"],
        "exclude": ["pasta", "mel", "chips"],
        "enhed": "kg",
    },
    "kokosmælk": {
        "include": ["kokos"],
        "exclude": ["chips", "flager", "olie", "creme", "yoghurt"],
        "enhed": "l",
    },
    "kokosfløde": {
        "include": ["kokosfløde", "kokos fløde"],
        "exclude": ["chips", "olie"],
        "enhed": "l",
    },
    "linser": {
        "include": ["linser", "linse"],
        "exclude": ["pasta", "mel", "suppe"],
        "enhed": "kg",
    },
    "kidneybønner": {
        "include": ["kidney"],
        "exclude": ["pasta", "chips"],
        "enhed": "kg",
    },
    "sorte bønner": {
        "include": ["sorte bønner", "black beans"],
        "exclude": ["pasta", "chips"],
        "enhed": "kg",
    },
    "røde bønner": {
        "include": ["røde bønner", "blandede bønner"],
        "exclude": ["pasta", "chips"],
        "enhed": "kg",
    },
    "dåsemajs": {
        "include": ["majs"],
        "exclude": ["chips", "popcorn", "tortilla", "mel"],
        "enhed": "kg",
    },
    "tun": {
        "include": ["tun"],
        "exclude": ["salat", "pasta", "pizza", "pålæg"],
        "enhed": "kg",
    },
    "makrel": {
        "include": ["makrel"],
        "exclude": ["salat", "pasta"],
        "enhed": "kg",
    },
    #"sardiner": {
    #    "include": ["sardin"],
    #    "exclude": ["salat", "pasta"],
    #    "enhed": "kg",
    #},
    "soltørrede tomater": {
        "include": ["soltørret", "soltørrede"],
        "exclude": ["sauce", "pesto"],
        "enhed": "kg",
    },

    # ── Tørvarer ─────────────────────────────────────────────
    "pasta": {
        "include": ["pasta", "spaghetti", "penne", "fusilli", "tagliatelle"],
        "exclude": ["sauce", "ret", "færdig", "instant", "suppe"],
        "enhed": "kg",
    },
    "ris": {
        "include": ["ris"],
        "exclude": ["risotto", "risengrød", "rispudding", "rismel", "riskage", "ristet", "rispapir"],
        "enhed": "kg",
    },
    "basmatiris": {
        "include": ["basmati"],
        "exclude": [],
        "enhed": "kg",
    },
    "couscous": {
        "include": ["couscous"],
        "exclude": ["færdig", "ret"],
        "enhed": "kg",
    },
    "quinoa": {
        "include": ["quinoa"],
        "exclude": ["færdig", "ret"],
        "enhed": "kg",
    },
    "havregryn": {
        "include": ["havregryn"],
        "exclude": ["bar", "kiks", "færdig"],
        "enhed": "kg",
    },
    "müsli": {
        "include": ["müsli", "musli", "granola"],
        "exclude": ["bar", "færdig"],
        "enhed": "kg",
    },

    # ── Nødder & frø ─────────────────────────────────────────
    "mandler": {
        "include": ["mandler", "mandel"],
        "exclude": ["mel", "mælk", "marcipan", "likør", "olie"],
        "enhed": "kg",
    },
    "cashewnødder": {
        "include": ["cashew"],
        "exclude": ["mel", "olie"],
        "enhed": "kg",
    },
    "valnødder": {
        "include": ["valnød"],
        "exclude": ["mel", "olie"],
        "enhed": "kg",
    },
    "jordnødder": {
        "include": ["jordnød"],
        "exclude": ["smør", "olie", "sauce"],
        "enhed": "kg",
    },
    "blandede nødder": {
        "include": ["blandede nødder", "mixed nuts", "nøddemix"],
        "exclude": ["mel", "olie"],
        "enhed": "kg",
    },
    "chiafrø": {
        "include": ["chia"],
        "exclude": [],
        "enhed": "kg",
    },
    "hørfrø": {
        "include": ["hørfrø", "hør frø"],
        "exclude": [],
        "enhed": "kg",
    },
    "solsikkekerner": {
        "include": ["solsikke"],
        "exclude": ["olie", "brød"],
        "enhed": "kg",
    },

    # ── Olier, eddike & saucer ───────────────────────────────
    "olivenolie": {
        "include": ["olivenolie", "oliven olie"],
        "exclude": ["spray", "dressing"],
        "enhed": "l",
    },
    "kokosolie": {
        "include": ["kokosolie", "kokos olie"],
        "exclude": [],
        "enhed": "l",
    },
    "sojasauce": {
        "include": ["soja", "soy sauce", "soysauce"],
        "exclude": ["bønner", "mælk"],
        "enhed": "l",
    },
    #"eddike": {
    #    "include": ["eddike"],
    #    "exclude": ["chips", "dressing"],
    #    "enhed": "l",
    #},
    "honning": {
        "include": ["honning"],
        "exclude": ["chips", "dressing", "shampoo"],
        "enhed": "kg",
    },

    # ── Mælkealternativer ────────────────────────────────────
    "havredrik": {
        "include": ["havre"],
        "exclude": ["grød", "flager", "mel", "kiks", "morgenmad"],
        "enhed": "l",
    },
    "sojamælk": {
        "include": ["sojamælk", "soja mælk"],
        "exclude": ["sauce", "yoghurt"],
        "enhed": "l",
    },
    "mandelmælk": {
        "include": ["mandelmælk", "mandel mælk"],
        "exclude": [],
        "enhed": "l",
    },

    # ── Pålæg & smør ─────────────────────────────────────────
    "peanutbutter": {
        "include": ["peanut", "jordnøddesmør"],
        "exclude": ["chips", "sauce", "olie"],
        "enhed": "kg",
    },
    #"mørk chokolade": {
    #    "include": ["mørk chokolade", "dark chocolate"],
    #    "exclude": ["kage", "is", "pulver", "mousse"],
    #    "enhed": "kg",
    #},

    # ── Bouillon ─────────────────────────────────────────────
    "bouillon": {
        "include": ["bouillon", "fond"],
        "exclude": ["suppe", "færdig", "nudler"],
        "enhed": "stk",
    },

    # ── Husholdning ──────────────────────────────────────────
    "toiletpapir": {
        "include": ["toiletpapir", "toilet papir", "wc papir"],
        "exclude": [],
        "enhed": "stk",
    },
    "køkkenrulle": {
        "include": ["køkkenrulle", "køkken rulle"],
        "exclude": [],
        "enhed": "stk",
    },
    "opvaskemiddel": {
        "include": ["opvaskemiddel", "opvasketabs", "opvasketablet"],
        "exclude": [],
        "enhed": "stk",
    },
    "vaskemiddel": {
        "include": ["vaskemiddel", "vaskepulver", "vasketabs", "vaske tabs"],
        "exclude": [],
        "enhed": "stk",
    },
    "sæbe": {
        "include": ["håndsæbe", "flydende sæbe"],
        "exclude": ["shampoo", "shower", "bad"],
        "enhed": "stk",
    },

    # ── Pleje ────────────────────────────────────────────────
    "tandpasta": {
        "include": ["tandpasta", "tand pasta"],
        "exclude": [],
        "enhed": "stk",
    },
    "shampoo": {
        "include": ["shampoo"],
        "exclude": [],
        "enhed": "stk",
    },
    "deodorant": {
        "include": ["deodorant"],
        "exclude": [],
        "enhed": "stk",
    },
}

# ── Mail-konfiguration ───────────────────────────────────────
MAIL_TIL = "din@email.dk"
MAIL_FRA = "din.gmail@gmail.com"
MAIL_ADGANGSKODE = ""  # Gmail App Password