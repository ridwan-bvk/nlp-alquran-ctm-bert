import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "csv", "txt"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "replace_this_with_a_random_secret"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("Tidak ada file yang diunggah.", "danger")
        return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename == "":
        flash("Pilih file terlebih dahulu.", "warning")
        return redirect(url_for("index"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dest = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(dest)
        flash(f"File '{filename}' berhasil diunggah.", "success")
        # Di sini kamu bisa trigger proses ekstraksi teks / RAG / topic modeling asinkron
        return redirect(url_for("index"))
    else:
        flash("Format file tidak didukung. Hanya PDF, CSV, TXT.", "danger")
        return redirect(url_for("index"))

@app.route("/analyze/general")
def analyze_general():
    # placeholder - replace with logic memanggil pipeline LDA/BERTopic
    return render_template("index.html", info="Mode Analisis Umum (placeholder)")

@app.route("/analyze/quran")
def analyze_quran():
    # placeholder for Quran-specific flow
    # return render_template("index.html", info="Mode Al-Qur'an & Hadis (placeholder)")
    return render_template("analyze_quran.html")

@app.route("/analyze/universal")
def analyze_universal():
    # placeholder for universal religious text flow
    return render_template("index.html", info="Mode Teks Keagamaan Universal (placeholder)")

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
