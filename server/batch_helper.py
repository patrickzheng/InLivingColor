from _configuration import CASSANDRA_KEYSPACE

import time
from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection

connection.setup(['127.0.0.1'], CASSANDRA_KEYSPACE)


def timeoflastrun(name, set_to_now):
    assert type(set_to_now) is bool

    class timeoflastruns(Model):
        name = columns.Text(primary_key=True)
        time = columns.Integer()

    from cqlengine.management import sync_table
    sync_table(timeoflastruns)

    if set_to_now is True:
        epoch_time_seconds = int(time.time())
        timeoflastruns.create(name=name, time=epoch_time_seconds)
        return epoch_time_seconds
    else:
        try:
            return timeoflastruns.objects(name=name).get()['time']
        except:
            print "First time running batch script. Returning the epoch."
            return 0

