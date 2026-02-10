import json
import os
import re
import smtplib
import time
from datetime import datetime, timezone
from email.message import EmailMessage

from flask import Flask, Response, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000

SITE_URL = "https://www.gilleslortet.fr"
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 600
RATE_LIMIT_MAX = 5
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PUBLIC_ROUTES = ["home", "approche", "pcm", "circuitvital", "a_propos", "contact"]


def absolute_url(path: str) -> str:
    return f"{SITE_URL}{path}"


def website_schema():
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": absolute_url("/#website"),
                "url": SITE_URL,
                "name": "Gilles Lortet",
                "inLanguage": "fr-FR",
            },
            {
                "@type": "Person",
                "@id": absolute_url("/#person"),
                "name": "Gilles Lortet",
                "url": SITE_URL,
                "email": "mailto:contact@gilleslortet.fr",
                "jobTitle": "Consultant senior en communication et décision sous pression",
                "knowsAbout": [
                    "Process Communication Model",
                    "Communication sous pression",
                    "Décision managériale",
                    "Interventions collectives",
                ],
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "FR",
                    "addressRegion": "Grand Est",
                },
            },
            {
                "@type": "ProfessionalService",
                "@id": absolute_url("/#service"),
                "name": "Gilles Lortet - Communication & décision sous pression",
                "url": SITE_URL,
                "areaServed": ["France", "Grand Est"],
                "serviceType": [
                    "Accompagnement individuel dirigeants",
                    "Interventions collectives communication et décision",
                ],
                "provider": {"@id": absolute_url("/#person")},
                "makesOffer": [
                    {
                        "@type": "Offer",
                        "@id": absolute_url("/approche#offre-individuelle"),
                        "name": "Clarté Managériale Individuelle",
                        "description": "Décider et communiquer avec clarté, même sous pression. Entretien individuel confidentiel de 1h30 à 2h.",
                        "price": "510",
                        "priceCurrency": "EUR",
                        "availability": "https://schema.org/InStock",
                        "url": absolute_url("/approche#offre-individuelle"),
                        "eligibleRegion": "FR",
                    },
                    {
                        "@type": "ItemList",
                        "@id": absolute_url("/pcm#offre-collective"),
                        "name": "Communication & décision sous pression (collectif)",
                        "url": absolute_url("/pcm#offre-collective"),
                        "itemListElement": [
                            {
                                "@type": "Offer",
                                "position": 1,
                                "name": "Niveau 1 - Sensibilisation / cadrage",
                                "description": "Format court, par exemple une journée.",
                                "url": absolute_url("/pcm#niveau-1"),
                            },
                            {
                                "@type": "Offer",
                                "position": 2,
                                "name": "Niveau 2 - Approfondissement opérationnel",
                                "description": "Intervention de 2 à 4 jours.",
                                "url": absolute_url("/pcm#niveau-2"),
                            },
                            {
                                "@type": "Offer",
                                "position": 3,
                                "name": "Niveau 3 - Accompagnement dans la durée",
                                "description": "Accompagnement construit sur mesure selon les enjeux.",
                                "url": absolute_url("/pcm#niveau-3"),
                            },
                        ],
                    },
                ],
            },
        ],
    }


@app.context_processor
def seo_context():
    path = request.path or "/"
    canonical = absolute_url(path)
    og_image = absolute_url(url_for("static", filename="images/hero.svg"))

    crumbs = [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": absolute_url("/")}
    ]
    if path != "/":
        name = path.strip("/").replace("-", " ").title()
        crumbs.append(
            {"@type": "ListItem", "position": 2, "name": name, "item": canonical}
        )

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": crumbs,
    }

    return {
        "site_url": SITE_URL,
        "canonical_url": canonical,
        "default_og_image": og_image,
        "organization_schema": json.dumps(website_schema(), ensure_ascii=False),
        "breadcrumb_schema": json.dumps(breadcrumb_schema, ensure_ascii=False),
        "current_year": datetime.now(timezone.utc).year,
    }


