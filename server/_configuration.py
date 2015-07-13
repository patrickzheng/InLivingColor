
import os
import time

################################################################################
# Config.

collection = "geotagged"

# This is the time we started downloading photos for the first time. This we we
# know what are the first bins to look for. Perhaps it would be better to simply
# list the source folders in S3. TODO: Move this to batch_helper module, well,
# and then replace it with a routine that simply looks at the source files in S3
FIRSTBINEVER = time.mktime((2015, 06, 20, 16, 0, 0, 0, 0, 0)) # "2015-06-20_16"

def ALLBINSFROMTHISTIMETILONEHOURAGO(thistime):
    return map(lambda d: time.strftime('%Y-%m-%d_%H', time.gmtime(d)), range(int(max(thistime,FIRSTBINEVER)),int(time.time())-3600,3600))

ALLBINSTILONEHOURAGO = ALLBINSFROMTHISTIMETILONEHOURAGO(0)


################################################################################
# The API keys are both stored on the machines as environment variables
flickr_api_key = os.getenv('FLICKR_API_KEY')
print "Using flickr API_KEY: ", flickr_api_key[:5], "..."
flickr_api_secret = os.getenv('FLICKR_API_SECRET')

AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
print "Using AWS_ACCESS_KEY_ID: ", AWS_ACCESS_KEY_ID[:5], "..."

################################################################################
# Prefixes for HDFS and S3.
HDFS_PREFIX = 'hdfs://52.8.132.154/inlivingcolor/%(collection)s'
S3_PREFIX = 's3n://%(key)s:%(secret)s@inlivingcolor/%(collection)s'

# Place accesskeys, etc in these prefixes
S3_PREFIX = S3_PREFIX % dict(key=AWS_ACCESS_KEY_ID,
                             secret=AWS_SECRET_ACCESS_KEY,
                             collection=collection
                             )
HDFS_PREFIX = HDFS_PREFIX % dict(collection=collection)



# The topic on which to send photoid's for workers to consume, download,
# preprocess and move to S3
KAFKA_PHOTOID_TOPIC = 'downloadpreprocessandstore'


# Host/IP lists
KAFKA_BROKER_LIST = "ip-172-31-0-16:9092,ip-172-31-9-80:9092,ip-172-31-9-81:9092,ip-172-31-9-82:9092,ip-172-31-9-83:9092,ip-172-31-9-84:9092,ip-172-31-9-85:9092,ip-172-31-9-86:9092,ip-172-31-9-87:9092,ip-172-31-9-88:9092,"
ZOOKEEPER_LIST = "ip-172-31-0-16:9092,ip-172-31-9-80:9092,ip-172-31-9-81:9092,ip-172-31-9-82:9092,ip-172-31-9-83:9092,ip-172-31-9-84:9092,ip-172-31-9-85:9092,ip-172-31-9-86:9092,ip-172-31-9-87:9092,ip-172-31-9-88:9092,"

ALL_LOCAL_IPS = '172.31.0.16,172.31.9.80,172.31.9.81,172.31.9.82,172.31.9.83,172.31.9.84,172.31.9.85,172.31.9.86,172.31.9.87,172.31.9.88'


S3_BUCKET = 'inlivingcolor'
CASSANDRA_KEYSPACE = 'inlivingcolor'
