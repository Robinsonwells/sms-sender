import os
import logging
from datetime import datetime

from flask import Flask, request, flash, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename

import tools
import settings

app = Flask(__name__)
app.config.from_object("settings")


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {e}", exc_info=True)
    flash(f"An unexpected error occurred: {e}")
    return redirect("/")


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

@app.route('/service-worker.js', methods=['GET'])
def service_worker():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        sid = request.form.get("sid") or settings.TWILIO_SID
        token = request.form.get("token") or settings.TWILIO_TOKEN
        csv_url = request.form.get("csv_url") or settings.CSV_URL

        if sid == "" or token == "":
            flash("Twilio ID and token required")
            return redirect(request.url)

        if not tools.valid_credentials(sid, token):
            flash("Invalid Twilio credentials. Please double check your Twilio account SID and token and try again")
            return redirect(request.url)

        if csv_url:
            if not tools.is_valid_url(csv_url):
                flash("Invalid CSV URL")
                return redirect(request.url)
            number_list = tools.get_number_list_from_url(csv_url)
        else:
            if "file" not in request.files:
                flash("No file selected")
                return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                flash("No file selected")
                return redirect(request.url)

            if file and tools.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                number_list = tools.get_number_list(filename)
                wrong_numbers = tools.check_numbers(number_list, sid, token)

                wrong_set = {tuple(n) for n in wrong_numbers}
                valid_numbers = [n for n in number_list if tuple(n) not in wrong_set]

                if wrong_numbers:
                    with open(settings.LOG_FILE, "a") as log_file:
                        log_string = f"{datetime.now()} - {len(wrong_numbers)} wrong numbers identified."
                        log_file.write(f"\n{log_string}")

                if not valid_numbers and wrong_numbers:
                    return render_template("wrong_numbers.html", number_list=wrong_numbers)

                sent_list = tools.send_messages(valid_numbers, sid, token)

                for row in wrong_numbers:
                    padded = list(row) + [''] * (3 - len(row))
                    padded.append("invalid number")
                    padded.append("")
                    padded.append("Number failed pre-send validation")
                    sent_list.append(padded)

                return render_template("report.html", number_list=sent_list)
            else:
                flash("File type not allowed. Please select a CSV file")
                return redirect(request.url)
    else:
        token_placeholder = "••••••••••••••••••••••••••" if settings.TWILIO_TOKEN else ""
        return render_template(
            "index.html",
            sid_placeholder=settings.TWILIO_SID,
            token_placeholder=token_placeholder,
            csv_url_placeholder=settings.CSV_URL
        )
