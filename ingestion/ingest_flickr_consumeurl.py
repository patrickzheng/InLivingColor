#!/usr/bin/env python
import threading
import logging
import time
# from flickr_helper import GetPhotoIDs_batch_iter

from kafka.client import KafkaClient
# from kafka.producer import SimpleProducer
from kafka.consumer import SimpleConsumer

class Consumer(threading.Thread):
    daemon = True

    def run(self):
        client = KafkaClient("localhost:9092")
        consumer = SimpleConsumer(client, "theonlygroup", "testtopic3")

        for message in consumer:
            print(message)

def main():
    threads = [
        # Producer(),
        Consumer()
    ]

    for t in threads:
        t.start()

    while True:
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.DEBUG
        )
    main()
