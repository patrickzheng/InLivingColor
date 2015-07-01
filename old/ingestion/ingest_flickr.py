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

        ctime_start = int(time.mktime(time.strptime("30-12-2010 14:00", "%d-%m-%Y %H:%M")))

        for i in range(1):
            ctime_length = 60
            ctime_interval = 60*60

            print range(ctime_start,
                        ctime_start+ctime_length,
                        ctime_interval            )

            ctime_starts = [ctime_start]

            for i,photo_id in enumerate(GetPhotoIDs_batch_iter(ctime_starts,
                                                               interval=ctime_interval)):

                print i, ctime_start, photo_id
                producer.send_messages('flickr-photo_id-dist', photo_id)
                #print photo_id
                time.sleep(0.3)

            ctime_start += ctime_interval

            time.sleep(1)


def main():
    threads = [
        Producer(),
        # Consumer()
    ]

    for t in threads:
        t.start()

    time.sleep(5)

    while True:
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.WARNING
        )
    main()
