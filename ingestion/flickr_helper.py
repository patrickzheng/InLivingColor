import time
import flickrapi
import wget

from flickrapi_conf import api_key, api_secret

flickr = flickrapi.FlickrAPI(api_key, api_secret)


def GetNumberOfPagesForSearchQuery(**kwargs):
    """
    Users the Flickr API to...

    {
      "photos": {
        "page": 1,
        "pages": 79, <---------------------Number of Pages
        "perpage": 100,
        "total": "7861",
        "photo": [
          {
            "id": "16717306373",
            "owner": "130406501@N08",
            "secret": "c074780d16",
            "server": "8714",
            "farm": 9,
            "title": "DSC_8627",
            "ispublic": 1,
            "isfriend": 0,
            "isfamily": 0
          },

          .....
          {
            "id": "16370206483",
            "owner": "131105760@N07",
            "secret": "db0a211487",
            "server": "8693",
            "farm": 9,
            "title": "New Book by Fern Michaels Added",
            "ispublic": 1,
            "isfriend": 0,
            "isfamily": 0
          }
        ]
      },
      "stat": "ok"
    }
    """
    photos = flickr.photos.search(**kwargs)[0]
    return int(photos.attrib['pages'])

def GetPhotoIDs_iter(**kwargs):
    numberofpages = GetNumberOfPagesForSearchQuery(**kwargs)

    for i in range(1,numberofpages+1):
    # for i in range(1,2):
        photos = flickr.photos.search(**kwargs)[0]

        for p in photos:
            yield p.attrib['id']

def GetPhotoIDs_batch_iter(ctime_values, interval=60):
    for ctime in ctime_values:
        print ctime
        min_taken_date = ctime
        max_taken_date = ctime+interval

        for photo_id in GetPhotoIDs_iter(min_taken_date=min_taken_date, max_taken_date=max_taken_date):
            yield photo_id




def GetMetaDataStrings(photo_id=None):
    InfoJSON = flickr.photos.getInfo(photo_id=photo_id, format="json")
    ExifJSON = flickr.photos.getExif(photo_id=photo_id, format="json")
    return InfoJSON, ExifJSON

def WriteFiles(directory='~/', photo_id=''):
    # service_name='Flickr'


    wget.download(photo_id2url(photo_id))

    InfoJSON = flickr.photos.getInfo(photo_id=photo_id, format="json")
    ExifJSON = flickr.photos.getExif(photo_id=photo_id, format="json")

    with open('Info.json', 'w+') as f:
        f.write(InfoJSON)

    with open('Exif.json', 'w+') as f:
        f.write(ExifJSON)


def photo_id2url(photo_id, urlformat="https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s.jpg"):
    p = flickr.photos.getInfo(photo_id=photo_id)[0]
    return urlformat % p.attrib

if __name__ == '__main__':
    # WriteFiles(photo_id='16661925622')
    ctime_start = int(time.mktime(time.strptime("30-11-2010 00:00", "%d-%m-%Y %H:%M")))
    ctime_length = 60
    ctime_interval = 60
    ctime_mod = 1
    for photo_id in GetPhotoIDs_batch_iter(range(ctime_start,
                                                 ctime_start+ctime_length,
                                                 ctime_interval*ctime_interval),
                                           interval=ctime_interval):
        print '.',


