import time
from ingest_photos import QueueIngestionByFlickrAPISearchQuery
import numpy as np

if __name__ == '__main__':
    collection = "geotagged"
    print "collection: ", collection

    now = int(time.time())

    interval = -3600*24*1
    # interval = 3600*24
    # querytime = now - initialdelay - interval
    querytime = time.mktime((2011,1,1,14,0,0,0,0,0))
    while True:

        if querytime < time.mktime((2008,1,1,0,0,0,0,0,0)):
            querytime = time.mktime((2011,1,1,14,0,0,0,0,0))
        else:
            querytime += interval

        try:


            # query = dict(min_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime)),
            query = dict(min_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+np.random.randint(-3600*6,3600*6))),
                         max_taken_date=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(querytime+3600*2)),
                         has_geo=1,
                         # tags='fields,leaves,trees,grass,hills',
                         # woe_id='2347563', # California
                         # is_commons='True',
                        sort='date-taken-asc',
                        )

            print 'downloading', query['min_taken_date'], 'time ', querytime

            QueueIngestionByFlickrAPISearchQuery(collection=collection, query=query, delay=0.02, limit_at_n=150)

        except KeyboardInterrupt:
            raise
        except:
            pass
