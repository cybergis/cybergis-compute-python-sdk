import pyspark
import os

from random import random
from operator import add

conf = pyspark.SparkConf()
conf.setAppName("hello3")
conf.setMaster("yarn")
conf.set("spark.submit.deployMode", "client")

sc = pyspark.SparkContext(conf=conf)
partitions = 3
n = 1000 * partitions


def f(_):
    x = random() * 2 - 1
    y = random() * 2 - 1
    return 1 if x ** 2 + y ** 2 <= 1 else 0

count = sc.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
print("Pi is roughly %f" % (4.0 * count / n))