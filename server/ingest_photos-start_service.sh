

kafka-console-consumer --zookeeper localhost:2181 --consumer.config consumerconfig.txt --topic test-downloadbyphotoid | python copy_by_json_to_cassandra.py
