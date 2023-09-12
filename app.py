from flask import Flask, render_template, request, flash, send_file
import os
import glob
from PIL import Image
from PyPDF2 import PdfMerger

app = Flask(__name__)
app.secret_key = "your_secret_key"
#UndefinedErrorが出るのは元から．出てもpdfファイルは出力される．もし出力されないなら，入力した拡張子の問題
def convert_images_to_pdf(input_folder, output_file):
    images = []
    for file in sorted(glob.glob(os.path.join(input_folder, "*.jpeg"))):
        images.append(Image.open(file))

    if images:
        images[0].save(
            output_file,
            save_all=True,
            append_images=images[1:],
            resolution=100.0,
            quality=95,
            optimize=True,
            compress_level=9
        )
        return True
    else:
        return False

def merge_pdfs(input_folder, output_file):
    pdfs = []
    for file in sorted(glob.glob(os.path.join(input_folder, "*.pdf"))):
        pdfs.append(file)

    if pdfs:
        pdf_merger = PdfMerger()
        for pdf in pdfs:
            with open(pdf, "rb") as pdf_file:
                pdf_merger.append(pdf_file)

        with open(output_file, "wb") as merged_pdf:
            pdf_merger.write(merged_pdf)

        return True
    else:
        return False

@app.route("/pdf_merge", methods=["GET", "POST"])
def pdf_merge():
    if request.method == "POST":
        input_folder = request.form["pdf_input_folder"]
        output_file = request.form["pdf_output_file"]

        if not os.path.exists(input_folder):
            flash("入力フォルダが見つかりません。", "error")
        elif not os.path.isdir(input_folder):
            flash("入力パスはフォルダを指定してください。", "error")
        elif not os.path.splitext(output_file)[1].lower() == ".pdf":
            flash("出力ファイル名はPDF形式で指定してください。", "error")
        else:
            if merge_pdfs(input_folder, output_file):
                flash("PDFファイルの結合が完了しました。", "success")
            else:
                flash("PDFファイルが見つかりませんでした。", "error")
    
    return render_template("pdf_merge.html", message_category=message_category)  

@app.route("/jpg_merge", methods=["GET", "POST"])
def jpg_merge():
    if request.method == "POST":
        input_folder = request.form["jpg_input_folder"]
        output_file = request.form["jpg_output_file"]

        if not os.path.exists(input_folder):
            flash("入力フォルダが見つかりません。", "error")
        elif not os.path.isdir(input_folder):
            flash("入力パスはフォルダを指定してください。", "error")
        elif not os.path.splitext(output_file)[1].lower() == ".pdf":
            flash("出力ファイル名はPDF形式で指定してください。", "error")
        else:
            if convert_images_to_pdf(input_folder, output_file):
                flash("JPG画像のPDF変換が完了しました。", "success")
            else:
                flash("JPG画像が見つかりませんでした。", "error")

    return render_template("jpg_merge.html")

def message_category(message):
    if "error" in message:
        return "error"
    elif "success" in message:
        return "success"
    else:
        return "info"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
