import sys
import time
import json

from flickr_helper import GetPhotoAndMetaData

######################################################
# CQL ROCKS
from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection

# Define a model
class flickrsot(Model):
    collection = columns.Text(primary_key=True)
    photoid = columns.Text(primary_key=True)
    imagejpg = columns.Blob()
    infojson = columns.Text()
    exifjson = columns.Text()
    def __repr__(self):
        return '<sourceoftruth: collection=%s photoid=%s %d-byte jpg>' % (self.collection, self.photoid, len(self.imagejpg))

connection.setup(['127.0.0.1'], "inlivingcolor")

from cqlengine.management import sync_table
sync_table(flickrsot)

def CopyByJsonToCassandra(jsoninput):

    collection = json.loads(jsoninput)['collection']  # 4='value'
    photoid = json.loads(jsoninput)['photoid']  # 4='value'


    if flickrsot.objects(collection=collection,
                         photoid=photoid).count() > 0:
        print "Already downloaded %s/%s" % (collection, photoid)
        return


    rsp = GetPhotoAndMetaData(photoid)
    # print collection, photoid, rsp['ImageJPG'][:10]

    forcassandra = dict(
            collection=collection,
            photoid=photoid,
            imagejpg=rsp['ImageJPG'],
            infojson=rsp['InfoJSON'],
            exifjson=rsp['ExifJSON'],
            )
    flickrsot.create(**forcassandra)

    print "Sent to Cassandra %s/%s" % (collection, photoid)


if __name__ == '__main__':
    # Unbuffered reading of the stream
    k = 0

    try:
        buff = ''

        while True:
            buff += sys.stdin.read(1)
            if buff.endswith('\n'):

                try:
                    CopyByJsonToCassandra(buff[:-1])
                except:
                    pass
                buff = ''
                k = k + 1

    except KeyboardInterrupt:
       sys.stdout.flush()
       pass
    print k
