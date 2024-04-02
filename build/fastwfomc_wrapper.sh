#!/usr/bin/env sh

cd fastwfomc
source virtualenvwrapper.sh
workon fastwfomc
for ((i=1; i<=$1; i++)); do
    echo "Domain size: $i"
    ulimit -t $3 -c 0 && /usr/bin/time -f "Elapsed: %e" python wrapper.py $2 $i || exit 1
done
