# InLivingColor

[http://The.InLivingColor.website](http://The.InLivingColor.website)

[Slideshow](http://inlivingcolor.website/static/slideshow/index.html)

InLivingColor is a data platform for exploring and analyzing the colors of
the world around by the use of unsupervised machine learning.
It is completely open-source and uses the following technologies:

- Apache Kafka
- Python / SciPy
- Amazon S3
- Spark
- Apache Cassandra
- Elastic Search
- Flask
- HighMaps

## The InLivingColor Website

![](https://github.com/rhymeswithlion/InLivingColor/blob/master/images/titlepage.png?raw=true)

InLivingColor.website is currently downloading (as of July 1, 2015) and analyzing photos from Flickr. These photos provide the data which drive the following components of InLivingColor:

- _ColorSearch_: Allows users to search by color.

![](https://github.com/rhymeswithlion/InLivingColor/blob/master/images/colorsearch.png?raw=true)

- _ColorMap_: Currently shows the number of photos that have been processed in different counties of the United States. (As you can see in the images above, the website is not just indexing the U.S., however.)

![](https://github.com/rhymeswithlion/InLivingColor/blob/master/images/colormap.png?raw=true)

## InLivingColor InANutshell

![](https://github.com/rhymeswithlion/InLivingColor/blob/master/images/datapipeline.png?raw=true)

InLivingColor ingests photos along with their metadata by using Python and
Kafka (more later). Upon ingestion, photos are anaylzed for their color content
using a k-means algorithm. Each record (containing a photo, its metadata, and
the color content data) is stored on S3. Spark then takes these records and
creates a number of batch-views, using both Elastic Search (for the color
search) as well as Cassandra (for the geographical/temporal aggregates). These
databases are then made accessable via an API using Flask, which the webpage
uses and accesses using JavaScript.


## How to Download Millions of Photos from Flickr

![](https://github.com/rhymeswithlion/InLivingColor/blob/master/images/ingestion.png?raw=true)

InLivingColor uses a distributed system to download photographs from Flickr. For instance, the
script `ingest_photos_continuously_2014.py` attempts to download as many photoid as possible
from 2014. There are hundreds of millions of them, however, so it really attempts to download
a uniformly-distributed portion of those photos. `ingest_photos_continuously_2014.py` then
sends these `photoids` in a Kafka message to any number of consumers, started by the
`d_p_s-multiservice.sh` script which allows you to run numerous processes on a single machine
using tmux windows (i.e., `./d_p_s-multiservice.sh 5` will open up 5 of them). These
consumers then download the JPEGs of the photos, as well as any meta data that Flickr has,
preprocesses the photos for their color information, and then uploads these enriched JSON
records to S3 (the images are also included in Base64 as PySpark currently does not enjoy
accessing binary files on S3).


## Batch Processing

`batch_hourly.sh` runs all the batch processes, and although it is named "hourly" it can be
used to rebuild all the intermediate batch steps and populate the Cassandra and Elasticsearch
databases. Subsequently, it can be run hourly for incremental updates. Now, `batch_hourly.sh`
calls the following:

-`python batch_hourly_1_aggregate.py` aggregates the small files created by the processes
that download, preprocess, and store the images/metadata. This is the step of the batch
process that is the most difficult, for if the hourly download bins have many files
this step may take several minutes. In the future it may be better to have the individual
processes route these messages back to Kafka and use Secor to bundle them into nicely-sized
files. The benefit of pushing the small files to S3 is that they are never queued anywhere,
and we we take advantage of S3's excellent availablility. On the other hand, sending them
back to Kafka would allow us to use Kafka's "Pub-Sub" capabilities to also send a real-time
stream to SparkStreaming.

-`python batch_hourly_prepare_colorsearch.py` takes the aggregated files on S3, extracts the
fields needed for the color search, saves those intermediate files back to S3, and then
uploads the data to Elasticsearch.

-`python batch_hourly_prepare_counts.py` takes the aggregated files on S3, runs a map-reduce
job to perform counts at 5 levels of geographic granularity and 3 levels of temporal
granularity (actually, the cartesian product, so 15). This is calculated for each hourly
download bin and stored on S3. The complete reduction is then handled by incorporating all
of these prereduced results.
