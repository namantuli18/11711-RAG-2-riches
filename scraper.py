import wikipediaapi
import pandas as pd
import os
import tqdm

if not os.path.exists('raw_data'):
    os.makedirs('raw_data')

wiki = wikipediaapi.Wikipedia('RAG 2 Riches', 'en', extract_format = wikipediaapi.ExtractFormat.WIKI)

import os
import pandas as pd

def save_processed_csv(wiki, page_title, exclude_sections):
    wiki_page = wiki.page(page_title)
    try:
        assert wiki_page.exists(), print("{} messed up".format(page_title))
    except:pass
    
    data = []

    def process_final_subsections(section, full_title):
        full_title = full_title + ' -> ' + section.title if full_title else section.title
        if section.title not in exclude_sections:
            if not section.sections:
                data.append({
                    'section': full_title,
                    'text': section.text
                })
            else:
                for subsection in section.sections:
                    process_final_subsections(subsection, full_title)

    for s in wiki_page.sections:
        process_final_subsections(s, '')

    df = pd.DataFrame(data, columns=['section', 'text'])
    df.to_csv(os.path.join(os.path.curdir, 'raw_data/{}.csv'.format(page_title)), index=False)

page_names = ['Pittsburgh',
    'History of Pittsburgh',
    'Pittsburgh Symphony Orchestra',
    'Pittsburgh Opera',
    'Pittsburgh Festival Opera',
    'Pittsburgh Cultural Trust',
    'Carnegie Museums of Pittsburgh',
    'Frick Collection',
    'American Jewish Museum',
    'Andy Warhol Museum',
    'August Wilson Center for African American Culture',
    'Bicycle Heaven',
    'Carnegie Museum of Art',
    'Carnegie Museum of Natural History',
    'Kamin Science Center',
    'Center for PostNatural History',
    "Children's Museum of Pittsburgh",
    'The Clemente Museum',
    'Elmer H. Grimm Sr. Pharmacy Museum',
    'Fort Pitt Museum',
    'The Frick Pittsburgh',
    'Mattress Factory',
    'Miller Gallery at Carnegie Mellon University',
    'Miniature Railroad & Village',
    'Nationality Rooms',
    'Pittsburgh Center for the Arts',
    'Pittsburgh Glass Center',
    'Randyland',
    'Society for Contemporary Craft',
    'Soldiers and Sailors Memorial Hall and Museum',
    'ToonSeum',
    'Trundle Manor',
    'Wood Street Galleries',
    'Picklesburgh',
    'Bloomfield (Pittsburgh)']

exclude_sections = ['See also', 'References', 'Bibliography', 'External links', 'Explanatory notes', 'Further reading']
for page in tqdm.tqdm(page_names):
    save_processed_csv(wiki, page, exclude_sections)