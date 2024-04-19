
from docxtpl import DocxTemplate
import os
import json
from docx2pdf import convert

class GenerateQpaper:
    def MakePaper(self):
# Load the JSON data from file
        with open('data/current.json', 'r') as file:
            data = json.load(file)

        # Extract page numbers and questions
        qid = [item['Qid'] for item in data['data']]
        questions = [item['question'] for item in data['data']]

        result_string = ""
        for num, question in zip(qid, questions):
            result_string += f"{num}. {question}\n"

        doc= DocxTemplate('templates/qpapertemp.docx')
            
        context= { 
        'questions': result_string
        }
        doc.render(context)
        doc.save('data/questionpaper.docx')


        convert("data/questionpaper.docx")

        return 1


