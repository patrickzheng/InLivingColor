# EXPORTED FROM IPYTHON NOTEBOOK

import os
import sys


spark_home = os.environ.get('SPARK_HOME', None)
if not spark_home:
    raise ValueError('SPARK_HOME environment variable is not set')
sys.path.insert(0, os.path.join(spark_home, 'python'))
sys.path.insert(0, os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))


# In[2]:

# PYSPARK_SUBMIT_ARGS = os.environ.get('PYSPARK_SUBMIT_ARGS', None) + """
#     --packages TargetHolding/pyspark-cassandra:0.1.5 \
#     --conf spark.cassandra.connection.host=172.31.0.16,172.31.9.80,172.31.9.81,172.31.9.82,172.31.9.83,172.31.9.84,172.31.9.85,172.31.9.86,172.31.9.87,172.31.9.88
# """
# os.environ['PYSPARK_SUBMIT_ARGS'] = PYSPARK_SUBMIT_ARGS
# print PYSPARK_SUBMIT_ARGS


# In[3]:


execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))


# ## Take aggregated metaplus.json files and create counts

# In[4]:

from _configuration import *
from batch_helper import timeoflastrun
import time
import json

def LocationLevel(d,form):
    try:
        output = d['info']['location'][form]['_content']
        assert type(output) == unicode or type(output) == str
        return output
    except:
        return '_'


# In[16]:

# Load the metaplus.json files for now-minus-4 hours till now
startprocessinghere = timeoflastrun("preparecountstest", set_to_now=False) - 3600*4
datetimebins = ALLBINSFROMTHISTIMETILONEHOURAGO(startprocessinghere)
datetimebins


# In[17]:

# rdd = sc.textFile(os.path.join(S3_PREFIX,'metaplus_2015-06-*.json')).map(lambda s: json.loads(s))


# In[18]:

# d = rdd.take(3)[-1]
# print d['clusters']


# In[19]:

def GetHueVector(k, d):
    import colorsys
    import numpy as np
    N = 16
    vector = np.zeros(N+1)
    vector[-1] = 1
    try:
        for i in range(1,k+1):
            vector[int(colorsys.rgb_to_hsv(*d['clusters'][str(k)]['centroids'][str(i)])[0]*N)] += d['clusters'][str(k)]['probs'][str(i)]
    except:
        pass
    return vector

# GetHueVector(5,d)


# In[20]:

# r = rdd.map(lambda d: GetHueVector(4,d)).reduce(lambda x,y: x+y)


# In[21]:

# r


# In[22]:

rdd = rdd.flatMap(lambda d: (
        ######MONTHLY########
            ((('country',LocationLevel(d, 'country')),
                          ('region',LocationLevel(d, 'region')),
                          ('county',LocationLevel(d, 'county')),
                          ('locality',LocationLevel(d, 'locality')),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','locality/month'),
                         ),GetHueVector(4,d)),

            ((('country',LocationLevel(d, 'country')),
                          ('region',LocationLevel(d, 'region')),
                          ('county',LocationLevel(d, 'county')),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','county/month'),
                         ),GetHueVector(4,d)),

            ((('country',LocationLevel(d, 'country')),
                          ('region',LocationLevel(d, 'region')),
                          ('county','*'),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','region/month'),
                         ),GetHueVector(4,d)),

            ((('country',LocationLevel(d, 'country')),
                          ('region','*'),
                          ('county','*'),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','country/month'),
                         ),GetHueVector(4,d)),

            ((('country','*'),
                          ('region','*'),
                          ('county','*'),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','all/month'),
                         ),GetHueVector(4,d)),))


# In[25]:

# rdd.take(50)


# In[12]:

# rdd.reduceByKey(lambda x,y: x+y).collect()


# In[13]:

# For debugging
# datetimebin =


import boto
s3 = boto.connect_s3()
bucket = s3.get_bucket(S3_BUCKET)


# In[14]:

N = len(datetimebins)
for i,datetimebin in enumerate(datetimebins):
    print "################################################################################"
    print "Step (%d/%d): Creating _batchstage_huecounts/%s.p for " % (i+1, N, datetimebin)

    # If YYYY-MM-DD_HH.p has already been generated, no need to do it again.
    if bucket.get_key(os.path.join(collection,'_batchstage_huecounts',datetimebin+'.p','_SUCCESS')) is not None:
        print '--- File %s already exists. Skipping...' % (datetimebin+'.p')
        continue

    # Delete files that might prevent us from writing to YYYY-MM-DD_HH.p
    filestodelete = list(bucket.list(os.path.join(collection,'_batchstage_huecounts',datetimebin+'.p')))
    if len(filestodelete) > 0:
        print '--- Deleting:', filestodelete
        bucket.delete_keys(list(bucket.list(os.path.join(collection,'_batchstage_huecounts',datetimebin+'.p'))))

    try:
        rdd = sc.textFile(os.path.join(S3_PREFIX,'metaplus_%s.json'%(datetimebin)))
        rdd = rdd.map(lambda s: json.loads(s))
        rdd = rdd.flatMap(lambda d: (
                ######MONTHLY########
                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality',LocationLevel(d, 'locality')),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','locality/month'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','county/month'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','region/month'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','country/month'),
                                 ),GetHueVector(4,d)),

                    ((('country','*'),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','all/month'),
                                 ),GetHueVector(4,d)),

                ########YEARLY########
                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality',LocationLevel(d, 'locality')),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','locality/year'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','county/year'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','region/year'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','country/year'),
                                 ),GetHueVector(4,d)),

                    ((('country','*'),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','all/year'),
                                 ),GetHueVector(4,d)),
                ########ALL TIME########
                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality',LocationLevel(d, 'locality')),
                                  ('datetaken','*'),
                                  ('granularity','locality/all'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','county/all'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','region/all'),
                                 ),GetHueVector(4,d)),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','country/all'),
                                 ),GetHueVector(4,d)),

                    ((('country','*'),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','all/all'),
                                 ),GetHueVector(4,d)),

                    ))
        rdd = rdd.reduceByKey(lambda x,y: x+y)
        rdd = rdd.coalesce(1)
        get_ipython().magic(u"time rdd.saveAsPickleFile(os.path.join(S3_PREFIX,'_batchstage_huecounts',datetimebin+'.p'))")
        print '--- Successfully wrote to '+datetimebin+'.p'
    except:
        print '--- DID NOT write to '+datetimebin+'.p'


