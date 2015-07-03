
# coding: utf-8

# # Load Spark

# In[1]:

import os
import sys

spark_home = os.environ.get('SPARK_HOME', None)
if not spark_home:
    raise ValueError('SPARK_HOME environment variable is not set')
sys.path.insert(0, os.path.join(spark_home, 'python'))
sys.path.insert(0, os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))

os.environ['PYSPARK_SUBMIT_ARGS']="--num-executors 10 --master yarn --deploy-mode client --executor-memory 1500m --driver-memory 1500m"

execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))


# In[ ]:

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

    datetimebin = firstdatetimebin + 3600*80


    # I don't want the latest hour because it's not completely downloaded yet!
    while datetimebin < time.time() - 3600:

        datetimebinstr = time.strftime('%Y-%m-%d_%H', time.gmtime(datetimebin))
        datetimebin += 3600

#         print time.time(), datetimebin

        key = bucket.get_key('%s/metaplus_%s.json/_SUCCESS'%(collection,datetimebinstr))

        # If YYYY-MM-DD_HH.p has already been generated, no need to do it again.
        if key is not None:
            print '--- File %s already exists. Skipping...' % (datetimebinstr+'.json')
            continue

        print datetimebinstr, ': Might need to aggregate'



        # Delete files that might prevent us from writing
        filestodelete = list(bucket.list(os.path.join(collection,'metaplus_%s.json'%(datetimebinstr))))
        if len(filestodelete) > 0:
            print '--- Deleting:', filestodelete
            bucket.delete_keys(filestodelete)

        if dry_run is True:
            continue


        # Open files like s3n://...@bucket/collection/2015-06-21_17/*metaplus.json
        a = sc.textFile(os.path.join(S3_PREFIX,datetimebinstr,'*metaplus.json'))
        # This will throw an exception if there is no file
#         a.first()





        # Coalesce into a small number of partitions so that each file piece is ~100MB
        a = a.coalesce(30, shuffle=True)
#         a.persist()
#         numberofpartitions = int(ceil(a.map(len).reduce(lambda x,y: x+y)/(100.0*1024*1024)))
#         a = a.coalesce(int(numberofpartitions), shuffle=True)

        a.saveAsTextFile(os.path.join(S3_PREFIX,'metaplus_%s.json'%(datetimebinstr)))
        print "Saved to S3"



batch_aggregate_small_s3files_bydatetimebin_onto_s3(collection=collection)

print 'Beginning batch job in 5 seconds...'

time.sleep(5)


# ## Take individual metaplus.json files, aggregate, and copy to S3 (for convenience) and HDFS (for speed)

# In[ ]:

#### print "---------------------------------------------"
print "STAGE 1: Aggregating small S3 files and copying to S3"

batch_aggregate_small_s3files_bydatetimebin_onto_s3(collection=collection, dry_run=False)





# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



