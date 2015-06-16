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



# def WriteFiles(path='', photo_id=None):

#     # path = os.path.join(path,)

#     mkdir_p(path)

#     urllib.urlretrieve(photo_id2url(photo_id), os.path.join(path, 'Image.jpg'))

#     InfoJSON = flickr.photos.getInfo(photo_id=photo_id, format="json")
#     ExifJSON = flickr.photos.getExif(photo_id=photo_id, format="json")

#     with open(os.path.join(path, 'Info.json'), 'w+') as f:
#         f.write(InfoJSON)

#     with open(os.path.join(path, 'Exif.json'), 'w+') as f:
#         f.write(ExifJSON)



# def WriteFilesToS3(path='', photo_id=None):

#     import boto
#     conn = boto.connect_s3()
#     bucket = conn.get_bucket('insight-brian-inlivingcolor')
#     # import urllib2

import tempfile
import shutil
import os
import subprocess

#     # print tempdir
#     WriteFiles(path=tempdir, photo_id=photo_id)

#     filenames = ['Info.json', 'Exif.json', 'Image.jpg']

#     for filename in filenames:

#         k = bucket.new_key(os.path.join(path, filename))
#         k.set_contents_from_filename(os.path.join(tempdir, filename))

# import tarfile
# import io
# byte_array = client.read_bytes()
# file_like_object = io.BytesIO(byte_array)
# tar = tarfile.open(fileobj=file_like_object)
# # use "tar" as a regular TarFile object
# for member in tar.getmembers():
#     f = tar.extractfile(member)
#     print(f)

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
                photo_id = kafkamessage[4]  # 4='value'

                if flickrsot.objects(collection=collection,
                                     photoid=photo_id).count() > 0:
                    print "Already downloaded %s/%s" % (collection,photoid)
                    continue


                # print photo_id
                # raise

                rsp = GetPhotoAndMetaData(photo_id)
                # print collection, photo_id, rsp['ImageJPG'][:10]

                forcassandra = dict(
                        collection=collection,
                        photoid=photo_id,
                        ImageJPG=rsp['ImageJPG'],
                        InfoJSON=rsp['InfoJSON'],
                        ExifJSON=rsp['ExifJSON'],
                        )
                flickrsot.create(**forcassandra)
                print "Send to Cassandra %s/%s" % (collection,photoid)
                # print forcassandra

                # Insert one record into the users table

                ################################################################
                # TO HBASE
                # table.put('row-key', {'collection:': collection,
                #                       'photoid:': photo_id,
                #                       'ImageJPG:': rsp['ImageJPG'],
                #                       'InfoJSON:': rsp['InfoJSON'],
                #                       'ExifJSON:': rsp['ExifJSON']})


                # print "Sent to HBase photoid, ", photoid

                ################################################################
                # TO CASSANDRA

                # prepared_stmt = session.prepare("INSERT INTO flickrsot (collection, photoid, imagejpg, infojson, exifjson) VALUES (?, ?, ?, ?, ?)")
                # bound_stmt = prepared_stmt.bind([collection,
                #                                 photo_id,
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
