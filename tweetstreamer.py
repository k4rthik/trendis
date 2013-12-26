#contains my access_tokens etc
# CONSUMER_KEY=....
# CONSUMER_SECRET=...
import auth
from twython import TwythonStreamer
from trendis import Trendis


#https://twython.readthedocs.org/en/latest/usage/streaming_api.html
class MyStreamer(TwythonStreamer):
    def __init__(self,*args,**kwargs):
        TwythonStreamer.__init__(self,*args,**kwargs)
        with open('stopwords.txt') as f:
            self.stopwords = set(map(lambda x:x.strip(),f.readlines()))
            print self.stopwords
        self.trendis = Trendis(namespace='twitter')
        
    def on_success(self, data):
        if 'text' in data:
            tweet = data['text'].encode('utf-8')
            tokens = [word for word in map(lambda x:x.lower(),tweet.split()) if len(word)>2 and word.isalnum() and word not in self.stopwords ]
            self.trendis.insert(*tokens)

    def on_error(self, status_code, data):
        print status_code

if __name__ == '__main__':
    stream = MyStreamer(auth.CONSUMER_KEY, auth.CONSUMER_SECRET, auth.ACCESS_TOKEN, auth.ACCESS_TOKEN_SECRET )
    stream.statuses.filter(track='twitter')

