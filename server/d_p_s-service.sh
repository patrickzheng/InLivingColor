

kafka-console-consumer --zookeeper localhost:2181 --consumer.config consumerconfig.txt --topic downloadpreprocessandstore | python download_preprocess_store.py
