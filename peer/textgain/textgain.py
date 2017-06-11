"""
Query textgain.com for age, gender, or education associated with prose.
"""

import requests
import json

def textgain(type, raw_text, language='en'):
    if type == 'gender':
        url = 'https://api.textgain.com/1/gender'
    elif type == 'edu':
        url = 'https://api.textgain.com/1/education'
    elif type == 'personality':
        url = 'https://api.textgain.com/1/personality'
    elif type == 'age':
        url = 'https://api.textgain.com/1/age'
    elif type == 'sentiment':
        url = 'https://api.textgain.com/1/sentiment'
    elif type == 'genre':
        url = 'https://api.textgain.com/1/genre'
    elif type == 'concepts':
        url = 'https://api.textgain.com/1/concepts'
    else:
        return "Type not specified"

    r = requests.post(url, data={'q':raw_text, 'lang':language})

    return json.loads(r.text).get(type)
"""
def gender(raw_text):
    g = textgain('gender', raw_text)
    return json.loads(g.text).get('gender')

def age(raw_text):
    g = textgain('age', raw_text)
    return json.loads(g.text).get('age')

def education(raw_text):
    g = textgain('edu', raw_text)
    return json.loads(g.text).get('education')

def personality(raw_text):
    g = textgain('personality', raw_text)
    return json.loads(g.text).get('personality')

def sentiment(raw_text):
    g = textgain('sentiment', raw_text)
    return json.loads(g.text).get('sentiment')

def genre(raw_text):
    g = textgain('genre', raw_text)
    return json.loads(g.text).get('genre')

def main(raw_text):
    chars = [gender(raw_text), age(raw_text), education(raw_text), personality(raw_text), sentiment(raw_text), genre(raw_text)]
    return chars
"""
