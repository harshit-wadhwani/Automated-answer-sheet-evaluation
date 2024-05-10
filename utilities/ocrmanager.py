import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "apikey.json"
import io
from google.cloud import vision
import re

def remove_space(l):
    send_list=[]
    for element in l:
        temp = ""
        for i in element:
            if i !=" ":
                temp += i
        send_list.append(temp)
    return send_list


def detect_document_text(pdf_file_path):
    """OCR with PDF file from local storage"""
    from google.cloud import vision

    # Supported mime_types are: 'application/pdf'
    mime_type = "application/pdf"
    c = 1
    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    with open(pdf_file_path, "rb") as pdf_file:
        content = pdf_file.read()

    image = vision.Image(content=content)

    response = client.batch_annotate_files(
        requests=[{"input_config": {"content": content, "mime_type": mime_type}, "features": [feature]}]
    )

    student_info = []
    student_ans = []
    patterns_found=[]

    #change regex as per format
    # pattern = r'\d{2}\s*[A-Z]{2}\s*\d{2}\s*Q\s*\d+'
    pattern = r'Question\s*[1-9]\s*\d*'

    for image_response in response.responses:
        for page in image_response.responses:
            text=page.full_text_annotation.text
            if c == 1:
                info=text.split('\n')
                name=info[1].strip()
                subcode=info[3].strip()
                usn=info[5].strip()
                date=info[7].strip()
                student_info.extend([name,subcode,usn,date])
                # student_info=[]
                
            else:
                patterns = re.findall(pattern, text)
                patterns_found.extend(patterns)
                answers = re.split(pattern, text)
                # Filter out empty strings
                answers = [answer.strip() for answer in answers if answer.strip()]
                student_ans.extend(answers)

            c=c+1

    patterns_found_new=remove_space(patterns_found)
    return student_info, student_ans, patterns_found_new
