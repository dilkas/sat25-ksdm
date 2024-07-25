#!/usr/bin/env sh

for ((i=1; ; i++)); do
    j=$((2 ** $i))
    echo "Domain size: $j"
    ulimit -t $2 -c 0 && /usr/bin/time -f "Elapsed: %e" julia --project=../deps/FastWFOMC.jl fastwfomc_wrapper.jl $1 $j || exit 1
done
