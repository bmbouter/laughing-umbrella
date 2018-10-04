import json
import math
import random
import string

from django.core.management.base import BaseCommand

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

from laughing_umbrella.models import Issue


CORPUS_WORD_SIZE = 2000


def stem_lem_words_for_issue(issue):
    porter_stemmer = PorterStemmer()
    wordnet_lemmatizer = WordNetLemmatizer()

    # Add in main title and body data
    issue_data = json.loads(issue.text)
    tokenized_words = word_tokenize(issue_data['title']) + word_tokenize(issue_data['body'])

    # Add in comment data
    # for comment in issue.comments.all():
    #     comment_data = json.loads(comment.text)
    #     tokenized_words.extend(word_tokenize(comment_data['body']))

    # Stem and Lemm all the words
    words = []
    for word in tokenized_words:
        stemmed_word = porter_stemmer.stem(word)
        words.append(wordnet_lemmatizer.lemmatize(stemmed_word))
    return words


def custom_corpus():
    return ['fail', 'error', 'support', 'password', 'root', 'add', 'feature', 'configur', 'allow',
            'warn', 'issu', 'localhost', 'fatal', 'option', 'new', 'problem']


def build_corpus():
    words = []
    for issue in Issue.objects.exclude(type=''):
        words.extend(stem_lem_words_for_issue(issue))

    freq_dist = nltk.FreqDist(words)
    unique_words = set(words)
    words_sorted_by_freq = sorted(unique_words , key=freq_dist.__getitem__, reverse=True)
    words_sorted_by_freq_no_punctuation = list(
        filter(
            lambda x: all(not j.isdigit() and j not in string.punctuation for j in x),
            words_sorted_by_freq
        )
    )
    return list(words_sorted_by_freq_no_punctuation)[:CORPUS_WORD_SIZE]


def feature_extractor(issue, corpus):
    features = {}
    document_words = stem_lem_words_for_issue(issue)
    for word in corpus:
        features['contains({})'.format(word)] = (word in document_words)
    return features


def main():
    # import pydevd
    # pydevd.settrace('localhost', port=17264, stdoutToServer=True, stderrToServer=True,
    #                 suspend=False)
    #corpus = build_corpus()
    corpus = custom_corpus()

    data = []
    for issue in Issue.objects.filter(type='B'):
        data.append((feature_extractor(issue, corpus), 'bugfix'))
    for issue in Issue.objects.filter(type='F'):
        data.append((feature_extractor(issue, corpus), 'feature'))
    for issue in Issue.objects.filter(type='O'):
        data.append((feature_extractor(issue, corpus), 'other'))
    for issue in Issue.objects.filter(type='S'):
        data.append((feature_extractor(issue, corpus), 'security'))

    random.shuffle(data)
    # data = data[:400]
    split_index = math.floor(len(data) * 0.9)  # get the index to divide into 70% train/test data.
    train_set, test_set = data[:split_index], data[split_index:]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    print(nltk.classify.accuracy(classifier, test_set))
    classifier.show_most_informative_features(20)


class Command(BaseCommand):
    help = 'Train the training model.'

    def handle(self, *args, **options):
        main()
