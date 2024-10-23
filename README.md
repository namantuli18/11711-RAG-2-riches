# 11711-RAG-2-riches


### Fine-Tuning Approach

For the fine-tuning task, we utilized the LLaMa-3.2 model, training it on synthetically generated question-and-answer pairs generated from our scraped corpus. 
The fine-tuning pipeline is structured in two phases:

* Phase 1 involves fine-tuning the model using synthetically generated question-answer pairs relevant to the target domain (CMU and Pittsburgh).
* Phase 2 focuses on retrieving relevant documents from a database, re-ranking them based on relevance, and then sending them to the model for final predictions.
<div align="center">
  <img src="https://github.com/namantuli18/11711-RAG-2-riches/blob/main/resources/imgs/RAG-Pipeline.png?raw=true" alt="RAG Finetuning Pipeline" width="800"/>
</div>

#### Phase 1
* For generating the question-answer pairs from the data in our corpus, we have used a paragraph level QA Generation system using a T5Large model finetuned on the SQuAD dataset.
* For fine-tuning the model on the context, and question-answer triplets, we have used a LLaMa-3.2 model and trained it for 2 epochs until convergence.

#### Phase 2
* Phase 2 focuses on retrieving relevant documents from a database, re-ranking them based on relevance, and then sending them to the model for final predictions.

#### Scripts for fine-tuning
1. The QA Generation notebook for our text corpus is located at path: scripts\finetuning\QA_Generation\QA-generate-all_data.ipynb
2. To use the same model to generate question and answer pairs, you can use the below script:
   
   ```bash
   pip3 install -r requirements.txt
   ```
   ```bash
   python3 scripts\finetuning\QA_Generation\generate_qa.py "Enter your text here"
4. The entire corpus of our question and answer pairs is located in separate text files in the folder data\finetune_data\QnA-corpus.
