# 11711-RAG-2-riches

## Data Creation

#### Raw Data Extraction
1. Wikipedia: The first part of our textual knowledge comprises data that is scraped from Wikipedia.
2. Reddit: Data was scraped from most of the famous subreddits related to Pittsburgh and related topics using PRAW API. Only recent 1000 threads of each subreddit were extracted. 
3. Brittanica Encyclopedia Web pages: All articles had a print button that when clicked, downloads the pdf version of the article. Exploited this to fetch all the articles in pdf version and extracted the raw text.
4. CMU edu pages: These were mostly static web pages and so performed recursive web scraping to a depth of 2. Extracted all the text and the text processing was done using llama-3.2-1B-Instruct LLM model.

#### Scripts to generate textual corpus:
  
  ```bash
   #Wikipedia Data
   python3 scraper\wiki_scraper.py
   ```
  ```bash
   #Reddit data
   python3 scraper\subRedditScrapper.py
   ```

  ```bash
   #Encyclopedia Data
   python3 scraper\BrittanicaPdfParser.py
   ```

  ```bash
   #CMU edu webpages
   python3 scraper\CmuEduScrapper.py
   ```
#### Event Data Extraction
1. To ensure consistency across the scraped events, we found that most web pages (regardless of source) contain event information in the form of event names, dates, locations, event categories, and an optional description of the event.
2. This approach uses **ChromeDriver** from **Selenium** to handle user-responsive actions on webpages dynamically, and **BeautifulSoup** to extract the contents from such pages once the race condition terminates. The formulated approach ensures consistency in the data format for the events being scraped and confirms that the event corpus is exhaustive.
3. It effectively handles both one-off and recurring events based on the extracted information.
4. In the end we had multiple json files containing events from various sources. We filtered them and removed the redundant ones. Also, if an event has multiple entries in the json, but the dates are consecutive, then those are merged by specifying the date ranges.
   
#### Sample JSON object
  ```javascript
      {
          "date": "Feb 3, 2024 - Feb 4, 2024",
          "description": "Volleyball teams will compete at the 2024 Mizuno Steel City Freeze.",
          "category": "Convention,, Sports + Recreation",
          "venue": "David L. Lawrence Convention Center 1000 Fort Dusquene Boulevard Pittsburgh, PA 15222",
          "more_details": "The Nike Steel City Freeze is a two day event hosted by GK Sports and insured by the JVA. Teams of any affiliation can play and will be insured. AAU, USAV and JVA teams are all   welcome!",
          "event_name": "2024 Steel City Freeze - GK Sports"
      }
  ```

#### Scripts to generate event corpus
  ```python
  python3 scraper\events_scraper.py
  ```

The file [data\raw_data\combined_events.json](https://github.com/namantuli18/11711-RAG-2-riches/blob/main/data\raw_data\combined_events.json) contains >3000 exhaustive events from Pittsburgh, CMU, CMU Alumni, Downtown Events pages with all relevant information.

#### Scripts to combine textual data (stored in csv and txt files) and events (stored in JSON format)
```python
python3 data\scripts\combine_data.py
```



## Fine-Tuning Approach

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
1. The QA Generation notebook for our text corpus is located at [scripts/finetuning/QA_Generation/QA-generate-all_data.ipynb](https://github.com/namantuli18/11711-RAG-2-riches/blob/main/scripts/finetuning/QA_Generation/QA-generate-all_data.ipynb).
2. To use the same model to generate question and answer pairs, you can use the below script:
   
   ```bash
   pip3 install -r requirements.txt
   ```
   ```bash
   python3 scripts\finetuning\QA_Generation\generate_qa.py "Enter your text here"
4. The entire corpus of our question and answer pairs is located in separate text files in the folder: data\finetune_data\QnA-corpus.
5. The notebook to train the LLaMa-3.2 model on the synthetically generated data is in [scripts\finetuning\llama-3-2-3b-finetune-train.ipynb](https://github.com/namantuli18/11711-RAG-2-riches/blob/main/scripts/finetuning/llama-3-2-3b-finetune-train.ipynb)
6. The notebook to run RAG inference using the fine-tuned LLaMa-3.2 model on the synthetically generated data is in [scripts\finetuning\llama-2-2-3b-finetune-inference.ipynb](https://github.com/namantuli18/11711-RAG-2-riches/blob/main/scripts/finetuning/llama-2-2-3b-finetune-inference.ipynb)
