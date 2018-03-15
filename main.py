import nltk
import numpy as np
from markov_norder import *

def main():
    bot = Markov()
    stages = ['']

    bot.walk_directory('clinton-trump-corpus/Trump')
    bot.generate_output(50)

if(__name__ == '__main__'):
    main()