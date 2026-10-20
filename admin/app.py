from flask import Flask, render_template, request, redirect, session
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


app = Flask(__name__)

app.secret_key = "assistly-demo-secret"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "anthropic/claude-sonnet-4",
    "google/gemini-2.5-flash"
]


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["logged_in"] = True

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="نام کاربری یا رمز عبور اشتباه است."
        )

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect("/")

    requests = []

    requests_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "requests.txt"
    )

    if os.path.exists(requests_file):

        with open(
            requests_file,
            "r",
            encoding="utf-8"
        ) as file:

            requests = [
                line.strip()
                for line in file
                if line.strip()
            ]

    return render_template(
        "dashboard.html",
        requests=requests,
        models=MODELS,
        current_model=config.CURRENT_MODEL
    )


@app.route("/change-model", methods=["POST"])
def change_model():

    if not session.get("logged_in"):
        return redirect("/")

    selected_model = request.form.get("model")

    if selected_model in MODELS:

        config.CURRENT_MODEL = selected_model

        with open(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                ),
                "config.py"
            ),
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                f'CURRENT_MODEL = "{selected_model}"\n'
            )

    return redirect("/dashboard")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":

    print("Assistly Admin Panel is running...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )