
# coding: utf-8

# History Server: http://52.8.132.94:18088/

# # Load Spark

# In[1]:

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


# def IsInLocation(d,form,entity):
#     try:
#         return d['info']['location'][form]['_content'] == entity
#     except:
#         return '_'

def LocationLevel(d,form):
    try:
        output = d['info']['location'][form]['_content']
        assert type(output) == unicode or type(output) == str
        return output
    except:
        return '_'


# In[5]:

# Load the metaplus.json files for now-minus-4 hours till now
startprocessinghere = timeoflastrun("preparecountstest", set_to_now=False) - 3600*4
datetimebins = ALLBINSFROMTHISTIMETILONEHOURAGO(startprocessinghere)


# In[13]:

rdd = sc.textFile(os.path.join(S3_PREFIX,'metaplus_%s.json'%(datetimebins[0]))).map(lambda s: json.loads(s))


# In[ ]:

rdd = rdd.flatMap(lambda d: (
        ######MONTHLY########
            ((('country',LocationLevel(d, 'country')),
                          ('region',LocationLevel(d, 'region')),
                          ('county',LocationLevel(d, 'county')),
                          ('locality',LocationLevel(d, 'locality')),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','locality/month'),
                         ),1),

            ((('country',LocationLevel(d, 'country')),
                          ('region',LocationLevel(d, 'region')),
                          ('county',LocationLevel(d, 'county')),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','county/month'),
                         ),1),

            ((('country',LocationLevel(d, 'country')),
                          ('region',LocationLevel(d, 'region')),
                          ('county','*'),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','region/month'),
                         ),1),

            ((('country',LocationLevel(d, 'country')),
                          ('region','*'),
                          ('county','*'),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','country/month'),
                         ),1),

            ((('country','*'),
                          ('region','*'),
                          ('county','*'),
                          ('locality','*'),
                          ('datetaken',str(d['info']['dates']['taken'][:7])),
                          ('granularity','all/month'),
                         ),1),))


# In[14]:

rdd.take(1)


# In[8]:

# For debugging
# datetimebin =


import boto
s3 = boto.connect_s3()
bucket = s3.get_bucket(S3_BUCKET)


# In[9]:

N = len(datetimebins)
for i,datetimebin in enumerate(datetimebins):
    print "################################################################################"
    print "Step (%d/%d): Creating _batchstage_counts/%s.p for " % (i+1, N, datetimebin)

    # If YYYY-MM-DD_HH.p has already been generated, no need to do it again.
    if bucket.get_key(os.path.join(collection,'_batchstage_counts',datetimebin+'.p','_SUCCESS')) is not None:
        print '--- File %s already exists. Skipping...' % (datetimebin+'.p')
        continue

    # Delete files that might prevent us from writing to YYYY-MM-DD_HH.p
    filestodelete = list(bucket.list(os.path.join(collection,'_batchstage_counts',datetimebin+'.p')))
    if len(filestodelete) > 0:
        print '--- Deleting:', filestodelete
        bucket.delete_keys(list(bucket.list(os.path.join(collection,'_batchstage_counts',datetimebin+'.p'))))

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
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','county/month'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','region/month'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','country/month'),
                                 ),1),

                    ((('country','*'),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:7])),
                                  ('granularity','all/month'),
                                 ),1),

                ########YEARLY########
                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality',LocationLevel(d, 'locality')),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','locality/year'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','county/year'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','region/year'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','country/year'),
                                 ),1),

                    ((('country','*'),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken',str(d['info']['dates']['taken'][:4])),
                                  ('granularity','all/year'),
                                 ),1),
                ########ALL TIME########
                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality',LocationLevel(d, 'locality')),
                                  ('datetaken','*'),
                                  ('granularity','locality/all'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county',LocationLevel(d, 'county')),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','county/all'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region',LocationLevel(d, 'region')),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','region/all'),
                                 ),1),

                    ((('country',LocationLevel(d, 'country')),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','country/all'),
                                 ),1),

                    ((('country','*'),
                                  ('region','*'),
                                  ('county','*'),
                                  ('locality','*'),
                                  ('datetaken','*'),
                                  ('granularity','all/all'),
                                 ),1),

                    ))
        rdd = rdd.reduceByKey(lambda x,y: x+y)
        rdd = rdd.coalesce(1)
        rdd.saveAsPickleFile(os.path.join(S3_PREFIX,'_batchstage_counts',datetimebin+'.p'))
        print '--- Successfully wrote to '+datetimebin+'.p'
    except:
        print '--- DID NOT write to '+datetimebin+'.p'


# In[10]:

# Each hour's bin produces a pickle file that is <2MB. For a year that isn't bad (~18GB)
# If this poses a problem in the future, previous days can always be grouped by day
# and months by month, etc.
rdd = sc.pickleFile(os.path.join(S3_PREFIX,'_batchstage_counts','*'))


# In[11]:

rdd = rdd.reduceByKey(lambda x,y: x+y)
rdd = rdd.map(lambda tup: dict(count=tup[1],**{item[0]:item[1] for item in tup[0]}))


# In[12]:

rdd.persist()


# In[13]:

def AddToCassandra_allcountsbatch_bypartition(d_iter):
    from cqlengine import columns
    from cqlengine.models import Model
    from cqlengine import connection
    from cqlengine.management import sync_table

    class allcountsbatch(Model):
        granularity = columns.Text(primary_key=True)
        country = columns.Text(primary_key=True)
        region = columns.Text(primary_key=True)
        county = columns.Text(primary_key=True)
        locality = columns.Text(primary_key=True)
        datetaken = columns.Text(primary_key=True)
        count = columns.Integer()

    connection.setup(['127.0.0.1'], CASSANDRA_KEYSPACE)

    sync_table(allcountsbatch)

    for d in d_iter:
        allcountsbatch.create(**d)

# Create table if it does not exist. Need to do this before submitting to Spark to avoid collisions
AddToCassandra_allcountsbatch_bypartition([])


# In[14]:

rdd.foreachPartition(AddToCassandra_allcountsbatch_bypartition)


# In[ ]:




# In[ ]:



