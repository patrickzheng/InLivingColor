
# coding: utf-8

# # Load Spark

# In[1]:

################################################################################
# LOAD SPARK

import os
import sys

spark_home = os.environ.get('SPARK_HOME', None)
if not spark_home:
    raise ValueError('SPARK_HOME environment variable is not set')
sys.path.insert(0, os.path.join(spark_home, 'python'))
sys.path.insert(0, os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))
os.environ['PYSPARK_SUBMIT_ARGS'] = "--num-executors 4 --master yarn --deploy-mode client"

execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))


# In[7]:

################################################################################
# LOAD NEEDED MODULES AND FUNCTIONS

from _configuration import *
from datetime import datetime
import time
import calendar
from math import ceil
import json

import boto
s3 = boto.connect_s3()
bucket = s3.get_bucket(S3_BUCKET)

from elasticsearch import Elasticsearch
es = Elasticsearch() # by default we connect to localhost:9200


def WriteToElasticSearch_bypartition(index, doc_type, kv_iter):
    """
    This preserves keys. Unlike elasticsearch-hadoop-2.1.0.jar .
    # print testrdd.saveAsNewAPIHadoopFile(
    #     path='-',
    #     outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
    #     keyClass="org.apache.hadoop.io.NullWritable",
    #     valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    #     conf={ "es.resource" : "test/test3" })
    """
    from elasticsearch import Elasticsearch
    es = Elasticsearch()

    for kv in kv_iter:
        _id = kv[0]
        body = kv[1]

        es.index(index=index,doc_type=doc_type, id=_id, body=body)


# In[8]:

def GetLastDownloadTimestamp(index='inlivingcolor', doc_type='colorcluster'):

    rsp = es.search(index=index, doc_type=doc_type, body="""
    {
      "fields" : ["_id","downloadtimestamp"],
      "query": {
        "match_all": {}
      },
      "size": "1",
      "sort": [
        {
          "downloadtimestamp": {
            "order": "desc"
          }
        }
      ]

    };""")
    return str(rsp['hits']['hits'][0]['fields']['downloadtimestamp'][0])

# GetLastDownloadTimestamp()


# In[9]:

# print datetimebins
# print '2015-06-20_16'
# print str(GetLastDownloadTimestamp

try:
    startatthistime = time.mktime(time.strptime(GetLastDownloadTimestamp(),"%Y-%m-%d_%H")) - 3600*24
except:
    startatthistime = FIRSTBINEVER


datetimebins = map(lambda d: time.strftime('%Y-%m-%d_%H', time.gmtime(d)), range(int(startatthistime),int(time.time()),3600))
print datetimebins
# len([str(GetLastDownloadTimestamp()) < bin for bin in datetimebins])


# In[11]:


maps = []
maps.append(['collection', lambda d: (d['collection']),None])
maps.append(['datetaken', lambda d: (d['info']['dates']['taken'][:10]),None])
maps.append(['photoid', lambda d: (d['photoid']),None])
# maps.append(['_id', lambda d: (d['photoid']),None])

maps.append(['tags', lambda d: ' '.join([i['_content'] for i in d['info']['tags']['tag']]),''])

maps.append(['latitude', lambda d: float(d['info']['location']['latitude']),None])
maps.append(['longitude', lambda d: float(d['info']['location']['longitude']),None])

maps.append(['country', lambda d: (d['info']['location']['country']['_content']) ,'_'])
maps.append(['region', lambda d: (d['info']['location']['region']['_content']) ,'_'])
maps.append(['county', lambda d: (d['info']['location']['county']['_content']) ,'_'])
maps.append(['locality', lambda d: (d['info']['location']['locality']['_content']) ,'_'])

maps.append(['url', lambda d: str(d['info']['urls']['url'][0]['_content']), ''])
maps.append(['thumbh', lambda d: int(d['thumbh']), None])
maps.append(['thumbw', lambda d: int(d['thumbw']), None])

maps.append(['downloadtimestamp', lambda d: d['secret'], None])


# # this crazy function gives a good guess for k
maps.append(['goodk',lambda d: (np.array([min(pdist([v for k,v in (d['clusters']['%d'%i]['centroids']).iteritems()])) for i in range(2,6)])>.25).sum()+1,3])

