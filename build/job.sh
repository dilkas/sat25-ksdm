#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --time=00:05:00
#SBATCH --job-name wfomc
#SBATCH --output=output_%j.txt
#SBATCH --mail-type=FAIL

cd $SLURM_SUBMIT_DIR

module load java/1.8.0_201
module load julia/1.10.4
module load intel/2020u4

ulimit -c 0
lscpu > cpuinfo.txt
make -j 1
