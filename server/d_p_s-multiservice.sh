#!/bin/bash

NUM_SPAWNS=$1
SESSION=downloading

tmux kill-session -t $SESSION
# tmux new-session -s downloading -n bash -d
tmux new-session -s $SESSION -n bash -d

COMMAND=". d_p_s-multiservice.sh"
# COMMAND='sleep 5'

# tmux send-keys -t $SESSION:$ID '$COMMAND' C-m

for ID in `seq 1 $NUM_SPAWNS`;
do
    # echo $ID
    tmux new-window -t $SESSION
    tmux send-keys -t $SESSION:$ID "$COMMAND" C-m
done

tmux attach -t $SESSION
