from flask import Flask, render_template, redirect, send_file, url_for,request,jsonify, session
from utilities.dbmanager import dbmanager
from utilities.qpapergenerator import GenerateQpaper
from utilities.ocrmanager import detect_document_text
from utilities.tempmanager import checkscore
from utilities.scoremanager import check_similarity
import json
from werkzeug.utils import secure_filename
import os
import hashlib
from huggingface_hub import from_pretrained_keras


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
model = from_pretrained_keras("keras-io/bert-semantic-similarity")

# Compile the model


app.secret_key = 'your_secret_key'

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template("index.html")

@app.route('/qp.html')  # Define route for qp.html
def qp():
    
    return render_template('qp.html')

@app.route('/data', methods=['POST'])
def save_data():
    
    data = request.get_json()
    with open('data/current.json', 'w') as f:
        json.dump(data, f)
    return jsonify({'message': 'Data saved successfully'})

@app.route('/generate', methods=['POST'])
def generate():
    db_manager = dbmanager()
    qp_generater= GenerateQpaper()
    collection_name='questions'
    with open('data/current.json', 'r') as file:
        json_data = json.load(file)
    json_data = json_data['data']
    new_json_data = {}
    for item in json_data:
        date= item['date']
        code = item['code']
        field = code+date
        if field not in new_json_data:
            new_json_data[field] = []
            
        del item['code']
        del item['date']
        new_json_data[field].append(item)

    db_manager.create(collection_name,new_json_data)
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

@app.route("/for_evaluation", methods = ["POST", "GET"])
def for_evaluation():
    f = request.get_json()  
    session["code"] = f["ls"][0]['code']
    session["dateup"] = f["ls"][0]['datestring']
    return ""
    
@app.route("/evaluation", methods=['GET', 'POST'])
def evaluation():
    
    return render_template("evaluation.html", f= session["code"], g= session["dateup"])


@app.route('/upload', methods=['POST', 'GET'])
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
    scores= []
    db_client = dbmanager()
    
    for filename in file_nms:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # print(file_path)
        
        l_info,l_ans,l_pat= detect_document_text(file_path)
        
        query = str(session["code"] + session["dateup"])
        print(query)
        
        ques, ref_ans = db_client.get_quenum_ans_dict("questions", query)
            
        
        for ans, ref_answer in zip(l_ans, ref_ans):
            scores.append(check_similarity(ans, ref_answer, model))
            
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

    
    return render_template('result.html', l_info=l_info_list, l_ans=l_ans_list, score =scores)


if __name__ == '__main__':
    app.run(debug=True)