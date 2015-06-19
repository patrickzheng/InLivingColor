import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery

# Run like this
# kafka-console-consumer --zookeeper localhost:2181 --consumer.config ~/kafkatest/consumerconfig.txt --topic test-downloadbyphotoid | python copy_by_json_to_cassandra.py

if __name__ == '__main__':
    collection = "has_geo"
    print "collection: ", collection

    now = int(time.time())

    initialdelay = 24*3600*30
    mindelay = 24*3600
    querytime = now - initialdelay - 60*5
    while True:

        # now = int(time.time())
        # timeelapsesincelastca

        try:
            # querytime = min(now - mindelay, querytime + 60*5)


            query = dict(min_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime)),
                         max_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+60*10)),
                         has_geo=1,
                        sort='date-posted-asc',
                        )

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.05)

            timeelapsed = int(time.time()) - now
            print "TIMEELAPSED (should be less than 5 mins): %d"%timeelapsed

            querytime += 60*5

            print 'waiting .',
            while querytime > time.time() - mindelay:
                print '.',
                time.sleep(5)
            print ''
            # sleepfor = max(0,timeelapsed-60*5)
            # print "Slept for %d seconds"%sleepfor
        except KeyboardInterrupt:
            raise
        except:
            pass
