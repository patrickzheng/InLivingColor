"""

python flickr_querytophotoids.py dict\(text=\'yosemite\',content_type=1,has_geo=0,is_commons=1\) | kafka-console-producer --broker-list ip-172-31-6-183:9092 --topic testtopic3 --new-producer
# https://www.flickr.com/services/api/flickr.photos.search.html
# user_id (Optional)
# tags (Optional)
# tag_mode (Optional)
# text (Optional)
# min_upload_date (Optional)
# max_upload_date (Optional)
# min_taken_date (Optional)
# max_taken_date (Optional)
# license (Optional)
# sort (Optional)
# privacy_filter (Optional)
# bbox (Optional)
# accuracy (Optional)
# safe_search (Optional)
# Safe search setting:
# 1 for safe.
# 2 for moderate.
# 3 for restricted.
# (Please note: Un-authed calls can only see Safe content.)
# content_type (Optional)
# Content Type setting:
# 1 for photos only.
# 2 for screenshots only.
# 3 for 'other' only.
# 4 for photos and screenshots.
# 5 for screenshots and 'other'.
# 6 for photos and 'other'.
# 7 for photos, screenshots, and 'other' (all).
# machine_tags (Optional)
# group_id (Optional)
# contacts (Optional)
# woe_id (Optional)
# place_id (Optional)
# media (Optional)
# has_geo (Optional)
# lat (Optional)
# lon (Optional)
# radius (Optional)
# radius_units (Optional)
# is_commons (Optional)
# extras (Optional)
# per_page (Optional)
# page (Optional)

"""

from flickr_helper import GetPhotoIDs_iter
import sys

if __name__ == '__main__':
    # For instance ["dict(text='yosemite',content_type=1,has_geo=0,is_commons=1)"]
    args = sys.argv[1:]

    # args = ["dict(text='yosemite',content_type=1,has_geo=0,is_commons=1)"] # For testing

    query = eval("".join(args))

    for photo_id in GetPhotoIDs_iter(**query):
        print photo_id
