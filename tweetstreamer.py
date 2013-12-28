#contains my access_tokens etc
# CONSUMER_KEY=....
# CONSUMER_SECRET=...
import auth
import re
from twython import TwythonStreamer
from trendis import Trendis


#https://twython.readthedocs.org/en/latest/usage/streaming_api.html
class MyStreamer(TwythonStreamer):
    def __init__(self, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)
        with open('stopwords.txt') as f:
            self.stopwords = set(map(lambda x: x.strip(), f.readlines()))
        self.trendis = Trendis(namespace='twitter')

    def on_success(self, data):
        if 'text' in data:
            tweet = data['text'].encode('utf-8')
            tokens = [(word, self.__weight(word))
                      for word in map(lambda x:x.lower(), tweet.split())
                      if len(word) > 4 and
                      (word.startswith('#') or word.isalnum()) and
                      word not in self.stopwords]
            if tokens:
                self.trendis.insert(*tokens)

    def on_error(self, status_code, data):
        print status_code

    def __weight(self, word):
        weight = 1
        if word.endswith('ing'):
            return 0
        if re.search(r'((\w)\2{2,})', word):
            #get rid of hellooooooo's
            return 0
        if len(word) > 20:
            return 0
        if word.startswith('#'):
            weight += 2
        if 8 <= len(word) <= 20:
            weight += 2
        return weight

if __name__ == '__main__':
    stream = MyStreamer(auth.CONSUMER_KEY, auth.CONSUMER_SECRET,
                        auth.ACCESS_TOKEN, auth.ACCESS_TOKEN_SECRET)
    stream.statuses.sample()
