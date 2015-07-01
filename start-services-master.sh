#!/bin/bash


################################################################################
# FLASK


SESSION=flask
COMMAND="python /home/ubuntu/InLivingColor/website/flask_website.py"

tmux kill-session -t $SESSION
tmux new-session -s $SESSION -n bash -d
tmux send-keys -t $SESSION:$ID "$COMMAND" C-m



################################################################################
# IPYTHON


SESSION=ipython
COMMAND="cd /home/ubuntu/ && ipython notebook"

tmux kill-session -t $SESSION
tmux new-session -s $SESSION -n bash -d
tmux send-keys -t $SESSION:$ID "$COMMAND" C-m


# done

# tmux attach -t $SESSION
