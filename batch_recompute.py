import os
import sys
spark_home = os.environ.get('SPARK_HOME', None)
if not spark_home:
    raise ValueError('SPARK_HOME environment variable is not set')
sys.path.insert(0, os.path.join(spark_home, 'python'))
# Make sure this file exists
sys.path.insert(0, os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))
os.environ['PYSPARK_SUBMIT_ARGS'] = """\
--jars /home/ubuntu/InLivingColor/server/pyspark-cassandra.jar \
--driver-class-path  /home/ubuntu/InLivingColor/server/pyspark-cassandra.jar \
--num-executors 8 \
--executor-cores 2 \
--executor-memory 1500m \
--driver-memory 1500m \
--master yarn --deploy-mode client \
--py-files /home/ubuntu/InLivingColor/server/_configuration.py \
--py-files /home/ubuntu/InLivingColor/server/flickr_helper.py \
    """
# --py-files /home/ubuntu/InLivingColor/server/pyspark_cassandra-0.1.5-py2.7.egg \
# --conf spark.cassandra.connection.host='172.31.6.181,172.31.6.1
# 82,172.31.6.183,172.31.6.184,172.31.6.185,172.31.6.186,172.31.6.187,172.31.6.188' \
#     yourscript.py
execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))
collection = 'all_geo'
