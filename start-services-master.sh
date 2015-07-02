#!/bin/bash


################################################################################
# FLASK


SESSION=flask
COMMAND="python /home/ubuntu/InLivingColor/website/flask_website.py"

tmux kill-session -t $SESSION
tmux new-session -s $SESSION -n bash -d
tmux send-keys -t $SESSION:$ID "$COMMAND" C-m

sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

################################################################################
# IPYTHON


SESSION=ipython
COMMAND="cd /home/ubuntu/ && ipython notebook"

tmux kill-session -t $SESSION
tmux new-session -s $SESSION -n bash -d
tmux send-keys -t $SESSION:$ID "$COMMAND" C-m


# done

# tmux attach -t $SESSION
