#!/usr/bin/env python
import threading
import time

from _configuration import KAFKA_BROKER_LIST

from kafka.client import KafkaClient
from kafka.producer import KeyedProducer
from kafka.consumer import KafkaConsumer

from flickr_helper import WriteFiles


import json


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

from subprocess import check_call

class Consumer(threading.Thread):
    daemon = True

    def run(self):
        consumer = KafkaConsumer("test-downloadbyphotoid", group_id="theonlygroup", metadata_broker_list=KAFKA_BROKER_LIST.split(',')[:])
        # producer = KeyedProducer(KafkaClient(KAFKA_BROKER_LIST))

        print consumer

        tempdir = tempfile.mkdtemp()
        tempdirout = tempfile.mkdtemp()

        for kafkamessage in consumer:
            print kafkamessage

# ?            try:
                # KafkaMessage(topic='testtopic3',partition=3,offset=10772,key='3',
                #           value='{"photoid":"3486782878","collection":"leaves"}')
                # print "<- Msg: %s" % [kafkamessage]

            message = json.loads(kafkamessage[4])  # 4='value'
            photoid = message['photoid']
            tarfilepath = os.path.join(tempdirout, 'tarfile.tar')

            WriteFiles(path=tempdir, photo_id=photoid)
            check_call(['tar', '-cf %s %s' % (tarfilepath, tempdir)])

            with open(tarfilepath) as f:
                print "-> Msg: %s" % f
                message_topic = 'test-tarfiles'
                message_key = kafkamessage[3]  # 3='key'
                message = f.read()


                #     print "-> Msg (topic=%s, key=%s, msg=%s)" % (message_topic,
                #                                                             message_key,
                #                                                             message)
                #     #     producer.send_messages(message_topic, message_key, message)
            # except:
            #     pass

        shutil.rmtree(tempdir)


if __name__ == "__main__":
    Consumer().start()

    while True:
        time.sleep(5)
