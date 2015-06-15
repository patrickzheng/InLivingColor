#!/usr/bin/env python
import threading
import logging
import time

from kafka.client import KafkaClient
from kafka.producer import SimpleProducer, KeyedProducer

TESTPHOTOIDS = [
                '10784228453',
                '11454603163',
                '12652204364',
                '14240897217',
                '14827062358',
                '15587031160',
                '16087749015',
                # '16878281001',
                '16878281000',  # This one should fail
                '10462972476',
                '10785411656',
                '11454608476',
                '12652247684',
                ]

TESTPHOTOIDS = range(20)

class ProducerPhotoID(threading.Thread):
    daemon = True

    def run(self, delay=0.1):
        client = KafkaClient("ip-172-31-6-183:9092")
        producer = SimpleProducer(client)

        import numpy as np

        for photoid in TESTPHOTOIDS:
            producer.send_messages('testtopic3',str(photoid))
            print "Sending PhotoID: %s"%photoid

            time.sleep(delay)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.DEBUG
        )
    ProducerPhotoID().start(),

    time.sleep(5)
