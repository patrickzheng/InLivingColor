import sys
import time
import json

from flickr_helper import GetPhotoAndMetaData, WritePhotoAndMetaToS3, GetColorClusteringMetadataFromJPG

######################################################
# CQL ROCKS
from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection

# Define a model
class flickrmetaplus(Model):
    collection = columns.Text(primary_key=True)
    photoid = columns.Text(primary_key=True)
    metaplusjson = columns.Text()
    def __repr__(self):
        return '<sourceoftruth: collection=%s photoid=%s>' % (self.collection, self.photoid)

connection.setup(['127.0.0.1'], "inlivingcolor")

from cqlengine.management import sync_table
sync_table(flickrmetasot)




def CopyByJsonToCassandra(jsoninput):

    collection = json.loads(jsoninput)['collection']  # 4='value'
    photoid = json.loads(jsoninput)['photoid']  # 4='value'

    # TODO, replace this checking with checking S3, the source of truth after all
    if flickrmetasot.objects(collection=collection,
                         photoid=photoid).count() > 0:
        print "Already downloaded %s/%s" % (collection, photoid)
        return


# bucket.get_key(os.path.join(collection, binstr, photoid, 'DOWNLOAD_AND_WRITE_SUCCEEDED'))
# get_key()
    clusters = GetColorClusteringMetadataFromJPG(photoandmetadict['imagejpg'])
    infojson = json.loads(photoandmetadict['infojson'])['photo']
    exifjson = json.loads(photoandmetadict['exifjson'])['photo']
    metaplusjson = dict(clusters=clusters,
                        infojson=infojson,
                        exifjson=exifjson)

    # print collection, photoid, photoandmetadict['ImageJPG'][:10]
    # TODO: add more checks here

    forcassandra = dict(
            collection=collection,
            photoid=photoid,
            metaplusjson=json.dumps(metaplusjson),
            )
    flickrmetasot.create(**forcassandra)

    print "Sent to Cassandra %s/%s" % (collection, photoid)

    WritePhotoAndMetaToS3(collection, photoid, photoandmetadict)

    print "Copied to S3 to Cassandra %s/%s" % (collection, photoid)


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

                try:
                    CopyByJsonToCassandra(buff[:-1])
                except KeyboardInterrupt:
                    raise
                except:
                    print 'Error processing msg: ', buff[:-1]
                    pass
                buff = ''
                k = k + 1

    except KeyboardInterrupt:
       sys.stdout.flush()
       pass
    print k
