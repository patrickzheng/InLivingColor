import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery

# Run like this
# kafka-console-consumer --zookeeper localhost:2181 --consumer.config ~/kafkatest/consumerconfig.txt --topic test-downloadbyphotoid | python copy_by_json_to_cassandra.py
if __name__ == '__main__':
    collection = "geotagged"
    print "collection: ", collection

    now = int(time.time())

    initialdelay = 24*3600*10
    mindelay = 24*3600
    interval = -3600*24
    # interval = 3600*24
    querytime = now - initialdelay - interval
    while True:


        try:


            query = dict(min_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime)),
                         max_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+2*interval)),
                         has_geo=1,
                        sort='date-posted-asc',
                        )

            print 'downloading', query['min_upload_date'], 'time ', querytime

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.03)

            timeelapsed = int(time.time()) - now
            print "TIMEELAPSED (should be less than 5 mins): %d"%timeelapsed

            querytime += interval

            print 'waiting .',
            while querytime > time.time() - mindelay:
                print '.',
                time.sleep(5)
            print ''

        except KeyboardInterrupt:
            raise
        except:
            pass
