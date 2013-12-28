TreNdis
=======

A simple and experimental tool/library to compute trends on any data. I was reading [this](http://highscalability.com/blog/2011/7/6/11-common-web-use-cases-solved-in-redis.html) article and thought I should try to solve this problem using Redis. I think it's a good tool for this job.

####Install

From the directory:
```
sudo python setup.py install
```

#### How to use

``` 
# Insert tokens from any stream of data 
# ex: parsed periodic log on multiple boxes. 
# on each box, each minute, run

>>> from trendis import Trendis
>>> trends = Trendis(namespace=sample, host=redis-host, port=6379)
>>> words = []
>>> for word in my_stream_for_this_minute:
.>>>    if word.startswith("P1_"):
.>>>        words.append((word, 2))
.>>>    else:
.>>>        words.append((word, 1))
.>>> trends.insert(*words)

# from command line
$ trendis-cli --namespace="sample" --host="redis-host" --port=6379
```
* Fast - Everything is in memory and will be expired if unused.
* Tries to identify topics that are becoming popular rather than the
  ones that have been popular for while. Currently uses slope of the
  [least squares fitting](http://mathworld.wolfram.com/LeastSquaresFitting.html)
  line over data points to compute score.
* Though inserting and storing the data is fast, the trends are currently computed by iterating over all the
  available keywords and it's not very fast. For 50,000 keys it took 
  around 30-35 seconds. This can also be easily distributed across machines (like compute [a-m]\*,[n-z]\* on 2 boxes)
* Allows seperate namespaces for each kind of job.

#####Stream and Insert data:

* There is an example script which fetches sample data from twitter
  using [streaming api](https://dev.twitter.com/docs/api/1.1/get/statuses/sample), applies filters to remove commonly used words
  ( forked from
  [here](https://code.google.com/p/twitter-sentiment-analysis/source/browse/trunk/files/stopwords.txt)
  ), <=3 character words and inserts the tokens.
* Number of buckets, time slot of each bucket can be tuned. Used last 2 hours of data counted per minute.
* The results were not so good in the beginning but slowly started
  getting better.
* The quality of the trending topics will be highly dependent on how the
  data is filtered before inserting. Better stop words, scoring should
  make it much better.

#####Compute and view trends:
* trendis-cli can be used to compute and view the trends. 'trendis-cli --help' will be helpful

