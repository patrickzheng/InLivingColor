from time import mktime, strptime, strftime, gmtime
from flickr_helper import GetPhotoIDs_iter, WriteFiles, GetSearchQueryAttrib
import os
import errno
# import urllib3
# urllib3.disable_warnings()

def DownloadFlickrImagesAndMetaData(path='', **kwargs):
    total = int(GetSearchQueryAttrib(**kwargs)['total'])

    for i, photo_id in enumerate(GetPhotoIDs_iter(**kwargs)):

        fullpath = os.path.join(path, photo_id)

        # try:
        #     os.makedirs(fullpath)

        # except OSError as exc: # Python >2.5
        #     if exc.errno == errno.EEXIST and os.path.isdir(path):
        #         print "[%03d/%d] Already exists "%(i,total), fullpath
        #         continue
        #     else:
        #         raise

        print "[%03d/%d] Downloading to "%(i,total), fullpath


        WriteFiles(path=fullpath, photo_id=photo_id)




if __name__ == '__main__':

    hour = "11-11-2011_0000"

    starttime = int(mktime(strptime(hour, "%d-%m-%Y_%H%M")))


    for min_taken_date in range(starttime,starttime+3600):
        timestamp = strftime("%d-%m-%Y_%H%M%S", gmtime(min_taken_date))
        query = dict(min_taken_date=min_taken_date, max_taken_date=min_taken_date+60)
        DownloadFlickrImagesAndMetaData(path=os.path.join('/tmp/InlivingColor/Flickr',timestamp), **query)
        # numberofminutes = 60
        # ctime_interval = 60
        # ctime_mod =
        # for photo_id in GetPhotoIDs_batch_iter(range(ctime_start,
        #                                              ctime_start+ctime_length,
        #                                              ctime_interval*ctime_interval),
        #                                        interval=ctime_interval):
        #     os
        #     print '.',
