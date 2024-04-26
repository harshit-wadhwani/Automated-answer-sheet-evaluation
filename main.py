from flask import Flask, render_template, redirect, send_file, url_for,request,jsonify
from utilities.dbmanager import dbmanager
from utilities.qpapergenerator import GenerateQpaper
from utilities.ocrmanager import detect_document_text
from utilities.tempmanager import checkscore
import json
from werkzeug.utils import secure_filename
import os
import hashlib

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
    file_names = []
    for f in request.files.getlist('file'):
        if f.filename != '':
            filename = secure_filename(f.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(file_path)
            file_names.append(file_path.replace("uploads/", ""))
            
    result_id = "||".join(file_names)
    return redirect(url_for("result", result_id=result_id))

@app.route("/result/<result_id>")
def result(result_id):
    
    file_nms =  result_id.split("||")
    
    l_info_list = []
    l_ans_list = []
    db_client = dbmanager()
    
    for filename in file_nms:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # print(file_path)
        
        l_info,l_ans,l_pat= detect_document_text(file_path)
        ref_ans = []
        
        for ques_id in l_pat:
            ref_ans.append(db_client.read("questions", {"code": ques_id})) ##CHANGE NEEDED 
            
        scores= []
        for ans, ref_answer in zip(l_ans, ref_ans):
            scores.append(checkscore(ans, ref_answer))
            
        data = {}
        
        for i in range(len(l_pat)):

            uni_key = l_info[2]+"-"+l_info[3]

            if uni_key not in data:
                data[uni_key] = {}

            if l_info[1] not in data[uni_key]:
                data[uni_key][l_info[1]] = []

            data[uni_key][l_info[1]].append({
                "quenum": l_pat[i],
                "ans":  l_ans[i] ,
                "score" : scores[i]
            })

        db_manager = dbmanager()
        collection_name='answers'
        db_manager.create(collection_name,data)
        l_info_list.append(l_info)
        l_ans_list.append(l_ans)

    
    return render_template('result.html', l_info=l_info_list, l_ans=l_ans_list)


if __name__ == '__main__':
    app.run(debug=True)