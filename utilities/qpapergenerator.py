
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
        score = [int(item['score']) for item in data['data']]
        total= sum(score)
        for item in data['data']:
            date= item['date']
            code = item['code']
            break
        result_string = ""
        for num, question,score in zip(qid, questions,score):
            result_string += f"{num}.\t{question}\t Total Marks:{score}\n"

        doc= DocxTemplate('templates/qpapertemp.docx')
            
        context= { 
        'questions': result_string,
        'total': total,
        'code': code,
        'date': date
        }
        doc.render(context)
        doc.save('data/questionpaper.docx')


        convert("data/questionpaper.docx")

        return 1


