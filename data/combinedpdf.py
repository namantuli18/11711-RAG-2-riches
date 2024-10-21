# -*- coding: utf-8 -*-
"""CombinedPdf.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mHrPT2dPGRwaRghMgj6QXJ6zFdO23fhf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import pandas as pd
import json
import os
import glob

def get_file_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def process_csv_files(csv_files, story):
    styles = getSampleStyleSheet()
    main_heading_style = ParagraphStyle('MainHeading', parent=styles['Heading1'], alignment=TA_CENTER, textColor=colors.darkblue)
    sub_heading_style = ParagraphStyle('SubHeading', parent=styles['Heading2'], textColor=colors.black)
    text_style = styles['BodyText']

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if 'section' in df.columns and 'text' in df.columns:
                file_name = get_file_name(file)
                story.append(Paragraph(str(file_name), main_heading_style))
                story.append(Spacer(1, 0.2 * inch))

                for _, row in df.iterrows():
                    section = row['section']
                    text = row['text']
                    story.append(Paragraph(str(section), sub_heading_style))
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(Paragraph(str(text), text_style))
                    story.append(Spacer(1, 0.2 * inch))

                story.append(Spacer(1, 0.5 * inch))
            else:
                print(f"'section' or 'text' column not found in {file}. Skipping.")
        except pd.errors.EmptyDataError:
            print(f"Skipping empty file: {file}")
        except pd.errors.ParserError as e:
            print(f"Error parsing file: {file}. Error: {str(e)}")

    return story

def process_txt_files(txt_files, story):
    styles = getSampleStyleSheet()
    main_heading_style = ParagraphStyle('MainHeading', parent=styles['Heading1'], alignment=TA_CENTER, textColor=colors.darkblue)
    text_style = styles['BodyText']

    for file in txt_files:
        try:
            with open(file, 'r') as f:
                content = f.read().strip()

            file_name = get_file_name(file)
            story.append(Paragraph(str(file_name), main_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(str(content), text_style))
            story.append(Spacer(1, 0.5 * inch))

        except Exception as e:
            print(f"Error reading file: {file}. {str(e)}")

    return story

def process_json_files(json_files, story):
    styles = getSampleStyleSheet()
    main_heading_style = ParagraphStyle('MainHeading', parent=styles['Heading1'], alignment=TA_CENTER, textColor=colors.darkblue)
    sub_heading_style = ParagraphStyle('SubHeading', parent=styles['Heading2'], textColor=colors.black)
    text_style = styles['BodyText']

    story.append(Paragraph("Pittsburgh Events", main_heading_style))
    story.append(Spacer(1, 0.2 * inch))

    for file in json_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                for event in data:
                    event_name = event.get("event_name", "Unknown Event")
                    story.append(Paragraph(str(event_name), sub_heading_style))
                    story.append(Spacer(1, 0.1 * inch))

                    for key, value in event.items():
                        if key != "event_name":
                            detail = f"<b>{str(key.capitalize())}:</b> {str(value)}"
                            story.append(Paragraph(detail, text_style))
                            story.append(Spacer(1, 0.1 * inch))

                    story.append(Spacer(1, 0.5 * inch))
            else:
                event_name = data.get("event_name", "Unknown Event")
                story.append(Paragraph(str(event_name), sub_heading_style))
                story.append(Spacer(1, 0.1 * inch))

                for key, value in data.items():
                    if key != "event_name":
                        detail = f"<b>{str(key.capitalize())}:</b> {str(value)}"
                        story.append(Paragraph(detail, text_style))
                        story.append(Spacer(1, 0.1 * inch))

                story.append(Spacer(1, 0.5 * inch))

        except Exception as e:
            print(f"Error reading file: {file}. {str(e)}")

    return story


def process_special_txt_file(special_file, story):
    styles = getSampleStyleSheet()
    main_heading_style = ParagraphStyle('MainHeading', parent=styles['Heading1'], alignment=TA_CENTER, textColor=colors.darkblue)
    sub_heading_style = ParagraphStyle('SubHeading', parent=styles['Heading2'], textColor=colors.black)
    text_style = styles['BodyText']

    story.append(Paragraph("More About Carnegie Mellon University", main_heading_style))
    story.append(Spacer(1, 0.2 * inch))

    try:
        with open(special_file, 'r') as f:
            content = f.read().strip()

        chunks = content.split(f"{'-'*80}")
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                first_word = chunk.split()[0] if chunk.split() else "No Title"
                story.append(Paragraph(str(first_word), sub_heading_style))
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(str(chunk), text_style))
                story.append(Spacer(1, 0.5 * inch))

    except Exception as e:
        print(f"Error reading special file: {special_file}. {str(e)}")

    return story

def generate_pdf_from_files(folder_path, special_file_name, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    story = []

    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    story = process_csv_files(csv_files, story)

    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    story = process_json_files(json_files, story)

    txt_files = [f for f in glob.glob(os.path.join(folder_path, "*.txt")) if os.path.basename(f) != special_file_name]
    story = process_txt_files(txt_files, story)

    special_file = os.path.join(folder_path, special_file_name)
    story = process_special_txt_file(special_file, story)

    doc.build(story)
    print(f"PDF generated and saved as '{output_pdf}'")

folder_path = ""
special_file_name = "processed_text.txt"
output_pdf = "output.pdf"
generate_pdf_from_files(folder_path, special_file_name, output_pdf)

!pip install reportlab