# In[15]:

# Each hour's bin produces a pickle file that is <2MB. For a year that isn't bad (~18GB)
# If this poses a problem in the future, previous days can always be grouped by day
# and months by month, etc."
rdd = sc.pickleFile(os.path.join(S3_PREFIX,'_batchstage_huecounts','*'))


# In[16]:

rdd = rdd.reduceByKey(lambda x,y: x+y)


# In[17]:

rdd.persist()


# In[18]:

# tup = rdd.take(500)[-1]


# In[19]:

import numpy as np
# np.zeros(len(tup[1][:-1]),'i')-1


# In[20]:

# (lambda tup: dict(count=int(tup[1][-1]),
#                                maxhueidxs=np.argsort(tup[1][:-1])[::-1] if np.max(tup[1][:-1])>1e-4 else np.zeros(len(tup[1][:-1]),'i')-1,
#                                huevalues=(tup[1][:-1]*100/tup[1][-1]).astype(np.int32),
#                                **{item[0]:item[1] for item in tup[0]}
#                               ))(tup)


# In[25]:

# granularity  | country       | region     | county | locality | datetaken | count | huevalues                                                                            | maxhueidxs
# --------------+---------------+------------+--------+----------+-----------+-------+-------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------
#  region/month | United States | California |      * |        * |   2016-01 |     3 |                                                             [103, 0, 0, 0, 0, 0, 0, 0, 17, 61, 0, 0, 0, 0, 16, 0] | [0, 9, 8, 14, 15, 13, 12, 11, 10, 7, 6, 5, 4, 3, 2, 1]
#  region/month | United States | California |      * |        * |   2025-03 |     1 |                                                               [0, 37, 0, 0, 32, 0, 0, 0, 0, 0, 29, 0, 0, 0, 0, 0] | [1, 4, 10, 15, 14, 13, 12, 11, 9, 8, 7, 6, 5, 3, 2, 0]
#  region/month | United States | California |      * |        * |   2029-01 |     1 |                                                                [76, 23, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] | [0, 1, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
#  region/month | United States | California |      * |        * |   2034-01 |     1 |                                                               [19, 0, 0, 0, 0, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14] | [5, 0, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 4, 3, 2, 1]
#  region/month | United States | California |      * |        * |   2037-01 |     3 |                                                             [0, 73, 0, 0, 0, 0, 0, 0, 16, 83, 10, 0, 16, 0, 0, 0] | [9, 1, 12, 8, 10, 15, 14, 13, 11, 7, 6, 5, 4, 3, 2, 0]

# now we can extract the count as well as the most popular hues
# rdddict = rdd.map(lambda tup: dict(count=int(tup[1][-1]),
#                                maxhueidxs=np.argsort(tup[1][:-1])[::-1] if np.max(tup[1][:-1])>1e-4 else np.zeros(len(tup[1][:-1]),'i')-1,
#                                maxhue=(np.argsort(tup[1][:-1])[-1]/16.0+1.0/32.0) if np.max(tup[1][:-1])>1e-4 else -1.0,
#                                huevalues=(tup[1][:-1]*100/tup[1][-1]).astype(np.int32),
#                                **{item[0]:item[1] for item in tup[0]}
#                               ))
rdddict = rdd.map(lambda tup: dict(count=int(tup[1][-1]),
                               maxhueidxs=np.argsort(tup[1][:-1])[::-1] if np.max(tup[1][:-1])>1e-4 else None,
                               maxhue=(np.argsort(tup[1][:-1])[-1]/16.0+1.0/32.0) if np.max(tup[1][:-1])>1e-4 else None,
                               huevalues=(tup[1][:-1]*100/tup[1][-1]).astype(np.int32) if np.max(tup[1][:-1])>1e-4 else None,
                               **{item[0]:item[1] for item in tup[0]}
                              ))


# In[26]:

rdddict.first()


# In[27]:

# rdd.persist()


# In[29]:

def AddToCassandra_allhuecountsbatch_bypartition(d_iter):
    from cqlengine import columns
    from cqlengine.models import Model
    from cqlengine import connection
    from cqlengine.management import sync_table

    class allhuecountsbatch(Model):
        granularity = columns.Text(primary_key=True)
        country = columns.Text(primary_key=True)
        region = columns.Text(primary_key=True)
        county = columns.Text(primary_key=True)
        locality = columns.Text(primary_key=True)
        datetaken = columns.Text(primary_key=True)
        count = columns.Integer()
        maxhueidxs = columns.List(columns.Integer())
        maxhue = columns.Float()
        huevalues = columns.List(columns.Integer())

    connection.setup(['127.0.0.1'], CASSANDRA_KEYSPACE)

    sync_table(allhuecountsbatch)

    for d in d_iter:
        allhuecountsbatch.create(**d)

# Create table if it does not exist. Need to do this before submitting to Spark to avoid collisions
AddToCassandra_allhuecountsbatch_bypartition(rdddict.take(5))


# In[30]:

rdddict.foreachPartition(AddToCassandra_allhuecountsbatch_bypartition)


# In[ ]:

3


# In[ ]:



