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

    return dict(ImageJPG=ImageJPG,
                InfoJSON=GetInfoAsJson(photoid),
                ExifJSON=GetExifAsJson(photoid))



def WriteFiles(path='', photoid=None):

    # path = os.path.join(path,)

    mkdir_p(os.path.join(path, photoid))

    urllib.urlretrieve(photoid2url(photoid), os.path.join(path, photoid, 'Image.jpg'))

    InfoJSON = flickr.photos.getInfo(photo_id=photoid, format="json")
    ExifJSON = flickr.photos.getExif(photo_id=photoid, format="json")

    with open(os.path.join(path, photoid, 'Info.json'), 'w+') as f:
        f.write(InfoJSON)

    with open(os.path.join(path, photoid, 'Exif.json'), 'w+') as f:
        f.write(ExifJSON)


def WriteFilesToTar(photoid=None):

    tempdir = tempfile.mkdtemp()
    # print tempdir

    WriteFiles(path=tempdir, photoid=photoid)

    with tempfile.NamedTemporaryFile(delete=True) as f:
        # print f.name

        command = ['tar', '-cf', f.name, '-C', tempdir, '.']
        # print command

        subprocess.call(command)

        output = f.read()

    shutil.rmtree(tempdir)

    return output


def WriteFilesToS3(path='', photoid=None):

    import boto
    conn = boto.connect_s3()
    bucket = conn.get_bucket('insight-brian-inlivingcolor')
    # import urllib2

    tempdir = tempfile.mkdtemp()
    # print tempdir
    WriteFiles(path=tempdir, photoid=photoid)

    filenames = ['Info.json', 'Exif.json', 'Image.jpg']

    for filename in filenames:

        k = bucket.new_key(os.path.join(path, filename))
        k.set_contents_from_filename(os.path.join(tempdir, filename))

    shutil.rmtree(tempdir)
    # import urllib2
    # import contextlib

    # search_query = photoid2url(photoid)

    # with contextlib.closing(urllib.urlopen(search_query)) as x:
    #    ...use x at will here...
    # try:

    #     sf = urllib2.urlopen(search_query)
    #     search_soup = BeautifulSoup.BeautifulStoneSoup(sf.read())
    # except urllib2.URLError, err:
    #     print(err.reason)
    # finally:
    #     try:
    #         sf.close()
    #     except NameError:
    #         pass

    # path = os.path.join(path,)
    # Create folder in S3
    # print os.path.join(path)+'/'
    # k = bucket.new_key(os.path.join(path)+'/')

    # # mkdir_p(path)

    # # wget.download(photoid2url(photoid), out=os.path.join(path, 'Image.jpg'))
    # urllib.urlretrieve(photoid2url(photoid), os.path.join(path, 'Image.jpg'))


    # # Write getInfo information to S3
    # resp_str = flickr.photos.getInfo(photo_id=photoid, format="json")
    # k = bucket.new_key(os.path.join(path, 'Info.json'))
    # k.set_contents_from_string(resp_str)

    # # Write getExif information to S3
    # resp_str = flickr.photos.getExif(photo_id=photoid, format="json")
    # k = bucket.new_key(os.path.join(path, 'Info.json'))
    # k.set_contents_from_string(resp_str)



    # with open(os.path.join(path, 'Info.json'), 'w+') as f:
    #     f.write(InfoJSON)

    # with open(os.path.join(path, 'Exif.json'), 'w+') as f:
    #     f.write(ExifJSON)



# def WriteFiles_AppendTimeStamp(path='', photoid=None):


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

def photo2url(photo, urlformat="https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s.jpg"):
    return urlformat % photo.attrib

# def photo2url(photoid, urlformat="https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s.jpg"):
#     p = flickr.photos.getInfo(photo_id=photoid)[0]
#     return urlformat % p.attrib

if __name__ == '__main__':
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

    output = GetPhotoAndMetaData(photoid='2869316960')
    print output['ImageJPG']

