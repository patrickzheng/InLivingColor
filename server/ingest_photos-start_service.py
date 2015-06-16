DON'T run

Replaced vy
kafka-console-consumer --zookeeper localhost:2181 --consumer.config ~/kafkatest/consumerconfig.txt --topic test-downloadbyphotoid | python copy_by_json_to_cassandra.py

#!/usr/bin/env python
import threading
import time

from _configuration import KAFKA_BROKER_LIST, KAFKA_PHOTOID_TOPIC

from kafka.client import KafkaClient
from kafka.producer import KeyedProducer
from kafka.consumer import KafkaConsumer

from flickr_helper import WriteFiles, WriteFilesToTar, GetPhotoAndMetaData


import json
import happybase


import tempfile
import shutil
import os
import subprocess

from subprocess import call
from cassandra.cluster import Cluster

######################################################
# CQL ROCKS
from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection

# Define a model
class flickrsot(Model):
    collection = columns.Text(primary_key=True)
    photoid = columns.Text(primary_key=True)
    imagejpg = columns.Blob()
    infojson = columns.Text()
    exifjson = columns.Text()
    def __repr__(self):
        return '<sourceoftruth: collection=%s photoid=%s %d-byte jpg>' % (self.collection, self.photoid, len(self.imagejpg))

connection.setup(['127.0.0.1'], "inlivingcolor")

from cqlengine.management import sync_table
sync_table(flickrsot)

from random import shuffle

def ConsumePhotoIDandStoreDataInSourceOfTruth(dry_run=False):
    """
    - dry_run (bool) : If True, will not download and will not write to cassandra.
    """


    brokers = KAFKA_BROKER_LIST.split(',')
    shuffle(brokers) # works in place

    consumer = KafkaConsumer(KAFKA_PHOTOID_TOPIC,
                             group_id="theonlygroup",
                             metadata_broker_list=brokers,
                             auto_commit_enable=True,
                             auto_commit_interval_messages=50,
                             auto_commit_interval_ms=10*1000,

                             )

    print consumer

    tempdir = tempfile.mkdtemp()

    # connection = happybase.Connection('localhost')
    # table = connection.table('FlickrSOT')


    for kafkamessage in consumer:

        # print kafkamessage
        try:
            # KafkaMessage(topic='test-downloadbyphotoid', partition=2, offset=113, key='{"page": 4, "collection": "leaves"}', value='3485994635')

            ### TODO: print partition
            # print forcassandra

            # Insert one record into the users table

            ################################################################
            # TO HBASE
            # table.put('row-key', {'collection:': collection,
            #                       'photoid:': photoid,
            #                       'ImageJPG:': rsp['ImageJPG'],
            #                       'InfoJSON:': rsp['InfoJSON'],
            #                       'ExifJSON:': rsp['ExifJSON']})


            # print "Sent to HBase photoid, ", photoid

            ################################################################
            # TO CASSANDRA

            # prepared_stmt = session.prepare("INSERT INTO flickrsot (collection, photoid, imagejpg, infojson, exifjson) VALUES (?, ?, ?, ?, ?)")
            # bound_stmt = prepared_stmt.bind([collection,
            #                                 photoid,
            #                                 rsp['ImageJPG'],
            #                                 rsp['InfoJSON'],
            #                                 rsp['ExifJSON']])

            # stmt = session.execute(bound_stmt)

            # print "Sent to cassandra photoid, ", photoid

        except:
            pass

    shutil.rmtree(tempdir)


# CREATE TABLE FlickrSOT ( collection text, photoid text, ImageJPG blob, InfoJSON text, ExifJSON text, PRIMARY KEY (collection,  photoid));# class ConsumeTarFileStringsAndUpload(threading.Thread):
#     daemon = True

#     def run(self):

#         consumer = KafkaConsumer("test-tarfiles", group_id="theonlygroup", metadata_broker_list=KAFKA_BROKER_LIST.split(',')[:])

#         tempdir = tempfile.mkdtemp()

#         print 'tempdir', tempdir

#         messagesinbuffer = 0
#         ctimeforlastmessage = {}

#         for kafkamessage in consumer:
#             print '<- (test-tarfiles)',
#             print  kafkamessage[3]

#             collection = json.loads(kafkamessage[3])['collection']

#             tarfilestring = kafkamessage[4]

#             with tempfile.NamedTemporaryFile() as f:
#                 f.write(tarfilestring)

#                 # subprocess.call(['tar', 'xf', f.name, '-C', tempdir])


#             try:
#                 timesincelastmessage = time.clock() - ctimeforlastmessage[collection]
#             except:
#                 timesincelastmessage = 0.0


#             messagesinbuffer += 1

#             if messagesinbuffer >= 10 or timesincelastmessage > 5.0:
#                 print "EMPTY BUFFER"
#                 # subprocess.call(['tar', 'xf', f.name, '-C', tempdir])

#                 messagesinbuffer = 0



#             ctimeforlastmessage[collection] = time.clock()
#             # subprocess.call(['ls', tempdir])


#             # try:
#             #     tarfilestring = kafkamessage[4]  # 4='value'

#             #     KAFKA_PHOTOID_TOPIC = 'test-tarfiles'
#             #     message_key = kafkamessage[3]  # 3='key'

#             #     producer.send_messages(KAFKA_PHOTOID_TOPIC, message_key, message)
#             # except:
#             #     pass

#         # shutil.rmtree(tempdir)

if __name__ == "__main__":
    threading.Thread(target=ConsumePhotoIDandStoreDataInSourceOfTruth, kwargs=dict(dry_run=False)).start()
    # ConsumeTarFileStringsAndUpload().start()

    while True:
        time.sleep(5)
