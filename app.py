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

@app.route("/get_stopwords")
def get_stopwords():
    """Mengambil daftar stopwords dari file"""
    try:
        with open("stopwords_id.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}
    except FileNotFoundError:
        # Jika file tidak ada, buat default
        default_stopwords = """yang
ke
dari
di
dan
ini
itu
dengan
untuk
tidak
akan
ada
adalah
atau
dalam
bisa
saya
kamu
kita
dia
mereka
bukan
tapi
juga
sudah
saja
boleh
harus
perlu
banyak
sedikit
sekali
sangat
terlalu
amat"""
        with open("stopwords_id.txt", "w", encoding="utf-8") as f:
            f.write(default_stopwords)
        return {"status": "success", "content": default_stopwords}

@app.route("/save_stopwords", methods=["POST"])
def save_stopwords():
    """Menyimpan stopwords ke file"""
    data = request.get_json()
    content = data.get("content", "")
    
    try:
        with open("stopwords_id.txt", "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": "Stopwords berhasil disimpan"}
    except Exception as e:
        return {"status": "error", "message": f"Gagal menyimpan stopwords: {str(e)}"}, 500

@app.route("/reset_stopwords", methods=["POST"])
def reset_stopwords():
    """Reset stopwords ke default"""
    default_stopwords = """yang
ke
dari
di
dan
ini
itu
dengan
untuk
tidak
akan
ada
adalah
atau
dalam
bisa
saya
kamu
kita
dia
mereka
bukan
tapi
juga
sudah
saja
boleh
harus
perlu
banyak
sedikit
sekali
sangat
terlalu
amat"""
    
    try:
        with open("stopwords_id.txt", "w", encoding="utf-8") as f:
            f.write(default_stopwords)
        return {"status": "success", "message": "Stopwords berhasil direset", "content": default_stopwords}
    except Exception as e:
        return {"status": "error", "message": f"Gagal reset stopwords: {str(e)}"}, 500

# @app.route("/list_preprocessed_files")
# def list_preprocessed_files():
#     """Mendapatkan daftar file hasil preprocessing"""
#     import glob
#     files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], 'preprocessed_*'))
#     # Hanya ambil nama file
#     file_names = [os.path.basename(f) for f in files]
#     return {"status": "success", "files": file_names}

# @app.route("/read_preprocessed_file")
# def read_preprocessed_file():
#     """Membaca isi file preprocessing untuk ditampilkan"""
#     filename = request.args.get("filename")
#     if not filename:
#         return {"status": "error", "message": "Filename tidak diberikan"}, 400
    
#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     if not os.path.exists(file_path):
#         return {"status": "error", "message": "File tidak ditemukan"}, 404
    
#     try:
#         df = pd.read_csv(file_path)
#         # Ambil kolom processed_text atau kolom pertama
#         if "processed_text" in df.columns:
#             content = df["processed_text"].head(10).to_string(index=False)  # Ambil 10 baris pertama
#         else:
#             content = df.iloc[:, 0].head(10).to_string(index=False)
        
#         return {"status": "success", "content": content}
#     except Exception as e:
#         return {"status": "error", "message": f"Gagal membaca file: {str(e)}"}, 500

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
         if config.get("stopword") == "true":
            stopwords_set = set()
            
            # Stopwords dari file
            if config.get("stopword_file") == "true":
                try:
                    with open("stopwords_id.txt", encoding="utf-8") as f:
                        file_stopwords = set(f.read().split())
                    stopwords_set.update(file_stopwords)
                    print("[INFO] Menggunakan stopwords dari file stopwords_id.txt")
                except FileNotFoundError:
                    print("[INFO] File stopwords_id.txt tidak ditemukan")
            
            # Stopwords dari Sastrawi
            if config.get("stopword_sastrawi") == "true":
                factory = StopWordRemoverFactory()
                sastrawi_stopwords = set(factory.get_stop_words())
                stopwords_set.update(sastrawi_stopwords)
                print("[INFO] Menggunakan stopwords dari Sastrawi")
            
            # Hapus stopwords
            if stopwords_set:
                data = data.apply(lambda x: " ".join([word for word in x.split() if word not in stopwords_set]))
        # try:
        #     # Gunakan file stopwords jika ada
        #     with open("stopwords_id.txt", encoding="utf-8") as f:
        #         stopwords = set(f.read().split())
        #     print("[INFO] Menggunakan stopwords dari stopwords_id.txt")
        # except FileNotFoundError:
        #     # fallback otomatis ke Sastrawi
        #     factory = StopWordRemoverFactory()
        #     stopwords = set(factory.get_stop_words())
        #     print("[INFO] File stopwords_id.txt tidak ditemukan → menggunakan Sastrawi bawaan")
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

@app.route("/list_preprocessed_files")
def list_preprocessed_files():
    """Mendapatkan daftar file hasil preprocessing"""
    import glob
    try:
        # Cari semua file yang diawali dengan 'preprocessed_'
        files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], 'preprocessed_*'))
        # Urutkan berdasarkan waktu modifikasi (terbaru pertama)
        files.sort(key=os.path.getmtime, reverse=True)
        # Hanya ambil nama file
        file_names = [os.path.basename(f) for f in files]
        return {"status": "success", "files": file_names}
    except Exception as e:
        return {"status": "error", "message": f"Gagal mengambil daftar file: {str(e)}"}, 500

