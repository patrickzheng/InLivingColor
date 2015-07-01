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

InLivingColor uses a distributed system to download photographs from Flickr...


## Batch Processing

Under Construction.


## API Calls

Under Construction.


##

Run Elasticsearch Cassanda, Flask
