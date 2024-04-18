from flask import Flask, render_template, redirect, send_file, url_for,request,jsonify
from utilities.dbmanager import dbmanager
from utilities.qpapergenerator import GenerateQpaper
from utilities.ocrmanager import detect_document_text
import json
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template("index.html")

@app.route('/qp.html')  # Define route for qp.html
def qp():
    return render_template('qp.html')

@app.route('/data', methods=['POST'])
def save_data():
    data = request.get_json()
    with open('data\\current.json', 'w') as f:
        json.dump(data, f)
    return jsonify({'message': 'Data saved successfully'})

@app.route('/generate', methods=['POST'])
def generate():
    db_manager = dbmanager()
    qp_generater= GenerateQpaper()
    collection_name='questions'
    with open('data/current.json', 'r') as file:
     json_data = json.load(file)
    db_manager.create(collection_name,json_data)
    qp_generater.MakePaper()

    message = "Python function executed successfully!"
    return jsonify({"message": message})


@app.route('/download.html')  # Define route for qp.html
def download():
    return render_template('download.html')

@app.route('/generate', methods=['GET'])
def get_generate_result():
    return send_file('data/questionpaper.pdf', as_attachment=True)

@app.route('/download/this.pdf')
def download_this_pdf():
    return send_file('data/questionpaper.pdf', as_attachment=True)

@app.route("/evaluation", methods=['GET', 'POST'])
def evaluation():
    return render_template("evaluation.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']

    # Check if the file was actually uploaded
    if file.filename == '':
        return 'No file selected', 400

    # Save the file to the upload folder
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    
    return redirect(url_for("result", filename=filename))

@app.route("/result/<filename>")
def result(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    l = detect_document_text(file_path)
    
    return render_template('result.html', filename=filename, l=l)


if __name__ == '__main__':
    app.run(debug=True)