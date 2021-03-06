# -*- coding: utf-8 -*-
"""Creates document instance for analysis for semantics and lexical statistics.

Opens and reads document to string raw_text. Relies on textract to handle
.txt, .odt, docx.
"""


import datetime
import json
import math
import os
import re
import string
import sys
import time
from collections import Counter
from curses.ascii import isdigit
from mimetypes import MimeTypes  # Not necessary, we think
from random import randint

import docx2txt
import nltk
import requests
import textract
import unidecode
from nltk import FreqDist, pos_tag, tokenize
from nltk.corpus import cmudict, stopwords
from nltk.tokenize import RegexpTokenizer
from proselint.tools import lint
from textstat.textstat import textstat

from cliches import cliches
from conventions.conventions import main as grammar
from enchant.checker import SpellChecker
from external.education import education_result
from external.rosette_auth import rosette_auth
from external.service_informant import Textgain
from gensim.summarization import summarize
from passive.passive import main as passive
from readability.readability import Readability
from rosette.api import API, DocumentParameters, RosetteException
from sentiment import sentiment
from textblob import TextBlob
from textgain.textgain import textgain
from difficult_spelling.difficult_words import difficult_spells

try:
    from external.aylien import auth as aylien_auth
except:
    print "The external modules that work with Aylien are not installed."
    pass
# from mimetypes import MimeTypes

CONFIG_FILE = 'config.json'



