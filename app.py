from flask import Flask, render_template, request, flash, send_file
import os
import glob
from PIL import Image
from PyPDF2 import PdfMerger

app = Flask(__name__)
app.secret_key = "your_secret_key"

def convert_images_to_pdf(input_folder, output_file):
    images = []
    #sortedはファイル名を昇順に並び替えている、別に昇順に並び替えないと処理無理とかじゃないはず
    for file in sorted(glob.glob(os.path.join(input_folder, "*.jpg"))):
        images.append(Image.open(file))

    if images:
        images[0].save(
            output_file,#出力するPDFファイルのパスと名前を指定
            save_all=True,#すべての画像をPDFに保存するオプションを有効に
            append_images=images[1:],#最初の画像以外の画像（images[1:]）を追加してPDFに結合
            resolution=100.0,#PDFの解像度を設定
            quality=95,#画像の品質を設定
            optimize=True,#PDFを最適化するオプションを有効に
            compress_level=9 #PDFを最適化するオプションを有効に
        )
        return True
    else:
        return False

def merge_pdfs(input_folder, output_file):
    pdfs = []
    for file in sorted(glob.glob(os.path.join(input_folder, "*.pdf"))):
        pdfs.append(file)

    if pdfs:
        pdf_merger = PdfMerger()#複数のPDFファイルを結合するためのメソッドを提供している
        for pdf in pdfs:
            with open(pdf, "rb") as pdf_file:#読み込みモードで開いている
                pdf_merger.append(pdf_file)#pdf_mergerにpdfを1枚ずつ追加している

        with open(output_file, "wb") as merged_pdf:#書き込みモードで開いている
            pdf_merger.write(merged_pdf)#outputファイルに、結合させたpdfを書き込んでいる

        return True
    else:
        return False

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
    
    return render_template("pdf_merge.html") 

# message_categoryフィルターを定義
@app.template_filter('message_category')
def message_category(msg):
    if msg.startswith("error"):
        return "error"
    elif msg.startswith("success"):
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
