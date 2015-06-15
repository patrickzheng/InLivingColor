Install
=======




    4  wget http://archive.cloudera.com/cm5/installer/latest/cloudera-manager-installer.bin
    5  chmod u+x cloudera-manager-installer.bin
    6  sudo ./cloudera-manager-installer.bin


   19  sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose


sudo apt-get install git


sudo apt-get install python-setuptools
#easy_install pip, don't use apt-get
sudo easy_install pip


git clone https://github.com/mumrah/kafka-python
sudo pip install ./kafka-python




add to parcel repository list
http://archive-primary.cloudera.com/kafka/parcels/latest/
or just download to/opt/cloudera/parcel-repo$


#I GOT IT!!!
kafka-console-producer --broker-list ip-172-31-6-183:9092 --topic testtopic3 --new-producer

kafka-console-consumer --zookeeper 172.31.6.182:2181 --consumer.config consumerconfig.txt --topic testtopic3


group.id=theonlygroup




# Install pyspark cassandra https://github.com/Parsely/pyspark-cassandra
# Install cassandra-driver

http://planetcassandra.org/getting-started-with-cassandra-and-python/










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