@app.route("/read_preprocessed_file")
def read_preprocessed_file():
    """Membaca isi file preprocessing untuk ditampilkan"""
    filename = request.args.get("filename")
    if not filename:
        return {"status": "error", "message": "Filename tidak diberikan"}, 400
    
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return {"status": "error", "message": "File tidak ditemukan"}, 404
    
    try:
        df = pd.read_csv(file_path)
        # Ambil kolom processed_text atau kolom teks pertama
        if "processed_text" in df.columns:
            content = df["processed_text"].head(20).to_string(index=False)  # Ambil 20 baris pertama
        else:
            # Cari kolom yang berisi teks
            text_columns = [col for col in df.columns if col.lower() in ['text', 'content', 'teks']]
            if text_columns:
                content = df[text_columns[0]].head(20).to_string(index=False)
            else:
                content = df.iloc[:, 0].head(20).to_string(index=False)
        
        return {"status": "success", "content": content, "filename": filename}
    except Exception as e:
        return {"status": "error", "message": f"Gagal membaca file: {str(e)}"}, 500
    
@app.route("/analyze_model", methods=["POST"])
def analyze_model():
    from flask import request, jsonify
    import os, pandas as pd
    import numpy as np
    from collections import Counter
    import json

    filename = request.form.get("filename")
    model_type = request.form.get("model")

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File hasil preprocessing tidak ditemukan."}), 400

    df = pd.read_csv(file_path)
    text_col = "processed_text" if "processed_text" in df.columns else df.columns[-1]
    texts = df[text_col].astype(str).tolist()

    results = {
        "model_type": model_type,
        "topics": [],
        "sources": [],
        "visualization_data": {},
        "search_data": []
    }

    try:
        if model_type == "lda":
            from sklearn.decomposition import LatentDirichletAllocation
            from sklearn.feature_extraction.text import CountVectorizer

            # Vectorize teks
            vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words=None)
            X = vectorizer.fit_transform(texts)
            
            # Train LDA model
            lda = LatentDirichletAllocation(n_components=5, random_state=42, max_iter=10)
            lda.fit(X)
            
            # Hitung distribusi topik per dokumen
            topic_distribution = lda.transform(X)
            
            # Ambil topik dan kata kunci
            feature_names = vectorizer.get_feature_names_out()
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[:-10 - 1:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                word_scores = [topic[i] for i in top_words_idx]
                
                # Hitung persentase dokumen yang dominan pada topik ini
                dominant_topics = topic_distribution.argmax(axis=1)
                topic_percentage = (np.sum(dominant_topics == topic_idx) / len(texts)) * 100
                
                # Cari dokumen yang mewakili topik ini
                topic_docs_idx = np.where(dominant_topics == topic_idx)[0][:3]  # Ambil 3 dokumen pertama
                representative_sources = []
                
                for doc_idx in topic_docs_idx:
                    if doc_idx < len(df):
                        doc_info = {
                            "source": f"Dokumen {doc_idx + 1}",
                            "content_preview": texts[doc_idx][:100] + "..." if len(texts[doc_idx]) > 100 else texts[doc_idx]
                        }
                        # Coba ambil informasi ayat/surat jika ada
                        if 'verse' in df.columns and 'chapter' in df.columns:
                            doc_info["verse"] = f"{df.iloc[doc_idx]['chapter']}:{df.iloc[doc_idx]['verse']}"
                        representative_sources.append(doc_info)
                
                topic_data = {
                    "topic_id": topic_idx + 1,
                    "name": f"Topik {topic_idx + 1}",
                    "keywords": top_words,
                    "word_scores": word_scores.tolist(),
                    "percentage": round(topic_percentage, 1),
                    "representative_sources": representative_sources
                }
                results["topics"].append(topic_data)

            # Data untuk visualisasi
            results["visualization_data"] = {
                "topic_distribution": [topic["percentage"] for topic in results["topics"]],
                "topic_names": [topic["name"] for topic in results["topics"]],
                "model_type": "LDA"
            }

        elif model_type == "ctm":
            try:
                import tomotopy as tp
                
                # Persiapan data untuk CTM
                model = tp.CTModel(k=5, seed=42)
                
                # Tokenisasi dokumen
                for doc in texts:
                    tokens = [t.lower() for t in str(doc).split() if len(t) > 2]
                    if len(tokens) > 0:
                        model.add_doc(tokens)
                
                # Training model
                model.burn_in = 100
                for i in range(0, 100, 10):
                    model.train(10)
                
                # Analisis hasil
                for k in range(model.k):
                    top_words = [word for word, _ in model.get_topic_words(k, top_n=10)]
                    
                    # Hitung persentase dokumen untuk topik ini
                    topic_count = 0
                    for doc in model.docs:
                        topic_dist = doc.get_topic_dist()
                        if np.argmax(topic_dist) == k:
                            topic_count += 1
                    
                    topic_percentage = (topic_count / len(model.docs)) * 100 if model.docs else 0
                    
                    topic_data = {
                        "topic_id": k + 1,
                        "name": f"Topik {k + 1}",
                        "keywords": top_words,
                        "percentage": round(topic_percentage, 1),
                        "representative_sources": []
                    }
                    results["topics"].append(topic_data)
                
                results["visualization_data"] = {
                    "topic_distribution": [topic["percentage"] for topic in results["topics"]],
                    "topic_names": [topic["name"] for topic in results["topics"]],
                    "model_type": "CTM"
                }

            except Exception as e:
                return jsonify({"status": "error", "message": f"Gagal menjalankan Correlated Topic Model: {str(e)}"}), 500

        elif model_type == "bertopic":
            try:
                from bertopic import BERTopic
                
                # Train BERTopic model
                topic_model = BERTopic(language="multilingual", calculate_probabilities=True)
                topics, probabilities = topic_model.fit_transform(texts)
                
                # Dapatkan info topik
                topic_info = topic_model.get_topic_info()
                
                for _, row in topic_info.iterrows():
                    if row['Topic'] != -1:  # Exclude outlier topic
                        topic_words = topic_model.get_topic(row['Topic'])
                        keywords = [word for word, _ in topic_words[:10]]
                        
                        topic_data = {
                            "topic_id": row['Topic'],
                            "name": row['Name'],
                            "keywords": keywords,
                            "percentage": round(row['Count'] / len(texts) * 100, 1),
                            "representative_sources": []
                        }
                        results["topics"].append(topic_data)
                
                results["visualization_data"] = {
                    "topic_distribution": [topic["percentage"] for topic in results["topics"]],
                    "topic_names": [topic["name"] for topic in results["topics"]],
                    "model_type": "BERTopic"
                }

            except Exception as e:
                return jsonify({"status": "error", "message": f"Gagal menjalankan BERTopic: {str(e)}"}), 500

        else:
            return jsonify({"status": "error", "message": "Model tidak dikenali."}), 400

        # Siapkan data untuk pencarian
        for topic in results["topics"]:
            for keyword in topic["keywords"]:
                results["search_data"].append({
                    "keyword": keyword,
                    "topic_id": topic["topic_id"],
                    "topic_name": topic["name"],
                    "percentage": topic["percentage"]
                })

        # Data sumber dokumen
        if len(df) > 0:
            sample_size = min(10, len(df))
            for i in range(sample_size):
                source_info = {
                    "doc_id": i + 1,
                    "preview": texts[i][:150] + "..." if len(texts[i]) > 150 else texts[i]
                }
                # Tambahkan info ayat/surat jika ada
                if 'verse' in df.columns and 'chapter' in df.columns:
                    source_info["reference"] = f"{df.iloc[i]['chapter']}:{df.iloc[i]['verse']}"
                elif 'surah' in df.columns and 'ayat' in df.columns:
                    source_info["reference"] = f"{df.iloc[i]['surah']}:{df.iloc[i]['ayat']}"
                else:
                    source_info["reference"] = f"Dokumen {i + 1}"
                
                results["sources"].append(source_info)

        return jsonify({
            "status": "success", 
            "results": results
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Terjadi kesalahan: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
