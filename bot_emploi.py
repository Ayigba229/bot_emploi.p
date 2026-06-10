import requests
import feedparser
import time

# ==========================
# CONFIGURATION
# ==========================
TOKEN_BOT = "8256624782:AAEdKroa-Xv5kRlnKWtfmdsgODVK7ThuWD4"
CHAT_ID = "7313553663"

FLUX_RSS = [
    "https://remotive.com/remote-jobs/feed",
    "https://jobicy.com/feed"
]

MOTS_BENIN = [
    "benin",
    "bénin",
    "cotonou",
    "porto-novo",
    "parakou",
    "abomey-calavi"
]

MOTS_CANADA = [
    "canada",
    "montreal",
    "montréal",
    "quebec",
    "québec",
    "ottawa",
    "toronto",
    "vancouver"
]

offres_envoyees = set()

# ==========================
# TELEGRAM
# ==========================
def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data, timeout=15)
    except Exception as e:
        print("Erreur Telegram :", e)

# ==========================
# DETECTION PAYS
# ==========================
def est_benin(texte):
    texte = texte.lower()
    return any(mot in texte for mot in MOTS_BENIN)

def est_canada(texte):
    texte = texte.lower()
    return any(mot in texte for mot in MOTS_CANADA)

# ==========================
# ANALYSE RSS
# ==========================
def verifier_offres():

    offres_benin = []
    offres_canada = []
    offres_monde = []

    for flux_url in FLUX_RSS:

        try:
            flux = feedparser.parse(flux_url)

            for offre in flux.entries:

                lien = getattr(offre, "link", "")

                if lien in offres_envoyees:
                    continue

                titre = getattr(offre, "title", "Non précisé")
                description = getattr(offre, "summary", "")

                contenu = f"{titre} {description}"

                if est_benin(contenu):
                    offres_benin.append(offre)

                elif est_canada(contenu):
                    offres_canada.append(offre)

                else:
                    offres_monde.append(offre)

                offres_envoyees.add(lien)

        except Exception as e:
            print("Erreur flux :", e)

    # PRIORITÉ BÉNIN
    for offre in offres_benin:

        message = (
            "🇧🇯 OFFRE PRIORITAIRE BÉNIN\n\n"
            f"📌 Poste : {offre.title}\n\n"
            f"🔗 {offre.link}"
        )

        envoyer_telegram(message)
        time.sleep(2)

    # PRIORITÉ CANADA
    for offre in offres_canada:

        message = (
            "🇨🇦 OFFRE CANADA\n\n"
            f"📌 Poste : {offre.title}\n\n"
            f"🔗 {offre.link}"
        )

        envoyer_telegram(message)
        time.sleep(2)

    # RESTE DU MONDE
    for offre in offres_monde[:10]:

        message = (
            "🌍 OFFRE INTERNATIONALE\n\n"
            f"📌 Poste : {offre.title}\n\n"
            f"🔗 {offre.link}"
        )

        envoyer_telegram(message)
        time.sleep(2)

# ==========================
# BOUCLE PRINCIPALE
# ==========================
print("Bot Emploi démarré...")

while True:

    verifier_offres()

    print("Nouvelle vérification dans 30 minutes...")

    time.sleep(1800)