@app.after_request
def add_cache_headers(response):
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.path in {"/", "/approche", "/pcm", "/circuitvital", "/a-propos", "/contact"}:
        response.headers["Cache-Control"] = "public, max-age=300"
    elif request.path in {"/robots.txt", "/sitemap.xml"}:
        response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/index.html")
def home_index():
    return redirect(url_for("home"), code=301)


@app.route("/approche")
def approche():
    return render_template("approche.html")


@app.route("/pcm")
def pcm():
    return render_template("pcm.html")


@app.route("/circuitvital")
def circuitvital():
    return render_template("circuitvital.html")


@app.route("/a-propos")
def a_propos():
    return render_template("a-propos.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/sitemap.xml")
def sitemap():
    pages = []
    now = datetime.now(timezone.utc).date().isoformat()
    for route in PUBLIC_ROUTES:
        loc = absolute_url(url_for(route))
        pages.append(f"<url><loc>{loc}</loc><lastmod>{now}</lastmod></url>")
    xml = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
        f"{''.join(pages)}"
        "</urlset>"
    )
    return Response(xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /api/",
            f"Sitemap: {absolute_url('/sitemap.xml')}",
        ]
    )
    return Response(content, mimetype="text/plain")


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="images/hero.svg"), code=301)


@app.route("/api/contact", methods=["POST"])
def contact_api():
    if request.form.get("website"):
        return ("", 204)

    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = (forwarded_for or request.remote_addr or "unknown").split(",")[0].strip()
    now = time.time()
    attempts = RATE_LIMIT.get(client_ip, [])
    attempts = [stamp for stamp in attempts if now - stamp < RATE_LIMIT_WINDOW]
    if len(attempts) >= RATE_LIMIT_MAX:
        return jsonify({"ok": False, "message": "Merci de patienter quelques minutes avant de réessayer."}), 429
    attempts.append(now)
    RATE_LIMIT[client_ip] = attempts

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    organization = request.form.get("organization", "").strip()
    role = request.form.get("role", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    consent = request.form.get("consent")

    errors = []
    if not full_name:
        errors.append("Merci d'indiquer votre nom.")
    if not email or not EMAIL_RE.match(email):
        errors.append("Merci de saisir un email valide.")
    if not subject:
        errors.append("Merci d'indiquer un sujet.")
    if len(message) < 50:
        errors.append("Merci de détailler votre message (50 caractères minimum).")
    if len(message) > 4000:
        errors.append("Merci de limiter votre message à 4000 caractères.")
    if not consent:
        errors.append("Merci de confirmer votre accord pour être recontacté.")

    if errors:
        return jsonify({"ok": False, "message": " ".join(errors)}), 400

    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    contact_to = os.getenv("CONTACT_TO")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_from = os.getenv("CONTACT_FROM") or smtp_user or contact_to

    if smtp_host and smtp_user and smtp_password and contact_to and smtp_from:
        email_message = EmailMessage()
        email_message["Subject"] = f"[Contact] {subject}"
        email_message["From"] = smtp_from
        email_message["To"] = contact_to
        email_message["Reply-To"] = email

        body_lines = [
            f"Nom: {full_name}",
            f"Email: {email}",
            f"Téléphone: {phone or 'Non renseigné'}",
            f"Organisation: {organization or 'Non renseignée'}",
            f"Rôle: {role or 'Non renseigné'}",
            f"Source: {request.form.get('source', '').strip() or 'inconnue'}",
            "",
            message,
        ]
        email_message.set_content("\n".join(body_lines))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
            if smtp_use_tls:
                smtp.starttls()
            smtp.login(smtp_user, smtp_password)
            smtp.send_message(email_message)

    return jsonify({"ok": True, "message": "Merci, votre demande a bien été envoyée."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
