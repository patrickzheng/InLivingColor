
import os
import time

collection = "geotagged"
FIRSTBINEVER = time.mktime((2015, 06, 20, 16, 0, 0, 0, 0, 0)) # "2015-06-20_16"

# print datetimebins
# ['2015-06-20_16', '2015-06-20_17', '2015-06-20_18', '2015-06-20_19', '2015-06-20_20', '2015-06-20_21', '2015-06-20_22', '2015-06-20_23', '2015-06-21_00', '2015-06-21_01', '2015-06-21_02', '2015-06-21_03', '2015-06-21_04', '2015-06-21_05', '2015-06-21_06', '2015-06-21_07', '2015-06-21_08', '2015-06-21_09', '2015-06-21_10', '2015-06-21_11', '2015-06-21_12', '2015-06-21_13', '2015-06-21_14', '2015-06-21_15', '2015-06-21_16', '2015-06-21_17', '2015-06-21_18', '2015-06-21_19', '2015-06-21_20', '2015-06-21_21', '2015-06-21_22', '2015-06-21_23', '2015-06-22_00', '2015-06-22_01', '2015-06-22_02', '2015-06-22_03', '2015-06-22_04', '2015-06-22_05', '2015-06-22_06', '2015-06-22_07', '2015-06-22_08', '2015-06-22_09', '2015-06-22_10', '2015-06-22_11', '2015-06-22_12', '2015-06-22_13', '2015-06-22_14', '2015-06-22_15', '2015-06-22_16', '2015-06-22_17', '2015-06-22_18', '2015-06-22_19', '2015-06-22_20', '2015-06-22_21', '2015-06-22_22', '2015-06-22_23', '2015-06-23_00', '2015-06-23_01', '2015-06-23_02', '2015-06-23_03', '2015-06-23_04', '2015-06-23_05', '2015-06-23_06', '2015-06-23_07', '2015-06-23_08', '2015-06-23_09', '2015-06-23_10', '2015-06-23_11', '2015-06-23_12', '2015-06-23_13', '2015-06-23_14', '2015-06-23_15', '2015-06-23_16', '2015-06-23_17', '2015-06-23_18', '2015-06-23_19', '2015-06-23_20', '2015-06-23_21', '2015-06-23_22', '2015-06-23_23', '2015-06-24_00', '2015-06-24_01', '2015-06-24_02', '2015-06-24_03', '2015-06-24_04', '2015-06-24_05', '2015-06-24_06', '2015-06-24_07', '2015-06-24_08', '2015-06-24_09', '2015-06-24_10', '2015-06-24_11', '2015-06-24_12', '2015-06-24_13', '2015-06-24_14', '2015-06-24_15', '2015-06-24_16', '2015-06-24_17', '2015-06-24_18', '2015-06-24_19', '2015-06-24_20', '2015-06-24_21', '2015-06-24_22', '2015-06-24_23', '2015-06-25_00', '2015-06-25_01', '2015-06-25_02', '2015-06-25_03', '2015-06-25_04', '2015-06-25_05', '2015-06-25_06', '2015-06-25_07', '2015-06-25_08', '2015-06-25_09', '2015-06-25_10', '2015-06-25_11', '2015-06-25_12', '2015-06-25_13', '2015-06-25_14', '2015-06-25_15', '2015-06-25_16', '2015-06-25_17', '2015-06-25_18', '2015-06-25_19', '2015-06-25_20', '2015-06-25_21', '2015-06-25_22', '2015-06-25_23', '2015-06-26_00', '2015-06-26_01', '2015-06-26_02', '2015-06-26_03', '2015-06-26_04', '2015-06-26_05', '2015-06-26_06', '2015-06-26_07', '2015-06-26_08', '2015-06-26_09', '2015-06-26_10', '2015-06-26_11', '2015-06-26_12', '2015-06-26_13', '2015-06-26_14', '2015-06-26_15', '2015-06-26_16', '2015-06-26_17', '2015-06-26_18', '2015-06-26_19', '2015-06-26_20', '2015-06-26_21', '2015-06-26_22', '2015-06-26_23', '2015-06-27_00', '2015-06-27_01', '2015-06-27_02', '2015-06-27_03', '2015-06-27_04', '2015-06-27_05', '2015-06-27_06', '2015-06-27_07', '2015-06-27_08', '2015-06-27_09', '2015-06-27_10', '2015-06-27_11', '2015-06-27_12', '2015-06-27_13', '2015-06-27_14', '2015-06-27_15', '2015-06-27_16', '2015-06-27_17', '2015-06-27_18', '2015-06-27_19', '2015-06-27_20', '2015-06-27_21', '2015-06-27_22', '2015-06-27_23', '2015-06-28_00', '2015-06-28_01', '2015-06-28_02', '2015-06-28_03', '2015-06-28_04', '2015-06-28_05', '2015-06-28_06', '2015-06-28_07', '2015-06-28_08', '2015-06-28_09', '2015-06-28_10', '2015-06-28_11', '2015-06-28_12', '2015-06-28_13', '2015-06-28_14', '2015-06-28_15', '2015-06-28_16', '2015-06-28_17', '2015-06-28_18', '2015-06-28_19', '2015-06-28_20']

def ALLBINSFROMTHISTIMETILONEHOURAGO(thistime):
    return map(lambda d: time.strftime('%Y-%m-%d_%H', time.gmtime(d)), range(int(max(thistime,FIRSTBINEVER)),int(time.time())-3600,3600))

ALLBINSTILONEHOURAGO = ALLBINSFROMTHISTIMETILONEHOURAGO(0)



HDFS_PREFIX = 'hdfs://52.8.132.154/inlivingcolor/geotagged'
S3_PREFIX = 's3n://%(key)s:%(secret)s@inlivingcolor/geotagged'


flickr_api_key = os.getenv('FLICKR_API_KEY')
print "Using flickr API_KEY: ", flickr_api_key[:5], "..."
flickr_api_secret = os.getenv('FLICKR_API_SECRET')


AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
print "Using AWS_ACCESS_KEY_ID: ", AWS_ACCESS_KEY_ID[:5], "..."
S3_PREFIX = S3_PREFIX % dict(key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY)

KAFKA_PHOTOID_TOPIC = 'downloadpreprocessandstore'
# change in d_p_s as well


KAFKA_BROKER_LIST = 'ip-172-31-6-182:9092,ip-172-31-6-183:9092,ip-172-31-6-184:9092,ip-172-31-6-185:9092,ip-172-31-6-186:9092,ip-172-31-6-187:9092,ip-172-31-6-188:9092'
ZOOKEEPER_LIST = 'ip-172-31-6-182:9092,ip-172-31-6-183:9092,ip-172-31-6-184:9092,ip-172-31-6-185:9092,ip-172-31-6-186:9092,ip-172-31-6-187:9092,ip-172-31-6-188:9092'


ALL_LOCAL_IPS = '172.31.6.181,172.31.6.182,172.31.6.183,172.31.6.184,172.31.6.185,172.31.6.186,172.31.6.187,172.31.6.188'


S3_BUCKET = 'inlivingcolor'
CASSANDRA_KEYSPACE = 'inlivingcolor'
