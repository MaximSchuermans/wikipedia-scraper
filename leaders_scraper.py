import json
import requests as r
import re
from bs4 import BeautifulSoup

def get_first_paragraph(wikipedia_url, leader_name, session):
    print(wikipedia_url) # keep this for the rest of the notebook
    paragraphs = BeautifulSoup(session.get(wikipedia_url).text, 'html.parser')
    paragraphs = [para for para in paragraphs.find_all('p')]
    for paragraph in paragraphs:
        if re.compile(r'[0-9]{4}').search(str(paragraph)) is not None:
            return paragraph.text
            break

def get_leaders():
    root_url = "https://country-leaders.onrender.com"
    countries_url, leaders_url = (root_url + "/countries", root_url + '/leaders')
    cookies = r.get(root_url + "/cookie").cookies
    countries = [country[1:-1] for country in r.get(countries_url, cookies=cookies).text.strip('][').split(',')]
    leaders_per_country = {country: r.get(leaders_url, cookies=cookies, params={'country': country}).json() for country in countries}
    session = r.Session()
    session.get(root_url + '/cookie')
    for country in leaders_per_country:
        for i, leader in enumerate(leaders_per_country[country]):
            leaders_per_country[country][i]['wikipedia_url'] = get_first_paragraph(leader['wikipedia_url'], leader['last_name'], session)
    return leaders_per_country

def clean_paragraph(paragraph):
    new_paragraph = re.sub(r'\[.*\]', '', paragraph) #clean references
    new_paragraph = re.sub(r'\(.*\)', '', new_paragraph) #clean phonetic pronouniation
    new_paragraph = re.sub(r'\<.*\>.*\<.*\>', '', new_paragraph) #remove html
    new_paragraph = re.sub(r'\u00bb', '', new_paragraph)
    new_paragraph = re.sub(r'\u00ab', '', new_paragraph)
    return re.sub(r'[\u2000-\u2fff]', '', new_paragraph)

def save(leaders_per_country):
    with open('leaders.json', 'w+') as json_file:
        leaders_json = json.dumps(leaders_per_country)
        json_file.write(leaders_json)

if __name__ == "__main__":
    leaders_per_country = get_leaders()
    save(leaders_per_country)
