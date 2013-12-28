import redis
import time


class Trendis(object):

    def __init__(self, namespace="twitter", host="localhost", port=6379,
                 buckets=120, bucket_size=60, compute_expire=3600):
        """ buckets => Number of time slots after which the statistic
        of a keyword are erased
        bucket_size => Number of seconds in each bucket
        By default, we store keyword count per minute for 2 hours but
        this should depend on the type of data that is fed
        """
        self.namespace = namespace
        self.compute_expire = compute_expire
        self.pool = redis.ConnectionPool(host=host, port=port, db=0)
        namespace_conf = self.__redis_con().hgetall(namespace + "_conf")
        if namespace_conf:
            self.buckets = int(namespace_conf['buckets'])
            self.bucket_size = int(namespace_conf['bucket_size'])
            #print "namespace \"" + namespace + "\" exists,
            # buckets:" + str(self.buckets) + ",
            # bucket_size:" + str(self.bucket_size)
        else:
            self.buckets = buckets
            self.bucket_size = bucket_size
            self.__redis_con().hset(namespace + '_conf', 'buckets', buckets)
            self.__redis_con().hset(namespace + '_conf', 'bucket_size',
                                    bucket_size)

    def insert(self, *tokens):
        "add one or more word,weight"
        print tokens
        redis_con = self.__redis_con()
        for word, wt in tokens:
            #why not lists? because incrementing/managing fields concurrently
            # will be hard
            redis_con.hincrby(self.__get_key(word), self.__get_bucket(), wt)
            redis_con.expire(self.__get_key(word),
                             self.buckets * self.bucket_size * 10)

    def compute_trends(self):
        """compute trends for ALL existing keywords in the namespace
        be careful about empty buckets
        redis sorted sets FTW"""
        redis_con = self.__redis_con()
        #this has to be SCANned
        keys = redis_con.keys(self.namespace + "_key_*")
        all_buckets = xrange(self.__get_bucket()-self.buckets*self.bucket_size,
                             self.__get_bucket(), self.bucket_size)
        score_key = self.__get_score_key()
        for key in keys:
            time_series = []
            epoch_count = redis_con.hgetall(key)
            for bucket in all_buckets:
                time_series.append(epoch_count.get(str(bucket), 0))
            score = self.__compute_score(time_series)
            key = "_".join(key.split("_")[2:])
            redis_con.zadd(score_key, key, score)
            redis_con.expire(score_key, self.compute_expire)

    def get_trends(self, n=10):
        "get the trends list and when it was computed"
        last_computed, score_key, _ = self.__score_keys_info()
        return last_computed, self.__redis_con().zrevrange(score_key, 0, n-1)

    def __compute_score(self, time_series):
        "currently it's slope of least squares fitting line, experimental"
        n = len(time_series)
        Sx = Sy = Sxx = Syy = Sxy = 0.0
        for x, y in enumerate(time_series):
            y = int(y)
            Sx += x
            Sy += y
            Sxx += (x * x)
            Syy += (y * y)
            Sxy += (x * y)
        score = 100000*(n*Sxy - Sx*Sy)/(n*Sxx - Sx*Sx)
        return score

    def namespace_stats(self):
        "number of keys and the last computed time of trends of the namespace"
        redis_con = self.__redis_con()
        last_computed, _, all_keys = self.__score_keys_info()
        return {'keys': len(redis_con.keys(self.namespace + "_key_*")),
                'last_computed': last_computed}

    def clear_namespace(self):
        "delete them all"
        redis_con = self.__redis_con()
        keys = redis_con.keys(self.namespace + "_*")
        for key in keys:
            redis_con.delete(key)
        return len(keys)

    def __get_key(self, word):
        return self.namespace + "_key_" + word

    def __get_score_key(self):
        return self.namespace + "_score_" + str(self.__get_bucket())

    def __score_keys_info(self):
        redis_con = self.__redis_con()
        score_keys = redis_con.keys(self.namespace + "_score_*")
        if not score_keys:
            return None, None, 0
        score_key = sorted(score_keys, key=lambda x: x.split("_")[-1])[-1]
        score_key_bucket = int(score_key.split("_")[-1])
        last_computed = time.strftime('%Y-%m-%d %H:%M',
                                      time.localtime(score_key_bucket))
        return last_computed, score_key, score_keys

    def __get_bucket(self):
        cur_epoch = int(time.time())
        return cur_epoch - cur_epoch % self.bucket_size

    def __redis_con(self):
        return redis.Redis(connection_pool=self.pool)
