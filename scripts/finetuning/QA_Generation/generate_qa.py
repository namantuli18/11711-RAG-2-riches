import argparse
from lmqg import TransformersQG

model = TransformersQG(language='en', model='lmqg/t5-large-squad-qag')

def get_q_a(model, context):
    question_answer = model.generate_qa(context)
    return question_answer

def main():
    parser = argparse.ArgumentParser(description='Generate question and answer pairs from user input.')
    parser.add_argument('text', type=str, help='Input text for generating questions and answers.')
    
    args = parser.parse_args()
    
    qa_pairs = get_q_a(model, args.text)
    for pair in qa_pairs:
        print(f"Q: {pair['question']}")
        print(f"A: {pair['answer']}")
        print()

if __name__ == "__main__":
    main()
