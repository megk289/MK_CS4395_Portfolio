# Meghana Kambhampati
# MXK190048
# CS 4395.001
# Portfolio 2: Word Guess Game
# This program takes in raw text and processes it. The important
# words are lemmatized and the nouns are separated. The 50 most commonly
# used nouns in the text will be used for a word guessing game.
# In this game, the user will have to guess a letter. If the letter
# is in the word they need to guess, they get a point.

import sys

import nltk
from nltk import *
from nltk.corpus import stopwords
from random import seed
from random import randint



'''
Opens the text file and processes it according to the steps:
    - tokenize the lower-case raw text, reduce the tokens to 
        only those that are alpha, not in the NLTK stopword list, 
        and have length > 5
    - lemmatize the tokens and make a list of unique lemmas
    - do pos tagging on the unique lemmas and print the first 20
    - make a list of only nouns from the lemmas
    - print the number of tokens and nouns
    
Args: 
    input_file: input raw text file with words
    
Returns: a list of lemmatized tokens and nouns from the input text file
'''


def preprocess_text(input_file):
    with open(input_file, "r") as f:
        raw_text = f.read().lower()
    tokens = word_tokenize(raw_text)
    
    # lexical analysis
    set_text = set(tokens)
    print("\nLexical diversity: %.2f" % (len(set_text) / len(tokens)))

    # reduce tokens to those that are alpha, at least 5 chars long,
    # and not in the STOP word list
    tokens = [t for t in tokens if t.isalpha() and
              t not in stopwords.words('english') and
              len(t) > 5]

    # lemmatize
    wnl = WordNetLemmatizer()
    tokens = [wnl.lemmatize(t) for t in tokens]

    # make a set of unique tokens
    unique_tokens = set(tokens)
    unique_tokens = nltk.pos_tag(unique_tokens)
    print(unique_tokens[:20])

    # list of nouns
    nouns = list()
    for word, pos in unique_tokens:
        if pos in ['NN', 'NNS', 'NNP', 'NNPS']:
            nouns.append(word)

    print("Number of tokens: ", len(tokens))
    print("Number of nouns: ", len(nouns))
    return tokens, nouns


'''
Takes the 50 most common words and creates a guessing 
game for the user

Args: a list of the 50 most common nouns from the input text 
'''


def guessing_game(game_words):
    score = 5
    print('Let\'s play a word guessing game!')

    word = game_words[randint(0, 49)]
    displayed_info = ['_' for _ in  range(len(word))]
    print(' '.join(displayed_info))

    while score > 0 and '_' in displayed_info:
        char = input('Guess a letter: ')
        
        # '!' causes the game to exit
        if char == '!':
            break

        if len(char) != 1:
            print('Guess exactly one letter.')
            continue
        
        if char in word:
            score += 1
            for i in range(len(word)):
                if word[i] == char:
                    displayed_info[i] = word[i]
            print('Right! Score is ' + str(score))
            print(' '.join(displayed_info))
        else:
            score -= 1
            print('Sorry, guess again. Score is ' + str(score))

    if '_' not in displayed_info:
        print('You solved it!')
    elif char == '!':
        print('Quit')
    else:
        print('Failed to guess word. The word is ' + word)


def main():
    if len(sys.argv) < 2:
        print('ERROR: No text file provided')
        return

    input_file = sys.argv[1]

    tokens, nouns = preprocess_text(input_file)

    counts = {t: tokens.count(t) for t in tokens}
    
    # sort counts
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print('50 most common words:')
    for i in range(50):
        print(sorted_counts[i][0] + ' (' + str(sorted_counts[i][1]) + ' times)')

    guessing_game([word for (word, _) in sorted_counts[0:50]])


if __name__ == '__main__':
    main()
