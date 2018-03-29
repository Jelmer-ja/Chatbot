# Chatbot

We started out with the standard telegram bot as proposed in the assignment. Our chatbot is called called "Freek", and his Telegram username is "@fr33k_bot".

# Functionalities

## Normal Dialogue
Freek is a rather dramatic chatbot. His standard dialogue interactions are taken from the Cornell Movie Database (Cornell Movie Dialog Corpus). We train our chatbot on this database using the Python package [Chatterbot](https://pypi.python.org/pypi/ChatterBot/0.4.3), which uses naive Bayes classifiers to train the bot for finding the most appropriate responses to the input. 

## Basic Question Answering
Although Freek likes movies a lot, he is not very knowledgeable about anything else. When he is asked a question about himself (e.g. one that includes the word "you") he answers that question the same way he would any other message. However, he refers to Google when he is asked questions that don't refer to him specifically. 

We implemented this using the web scraping packages [cfscrape](https://pypi.python.org/pypi/cfscrape/) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). Freek uses the former to retrieve the HTML page for a Google query corresponding to the question he is asked, and the latter to scan the HTML code for the tag _Z0LcW_, which marks Google's custom answer to questions. When this tag cannot be found, Freek reverts to his regular pattern of responding to messages. 
```python
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
```

## Movie Quotation


# Notes
* UTF-8 didn't recognise things like ('),(è),(,), etc. so we changed these manually before importing the Cornell database.
