import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "apikey.json"
import io
from google.cloud import vision
import re


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

    #change regex as per format
    pattern = r'\d{2}Q\d{2}'

    for image_response in response.responses:
        for page in image_response.responses:
            text=page.full_text_annotation.text
            if c == 1:
                info=text.split('\n')
                name=info[1].strip()
                subcode=info[3].strip()
                usn=info[5].strip()
                student_info.extend([name,subcode,usn])
            else:
                answers = re.split(pattern, page.full_text_annotation.text)
                # Filter out empty strings
                answers = [answer.strip() for answer in answers if answer.strip()]
                student_ans.extend(answers)

            c=c+1


    return student_info, student_ans

