#!/usr/bin/env sh

cd ../deps/Forclift
for ((i=1; ; i++)); do
    echo "Domain size: $i"
    sed -i "s/\.\.\.,[[:digit:]]\+/\.\.\.,$i/g" $1
    output=$(ulimit -t $2 -c 0 && /usr/bin/time -f "Elapsed: %e" java -jar target/scala-2.11/crane-assembly-1.0.jar -z --format-in mln $1 2>&1)
    echo $output
    if [[ $output == *"Infinity"* ]] || [[ $output == *"Cannot"* ]] || [[ $output == *"Exception"* ]]; then
        exit 0
    fi
done
