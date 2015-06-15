# Run this file to install InLivingColor on a cluster

# Tasks that must be done

# Install Kafka
# Install Cassandra
# Setup iPython Notebook
# http://blog.cloudera.com/blog/2014/08/how-to-use-ipython-notebook-with-apache-spark/

ipython profile create pyspark

python -c 'from IPython.lib import passwd; print passwd()' > ~/.ipython/profile_pyspark/nbpasswd.txt

echo "

# -------------------------
# Inserted by InLivingColor

c = get_config()

c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8880

import os
PWDFILE='~/.ipython/profile_pyspark/nbpasswd.txt'
c.NotebookApp.password = open(os.path.expanduser(PWDFILE)).read().strip()
c.NotebookManager.notebook_dir = u'/home/ubuntu/InLivingColor/server'

" > ~/.ipython/profile_pyspark/ipython_notebook_config.py

tmux new-session -s iPython -n bash -d
tmux send-keys -t iPython 'ipython notebook --profile=pyspark' C-m



##########################
# If you don't like the SSL warning


sudo pip install pyopenssl ndg-httpsclient pyasn1

# then in python
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# https://github.com/jupyter/notebook

