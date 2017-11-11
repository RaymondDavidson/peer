"""
Query textgain.com for age, gender, or education associated with prose.
"""



import json
import requests


def textgain(call, raw_text, language='en'):
    if call == 'gender':
        url = 'https://api.textgain.com/1/gender'
    elif call == 'edu':
        url = 'https://api.textgain.com/1/education'
    elif call == 'personality':
        url = 'https://api.textgain.com/1/personality'
    elif call == 'age':
        url = 'https://api.textgain.com/1/age'
    elif call == 'sentiment':
        url = 'https://api.textgain.com/1/sentiment'
    elif call == 'genre':
        url = 'https://api.textgain.com/1/genre'
    elif call == 'concepts':
        url = 'https://api.textgain.com/1/concepts'
    else:
        return "Call not specified"

    try:
        r = requests.post(url, data={'q':raw_text, 'lang':language})
        return json.loads(r.text).get(call)
    except:
        print("Textgain - %s failed - probably too many requests." % call)
