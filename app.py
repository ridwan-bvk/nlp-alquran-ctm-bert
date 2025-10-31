import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import re
import string
import os

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

@app.route("/preprocess", methods=["POST"])
def preprocess():
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], request.form.get("filename"))
    if not os.path.exists(file_path):
        return {"status": "error", "message": "File tidak ditemukan."}, 400

    df = pd.read_csv(file_path)

    # Ambil konfigurasi dari front-end
    config = request.form
    text_col = "text" if "text" in df.columns else df.columns[-1]
    data = df[text_col].astype(str)

    # Pipeline preprocessing
    if config.get("case_folding") == "true":
        data = data.str.lower()
    if config.get("remove_punct") == "true":
        data = data.apply(lambda x: re.sub(f"[{re.escape(string.punctuation)}]", "", x))
    if config.get("remove_numbers") == "true":
        data = data.apply(lambda x: re.sub(r"\d+", "", x))
    if config.get("stopword") == "true":
        stopwords = set(open("stopwords_id.txt", encoding="utf-8").read().split())
        data = data.apply(lambda x: " ".join([w for w in x.split() if w not in stopwords]))
    if config.get("tokenization") == "true":
        data = data.apply(lambda x: x.split())
    if config.get("stemming") == "true":
        from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        data = data.apply(lambda x: [stemmer.stem(w) for w in x] if isinstance(x, list) else stemmer.stem(x))
    if config.get("lemmatization") == "true":
        # Dummy lemmatization (bisa diganti dengan model NLP)
        data = data

    df["processed_text"] = data
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], "preprocessed_" + os.path.basename(file_path))
    df.to_csv(out_path, index=False)

    return {"status": "success", "file": os.path.basename(out_path)}



if __name__ == "__main__":
    app.run(debug=True)
