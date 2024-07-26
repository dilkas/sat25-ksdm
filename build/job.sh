#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --time=00:05:00
#SBATCH --job-name wfomc
#SBATCH --output=output_%j.txt
#SBATCH --mail-type=FAIL

cd $SLURM_SUBMIT_DIR

# TODO: module load intel/2018.2

ulimit -c 0
lscpu > cpuinfo.txt
make -j 1
