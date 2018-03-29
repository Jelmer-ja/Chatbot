import numpy
import random
import ast
from chatterbot import ChatBot
from markov_norder import Markov
from chatterbot.trainers import ListTrainer
from bs4 import BeautifulSoup
from bs4.element import Comment
import cfscrape as cfs
from unidecode import unidecode
import time
#Niet zeker of dit ook echt nodig is?
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import gensim
from gensim.models.doc2vec import TaggedDocument
from nltk.corpus import stopwords


#Conversations have three stages, 'OPENING', 'MIDDLE', and 'CLOSING' during which the
#chatbot will respond differently to messages. Currently, the chatbot will greet his conversation partner,
#then respond to any message with a random message from Trump and finally say goodbye after the user
#
class Dialogue:
    def __init__(self):
        self.conversations = {}
        self.bot = ChatBot("Filmquotes")
        self.bot.set_trainer(ListTrainer)
        filmconvos,conversation_iter = import_movielines()
        #also create doc2vec model
        #Code adapted from https://medium.com/scaleabout/a-gentle-introduction-to-doc2vec-db3e8c0cce5e
        #use by calling model.docvecs.most_similar(UNIQUE_ID, topn=5)
        #dm=1 means PV-DM, otherwise use PV-BOW
        #size = dimensionality of features
        #Iput = TaggedDocument (words,lablels) should be iterable.
        model = gensim.models.Doc2Vec.load("Freeksmodel")
            #gensim.models.Doc2Vec()#(documents=conversation_iter,dm=0,size=10)
        print("Model loading")
        #model.save("FreeksModel")
        #model.load("FreeksModel")
        print("\n model loaded \n")
        #model.train(filmconvos)
        for convo in filmconvos[0:50]:
            self.bot.train(convo)

        #self.m = Markov()
        #self.m.walk_directory('clinton-trump-corpus/Trump')

    def in_convos(self,chat):
        return chat in self.conversations

    def add_chat(self,chat):
        self.conversations[chat] = 'OPENING'

    def reply(self,chat,text):
        response = ''

        #Check whether partner wants to end the conversation
        goodbyes = ['see you later','cya','bye','goodbye','gotta go','later',]
        if(True in [g in text.lower() for g in goodbyes]):
            self.conversations[chat] = 'CLOSING'

        #Create a response
        if(self.conversations[chat] == 'OPENING'):
            response = random.choice(['Hi','Hello','Hello there!','Hey','Hi there'])
            self.conversations[chat] = 'MIDDLE'
        elif(self.conversations[chat] == 'MIDDLE'):
            #If the message is a general question (not about the bot itself)
            if('?' in text and 'you' not in text.lower()):
                #Get answer from Google
                scraper = cfs.create_scraper()
                url = 'https://www.google.com/search?q='
                for x in text.lower().split():
                    url += x + '+'
                url = url[:-2]
                page = scraper.get(url).content
                soup = BeautifulSoup(page, 'html.parser')
                divs = soup.findAll("div", {"class": "Z0LcW"})
                if divs == []:
                    response = str(self.bot.get_response(text))
                else:
                    response = str(divs[0])[19:-6]
            else:
                response = str(self.bot.get_response(text))
        elif(self.conversations[chat] == 'CLOSING'):
            response = random.choice(['Bye!','Goodbye!','Cya later!'])
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
    return final_convos,corpus_iter
