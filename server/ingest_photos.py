"""
Helper file for ingesting photoids. Used by the "ingest_photos_continuously" scripts.
"""
# TODO: Make this file runnable from the command line


from _configuration import KAFKA_BROKER_LIST, KAFKA_PHOTOID_TOPIC

from flickr_helper import GetSearchQueryAttrib, GetPhotoIDs_iter, GetInfoAsJson

from kafka.client import KafkaClient
from kafka.producer import KeyedProducer

# KAFKA_BROKER_LIST = 'localhost:9092'

producer = KeyedProducer(KafkaClient(KAFKA_BROKER_LIST))

print producer


import json
import time

# def SmartQueueIngestionByDateUploaded(collection, startctime, dry_run=False):

#     while True:

#         print startctime


#         query = dict(min_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(startctime)),
#                      max_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(startctime+10*60)),
#                     sort='date-posted-asc',
#                     )
#         QueueIngestionByFlickrAPISearchQuery(collection=collection,query=query,dry_run=dry_run, limit_at_n=4000)

#         startctime += 10*60
#         # print photoids

def QueueIngestionByFlickrAPISearchQuery(collection, query, dry_run=False,
                                         skip_if_downloaded=False, check_api_limit=False, limit_at_n=4000, delay=0.1):
    """
    Queues the results of a FlickrAPI search query for downloading into an
    InLivingColor collection by sending message via Kafka to the cluster (i.e.,
    this is a producer in Kafka-speak)

    Arguments:

    - collection : the name of the InLivingColor collection to which to add
                   the corresponding photos and their metadata

    - query (dict) : a Python dict of the search query parameters,
                     e.g. dict(text='yosemite',content_type=1,has_geo=1)

    - dry_run (bool) : If True, then the messages will not be send to
                       the Kafka cluster. Useful for finding out the number
                       of pictures a query has.

    - skip_if_downloaded (bool) : removes photoids for pictures that
                                       have already been downloaded by
                                       checking the Cassandra database
                                       (not implemented)
    - check_api_limit (bool) : if True, raise an exception when the query
                               returns more than 4000 results, the Flickr
                               limit

    """


    ###########################################################################
    # Get search query meta results, which look like this:
    # {'total': '1023180', 'perpage': '250', 'page': '1', 'pages': '4093'}

    rsp = GetSearchQueryAttrib(**query)
    print "Initiating Flickr PhotoID Search (%s results)" % rsp['total']

    if check_api_limit is True:
        # We cannot download more than 4000 distinct photoids, so make sure your
        # searches contain less than this amount
        assert int(rsp['total']) <= 4000

    ###########################################################################
    # Download the photoids from the server page by page

    numpages = int(rsp['pages'])

    wholelistofphotoids = []

    count = 0

    for page in range(1, numpages +1):

        # Put photoids from this page into a list
        photoids = list(GetPhotoIDs_iter(page=str(page), **query))


        wholelistofphotoids += photoids


        for photoid in [photoids[0],photoids[-1]]:
            datetaken = json.loads(GetInfoAsJson(photoid))['photo']['dates']['taken']
            print photoid, datetaken

        print "Downloading page %s/%s" % (page, rsp['pages']),
        print "%s ... %s" % (photoids[0],photoids[-1])

        # Send
        if dry_run is False:
            QueueIngestionByPhotoIDs(collection,
                                     # wholelistofphotoids,
                                     photoids,
                                     # key=json.dumps(dict(collection=collection,
                                     #                page=page)),
                                     skip_if_downloaded=skip_if_downloaded,
                                     delay=delay)

        if limit_at_n > 0:
            count += len(photoids)
            print "(%d photoids so far)" % count
            if count >= limit_at_n:
                break

    return wholelistofphotoids

def QueueIngestionByPhotoIDs(collection, photoids, key=None,
                             skip_if_downloaded=False, delay=0.1):
    """
    Queues the given Flickr photoid's for downloading into an InLivingColor
    collection by sending message via Kafka to the cluster (i.e., this is
    a producer in Kafka-speak)

    Arguments:

    - collection (str) : the name of the InLivingColor collection to which to
                         add the corresponding photos and their metadata

    - photoids (list of str) : a list of strings of the actual photoids

    - key (str) : the key to use for the Kafka message

    - skip_if_downloaded (bool) : removes photoids for pictures that
                                       have already been downloaded by
                                       checking the Cassandra database
                                       (not implemented)

    """


    assert type(collection) is str
    print "-> Kafka(topic=%s)" % KAFKA_PHOTOID_TOPIC,

    for photoid in photoids:
        assert type(photoid) is str
        #######################################################################
        # Send the message via Kafka
        message_key = key if key is not None else photoid
        message = json.dumps(dict(collection=collection, photoid=str(photoid)))


        print photoid,
        # '{"photoid": "3311097747", "collection": "leaves"}'

        # print "-> Kafka(topic=%s, key=%s, msg=%s)" % (KAFKA_PHOTOID_TOPIC,
        #                                                         message_key,
        #                                                         message)
         # % (KAFKA_PHOTOID_TOPIC,
         #                                                        message_key,
         #                                                        message)
        time.sleep(delay)
        producer.send_messages(KAFKA_PHOTOID_TOPIC, message_key, message)


if __name__ == '__main__':
    import time
    # query = dict(text='leaves', content_type=1, has_geo=1, is_commons=1, order='date-taken-asc')
    # QueueIngestionByFlickrAPISearchQuery('leaves', query, dry_run=False)
    # query = dict(min_upload_date=int(time.clock()), order='date-taken-asc')
    # QueueIngestionByFlickrAPISearchQuery('allrecent', query, dry_run=False)

    SmartQueueIngestionByDateUploaded(collection='allrecent', startctime=int(time.time())-24*3600, dry_run=False)
