import pandas as pd
import json
import glob
import os

def get_file_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def concatenate_csv_files(folder_path):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    total_rows = 0
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if 'text' in df.columns:
                file_name = get_file_name(file)
                df['file_name'] = file_name 
                dfs.append(df[['text', 'file_name']])
                total_rows += len(df)
            else:
                print(f"'text' column not found in {file}. Skipping.")
        except pd.errors.EmptyDataError:
            print(f"Skipping empty file: {file}")
        except pd.errors.ParserError as e:
            print(f"Error parsing file: {file}. Error: {str(e)}")
    concatenated_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame(columns=["text", "file_name"])
    print(f"Processed {len(csv_files)} CSV files and added {total_rows} rows.")
    return concatenated_df

def append_json_to_dataframe(folder_path, df):
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    total_rows = 0
    for file in json_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            file_name = get_file_name(file)
            if isinstance(data, list):
                for item in data:
                    new_row = pd.DataFrame({"text": [str(item)], "file_name": [file_name]})
                    df = pd.concat([df.reset_index(drop=True), new_row.reset_index(drop=True)], ignore_index=True)
                    total_rows += 1
            else:
                new_row = pd.DataFrame({"text": [str(data)], "file_name": [file_name]})
                df = pd.concat([df.reset_index(drop=True), new_row.reset_index(drop=True)], ignore_index=True)
                total_rows += 1
        except json.JSONDecodeError as e:
            print(f"Error parsing file: {file}. {str(e)}")
    print(f"Processed {len(json_files)} JSON files and added {total_rows} rows.")
    return df

def append_txt_to_dataframe(folder_path, df):
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    total_rows = 0
    for file in txt_files:
        if os.path.basename(file) == "processed_text.txt":
            print(f"Skipping special file: {file}")
            continue
        try:
            with open(file, 'r') as f:
                content = f.read().strip()
            file_name = get_file_name(file)
            new_row = pd.DataFrame({"text": [content], "file_name": [file_name]})
            df = pd.concat([df.reset_index(drop=True), new_row.reset_index(drop=True)], ignore_index=True)
            total_rows += 1
        except Exception as e:
            print(f"Error reading file: {file}. {str(e)}")
    print(f"Processed {len(txt_files)} TXT files and added {total_rows} rows.")
    return df

def process_special_file(file_path, df):
    total_rows = 0
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        file_name = get_file_name(file_path)
        chunks = content.split(f"{'-'*80}\n\n")
        for chunk in chunks:
            if chunk.strip():
                new_row = pd.DataFrame({"text": [chunk.strip()], "file_name": [file_name]})
                df = pd.concat([df.reset_index(drop=True), new_row.reset_index(drop=True)], ignore_index=True)
                total_rows += 1
    except Exception as e:
        print(f"Error processing special file: {file_path}. {str(e)}")
    print(f"Processed special file and added {total_rows} rows.")
    return df

folder_path = "./data/cleaned_data"
result_df = concatenate_csv_files(folder_path)
result_df_cleaned = result_df.dropna().reset_index(drop=True)
result_df_with_json = append_json_to_dataframe(folder_path, result_df_cleaned)
result_df_with_txt = append_txt_to_dataframe(folder_path, result_df_with_json)

special_file_path = os.path.join(folder_path, "processed_text.txt")
if os.path.exists(special_file_path):
    result_df_with_special = process_special_file(special_file_path, result_df_with_txt)
else:
    result_df_with_special = result_df_with_txt

print(result_df_with_special.head())
output_path = "./data/combined_data/final_data.csv"
result_df_with_special.to_csv(output_path, index=False)
print(f"Concatenated CSV with JSON, TXT, and special file data saved as '{output_path}'")