maps.append(['c1c1r',lambda d: int(d['clusters']['1']['centroids']['1'][0]*256),None])
maps.append(['c1c1g',lambda d: int(d['clusters']['1']['centroids']['1'][1]*256),None])
maps.append(['c1c1b',lambda d: int(d['clusters']['1']['centroids']['1'][2]*256),None])
maps.append(['c1p1',lambda d: int(d['clusters']['1']['probs']['1']*100),None])
maps.append(['c2c1r',lambda d: int(d['clusters']['2']['centroids']['1'][0]*256),None])
maps.append(['c2c1g',lambda d: int(d['clusters']['2']['centroids']['1'][1]*256),None])
maps.append(['c2c1b',lambda d: int(d['clusters']['2']['centroids']['1'][2]*256),None])
maps.append(['c2p1',lambda d: int(d['clusters']['2']['probs']['1']*100),None])
maps.append(['c2c2r',lambda d: int(d['clusters']['2']['centroids']['2'][0]*256),None])
maps.append(['c2c2g',lambda d: int(d['clusters']['2']['centroids']['2'][1]*256),None])
maps.append(['c2c2b',lambda d: int(d['clusters']['2']['centroids']['2'][2]*256),None])
maps.append(['c2p2',lambda d: int(d['clusters']['2']['probs']['2']*100),None])
maps.append(['c3c1r',lambda d: int(d['clusters']['3']['centroids']['1'][0]*256),None])
maps.append(['c3c1g',lambda d: int(d['clusters']['3']['centroids']['1'][1]*256),None])
maps.append(['c3c1b',lambda d: int(d['clusters']['3']['centroids']['1'][2]*256),None])
maps.append(['c3p1',lambda d: int(d['clusters']['3']['probs']['1']*100),None])
maps.append(['c3c2r',lambda d: int(d['clusters']['3']['centroids']['2'][0]*256),None])
maps.append(['c3c2g',lambda d: int(d['clusters']['3']['centroids']['2'][1]*256),None])
maps.append(['c3c2b',lambda d: int(d['clusters']['3']['centroids']['2'][2]*256),None])
maps.append(['c3p2',lambda d: int(d['clusters']['3']['probs']['2']*100),None])
maps.append(['c3c3r',lambda d: int(d['clusters']['3']['centroids']['3'][0]*256),None])
maps.append(['c3c3g',lambda d: int(d['clusters']['3']['centroids']['3'][1]*256),None])
maps.append(['c3c3b',lambda d: int(d['clusters']['3']['centroids']['3'][2]*256),None])
maps.append(['c3p3',lambda d: int(d['clusters']['3']['probs']['3']*100),None])
maps.append(['c4c1r',lambda d: int(d['clusters']['4']['centroids']['1'][0]*256),None])
maps.append(['c4c1g',lambda d: int(d['clusters']['4']['centroids']['1'][1]*256),None])
maps.append(['c4c1b',lambda d: int(d['clusters']['4']['centroids']['1'][2]*256),None])
maps.append(['c4p1',lambda d: int(d['clusters']['4']['probs']['1']*100),None])
maps.append(['c4c2r',lambda d: int(d['clusters']['4']['centroids']['2'][0]*256),None])
maps.append(['c4c2g',lambda d: int(d['clusters']['4']['centroids']['2'][1]*256),None])
maps.append(['c4c2b',lambda d: int(d['clusters']['4']['centroids']['2'][2]*256),None])
maps.append(['c4p2',lambda d: int(d['clusters']['4']['probs']['2']*100),None])
maps.append(['c4c3r',lambda d: int(d['clusters']['4']['centroids']['3'][0]*256),None])
maps.append(['c4c3g',lambda d: int(d['clusters']['4']['centroids']['3'][1]*256),None])
maps.append(['c4c3b',lambda d: int(d['clusters']['4']['centroids']['3'][2]*256),None])
maps.append(['c4p3',lambda d: int(d['clusters']['4']['probs']['3']*100),None])
maps.append(['c4c4r',lambda d: int(d['clusters']['4']['centroids']['4'][0]*256),None])
maps.append(['c4c4g',lambda d: int(d['clusters']['4']['centroids']['4'][1]*256),None])
maps.append(['c4c4b',lambda d: int(d['clusters']['4']['centroids']['4'][2]*256),None])
maps.append(['c4p4',lambda d: int(d['clusters']['4']['probs']['4']*100),None])
maps.append(['c5c1r',lambda d: int(d['clusters']['5']['centroids']['1'][0]*256),None])
maps.append(['c5c1g',lambda d: int(d['clusters']['5']['centroids']['1'][1]*256),None])
maps.append(['c5c1b',lambda d: int(d['clusters']['5']['centroids']['1'][2]*256),None])
maps.append(['c5p1',lambda d: int(d['clusters']['5']['probs']['1']*100),None])
maps.append(['c5c2r',lambda d: int(d['clusters']['5']['centroids']['2'][0]*256),None])
maps.append(['c5c2g',lambda d: int(d['clusters']['5']['centroids']['2'][1]*256),None])
maps.append(['c5c2b',lambda d: int(d['clusters']['5']['centroids']['2'][2]*256),None])
maps.append(['c5p2',lambda d: int(d['clusters']['5']['probs']['2']*100),None])
maps.append(['c5c3r',lambda d: int(d['clusters']['5']['centroids']['3'][0]*256),None])
maps.append(['c5c3g',lambda d: int(d['clusters']['5']['centroids']['3'][1]*256),None])
maps.append(['c5c3b',lambda d: int(d['clusters']['5']['centroids']['3'][2]*256),None])
maps.append(['c5p3',lambda d: int(d['clusters']['5']['probs']['3']*100),None])
maps.append(['c5c4r',lambda d: int(d['clusters']['5']['centroids']['4'][0]*256),None])
maps.append(['c5c4g',lambda d: int(d['clusters']['5']['centroids']['4'][1]*256),None])
maps.append(['c5c4b',lambda d: int(d['clusters']['5']['centroids']['4'][2]*256),None])
maps.append(['c5p4',lambda d: int(d['clusters']['5']['probs']['4']*100),None])
maps.append(['c5c5r',lambda d: int(d['clusters']['5']['centroids']['5'][0]*256),None])
maps.append(['c5c5g',lambda d: int(d['clusters']['5']['centroids']['5'][1]*256),None])
maps.append(['c5c5b',lambda d: int(d['clusters']['5']['centroids']['5'][2]*256),None])
maps.append(['c5p5',lambda d: int(d['clusters']['5']['probs']['5']*100),None])


