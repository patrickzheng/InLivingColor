import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery

if __name__ == '__main__':
    collection = "geotagged"
    print "collection: ", collection

    now = int(time.time())

    # initialdelay = 24*3600*10
    # mindelay = 24*3600
    interval = -3600*6
    # interval = 3600*24
    # querytime = now - initialdelay - interval
    querytime = time.mktime((2015,1,1,0,0,0,0,0,0))
    while True:

        if querytime < time.mktime((2014,1,1,0,0,0,0,0,0)):
            querytime = time.mktime((2015,1,1,0,0,0,0,0,0))
        else:
            querytime += interval

        try:


            query = dict(min_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime)),
                         max_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+interval)),
                         has_geo=1,
                         # is_commons='True',
                        sort='date-taken-asc',
                        )

            print 'downloading', query['min_taken_date'], 'time ', querytime

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.03, limit_at_n=500)

            # timeelapsed = int(time.time()) - now
            # print "TIMEELAPSED (should be less than 5 mins): %d"%timeelapsed


            print 'waiting .',
            while querytime > time.time() - mindelay:
                print '.',
                time.sleep(5)
            print ''

        except KeyboardInterrupt:
            raise
        except:
            pass
