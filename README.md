Authors: Jesse Zwamboom (s4314182) & Jelmer Jansen (s4480848)

# Chatbot

We started out with the standard telegram bot as proposed in the assignment. Our chatbot is called called "Freek", and his Telegram username is "@fr33k_bot".

# Functionalities

## Normal Dialogue
Freek is a rather dramatic chatbot. His standard dialogue interactions are taken from the Cornell Movie Database (Cornell Movie Dialog Corpus). We train our chatbot on this database using the Python package [Chatterbot](https://pypi.python.org/pypi/ChatterBot/0.4.3), which uses naive Bayes classifiers to train the bot for finding the most appropriate responses to the input. 
```python
self.conversations = {}
        self.bot = ChatBot("Filmquotes")
        self.bot.set_trainer(ListTrainer)
        filmconvos,conversation_iter = import_movielines()
        print("Model created")
        for convo in filmconvos[0:50]:
            self.bot.train(convo)
```

## Basic Question Answering and News Retrieval
Although Freek likes movies a lot, he is not very knowledgeable about anything else. When he is asked a question about himself (e.g. one that includes the word "you") he answers that question the same way he would any other message. However, he refers to Google when he is asked questions that don't refer to him specifically. 

We implemented this using the web scraping packages [cfscrape](https://pypi.python.org/pypi/cfscrape/) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). Freek uses the former to retrieve the HTML page for a Google query corresponding to the question he is asked, and the latter to scan the HTML code for the tag _Z0LcW_, which marks Google's custom answer to questions. When this tag cannot be found, Freek reverts to his regular pattern of responding to messages. 
```python
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
```
After Freek returns the answer to the question, Freek wants to show off his new knowledge and asks whether the user wants to hear some news about the subject. If the user responds with "Yes" or any similar affirmation, Freek will go to use Google News to look for news articles about the topic and send the user a summary of the first good article that he can find. To achieve this, we used the packages [gensim](https://radimrehurek.com/gensim/), [news_corpus_builder](https://github.com/skillachie/news-corpus-builder) and [sqlite3](https://www.sqlite.org/). 
```python
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
                return summary
        return ''
```
The resulting conversations look something like this:

![alt text](https://i.imgur.com/KjfjwyW.png "Logo Title Text 1")

The user can also trigger this functionality at other moments in the conversation by simply saying _"I'd like to hear some news about X"_ or any similar phrase. 

![alt text](https://i.imgur.com/E7nhSlo.png "Logo Title Text 1")

## Movie Quotation
Because Freek knows so much about movies, he likes helping people getting them right. When he is asked to help with finishing or fixing a movie quote (e.g. a sentence inclusing quotation marks (") somewhere in the sentence) he uses a Gensim model trained using [Doc2Vec](https://radimrehurek.com/gensim/models/doc2vec.html) on the movie quotes. The quote input by the user is then compared with the model and the most similar quote is returned. Because training this model takes a lot of time, the training was done once and the resulting model was stored as 'FreeksModel' in the repo. Since the doc2vec model can only compare similarities between a document and another document that are part of the model, the (mis)quote entered by the user needs to be entered into the model. Adding to the model requires retraining the model again, which takes the better part of half an hour. This is too long for a normal conversation so the only option Freek has is to add the text as a inferred vector and compare this to the vectors of the sentences.
```python
    def get_movie_quote(self, text):
        tag = "UniqueTag" + str(self.nr_last_tag+1)
        self.nr_last_tag += 1
        similars = model.docvecs.most_similar(positive=[model.infer_vector(text)])
        return str(similars[0])
```
## Notes
* UTF-8 didn't recognise characters like ('),(è),(,), etc. so we changed these manually before importing the Cornell database. We also had to remove the unicode characters from our news databases. 
