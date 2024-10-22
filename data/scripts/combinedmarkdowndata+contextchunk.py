# -*- coding: utf-8 -*-
"""CombinedMarkdownData+ContextChunk.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DacqP1etodox39ODvBhjoVC9Ek1CNESK
"""

import os
import glob
import pandas as pd
import json

def get_file_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def load_reference_csvs(ref_csv_files):
    ref_dfs = []
    for ref_file in ref_csv_files:
        try:
            ref_df = pd.read_csv(ref_file)
            ref_dfs.append(ref_df)
        except pd.errors.EmptyDataError:
            print(f"Skipping empty reference file: {ref_file}")
        except pd.errors.ParserError as e:
            print(f"Error parsing reference file: {ref_file}. Error: {str(e)}")

    combined_ref_df = pd.concat(ref_dfs, ignore_index=True)
    return combined_ref_df

def process_csv_files(csv_files, markdown_lines, reference_df):
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if 'section' in df.columns and 'text' in df.columns:
                file_name = get_file_name(file)
                markdown_lines.append(f"# {file_name}\n\n")

                for _, row in df.iterrows():
                    section = row['section']
                    text = row['text']

                    if pd.notna(section):
                        markdown_lines.append(f"## {section}\n\n")

                    if pd.notna(text):
                        matched_row = reference_df[reference_df['text'] == text]
                        if not matched_row.empty:
                            contextual_chunk = matched_row.iloc[0]['contextual_chunk']
                            if pd.notna(contextual_chunk):
                                markdown_lines.append(f"### Context: {contextual_chunk}\n\n")

                        markdown_lines.append(f"{text}\n\n")

            else:
                print(f"'section' or 'text' column not found in {file}. Skipping.")
        except pd.errors.EmptyDataError:
            print(f"Skipping empty file: {file}")
        except pd.errors.ParserError as e:
            print(f"Error parsing file: {file}. Error: {str(e)}")

    return markdown_lines

def process_txt_files(txt_files, markdown_lines, reference_df):
    for file in txt_files:
        try:
            with open(file, 'r') as f:
                content = f.read().strip()

            file_name = get_file_name(file)
            if pd.notna(content):
                markdown_lines.append(f"# {file_name}\n\n")

                matched_row = reference_df[reference_df['text'] == content]
                if not matched_row.empty:
                    contextual_chunk = matched_row.iloc[0]['contextual_chunk']
                    if pd.notna(contextual_chunk):
                        markdown_lines.append(f"### Context: {contextual_chunk}\n\n")

                markdown_lines.append(f"{content}\n\n")

        except Exception as e:
            print(f"Error reading file: {file}. {str(e)}")

    return markdown_lines

def process_json_files(json_files, markdown_lines, reference_df):
    markdown_lines.append("# Pittsburgh Events\n\n")

    row_counter = 364

    for file in json_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                for event in data:
                    event_name = event.get("event_name", "Unknown Event")
                    if pd.notna(event_name):
                        markdown_lines.append(f"## {event_name}\n\n")

                    contextual_chunk = reference_df.iloc[row_counter]['contextual_chunk']
                    markdown_lines.append(f"### Context: {contextual_chunk}\n\n")

                    row_counter += 1

                    for key, value in event.items():
                        if key != "event_name" and pd.notna(value):
                            markdown_lines.append(f"**{key.capitalize()}**: {value}\n")

                    markdown_lines.append("\n")

            else:
                event_name = data.get("event_name", "Unknown Event")
                if pd.notna(event_name):
                    markdown_lines.append(f"## {event_name}\n\n")

                contextual_chunk = reference_df.iloc[row_counter]['contextual_chunk']
                markdown_lines.append(f"### Context: {contextual_chunk}\n\n")

                row_counter += 1

                for key, value in data.items():
                    if key != "event_name" and pd.notna(value):
                        markdown_lines.append(f"**{key.capitalize()}**: {value}\n")

                markdown_lines.append("\n")

        except Exception as e:
            print(f"Error reading file: {file}. {str(e)}")

    return markdown_lines

def process_special_txt_file(special_file, markdown_lines, reference_df):
    markdown_lines.append("# More About Carnegie Mellon University\n\n")

    try:
        with open(special_file, 'r') as f:
            content = f.read().strip()

        chunks = content.split(f"{'-'*80}")
        for chunk in chunks:
            chunk = chunk.strip()
            if pd.notna(chunk):
                first_word = chunk.split()[0] if chunk.split() else "No Title"
                markdown_lines.append(f"## {first_word}\n")

                matched_row = reference_df[reference_df['text'] == chunk]
                if not matched_row.empty:
                    contextual_chunk = matched_row.iloc[0]['contextual_chunk']
                    if pd.notna(contextual_chunk):
                        markdown_lines.append(f"### Context: {contextual_chunk}\n\n")

                markdown_lines.append(f"{chunk}\n\n")

    except Exception as e:
        print(f"Error reading special file: {special_file}. {str(e)}")

    return markdown_lines

def generate_markdown_from_files(folder_path, special_file_name, reference_folder, output_md):
    markdown_lines = []

    reference_files = [os.path.join(reference_folder, f) for f in ["contextual_summary_huggingface_0.csv", "contextual_summary_huggingface_1.csv", "contextual_summary_huggingface_2.csv"]]
    reference_df = load_reference_csvs(reference_files)

    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    markdown_lines = process_csv_files(csv_files, markdown_lines, reference_df)

    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    markdown_lines = process_json_files(json_files, markdown_lines, reference_df)

    txt_files = [f for f in glob.glob(os.path.join(folder_path, "*.txt")) if os.path.basename(f) != special_file_name]
    markdown_lines = process_txt_files(txt_files, markdown_lines, reference_df)

    special_file = os.path.join(folder_path, special_file_name)
    markdown_lines = process_special_txt_file(special_file, markdown_lines, reference_df)

    with open(output_md, 'w') as f:
        f.writelines(markdown_lines)

    print(f"Markdown file generated and saved as '{output_md}'")


folder_path = ""
special_file_name = "processed_text.txt"
reference_folder = "./Reference files/"
output_md = "final_data.md"

generate_markdown_from_files(folder_path, special_file_name, reference_folder, output_md)
