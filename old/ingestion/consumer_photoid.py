#!/usr/bin/env python
from flickrapi import FlickrError
import threading
import logging
import time
from flickr_helper import photo2url, photoid2getInfoResponse, WriteFilesToS3
import os

from kafka.client import KafkaClient
# from kafka.producer import SimpleProducer
from kafka.consumer import SimpleConsumer

def normalize_timestamp(timestampstr):
    timestamp = time.strptime(timestampstr, "%Y-%m-%d %H:%M:%S")
    timestamp_normalized = time.strftime("%Y-%m-%d",timestamp)
    return timestamp_normalized



class Consumer(threading.Thread):
    daemon = True

    def run(self):
        client = KafkaClient("localhost:9092")
        consumer = SimpleConsumer(client, "theonlygroup", "flickr-photoid")

        # Has the form OffsetAndMessage(offset=37, message=Message(magic=0, attributes=0, key=None, value='11454608476'))

        for offset_and_message in consumer:

            try:
                photoid = offset_and_message[1][3]
                photo = photoid2getInfoResponse(photoid)



                ####################### WRITE PHOTOID TO FILE





                ####################### DOWNLOAD PHOTO
                url = photo2url(photo)

                # Get date taken from Flickr response in the form "2011-11-11 11:20:13"
                datetakenstr = photo.find('dates').attrib['taken']
                datetakenstr_normalized = normalize_timestamp(datetakenstr)

                print 'PhotoID: %s, %s' % (photoid,url)
                print 'Date Taken: %s' % (datetakenstr_normalized)


                fullpath = os.path.join('Flickr/new', datetakenstr_normalized, photoid)
                print "Transferring to S3: %s" % fullpath
                WriteFilesToS3(path=fullpath, photo_id=photoid)



            except FlickrError as exc: #
                print "Error with %s (might not exist)"%photoid
                pass





def main():
    Consumer().start()

    while True:
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.WARNING
        )
    main()
