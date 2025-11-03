import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import re
import string
import os
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

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
        return {"status": "error", "message": "Tidak ada file diunggah."}, 400
        # return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename == "":
        flash("Pilih file terlebih dahulu.", "warning")
        return {"status": "error", "message": "Nama file kosong."}, 400
        # return redirect(url_for("index"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dest = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(dest)
        flash(f"File '{filename}' berhasil diunggah.", "success")
        return {"status": "success", "filename": filename}
        # Di sini kamu bisa trigger proses ekstraksi teks / RAG / topic modeling asinkron
        # return redirect(url_for("index"))
    else:
        flash("Format file tidak didukung. Hanya PDF, CSV, TXT.", "danger")
        return {"status": "error", "message": "Format file tidak didukung."}, 400
        # return redirect(url_for("index"))

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
        try:
            # Gunakan file stopwords jika ada
            with open("stopwords_id.txt", encoding="utf-8") as f:
                stopwords = set(f.read().split())
            print("[INFO] Menggunakan stopwords dari stopwords_id.txt")
        except FileNotFoundError:
            # fallback otomatis ke Sastrawi
            factory = StopWordRemoverFactory()
            stopwords = set(factory.get_stop_words())
            print("[INFO] File stopwords_id.txt tidak ditemukan → menggunakan Sastrawi bawaan")
    if config.get("tokenization") == "true":
        data = data.apply(lambda x: x.split())
    if config.get("stemming") == "true":
       
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

@app.route("/analyze_model", methods=["POST"])
def analyze_model():
    from flask import request, jsonify
    import os, pandas as pd

    filename = request.form.get("filename")
    model_type = request.form.get("model")

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File hasil preprocessing tidak ditemukan."}), 400

    df = pd.read_csv(file_path)
    text_col = "processed_text" if "processed_text" in df.columns else df.columns[-1]
    texts = df[text_col].astype(str).tolist()

    topics = []

    try:
        # ======== LDA ==========
        if model_type == "lda":
            from sklearn.decomposition import LatentDirichletAllocation
            from sklearn.feature_extraction.text import CountVectorizer

            vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
            X = vectorizer.fit_transform(texts)
            lda = LatentDirichletAllocation(n_components=5, random_state=42)
            lda.fit(X)

            for idx, topic in enumerate(lda.components_):
                words = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[:-10 - 1:-1]]
                topics.append(f"<strong>Topik {idx+1}:</strong> {', '.join(words)}")

        # ======== CTM (Correlated Topic Model) ==========
        elif model_type == "ctm":
            try:
                import tomotopy as tp
                model = tp.CTModel(k=5, seed=42)

                # Tokenisasi sederhana
                for doc in texts:
                    tokens = [t.lower() for t in str(doc).split() if len(t) > 2]
                    if tokens:
                        model.add_doc(tokens)

                model.train(0)
                for i in range(100):
                    model.train(10)
                print(f"[INFO] Log-likelihood: {model.ll_per_word}")

                # Ambil topik
                for k in range(model.k):
                    top_words = [w for w, _ in model.get_topic_words(k, top_n=10)]
                    topics.append(f"<strong>Topik {k+1}:</strong> {', '.join(top_words)}")

            except Exception as e:
                return jsonify({"status": "error", "message": f"Gagal menjalankan Correlated Topic Model: {str(e)}"}), 500

        # ======== BERTopic ==========
        elif model_type == "bertopic":
            from bertopic import BERTopic
            topic_model = BERTopic(language="indonesian")
            topic_model.fit(texts)
            info = topic_model.get_topic_info().head(5)
            for _, row in info.iterrows():
                topics.append(f"<strong>{row['Name']}</strong>: {row['Representation']}")

        else:
            return jsonify({"status": "error", "message": "Model tidak dikenali."}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Terjadi kesalahan: {str(e)}"}), 500

    html = "<div class='space-y-3'>" + "".join([
        f"<div class='bg-emerald-50 p-3 rounded-lg border border-emerald-200'>{t}</div>"
        for t in topics
    ]) + "</div>"

    return jsonify({"status": "success", "html": html})



if __name__ == "__main__":
    app.run(debug=True)
