#!/usr/bin/env python
import threading
import logging
import time
from flickr_helper import GetPhotoIDs_batch_iter

from kafka.client import KafkaClient
from kafka.producer import SimpleProducer


class Producer(threading.Thread):
    daemon = True

    def run(self):
        client = KafkaClient("localhost:9092")
        producer = SimpleProducer(client)

        while True:
            ctime_start = int(time.mktime(time.strptime("30-11-2010 00:00", "%d-%m-%Y %H:%M")))
            ctime_length = 60*60
            ctime_interval = 60
            ctime_mod = 1

            for i,photo_id in enumerate(GetPhotoIDs_batch_iter(range(ctime_start,
                                                                     ctime_start+ctime_length,
                                                                     ctime_interval*ctime_interval),
                                                               interval=ctime_interval)):

                producer.send_messages('flickr-photo_id-%d'%(1+(i%3)), photo_id)
                #print photo_id
                time.sleep(0.1)

            ctime_start += ctime_length

            time.sleep(1)


def main():
    threads = [
        Producer(),
        # Consumer()
    ]

    for t in threads:
        t.start()

    time.sleep(5)

    while False:
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.DEBUG
        )
    main()