# Use the following to generate the above
# for i in range(1,6):
#     for j in range(1,i+1):
#         print "maps.append(['c%dc%dr',lambda d: int(d['clusters']['%d']['centroids']['%d'][0]*256),None])"%(i,j,i,j)
#         print "maps.append(['c%dc%dg',lambda d: int(d['clusters']['%d']['centroids']['%d'][1]*256),None])"%(i,j,i,j)
#         print "maps.append(['c%dc%db',lambda d: int(d['clusters']['%d']['centroids']['%d'][2]*256),None])"%(i,j,i,j)
#         print "maps.append(['c%dp%d',lambda d: int(d['clusters']['%d']['probs']['%d']*100),None])"%(i,j,i,j)


def simplifyrecord(d):
    output = {}

    for m in maps:
        try:
            output[m[0]] = m[1](d)
        except:
            if m[2] is None:
                return None
            else:
                output[m[0]] = m[2]

    return output



# In[ ]:




# In[12]:



def batch_movetoelasticsearch(collection=None,datetimebins=[], dry_run=True):

    print '------------------------------------------------------------------------'
    print 'Moving Color Clustering data to Elastic Search'
    print ''

    for datetimebinstr in datetimebins:
        print datetimebinstr

        try:
            # Load JSON files form S3 and convert to Python dict's
            rdd = sc.textFile(os.path.join(S3_PREFIX,'metaplus_%s.json'%datetimebinstr))
            rdd = rdd.map(lambda s: json.loads(s))

            # Simplify for ElasticSearch, remove erroneous entries, and place in key-value form
            rdd = rdd.map(simplifyrecord).filter(lambda d: d is not None).map(lambda d: (d['photoid'],d))

            # Write to ElasticSearch partition by partition
            rdd.foreachPartition(lambda kv_iter: WriteToElasticSearch_bypartition('inlivingcolor','colorcluster',kv_iter))
        except:
            print "Error: Perhaps %s does not exist?" % ('metaplus_%s.json'%datetimebinstr)


batch_movetoelasticsearch(collection=collection,datetimebins=datetimebins[:])

