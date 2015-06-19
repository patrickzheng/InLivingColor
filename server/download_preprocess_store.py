import sys
import time
import json

from _configuration import S3_BUCKET

from flickr_helper import GetPhotoAndMetaData
from flickr_helper import WritePhotoAndMetaToS3
from flickr_helper import AlreadyDownloadedAndPreprocessed
from flickr_helper import GetColorClusteringMetadataFromJPG


######################################################
# CQL ROCKS
from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection

# Define a model
# class flickrmetaplus(Model):
#     collection = columns.Text(primary_key=True)
#     photoid = columns.Text(primary_key=True)
#     metaplusjson = columns.Text()
#     def __repr__(self):
#         return '<sourceoftruth: collection=%s photoid=%s>' % (self.collection, self.photoid)

# connection.setup(['127.0.0.1'], "inlivingcolor")

# from cqlengine.management import sync_table
# sync_table(flickrmetaplus)


# import boto
# conn = boto.connect_s3()
# bucket = conn.get_bucket(S3_BUCKET)



def DownloadPreprocessAndStore(jsoninput):

    collection = json.loads(jsoninput)['collection']  # 4='value'
    photoid = json.loads(jsoninput)['photoid']  # 4='value'

    # TODO, replace this checking with checking S3, the source of truth after all
    # if flickrmetaplus.objects(collection=collection,
    #                      photoid=photoid).count() > 0:
    #     print "Already downloaded %s/%s" % (collection, photoid)
    #     return

    if AlreadyDownloadedAndPreprocessed(collection, photoid) is True:
        print "Already downloaded %s/%s" % (collection, photoid)
        return

# bucket.get_key(os.path.join(collection, binstr, photoid, 'DOWNLOAD_AND_WRITE_SUCCEEDED'))
# get_key()
    photoandmetadict = GetPhotoAndMetaData(photoid)

    clusters = GetColorClusteringMetadataFromJPG(photoandmetadict['imagejpg'])
    infodict = json.loads(photoandmetadict['infojson'])['photo']
    exifdict = json.loads(photoandmetadict['exifjson'])['photo']
    metaplusjson = json.dumps(dict(collection=collection,
                                   photoid=photoid,
                                   secret=(int(photoid)*13) % 100,
                                   clusters=clusters,
                                   info=infodict,
                                   exif=exifdict,
                                   ))

    # print collection, photoid, photoandmetadict['ImageJPG'][:10]
    # TODO: add more checks here, see if the data we need is here

    # forcassandra = dict(
    #         collection=collection,
    #         photoid=photoid,
    #         metaplusjson=metaplusjson,
    #         )
    # flickrmetaplus.create(**forcassandra)

    # print "Sent to Cassandra %s/%s" % (collection, photoid)

    WritePhotoAndMetaToS3(collection,
                          photoid,
                          photoandmetadict['imagejpg'],
                          metaplusjson
                          )

    print "Copied to S3 %s/%s" % (collection, photoid)


if __name__ == '__main__':


    # Unbuffered reading of the stream. Yes, this code is necessary, because
    # python's "input files" does not read continuously, rather only when
    # the pipe closes
    k = 0

    try:
        buff = ''

        while True:
            buff += sys.stdin.read(1)
            if buff.endswith('\n'):

                DownloadPreprocessAndStore(buff[:-1])
                # try:
                #     DownloadPreprocessAndStore(buff[:-1])
                # except KeyboardInterrupt:
                #     raise
                # except:
                #     print 'Error processing msg: ', buff[:-1]
                #     pass
                buff = ''
                k = k + 1

    except KeyboardInterrupt:
       sys.stdout.flush()
       pass
    print k
