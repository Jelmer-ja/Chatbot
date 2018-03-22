import nltk
import numpy as np
from dialogue import import_movielines
from markov_norder import *

def main():
    #bot = Markov()
    stages = ['']

    #bot.walk_directory('clinton-trump-corpus/Trump')
    #bot.generate_output(50)
    import_movielines()

if(__name__ == '__main__'):
    main()