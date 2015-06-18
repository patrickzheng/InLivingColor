#!/bin/bash

NUM_SPAWNS=$1

tmux new-session -s $SESSION -n bash -d

COMMAND=kafka-console-consumer --zookeeper localhost:2181 --consumer.config consumerconfig.txt --topic test-downloadbyphotoid | python download_preprocess_store.py

for ID in `seq 1 $NUM_SPAWNS`;
do
    echo $ID
    tmux new-window -t $ID
    tmux send-keys -t $SESSION:$ID '$COMMAND' C-m
done
