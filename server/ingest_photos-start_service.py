#!/usr/bin/env python
import threading
import time

from _configuration import KAFKA_BROKER_LIST

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



class ConsumePhotoIDandStoreDataInSourceOfTruth(threading.Thread):
    daemon = True

    def run(self):
        # cluster = Cluster()
        # session = cluster.connect('inlivingcolor')


        consumer = KafkaConsumer("test-downloadbyphotoid",
                                 group_id="theonlygroup",
                                 metadata_broker_list=KAFKA_BROKER_LIST.split(',')[:],
                                 auto_commit_enable=True,
                                 auto_commit_interval_messages=50,
                                 auto_commit_interval_ms=10*1000,
                                 )
        # producer = KeyedProducer(KafkaClient(KAFKA_BROKER_LIST))

        # print consumer

        tempdir = tempfile.mkdtemp()

        # connection = happybase.Connection('localhost')
        # table = connection.table('FlickrSOT')


        for kafkamessage in consumer:

            # print kafkamessage
            # KafkaMessage(topic='test-downloadbyphotoid', partition=2, offset=113, key='{"page": 4, "collection": "leaves"}', value='3485994635')
            try:
                collection = json.loads(kafkamessage[3])['collection']  # 4='value'
                photoid = kafkamessage[4]  # 4='value'

                # print "hi"

                if flickrsot.objects(collection=collection,
                                     photoid=photoid).count() > 0:
                    print "Already downloaded %s/%s" % (collection, photoid)
                    continue


                # print photoid
                # raise

                rsp = GetPhotoAndMetaData(photoid)
                # print collection, photoid, rsp['ImageJPG'][:10]

                forcassandra = dict(
                        collection=collection,
                        photoid=photoid,
                        ImageJPG=rsp['ImageJPG'],
                        InfoJSON=rsp['InfoJSON'],
                        ExifJSON=rsp['ExifJSON'],
                        )
                flickrsot.create(**forcassandra)
                print "Sent to Cassandra %s/%s" % (collection, photoid)
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

#             #     message_topic = 'test-tarfiles'
#             #     message_key = kafkamessage[3]  # 3='key'

#             #     producer.send_messages(message_topic, message_key, message)
#             # except:
#             #     pass

#         # shutil.rmtree(tempdir)

if __name__ == "__main__":
    ConsumePhotoIDandStoreDataInSourceOfTruth().start()
    # ConsumeTarFileStringsAndUpload().start()

    while True:
        time.sleep(5)
