import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery

# Run like this
# kafka-console-consumer --zookeeper localhost:2181 --consumer.config ~/kafkatest/consumerconfig.txt --topic test-downloadbyphotoid | python copy_by_json_to_cassandra.py

if __name__ == '__main__':
    collection = "all_recent"
    print "collection: ", collection

    now = int(time.time())
    adayago = now - 24*3600
    while True:

        # now = int(time.time())
        # timeelapsesincelastca

        try:
            now = time.time()
            adayago = now - 24*3600


            query = dict(min_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(adayago)),
                         max_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(adayago+60*10)),
                        sort='date-posted-asc',
                        )

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.05)

            timeelapsed = int(time.time()) - now
            print "TIMEELAPSED (should be less than 5 mins): %d"%timeelapsed

            sleepfor = max(0,timeelapsed-60*5)
            print "Slept for %d seconds"%sleepfor
        except KeyboardInterrupt:
            raise
        except:
            pass
