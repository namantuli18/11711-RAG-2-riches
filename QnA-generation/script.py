import os
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("potsawee/t5-large-generation-squad-QuestionAnswer")
model = AutoModelForSeq2SeqLM.from_pretrained("potsawee/t5-large-generation-squad-QuestionAnswer")

def get_q_a(context):
    inputs = tokenizer(context, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=128)
    question_answer = tokenizer.decode(outputs[0], skip_special_tokens=False)
    question_answer = question_answer.replace(tokenizer.pad_token, "").replace(tokenizer.eos_token, "")
    question, answer = question_answer.split(tokenizer.sep_token)

    return question, answer


def generate_dynamic_event_description(event):
    event_name = event.get("event_name", "This event")
    date = event.get("date", "")
    time = event.get("time", "")
    description = event.get("description", "")
    price = event.get("price", "")
    
    description_parts = [f"{event_name} is happening "]

    if date:
        description_parts.append(f"on {date}")

    if time:
        description_parts.append(f", {time}")

    if price:
        description_parts.append(f"Tickets are priced at {price}")

    if description:
        description_parts.append(description)

    return " ".join(description_parts)


data_path = 'raw_data'
q_list = []
a_list = []
for path in os.listdir(data_path):
    if path.split(".")[-1] == "csv":
        path = os.path.join(data_path, path)
        data = pd.read_csv(path)
        print("Started generating q a for file: {}".format(path))
        for count, rows in enumerate(data.text):
            context = data['text'][count]
            try:
                q, a = get_q_a(context)
                q_list.append(q)
                a_list.append(a)
            except:
                pass

l = []
with open('raw_data/dump-event_data.json', 'r') as f:
    data = json.load(f)
for event in data:
    l.append(generate_dynamic_event_description(event))

for count, rows in enumerate(l):
    context = rows
    try:
        q, a = get_q_a(context)
        q_list.append(q)
        a_list.append(a)
    except:
        pass


with open('raw_data/questions.txt', 'a') as f:
    for q in q_list:
        f.write("{}\n".format(q))

with open('raw_data/answers.txt', 'a') as f:
    for a in a_list:
        f.write("{}\n".format(a))