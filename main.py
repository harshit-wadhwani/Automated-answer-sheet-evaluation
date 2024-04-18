from flask import Flask, render_template, redirect, send_file, url_for,request,jsonify
from utilities.dbmanager import dbmanager
from utilities.qpapergenerator import GenerateQpaper
import json

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/qp.html')  # Define route for qp.html
def qp():
    return render_template('qp.html')

@app.route('/data', methods=['POST'])
def save_data():
    data = request.get_json()
    with open('Answersheet-AI/data/current.json', 'w') as f:
        json.dump(data, f)
    return jsonify({'message': 'Data saved successfully'})

@app.route('/generate', methods=['POST'])
def generate():
    db_manager = dbmanager()
    qp_generater= GenerateQpaper()
    collection_name='questions'
    with open('Answersheet-AI/data/current.json', 'r') as file:
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

if __name__ == '__main__':
    app.run(debug=True)