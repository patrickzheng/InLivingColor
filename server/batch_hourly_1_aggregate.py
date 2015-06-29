
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

execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))


# In[6]:

from _configuration import *

import time
import boto
from math import ceil


s3 = boto.connect_s3()
bucket = s3.get_bucket(S3_BUCKET)


def batch_aggregate_small_s3files_bydatetimebin_onto_s3(collection=None,firstdatetimebin=FIRSTBINEVER, dry_run=True):

    print '------------------------------------------------------------------------'
    print 'Beginning Batch Job of Aggregating Small files on S3 and storing on S3'
    print ''
    print 'Initial Scan:'

    datetimebin = firstdatetimebin

    while datetimebin < time.time():
        datetimebin += 3600
        datetimebinstr = time.strftime('%Y-%m-%d_%H', time.gmtime(datetimebin))

        key = bucket.get_key('%s/metaplus_%s.json/_SUCCESS'%(collection,datetimebinstr))

        if key is None:

            print datetimebinstr, ': Might need to aggregate'

            if dry_run is True:
                continue

            try:
                # Open files like s3n://...@bucket/collection/2015-06-21_17/*metaplus.json
                a = sc.textFile(os.path.join(S3_PREFIX,datetimebinstr,'*metaplus.json'))
                # This will throw an exception if there is no file
                a.first()





                # Coalesce into a small number of partitions so that each file piece is ~100MB
                a = a.coalesce(30, shuffle=True)
                a.persist()
                numberofpartitions = int(ceil(a.map(len).reduce(lambda x,y: x+y)/(100.0*1024*1024)))
                a = a.coalesce(int(numberofpartitions), shuffle=True)

                get_ipython().magic(u"time a.saveAsTextFile(os.path.join(S3_PREFIX,'metaplus_%s.json'%(datetimebinstr)))")
                print "Saved to S3"
    #             except:
    #                 print "No individual files"
    #                 pass

            except:
                # No files on S3 source
                print datetimebinstr, ': --->No source files to aggregate'

        else:
            print datetimebinstr, ': Already aggregated'



batch_aggregate_small_s3files_bydatetimebin_onto_s3(collection=collection)

print 'Beginning batch job in 5 seconds...'

time.sleep(5)


# ## Take individual metaplus.json files, aggregate, and copy to S3 (for convenience) and HDFS (for speed)

# In[7]:


print "---------------------------------------------"
print "STAGE 1: Aggregating small S3 files and copying to S3"

batch_aggregate_small_s3files_bydatetimebin_onto_s3(collection=collection, dry_run=False)





# In[8]:


# #######################################################
# #  S3 Aggregate files ----> HDFS

# print "---------------------------------------------"
# print "STAGE 2: Copying Aggregated Files from S3 to HDFS"

# from snakebite.client import Client
# client = Client("52.8.132.154")

# datetimebin = FIRSTBINEVER
# while datetimebin < time.time():
#     datetimebin += 3600

#     datetimebinstr = time.strftime('%Y-%m-%d_%H', time.gmtime(datetimebin))

#     # If target directory does not exist with _SUCCESS file, then make the transfer
#     key = bucket.get_key('%s/metaplus_%s.json/_SUCCESS'%(collection,datetimebinstr))

#     hdfs_aggregated_file_exists = client.test('/inlivingcolor/' + '%s/metaplus_%s.json/_SUCCESS'%(collection,datetimebinstr), exists=True)
#     if hdfs_aggregated_file_exists is False:
#         print datetimebinstr, ': Might need to copy  aggregated file to HDFS'

#         try:
#             a = sc.textFile(os.path.join(S3_PREFIX,'metaplus_%s.json'%datetimebinstr))

#             # This will throw an exception if there is no file
#             a.first()

#             get_ipython().magic(u"time a.saveAsTextFile(os.path.join(HDFS_PREFIX,'metaplus_%s.json'%datetimebinstr))")
#             print "Saved aggregated file to HDFS"
#         except:
#             print "No source aggregated file on S3"
#             pass


#     else:
#         print datetimebinstr, ': Already copied aggregated file to HDFS'







# In[ ]:



