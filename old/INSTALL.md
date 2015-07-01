Install
=======


1. Install CDH (http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cm_ig_install_path_a.html).

For Ubuntu: wget http://archive.cloudera.com/cm5/installer/latest/cloudera-manager-installer.bin

Make sure you install Kafka

When it is installed, go to the HDFS sessions and disable "Check HDFS" permissions.

Restart cluster


2. Install Anaconda

wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.2.0-Linux-x86_64.sh

sudo ln -fs /home/ubuntu/anaconda/bin/python /usr/bin/python
sudo ln -fs /home/ubuntu/anaconda/bin/ipython /usr/bin/ipython
sudo ln -fs /home/ubuntu/anaconda/bin/pip /usr/bin/pip


3. Install a bunch of stuff
sudo apt-get update
sudo apt-get -y install git gcc maven
sudo apt-get install openjdk-7-jdk


4. Python install

sudo pip install blist cqlengine wget kafka-python flickrapi snakebite

5. setup iPython


ipython profile create default

# Configuration file for ipython-notebook.

c = get_config()

c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8880

PWDFILE='/home/ubuntu/.ipython/profile_default/nbpasswd.txt'
c.NotebookApp.password = open(PWDFILE).read().strip()


python -c 'from IPython.lib import passwd; print passwd()' > ~/.ipython/profile_default/nbpasswd.txt




6 Get cassandra

https://sites.google.com/a/insightdatascience.com/dataengineering/devsetups/cassandra-dev

git cleon https://github.com/Stratio/cassandra-lucene-index


mvn clean -Dmaven.test.skip=true  package  -Ppatch -Dcassandra_home=/usr/local/cassandra/

cassandra

7 create keyspace


cqlsh> create KEYSPACE  inlivingcolor with replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };







8. echo .profile to put in your data








   19  sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose



#I GOT IT!!!
kafka-console-producer --broker-list ip-172-31-6-183:9092 --topic testtopic3 --new-producer

kafka-console-consumer --zookeeper 172.31.6.182:2181 --consumer.config consumerconfig.txt --topic testtopic3


group.id=theonlygroup




# Install pyspark cassandra https://github.com/Parsely/pyspark-cassandra
# Install cassandra-driver

http://planetcassandra.org/getting-started-with-cassandra-and-python/




# get rid of warnings@
sudo pip install pyopenssl ndg-httpsclient pyasn1

sudo pip install blist




git clone
https://github.com/Parsely/pyspark-cassandra

mvn clean package


------------------------------


run each time you reboot

sudo $REDIS_HOME/src/redis-server $REDIS_HOME/redis.conf &
cassandra
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

install stratio





Install with your favorite package manager

Latest Release
--------------
Pip:

.. code:: bash

    pip install kafka-python

Releases are also listed at https://github.com/mumrah/kafka-python/releases


Bleeding-Edge
-------------

.. code:: bash

    git clone https://github.com/mumrah/kafka-python
    pip install ./kafka-python

Setuptools:

.. code:: bash

    git clone https://github.com/mumrah/kafka-python
    easy_install ./kafka-python

Using `setup.py` directly:

.. code:: bash

    git clone https://github.com/mumrah/kafka-python
    cd kafka-python
    python setup.py install


Optional Snappy install
-----------------------

Install Development Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download and build Snappy from http://code.google.com/p/snappy/downloads/list

Ubuntu:

.. code:: bash

    apt-get install libsnappy-dev

OSX:

.. code:: bash

    brew install snappy

From Source:

.. code:: bash

    wget http://snappy.googlecode.com/files/snappy-1.0.5.tar.gz
    tar xzvf snappy-1.0.5.tar.gz
    cd snappy-1.0.5
    ./configure
    make
    sudo make install

Install Python Module
^^^^^^^^^^^^^^^^^^^^^

Install the `python-snappy` module

.. code:: bash

    pip install python-snappy
