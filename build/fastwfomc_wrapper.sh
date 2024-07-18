#!/usr/bin/env sh

for ((i=1; ; i++)); do
    echo "Domain size: $i"
    ulimit -t $2 -c 0 && /usr/bin/time -f "Elapsed: %e" julia --project=../deps/FastWFOMC.jl fastwfomc_wrapper.jl $1 $i || exit 1
done
