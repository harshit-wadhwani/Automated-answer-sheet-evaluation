import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\PERSONAL_PROJS\Cloudvision\\apikey.json"
import io
from google.cloud import vision


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

    # Store the text in a dictionary with page numbers as keys
    extracted_text = {}
    for image_response in response.responses:
        for page in image_response.responses:
            if c not in extracted_text:
                extracted_text[c] = ""
            extracted_text[c] += page.full_text_annotation.text + "\n"
            c=c+1

    # Combine the text in the desired order
    result = ""
    for page_num, text in extracted_text.items():
        if(page_num==1 or page_num==2):
            result += f"PAGE {page_num} :\n{text}\n"
        else:
            result += f"{text}\n"

    return result


