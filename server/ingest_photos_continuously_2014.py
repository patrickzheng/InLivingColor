import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery

# Run like this
# kafka-console-consumer --zookeeper localhost:2181 --consumer.config ~/kafkatest/consumerconfig.txt --topic test-downloadbyphotoid | python copy_by_json_to_cassandra.py
if __name__ == '__main__':
    collection = "geotagged"
    print "collection: ", collection

    now = int(time.time())

    interval = -3600*6
    # interval = 3600*24
    # querytime = now - initialdelay - interval
    querytime = time.mktime((2015,1,1,0,0,0,0,0,0))
    while True:

        if querytime < time.mktime((2014,1,1,0,0,0,0,0,0)):
            querytime = time.mktime((2015,1,1,0,0,0,0,0,0)) + time.mktime((2014,1,1,0,0,0,0,0,0)) - querytime + 11340
        else:
            querytime += interval

        try:


            query = dict(min_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime)),
                         max_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+interval)),
                         has_geo=1,
                         tags='fields,leaves,trees,grass,hills',
                         woe_id='2347563', # California
                         # is_commons='True',
                        sort='date-taken-asc',
                        )

            print 'downloading', query['min_taken_date'], 'time ', querytime

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.02, limit_at_n=500)

        except KeyboardInterrupt:
            raise
        except:
            pass
