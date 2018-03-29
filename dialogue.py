import numpy
import random
import ast
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from bs4 import BeautifulSoup
import cfscrape as cfs
import sqlite3
import logging
import os
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import gensim
from gensim.summarization.summarizer import summarize
from gensim.models.doc2vec import TaggedDocument
from nltk.corpus import stopwords
from news_corpus_builder import NewsCorpusGenerator


#Conversations have three stages, 'OPENING', 'MIDDLE', and 'CLOSING' during which the
#chatbot will respond differently to messages. Currently, the chatbot will greet his conversation partner,
#then respond to any message with a random message from Trump and finally say goodbye after the user
#
class Dialogue:
    def __init__(self):
        self.conversations = {}
        self.nr_last_tag = 1.0
        self.answer = None
        self.bot = ChatBot("Filmquotes")
        self.bot.set_trainer(ListTrainer)
        filmconvos = import_movielines()
        #also create doc2vec model
        #Code adapted from https://medium.com/scaleabout/a-gentle-introduction-to-doc2vec-db3e8c0cce5e
        #use by calling model.docvecs.most_similar(UNIQUE_ID, topn=5)
        #dm=1 means PV-DM, otherwise use PV-BOW
        #size = dimensionality of features
        #Iput = TaggedDocument (words,lablels) should be iterable.
        global model
        model = gensim.models.Doc2Vec.load('FreeksModel')
            #gensim.models.Doc2Vec()#(documents=conversation_iter,dm=0,size=10)
        print("Model loading")
        print("\nModel loaded \n")
        for convo in filmconvos[0:2]:
            self.bot.train(convo)

    def in_convos(self,chat):
        return chat in self.conversations

    def add_chat(self,chat):
        self.conversations[chat] = 'OPENING'

    def get_movie_quote(self, text):
        tag = "UniqueTag" + str(self.nr_last_tag)
        self.nr_last_tag += 1
        model.train(TaggedDocument(text.split(), tag))
        print(model.docvecs.most_similar(tag))
        return text

    def get_answer(self,text):
        # Get answer from Google
        scraper = cfs.create_scraper()
        url = 'https://www.google.co.uk/search?q='#client=ubuntu&channel=fs&q='
        for x in text.lower().split():
            url += x + '+'
        url = url[:-2]
        page = scraper.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        divs = soup.findAll("div", {"class": "Z0LcW"})
        return divs

    def get_news_sentence(self,answer):
        #Create a database of news articles about the subject of te question
        cg = NewsCorpusGenerator('temp_news_corpus', 'sqlite')
        links = cg.google_news_search(answer, 'Standard', 5)
        cg.generate_corpus(links)
        conn = sqlite3.connect('temp_news_corpus/corpus.db')
        news_strings = []
        for row in conn.execute('SELECT body FROM articles'):
            news_strings.append(str(row).decode('unicode_escape').encode('ascii','ignore'))
        os.remove('temp_news_corpus/corpus.db') # Remove the database
        for n in news_strings[1:]:
            summary = summarize(n)
            if(summary != u"" and summary != []):
                if(summary[0:3] == '(u"'):
                    return summary[3:]
                else:
                    return summary
        return ''

    def reply(self, chat, text):
        response = ''

        # Check whether partner wants to end the conversation
        goodbyes = ['see you later', 'cya', 'bye', 'goodbye', 'gotta go', 'later', ]
        if (True in [g in text.lower() for g in goodbyes]):
            self.conversations[chat] = 'CLOSING'

        # Create a response
        if (self.conversations[chat] == 'OPENING'):
            response = random.choice(['Hi', 'Hello', 'Hello there!', 'Hey', 'Hi there'])
            self.conversations[chat] = 'MIDDLE'
        elif (self.conversations[chat] == 'MIDDLE'):
            # If the message is a general question (not about the bot itself)
            if ('some news about' in text.lower()):
                words = text.lower().split()
                about_index = words.index('about')
                subject = ''
                for i in range(about_index + 1, len(words)):
                    subject += words[i] + ' '
                response = self.get_news_sentence(subject)
            elif ('?' in text and 'you' not in text.lower()):
                divs = self.get_answer(text)
                if divs == []:
                    response = str(self.bot.get_response(text))
                else:
                    self.answer = str(divs[0])[19:-6]
                    news_sentence = self.get_news_sentence(self.answer)
                    response = self.answer[0].upper() + self.answer[1:] + '. Would you like to hear some news about ' + self.answer + '?'
                    self.conversations[chat] = 'QUESTION'
            else:
                response = str(self.bot.get_response(text))
        elif (self.conversations[chat] == 'QUESTION'):
            if text.lower() in ['yeah','yes','absolutely','yes.','yes?','yeah!','yes!']:
                response = self.get_news_sentence(self.answer)
            else:
                response = 'Okay.'
            self.conversations[chat] = 'MIDDLE'
        elif (self.conversations[chat] == 'CLOSING'):
            response = random.choice(['Bye!', 'Goodbye!', 'Cya later!'])
        return response

def import_movielines():
    #print("creating corpus iterator")
    corpus_iter = []
    with open('cornell_movie_dialogs_corpus/movie_conversations.txt') as convf:
        conversations = [x.split('+++$+++')[-1] for x in convf.readlines()]
        conversations = [[n.strip() for n in ast.literal_eval(x[1:])] for x in conversations]
    with open('cornell_movie_dialogs_corpus/movie_lines.txt') as linesf:
        lines = [[x.split('+++$+++')][-1] for x in linesf.readlines()]
        linedict = dict((x[0][:-1],x[4]) for x in lines)
    final_convos = [[linedict[x] for x in y] for y in conversations]
    #create corpus, possibly check for vocabulary (drop words not in it from sentence)
    #stop = set(stopwords.words('english'))
    #for key in linedict:
    #    if linedict[key] not in stop:
    #        corpus_iter.append(TaggedDocument(linedict[key][:-1].split(),key))
    #print(corpus_iter)
    return final_convos #,corpus_iter
