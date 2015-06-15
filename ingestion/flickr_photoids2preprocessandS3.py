"""
cat file.txt | tee >(pbcopy) >(do_stuff) >(do_more_stuff) | grep errors

kafka-console-consumer --zookeeper 172.31.6.182:2181 --consumer.config consumerconfig.txt --topic testtopic3 | flickr_photoids2preprocessandS3.py
"""

import fileinput



if __name__ == "__main__":

    for line in fileinput.input():
        try:
            photo = photoid2getInfoResponse(photoid)

            ####################### WRITE PHOTOID TO FILE
            # write to cassandra


            ####################### DOWNLOAD PHOTO
            url = photo2url(photo)

            # Get date taken from Flickr response in the form "2011-11-11 11:20:13"
            datetakenstr = photo.find('dates').attrib['taken']
            datetakenstr_normalized = datetakenstr[:8]

            print 'PhotoID: %s, %s' % (photoid,url)
            print 'Date Taken: %s' % (datetakenstr)

            fullpath = os.path.join('Flickr', datetakenstr_normalized, photoid)
            print "Transferring to S3: %s" % fullpath
            WriteFilesToS3(path=fullpath, photo_id=photoid)



        except FlickrError as exc: #
            print "Error with photo_id %s (might not exist)"%photoid
            pass