class Sample:
    """Represents a document analysis.

    Uses textract to read document into a long string.  The methods are various
    sequences to get information to help make decisions for deliberate academic
    writing.
    """

    def __init__(self, writing):
        """
        Create document instance for analysis.

        Opens and reads document to string raw_text.
        Textract interprets the document format and
        opens to plain text string (docx, pdf, odt, txt)

        Args:
            path (str): path to file to open, anaylze, close


        Public attributes:
        -user: (str) optional string to set username.
        -path: (str) relative path to document.
        -abs_path: (str) the absolute path to the document.
        -file_name:  (str) the file name with extension of document (base
        name).
        -mime:  tbd
        -guessed_type:  makes best guess of mimetype of document.
        -file_type:  returns index[0] from guessed_type.
        -raw_text:  (str) plain text extracted from .txt, .odt, .pdf, .docx,
        and .doc.
        -ptext:  (str) raw text after a series of regex expressions to
        eliminate special characters.
        -text_no_feed:  (str) ptext with most new line characters eliminated
        /n/n stays intact.
        -sentence_tokens:  list of all sentences in a comma separated list
        derived by nltk.
        -sentence_count:  (int) count of sentences found in list.
        -passive_sentences:  list of passive sentences identified by the
        passive module.
        -passive_sentence_count:  count of the passive_sentences list.
        -percent_passive:  (float) ratio of passive sentences to all sentences
        in percent form.
        -be_verb_analysis:  (int) sum number of occurrences of each to be verb
        (am, is, are, was, were, be, being been).
        -be_verb_count: tbd
        -be_verb_analysis: tbd
        -weak_sentences_all:  (int) sum of be verb analysis.
        -weak_sentences_set:  (set) set of all sentences identified as
        having to be verbs.
        -weak_sentences_count:  (int) count of items in weak_sentences_set.
        -weak_verbs_to_sentences:  (float) proportion of sentences with to
        be to all sentences in percent (this might not be sound).
        -word_tokens:  list of discreet words in text that breaks
        contractions up (default nltk tokenizer).
        -word_tokens_no_punct:  list of all words in text including
        contractions but otherwise no punctuation.
        -no_punct:  (str) full text string without sentence punctuation.
        -word_tokens_no_punct:  uses white-space tokenizer to create a list
        of all words.
        -readability_flesch_re:  (int) Flesch Reading Ease Score (numeric
        score) made by textstat module.
        -readability_smog_index:  (int) grade level as determined by the
        SMOG algorithum made by textstat module.
        -readability_flesch_kincaid_grade:  (int)  Flesch-Kincaid grade level
        of reader made by textstat module.
        -readability_coleman_liau_index:  (int) grade level of reader as made by
        textstat module.
        -readability_ari:  (int) grade leader of reader determined by
        automated readability index algorithum implemented by textstat.
        -readability_linser_write:  FIX SPELLING grade level as determined
        by Linsear Write algorithum implemented by textstat.
        -readability_dale_chall:  (int) grade level based on Dale-Chall
        readability as determined by textstat.
        -readability_standard:  composite grade level based on readability
        algorithums.
        -flesch_re_key:  list for interpreting Flesch RE Score.
        -word_count:  word count of document based on white space tokener,
        this word count should be used.
        -page_length:  (float) page length in decimal format given 250
        words per page.
        -paper_count:  (int) number of printed pages given 250 words per
        page.
        -parts_of_speech:  words with parts of speech tags.
        -pos_counts:  values in word, tag couple grouped in a list (Counter).
        -pos_total:  (int) sum of pos_counts values
        -pos_freq:  (dict) word, ratio of whole
        -doc_pages:  (float) page length based on 250 words per page
        (warning, this is the second time this attribute is defined).
        -freq_words:  word frequency count not standardized based on the
        correct word tokener (not ratio, just count).
        modal_dist:  count of auxillary verbs based on word_tokens_no_punct.
        sentence_count (int): Count the sentence tokens
        passive_sentences (list): List of all sentences identified as passive
        passive_sentence_count (int): count of items in passive_sentences
        be_verb_count (int): count "to be" verbs in text
        word_tokens_no_punct (list): words separated, stripped of punctuation,
         made lower case
        flesch_re_key (str): reading ease score to description
        freq_words (list or dict): frequency distribution of all words
        modal_dist (list): frequency distribution of aux verbs
        """
        self.user = ""
        if os.path.isfile(writing):
            self.abs_path = os.path.abspath(writing)
            self.file_bytes = os.path.getsize(self.abs_path)
            self.file_kbytes = float(self.file_bytes/1000.0)
            self.file_name = os.path.basename(writing)
            self.mime = MimeTypes()
            self.guessed_type = self.mime.guess_type(writing)
            self.file_type = self.guessed_type[0]
            #self.raw_text = textract.process(writing,
                #encoding="unicode_internal")
            #self.raw_text = unidecode.unidecode_expect_nonascii(self.raw_text)
            if self.file_type == \
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                self.raw_text = unicode(self.docxDeal(self.abs_path))
            elif self.file_type == "text/plain":
                self.raw_text = open(self.abs_path).read()
                self.raw_text = \
                    unidecode.unidecode_expect_nonascii(self.raw_text)
            else:
                self.raw_text = textract.process(writing, encoding="ascii")
                #self.raw_text = unidecode.unidecode_expect_nonascii(self.raw_text)
        else:
            self.raw_text = unicode(writing)
            self.raw_text = unidecode.unidecode_expect_nonascii(self.raw_text)
        if self.raw_text:
            self.time_stamp = self.timestamp()
            #self.ptext = re.sub(u'[\u201c\u201d]', '"', self.raw_text)
            #self.ptext = re.sub(u"\u2014", "--", self.ptext)
            #self.ptext = re.sub(",", ",", self.ptext)
            #self.ptext = re.sub("—", "--", self.ptext)
            #self.ptext = re.sub("…", "...", self.ptext)
            self.text_no_feed = self.clean_new_lines(self.raw_text)
            self.sentence_tokens = self.sentence_tokenize(self.text_no_feed)
            self.sentence_count = len(self.sentence_tokens)
            self.passive_sentences = passive(self.text_no_feed)
            self.passive_sentence_count = len(self.passive_sentences)
            self.percent_passive = (100 *
                                        (float(self.passive_sentence_count) /
                                         float(self.sentence_count)))
            self.percent_passive_round = round(self.percent_passive, 2)
            self.hard_spelling = difficult_spells(self.raw_text)
            self.be_verb_analysis = self.count_be_verbs(self.sentence_tokens)
            self.be_verb_count = self.be_verb_analysis[0]
            self.weak_sentences_all = self.be_verb_analysis[1]
            self.weak_sentences_set = set(self.weak_sentences_all)
            self.weak_sentences_count = len(self.weak_sentences_set)
            self.weak_verbs_to_sentences = 100 * float(
                self.weak_sentences_count) / float(self.sentence_count)
            self.weak_verbs_to_sentences_round = round(
                self.weak_verbs_to_sentences, 2)
            self.word_tokens = self.word_tokenize(self.text_no_feed)
            self.word_tokens_no_punct = \
                self.word_tokenize_no_punct(self.text_no_feed)
            self.no_punct = self.strip_punctuation(self.text_no_feed)
            # use this! It make lower and strips symbols
            self.word_tokens_no_punct = self.ws_tokenize(self.no_punct)
            # readability data
            self.readability_flesch_re = \
                textstat.flesch_reading_ease(self.text_no_feed)
            #self.readability_smog_index = \
            #    textstat.smog_index(self.text_no_feed)
            self.readability_flesch_kincaid_grade = \
                textstat.flesch_kincaid_grade(self.text_no_feed)
            self.readability_coleman_liau_index = \
                textstat.coleman_liau_index(self.text_no_feed)
            self.readability_ari = \
                textstat.automated_readability_index(self.text_no_feed)
            self.readability_linser_write = \
                textstat.linsear_write_formula(self.text_no_feed)
            self.readability_dale_chall = \
                textstat.dale_chall_readability_score(self.text_no_feed)
            self.readability_standard = \
                textstat.text_standard(self.text_no_feed)
            self.flesch_re_desc_str = self.flesch_re_desc(int(
                textstat.flesch_reading_ease(self.text_no_feed)))
            self.polysyllabcount = textstat.polysyllabcount(self.text_no_feed)
            self.lexicon_count = textstat.lexicon_count(self.text_no_feed)
            # readability from a different module
            self.readability_smog_index = self.smog(self.text_no_feed)
            self.readability_gunning = self.gunning_fog(self.text_no_feed) # doesn't work
            self.readability_lix = self.lix(self.raw_text) # no result
            self.readability_rix = self.rix(self.raw_text) # no result
            # Back to original module
            self.avg_syllables_per_word = textstat.avg_syllables_per_word(
                self.text_no_feed)
            self.avg_sentence_per_word = textstat.avg_sentence_per_word(
                self.text_no_feed)
            self.avg_sentence_length = textstat.avg_sentence_length(
                self.text_no_feed)
            self.avg_letter_per_word = textstat.avg_letter_per_word(
                self.text_no_feed)
            self.long_sentences = self.sentences_20(self.sentence_tokens)
            self.difficult_words = textstat.difficult_words(self.text_no_feed)
            # passive
            self.rand_passive = self.select_random(self.passive_sentence_count,
                                                   self.passive_sentences)
            self.rand_weak_sentence = self.select_random(
                len(self.weak_sentences), self.weak_sentences)
            self.word_count = len(self.word_tokens_no_punct)
            self.page_length = float(self.word_count)/float(250)
            self.paper_count = int(math.ceil(self.page_length))
            self.parts_of_speech = pos_tag(self.word_tokens_no_punct)
            self.pos_counts = Counter(tag for word, tag in
                                      self.parts_of_speech)
            self.pos_total = sum(self.pos_counts.values())
            self.pos_freq = dict((word, float(count)/self.pos_total) for
                                 word, count in self.pos_counts.items())
            self.doc_pages = float(float(self.word_count)/float(250))
            self.freq_words = \
                self.word_frequency(self.word_tokens_no_punct)
            self.modal_dist = self.modal_count(self.word_tokens_no_punct)
            # self.ws_tokens = self.ws_tokenize(self.text_no_cr)
            self.pos_count_dict = self.pos_counts.items()
            # model for ony pos count
            self.modals = self.pos_isolate(
                'MD', self.pos_count_dict)
            self.preposition_count = self.pos_isolate(
                            'IN', self.pos_count_dict)
            self.adjective_count = self.pos_isolate_fuzzy(
                'JJ', self.pos_count_dict)
            self.adverb_count = self.pos_isolate_fuzzy(
                'RB', self.pos_count_dict)
            self.proper_nouns = self.pos_isolate_fuzzy(
                'NNP', self.pos_count_dict)
            self.cc_count = self.pos_isolate('CC', self.pos_count_dict)
            # commas
            self.commas = self.char_count(",")
            self.comma_sentences = self.list_sentences(",")
            self.comma_example = self.select_random(len(self.comma_sentences), self.comma_sentences)
            # semicolons
            self.semicolons = self.char_count(";")
            self.semicolon_sentences = self.list_sentences(";")
            self.semicolon_example = self.select_random(len
                                                         (self.semicolon_sentences),
                                                self.semicolon_sentences)
            #questions
            self.question_marks = self.char_count("?")
            self.questions = self.list_sentences("?")
            self.question_example = self.select_random(len(
                self.questions), self.questions)
            # exclamations
            self.bangs = self.char_count("!")
            self.exclamations = self.list_sentences("!")
            self.exclamation_example = self.select_random(len(
                self.exclamations), self.exclamations)

            #proselint
            self.lint_suggestions = lint(self.raw_text)
            # unrecognized words
            self.unrecognized_words = self.spelling(self.raw_text)
            self.unrecognized_words_count = len(self.unrecognized_words)
            self.unrecognized_words_random = self.select_random(
                    self.unrecognized_words_count,self.unrecognized_words)
            #cliche catcher
            self.cliche_list = cliches.cliches()
            self.cliche_results = cliches.process_cliches(self.cliche_list,
                                              self.raw_text.lower())
            self.cliches_in_text = self.cliche_results[1]
            self.cliche_count = self.cliche_results[0]
            #sentiment - external via api
            try:
                self.api_sentiment = sentiment.sentiment_result(self.raw_text)
            except:
                self.api_sentiment = ""
                pass
            # education level (external - calls to textgain)
            try:
                self.edu = education_result(self.raw_text)
            except:
                pass
            # age level (external - call to textgain)
            try:
                self.age = textgain('age', self.raw_text, language='en')
            except:
                pass
            # guessed gender (external - calls to textgain)
            try:
                self.gender = textgain('gender', self.raw_text)
            except:
                pass
            #genre (external - calls to textgain)
            try:
                self.genre = textgain('genre', self.raw_text)
            except:
                pass
            # textgain concepts
            try:
                self.textgain_concepts = textgain('concepts', self.raw_text)
            except:
                pass
            #personality (external call to textgain)
            try:
                self.personality = textgain('personality', self.raw_text)
                if self.personality == 'E':
                    self.personality = 'Extrovert'
                elif self.personality == u'I':
                    self.personality = 'Introvert'
                else:
                    pass
            except:
                pass
            #Rosette
            try:
                self.rosette_client = rosette_auth()
                self.rosette_params = DocumentParameters()
                self.rosette_params["language"] = "eng"
                self.rosette_params.load_document_string(self.raw_text)
                self.rosette_sentiment = self.rosette_api.sentiment(self.result)
                self.rosette_sentiment_result = self.rosette_sentiment['document']
            except:
                print("Could not contact Rosette dependencies.")
                pass
            # Aylien
            try:
                self.aylien_client = aylien_auth()
                self.combined_aylien = self.aylien_client.Combined({'text': self.raw_text, 'endpoint':["hashtags", "concepts", "classify", "entities"]})
                self.summary_aylien = self.aylien_client.Summarize({'text': self.raw_text, 'title': self.file_name, 'sentence_number':4})
                self.summary_paragraph_aylien = " ".join(self.summary_aylien['sentences'])
                self.hashtags_aylien = self.aylien_client.Hashtags({'text': self.raw_text})
                self.hashtags =                      self.hashtag_cleaner(self.hashtags_aylien['hashtags'])
                #self.entities_aylien = self.aylien_client.Entities({'text':self.raw_text})
                #self.keywords_aylien = self.entities_aylien['entities']['keyword']

            except:
                print("Problem with Aylien")
                pass
            #TextBlob attributes
            self.blob = TextBlob(self.raw_text)
            self.polarity = self.blob.sentiment.polarity
            self.subjectivity = self.blob.sentiment.subjectivity
            self.intro = self.sentence_tokens[0]
            self.exit = self.sentence_tokens[-1]
            # noun phrases
            self.phrases = self.tag_phrases(TextBlob(self.raw_text))
            #textgain
            ###self.concepts = textgain('concepts', self.raw_text)
            #language_check
            self.check = grammar(self.raw_text)
            self.grammar_error_count = self.check[0]
            self.grammar_feedback = self.check[1]
            # pov
            self.first_person = self.pronouns(['I', 'me', 'mine', 'myself', 'I\'ve', 'I\'m'], self.raw_text)
            self.first_person_count = len(self.first_person)
            self.second_person = self.pronouns(['you', 'you\'re', 'yours', 'yourself', 'you\'ve'], self.raw_text)
            self.second_person_count = len(self.second_person)
            self.summary = summarize(self.raw_text)
    def flesch_re_desc(self, score):
        if score < 30:
            return "Very Confusing"
        elif score < 50 and score > 29:
            return "Difficult"
        elif score < 60 and score > 49:
            return "Fairly Difficult"
        elif score > 59 and score < 70:
            return "Standard"
        elif score > 69 and score < 80:
            return "Fairly Easy"
        elif score < 90 and score > 79:
            return "Easy"
        else:
            return "Very Easy"

    def strip_punctuation(self, string_in):
        """
        Strip punctuation from string and make it lower case.

        Given a string of sentences, translate string
        to remove *some* common symbols and convert capital
        letters to lower case.

        Args:
            string_in (str): Text to strip punctuation from

        return:
            str
        """
        string_in = str(string_in).translate(None, ',.!?\"<>{}[]--@()\'--')
        return str(string_in.lower())

    def ws_tokenize(self, text):
        """
        Given string of words, return word tokens with  contractions OK.

        Other tokenizers tokenize punctuation. The WhitespaceTokenizer
        is important because of contractions.

        Args:
            text (str)

        returns:
            list

        """
        self.tokenizer = nltk.tokenize.regexp.WhitespaceTokenizer()
        return self.tokenizer.tokenize(text)

    def syllables_per_word(self, text):
        """
        Return count of syllables per word.

        Loops through all words to add word and syllable
        count to a list.

        Args:
        text (str)

        Returns:
        list
        """
        self.word_syllables = []
        for word in text:
            self.word_syllables.append([word,
                                        textstat.textstat.syllable_count(
                                            word)])
        return self.word_syllables

    def polysyllables(self, text):
        """
        Count polysyllables.

        Count words in text string that have >= 3 syllables.

        Args:
        text(str)

        Returns:
        int: polysllable word count in text arg

        """
        return textstat.textstat.polysyllabcount(text)

    def word_frequency(self, words):
        """
        List 20 most common words in tokenized list.

        memo: words = [word for word in words if not word.isnumeric()].

        Args:
        text(str)

        Returns:
        list
        """
        words = [word.lower() for word in words]
        self.word_dist = FreqDist(words)
        return self.word_dist.most_common(20)

    def word_tokenize_no_punct(self, text):
        """
        Make list of words without listing punctuation.

        Args:
            text (str): Plain text string

        Returns:
             list of words
        """
        tokenizer = RegexpTokenizer(r'\w+')
        return tokenizer.tokenize(text)

    def word_tokenize(self, paragraph):
        """
        Tokenize words from long string that includes sentences.

        Uses default tokenizer from nltk.

        Args:
            paragraph (str)

        Return:
            list

        """
        try:
            self.word_tokens = tokenize.word_tokenize(paragraph)
            return self.word_tokens
        except:
            print("Error: Cannot perform word analyses.")
            return False

    def sentence_tokenize(self, paragraphs):
        """
        Tokenize sentences.

        Uses default sent tokenizer.

        Args:
        paragraph (str)

        Returns:
        list

        """
        try:
            self.sentences = tokenize.sent_tokenize(paragraphs)
            return self.sentences
        except:
            print "Could not tokenize text."
            return False

    def clean_new_lines(self, paragraphs):
        """Strip new line characters except for new paragraphs."""
        self.text_no_cr =\
            paragraphs.replace("\n\n",
                           "TOADIES").replace("\r",
                                              "  ").replace("\n",
                                                          "  ").replace(
                                                              "TOADIES", "\n")
        return self.text_no_cr

    def count_be_verbs(self, sentences):
        """
        Count be verbs in each sentence in a list.

        Loop through sentences to provide weak verb count.
        If count >= 1, add sentence to list.

        Args:
            sentences (str, list)

        Return:
            list of be-verb count and stand-out sentences

        """
        self.verbs = [" am ", " is ", " are ", " was ", " were ", " be ",\
            "being ", " been "]
        self.weak_sentences = []
        self.verb_count = 0
        for sentence in sentences:
            for verb in self.verbs:
                if verb in sentence:
                    self.verb_count = self.verb_count + 1
                    self.weak_sentences.append(sentence)

        return [self.verb_count, self.weak_sentences]

    def syllable_count(self, word):
        """
        Count syllables in a word.

        Uses NLTK dictionary to find word syllabication.

        Args:
            word (string)

        Returns:
            int syllable count

        """
        self.d = cmudict.dict()
        return min([len([y for y in x if isdigit(y[-1])])
                    for x in self.d[str(word).lower()]])

    def modal_count(self, text):
        """
        Return FreqDist of modal verbs in text.

        Args:
            text (str)

        Return:
            list
        """
        fdist = FreqDist(w.lower() for w in text)
        modals = ['can', 'could', 'shall', 'should', 'will', 'would', 'do',
                  'does', 'did', 'may', 'might', 'must', 'has', 'have', 'had']
        modals_freq = []
        for m in modals:
            modals_freq.append(str(m + ': ' + str(fdist[m])))
        return modals_freq

    def timestamp(self, fmt='%Y-%m-%d %H:%M'):
        """
        Set the date and time a document was uploaded.

        Record the datetime a document is uploaded or
        a paste is submitted.

        returns:
           Data and Time in US format, separated by space.
        """
        return datetime.datetime.now().strftime(fmt)

    def select_random(self, count, content):
        """
        Choose a random example from a list.

        Given a list and the length of the list,
        return a random list member.
        """
        #time.sleep(3)
        try:
            if count > 0:
                top_of_range = 0 + count
                choose = randint(0, top_of_range)
                return content[choose]
        except:
            print "Failed to select a random example from a list. Please try again."
            pass
    def pos_count(self, pos, resource):
        for x,y in resource:
            if x == pos:
                return y

    def pos_isolate(self, pos, dictionary):
        for x, y in dictionary:
            if x == pos:
                return y

    def pos_isolate_fuzzy(self, pos, dictionary):
        for x, y in dictionary:
            if pos in x:
                return y

    def char_count(self, character):
        count = 0
        for sentence in self.sentence_tokens:
            if character in sentence:
                count = count + 1
        return count

    def list_sentences(self, character):
        sentences = []
        for sentence in self.sentence_tokens:
            if character in sentence:
                sentences.append(sentence)
        return sentences

    def spelling(self, text_string):
        chkr = SpellChecker("en_US", text_string)
        unrecognized = []
        for err in chkr:
            if err.word not in unrecognized:
                unrecognized.append(err.word)
        return unrecognized

    def docxDeal(self, file):
        raw_text = docx2txt.process(self.abs_path)
        raw_text = unidecode.unidecode_expect_nonascii(raw_text)
        return raw_text

    def sentences_20(self, sentences):
        count = 0
        for sentence in sentences:
            if len(sentence.split()) > 20:
                count += 1
        return count

    def tag_phrases(self, blob):
        blob_noun_phrases = blob.noun_phrases
        noun_phrases = []
        for phrase in blob_noun_phrases:
            if phrase not in noun_phrases:
                noun_phrases.append(phrase)
        return noun_phrases

    def pronouns(self, list, words):
        pronouns = []
        for pronoun in list:
            if pronoun in words:
                pronouns.append(pronoun)
        return pronouns

    def hashtag_cleaner(self, hashtags):
        tags = []
        for tag in hashtags:
            tag = tag.replace("#", "")
            tags.append(tag)
        return tags

    def smog(self, txt):
        r = Readability(txt)
        r = r.SMOGIndex()
        return r

    def gunning_fog(self, txt):
        r = Readability(txt)
        r = r.GunningFogIndex()
        return r

    def lix(self, txt):
        r = Readability(txt)
        r = r.LIX()
        return r

    def rix(self, txt):
        r = Readability(txt)
        r = r.RIX()
        return r


def __del__(self):
    print("Instance of Class 'Sample' removed.")
