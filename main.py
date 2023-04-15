import heapq
import json
import random
import re
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from typing import Callable, Any, List, Tuple, Dict, TextIO

'''
Save to disk to save time

Args: the function being called

Returns: Modified wrapped function
'''


def save_to_disk(f: Callable[..., Any]) -> Any:
    def inner(*args: List[Any]) -> str:
        cache_path = f.__name__ + '.cache'
        try:
            with open(cache_path) as cache_file:
                return json.load(cache_file)
        except FileNotFoundError:
            result = f(*args)
            with open(cache_path, 'w') as cache_file:
                json.dump(result, cache_file)
            return result
    return inner


'''
Get the text (Hamlet) from the web

Returns: text scraped from website
'''


@save_to_disk
def download_text() -> str:
    url = 'https://www.gutenberg.org/cache/epub/1524/pg1524-images.html'

    def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))):
            return False
        return True

    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content.decode('utf-8'), 'html.parser')
    texts = soup.findAll(string=True)
    lines = ' '.join([text.strip() for text in texts if visible(text)])
    return ''.join(lines)[100:]


'''
Clean up the scraped text and only save the lines of dialogue
'''


@save_to_disk
def clean_and_tokenize_text(raw_text: str) -> List[str]:
    # replace unicode indicators with their actual chars
    raw_text = raw_text.replace('\u2018', "'").replace('\u2019', "'").replace('\u2014', '-')

    # start and end lines
    start_line = 'THE TRAGEDY OF HAMLET, PRINCE OF DENMARK'
    end_line = 'END OF THE PROJECT GUTENBERG EBOOK HAMLET, PRINCE OF DENMARK'

    # list of words to remove the lines of
    remove = {'Scene', 'SCENE', 'ACT', 'Enter', 'HAMLET', 'CLAUDIUS',
              'KING', 'GHOST', 'GERTRUDE', 'POLONIUS', 'LAERTES',
              'OPHELIA', 'HORATIO', 'FORTINBRAS', 'VOLTEMAND',
              'CORNELIUS', 'ROSENCRANTZ', 'GUILDENSTERN', 'MARCELLUS',
              'BARNARDO', 'OSRIC', 'FRANCISCO', 'REYNALDO', 'PLAYER',
              'GENTLEMAN', 'COURTIER', 'PRIEST', 'CLOWN', 'GRAVEDIGGER',
              'ENGLISH AMBASSADOR', 'CAPTAIN', 'LORD', 'LADY', 'OFFICER',
              'SOLDIER', 'SAILOR', 'MESSENGER', 'ATTENDANT', '*',
              'PROJECT GUTENBERG', 'Project Gutenberg', 'website'}
    running = False

    # indicates what lines should be included in the result
    def should_include(sent: str) -> bool:
        nonlocal running
        if start_line in sent:
            running = True
            return False
        if end_line in sent:
            running = False
        if not running:
            return False
        for word in word_tokenize(sent):
            if word in remove:
                return False
        return True
    return [' '.join(sent.splitlines()) for sent in sent_tokenize(raw_text) if should_include(sent)]


'''
Saves each line of dialogue with its sentiment score in the knowledge base

Args: text sent tokens

Returns: knowledge base as a dictionary
'''


@save_to_disk
def create_knowledge_base(text: List[str]) -> Dict[str, float]:
    return {line: analyze_sentiment(line) for line in text}


'''
Calculates cosine similarity of the user's response and items in the dictionary

Args: the user's message, knowledge base, a list of the user's data

Returns: similarity scores of each item in the knowledge base with the user's message
'''


def get_similarity_scores(user_message: str, knowledge_base: Dict[str, float], user_info: List[Tuple[str, float]]) -> Dict[str, float]:
    user_sentiment = analyze_sentiment(user_message)
    user_info.append((user_message, user_sentiment))  # add to user's information

    # cosine similarity
    knowledge_base_sentences = [sent for sent in knowledge_base]
    tf_idf = TfidfVectorizer().fit_transform(knowledge_base_sentences + [sent[0] for sent in user_info])
    sentiment_similarity_scores = {sent: abs(user_sentiment - knowledge_base[sent]) / 2 for sent in knowledge_base_sentences}
    cosine_similarity_scores = cosine_similarity(tf_idf[-1], tf_idf).tolist()

    # store sentiment similarity scores
    scores = {}
    for i in range(len(knowledge_base_sentences)):
        sent = knowledge_base_sentences[i]
        scores[sent] = sentiment_similarity_scores[sent] + cosine_similarity_scores[0][i]
    return scores


'''
Finds the most related message to the user's input based on cosine similarity (calculated in
    get_similarity_scores)
    
Args: the user's message, the knowledge base of dialogue, user information

Returns: A string with the best choice of chatbot response
'''


def formulate_response(user_message: str, knowledge_base: Dict[str, float], user_info: List[Tuple[str, float]]) -> str:
    scores = get_similarity_scores(user_message, knowledge_base, user_info)
    result = heapq.nlargest(10, list(scores.items()), key=lambda x: x[1])
    # top, most similar picks
    return random.choices([sent[0] for sent in result], weights=[sent[1] for sent in result])[0]


'''
Calculates sentiment score of a string

Args: string to be analyzed

Returns: composite sentiment score
'''


def analyze_sentiment(response: str) -> float:
    return SentimentIntensityAnalyzer().polarity_scores(response)['compound']


def main():
    raw_text = download_text()
    text = clean_and_tokenize_text(raw_text)
    knowledge_base = create_knowledge_base(text)

    name = input('BOT:\nWhat is thy name?\n\nUSER:\n')
    filename = name
    try:
        with open(filename, "r") as userfile:
            user_info = json.load(userfile)
    except FileNotFoundError:
        user_info = []

    user_message = input("\nBOT:\nHow fares my lord?\n\nUSER:\n")

    bye = ['bye', 'bye!', 'Bye', 'Bye!', 'Farewell', 'Fare thee well', 'farewell', 'fare thee well', 'see you!',
           'Goodbye', 'goodbye']

    while user_message not in bye:
        response = formulate_response(user_message, knowledge_base, user_info)
        knowledge_base.pop(response, None)
        print('\nBOT:')
        user_message = input(response + '\n\n' + name.upper() + ':\n')

    print('\nFare ye well, ' + name)

    with open(filename, "w") as userfile:
        json.dump(user_info[-50:], userfile)


if __name__ == '__main__':
    main()
