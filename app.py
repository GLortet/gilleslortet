import os
import re
import smtplib
import time
from email.message import EmailMessage

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 600
RATE_LIMIT_MAX = 5

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/")
def home():
    return render_template("home.html")


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
