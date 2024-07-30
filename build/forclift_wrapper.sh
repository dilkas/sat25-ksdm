#!/bin/bash

cd ../deps/Forclift || exit 1
for ((k=1; ; k++)); do
    i=$((2 ** $k))
    echo "Domain size: $i"
    sed -i "s/\.\.\.,[[:digit:]]\+/\.\.\.,$i/g" "$1"
    error_found=false
    while IFS= read -r line; do
        echo "$line"
        if echo "$line" | grep -qE "Infinity|Cannot|cannot|Exception|Error"; then
            error_found=true
        fi
    done < <(ulimit -t "$2" -c 0 -Sv "$3" && /usr/bin/time -f "Elapsed: %e" java -jar target/scala-2.11/crane-assembly-1.0.jar -z --format-in mln "$1" 2>&1)
    if $error_found; then
        exit 0
    fi
done
