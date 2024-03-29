import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery

if __name__ == '__main__':
    collection = "geotagged"
    print "collection: ", collection

    now = int(time.time())

    initialdelay = 24*3600*365*10
    mindelay = 24*3600
    interval = 24*3600
    querytime = now - initialdelay - interval
    while True:

        # now = int(time.time())
        # timeelapsesincelastca

        try:
            # querytime = min(now - mindelay, querytime + interval)


            query = dict(min_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime)),
                         max_upload_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+2*interval)),
                         has_geo=1,
                        sort='date-posted-asc',
                        )

            print 'downloading', query['min_upload_date']

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.03)

            timeelapsed = int(time.time()) - now
            print "TIMEELAPSED (should be less than 5 mins): %d"%timeelapsed

            querytime += interval

            print 'waiting .',
            while querytime > time.time() - mindelay:
                print '.',
                time.sleep(5)
            print ''
            # sleepfor = max(0,timeelapsed-interval)
            # print "Slept for %d seconds"%sleepfor
        except KeyboardInterrupt:
            raise
        except:
            pass
