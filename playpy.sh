#!/bin/bash

# Play agent.py against specified program
# Example:
# ./playpl.sh lookt 54321

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <player> <port>" >&2
  exit 1
fi

./servt -p $2          & sleep 0.1
python agent.py -p $2 & sleep 0.1
./$1     -p $2
