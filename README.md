TreNdis
=======

A simple and experimental code to compute trends on any data

* Uses redis hashes to store keywords, redis sorted-set to store/get
  trending topics which makes the data insertion process to be
  distributed, fast. But the trends are computed linearly over all the
  available keywords. Yet to benchmark this will start becoming too slow.
  ( trends are supposed to be as close to real time as possible )
* Currently uses slopes of the
  [least squares fitting](http://mathworld.wolfram.com/LeastSquaresFitting.html)
  line over data points to compute score.
* Maintains a seperate namespace for each kind of data

#####Stream and Insert data:
* There is an example script which fetches data from twitter using
  streaming api, applies filters to remove commonly used english words
  ( forked from
  [here](https://code.google.com/p/twitter-sentiment-analysis/source/browse/trunk/files/stopwords.txt)), 
  ,1-2 character words and inserts the tokens.
*  The quality of the trending topics will be highly dependent on how the
  data is filtered before inserting
#####compute and view trends:
* trendis-cli can be used to compute and view the trends. check
  trendis-cli --help

####Install

From the directory:
```
sudo python setup.py install
```
