import time
import flickrapi
import wget
import os
import urllib
import errno
import tempfile
import shutil
import tarfile
import subprocess

from _configuration import flickr_api_key, flickr_api_secret

flickr = flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret)

import boto
conn = boto.connect_s3()
bucket = conn.get_bucket('inlivingcolor')


def GetSearchQueryAttrib(**kwargs):
    """
    Users the Flickr API to...

    {
      "photos": {        -+
        "page": 1,        |
        "pages": 79,      +---- Retrive this information
        "perpage": 100,   |     as a Python dictionary
        "total": "7861", -+
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
    return photos.attrib


def GetPhotoIDs_iter(page=None, max_number_of_pages=40, **kwargs):
    """
    - page : If a page number is specified, then return that page. If
             a page number is not specified, then return all pages.
    """


    # If a page number is specified, retreive results directly.
    if page is not None:

        photos = flickr.photos.search(page=page, **kwargs)[0]
        for p in photos:
            yield p.attrib['id']

    # If a page number is not specified, then recursively obtain results
    # by making a call to this generator for each page in the search.
    else:
        numberofpages = min(GetSearchQueryAttrib(**kwargs)['pages'], max_number_of_pages)


        for page in range(1,numberofpages+1):
            # print "Retreiving page %d"%page
            for photoid in GetPhotoIDs_iter(page=page, **kwargs):
                yield photoid

def GetPhotos_iter(page=None, **kwargs):
    """
    - page : If a page number is specified, then return that page. If
             a page number is not specified, then return all pages.

             Note that Flickr limits you to 4000 results
    """


    # If a page number is specified, retreive results directly.
    if page is not None:

        photos = flickr.photos.search(page=page, **kwargs)[0]
        for p in photos:
            yield p

    # If a page number is not specified, then recursively obtain results
    # by making a call to this generator for each page in the search.
    else:
        numberofpages = GetSearchQueryAttrib(**kwargs)['pages']

        for page in range(1,numberofpages+1):
            # print "Retreiving page %d"%page
            for p in GetPhotos_iter(page=page, **kwargs):
                yield p


def GetPhotoIDs_batch_iter(ctime_values, interval=60):
    for ctime in ctime_values:
        # print ctime
        min_taken_date = ctime
        max_taken_date = ctime+interval

        for photoid in GetPhotoIDs_iter(min_taken_date=min_taken_date, max_taken_date=max_taken_date):
            yield photoid




def GetMetaDataStrings(photoid=None):
    InfoJSON = flickr.photos.getInfo(photo_id=photoid, format="json")
    ExifJSON = flickr.photos.getExif(photo_id=photoid, format="json")
    return InfoJSON, ExifJSON


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def GetInfoAsJson(photoid):
    return flickr.photos.getInfo(photo_id=photoid, format="json")

def GetExifAsJson(photoid):
    return flickr.photos.getInfo(photo_id=photoid, format="json")

def GetPhotoAndMetaData(photoid):
    # photoid = photo.attrib['id']

    with tempfile.NamedTemporaryFile(delete=True) as f:
        urllib.urlretrieve(photoid2url(photoid), f.name)

        ImageJPG = f.read()

    return dict(imagejpg=ImageJPG,
                infojson=GetInfoAsJson(photoid),
                exifjson=GetExifAsJson(photoid))



def WriteFiles(path='', photoid=None):

    # path = os.path.join(path,)

    mkdir_p(os.path.join(path, photoid))

    urllib.urlretrieve(photoid2url(photoid), os.path.join(path, photoid, 'image.jpg'))

    InfoJSON = flickr.photos.getInfo(photo_id=photoid, format="json")
    ExifJSON = flickr.photos.getExif(photo_id=photoid, format="json")

    with open(os.path.join(path, photoid, 'info.json'), 'w+') as f:
        f.write(InfoJSON)

    with open(os.path.join(path, photoid, 'exif.json'), 'w+') as f:
        f.write(ExifJSON)

def GetColorClusteringMetadataFromJPG(jpgdata, ks=range(1,8), return_type='dict'):
    import tempfile
    import matplotlib.image as mpimg
    import numpy as np
    from scipy.cluster.vq import kmeans2
    import json

    from PIL import ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    try:

        with tempfile.NamedTemporaryFile() as f:
            f.write(jpgdata)
            img=mpimg.imread(f.name)

        imgflat = img.reshape(-1, 3)[::3]/256.0
#         imgflat = img.reshape(-1,3)[::50]/256.0*0+0.5+np.random.randn(imgflat.shape[0],img.shape[2])*0.0001

        output = {}

        for numberofcolors in ks:
            centroids,labels = kmeans2(imgflat,numberofcolors,iter=50)


            labelsums = np.array(map(lambda i: sum(labels==i),range(numberofcolors)))
            labelprobs = 1.0*labelsums / sum(labelsums)

            labelprobs, centroids = zip(*sorted(zip(labelprobs,centroids), reverse=True))


            output[numberofcolors] = dict(centroids={i+1:tuple(centroids[i]) for i in range(numberofcolors)},
                                                    probs={i+1:labelprobs[i] for i in range(numberofcolors)})

            output['maxk'] = numberofcolors

        return output
    except:
        return 'None'


def AlreadyDownloadedAndPreprocessed(collection, photoid):
    # change to something else, like cassandra

    keyname = os.path.join(collection, '_alreadydownloadedphotoids' , photoid,
                       'DOWNLOAD_AND_PREPROCESS_SUCCEEDED')

    key = bucket.get_key(keyname)

    if key is not None:
        return True
    else:
        return False


def WritePhotoAndMetaToS3(collection, photoid, jpgdata, metaplusjson, datebin):
    import matplotlib.image as mpimg


    # print os.path.join(collection, photoid, filename)

    # with tempfile.NamedTemporaryFile(delete=True) as f:
    #     f.write(photoandmetadict['imagejpg'])
    #     k = bucket.new_key(os.path.join(collection, photoid, 'image.jpg'))
    #     k.set_contents_from_filename(f.name)

    # k = bucket.new_key(os.path.join(collection, datebin, photoid, 'image.jpg'))
    # k.set_contents_from_string(jpgdata)
    # k.make_public()

    k = bucket.new_key(os.path.join(collection, datebin, photoid + '.jpg'))
    k.set_contents_from_string(jpgdata)
    k.make_public()

    k = bucket.new_key(os.path.join(collection, 'thumbs', photoid + '.jpg'))
    k.set_contents_from_string(jpgdata)
    k.make_public()

    k = bucket.new_key(os.path.join(collection, datebin, photoid + '-metaplus.json'))
    k.set_contents_from_string(metaplusjson)
    k.make_public()

    k = bucket.new_key(os.path.join(collection, datebin, photoid,
                       'DOWNLOAD_AND_PREPROCESS_SUCCEEDED'))
    k.set_contents_from_string("")

    k = bucket.new_key(os.path.join(collection, '_alreadydownloadedphotoids' , photoid,
                       'DOWNLOAD_AND_PREPROCESS_SUCCEEDED'))
    k.set_contents_from_string("")

    # k = bucket.new_key(os.path.join(collection, photoid,
    #                    'NEW'))
    k.set_contents_from_string("")





def photoid2getInfoResponse(photoid):
    """
    Returns the response (in LXML format) from the method flickr.photos.getInfo
    given a photoid. In JSON format it looks like
    {
      "photo": {
        "id": "16661925622",
        "secret": "914e0ab062",
        "server": "8657",
        "farm": 9,
        "dateuploaded": "1425048230",
        "license": "0",
        "safety_level": "0",
        "rotation": 0,
        "originalsecret": "3b5a302c95",
        "originalformat": "jpg",
        "owner": {
          "nsid": "131496460@N02",
          "username": "pannysong",
          "realname": "panny song",
          "location": "",
          "iconserver": "0",
          "iconfarm": 0,
          "path_alias": null
        },
        "title": {
          "_content": "IMG_9130"
        },
        "description": {
          "_content": ""
        },
        "dates": {
          "posted": "1425048230",
          "taken": "2010-11-30 16:08:37",
          "takengranularity": "0",
          "takenunknown": "0",
          "lastupdate": "1425446195"
        },
        "usage": {
          "candownload": 1,
          "canblog": 0,
          "canprint": 0,
          "canshare": 1
        },
        "tags": {
          "tag": [
          ]
        },
        "urls": {
          "url": [
            {
              "type": "photopage",
              "_content": "https:\/\/www.flickr.com\/photos\/131496460@N02\/16661925622\/"
            }
          ]
        },
      },
    }
    """

    p = flickr.photos.getInfo(photo_id=photoid)[0]
    return p


def photoid2url(photoid):
    p = flickr.photos.getInfo(photo_id=photoid)[0]
    return photo2url(p)

def photo2url(photo, urlformat="https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s_n.jpg"):
    return urlformat % photo.attrib

# def photo2url(photoid, urlformat="https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s.jpg"):
#     p = flickr.photos.getInfo(photo_id=photoid)[0]
#     return urlformat % p.attrib


if __name__ == '__main__':
    pass
    # WriteFiles(photoid='16661925622')
    # ctime_start = int(time.mktime(time.strptime("30-11-2010 00:00", "%d-%m-%Y %H:%M")))
    # ctime_length = 60
    # ctime_interval = 60
    # ctime_mod = 1
    # for photoid in GetPhotoIDs_batch_iter(range(ctime_start,
    #                                              ctime_start+ctime_length,
    #                                              ctime_interval*ctime_interval),
    #                                        interval=ctime_interval):
    #     print '.',


    # string =  WriteFilesToTar(photoid='2869316960')

    # with open("/tmp/test.tar",'w+b') as f:
    #     f.write(string)

    # output = GetPhotoAndMetaData(photoid='2869316960')
    # print output['ImageJPG']

