from flask import Flask, render_template

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
