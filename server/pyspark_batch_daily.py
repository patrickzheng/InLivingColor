"""


"""


import os
import sys
spark_home = os.environ.get('SPARK_HOME', None)
if not spark_home:
    raise ValueError('SPARK_HOME environment variable is not set')
sys.path.insert(0, os.path.join(spark_home, 'python'))
# Make sure this file exists
sys.path.insert(0, os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))
os.environ['PYSPARK_SUBMIT_ARGS'] = """\
--num-executors 8 \
--executor-cores 2 \
--executor-memory 1500m \
--driver-memory 1500m \
--master yarn --deploy-mode client \
--py-files /home/ubuntu/InLivingColor/server/_configuration.py \
--py-files /home/ubuntu/InLivingColor/server/flickr_helper.py \
    """

execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))

###############################################################################
# Aggregate files from S3 if that has not been done already, save it back to
# HDFS and S3. Only do for the hours of the previous day

# First query S3 to see what dates/hours are already there

# Then for the ones that do not have a corresponding aggregated json file,
# create one



###############################################################################
# Read HDFS and create counts


###############################################################################
# Read HDFS and create masterlist



