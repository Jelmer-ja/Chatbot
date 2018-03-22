import numpy
import random
import ast
from chatterbot import ChatBot
from markov_norder import Markov
from chatterbot.trainers import ListTrainer
from unidecode import unidecode
import time

#Conversations have three stages, 'OPENING', 'MIDDLE', and 'CLOSING' during which the
#chatbot will respond differently to messages. Currently, the chatbot will greet his conversation partner,
#then respond to any message with a random message from Trump and finally say goodbye after the user
#
class Dialogue:
    def __init__(self):
        self.conversations = {}
        self.bot = ChatBot("Filmquotes")
        self.bot.set_trainer(ListTrainer)
        filmconvos = import_movielines()
        for convo in filmconvos:
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
            #response = str(self.m.generate_output(max_words=40))
            response = self.bot.get_response(text)
        elif(self.conversations[chat] == 'CLOSING'):
            response = random.choice(['Bye!','Goodbye!','Cya later!'])
        return response

def import_movielines():

    with open('cornell_movie_dialogs_corpus/movie_conversations.txt') as convf:
        conversations = [x.split('+++$+++')[-1] for x in convf.readlines()]
        conversations = [[n.strip() for n in ast.literal_eval(x[1:])] for x in conversations]
    with open('cornell_movie_dialogs_corpus/movie_lines.txt') as linesf:
        lines = [[x.split('+++$+++')][-1] for x in linesf.readlines()]
        linedict = dict((x[0][:-1],x[4]) for x in lines)
    final_convos = [[linedict[x] for x in y] for y in conversations]
    return final_convos
