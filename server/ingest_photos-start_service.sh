

kafka-console-consumer --zookeeper localhost:2181 --consumer.config consumerconfig.txt --topic test-downloadbyphotoid | python download_preprocess_store.py
