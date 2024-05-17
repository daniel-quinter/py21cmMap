#!/bin/bash

#SBATCH -p bigmem
#SBATCH -J xspec

#SBATCH -t 5:00:00

#SBATCH --array=0-31

#SBATCH -e output-files/xspec_all-%a.err
#SBATCH -o output-files/xspec_all-%a.out

#SBATCH -N 1
#SBATCH -c 2

#SBATCH --mem=30G

module load miniconda3/23.11.0s
source /oscar/runtime/software/external/miniconda3/23.11.0/etc/profile.d/conda.sh

conda activate hp_env

echo "Running job array number: "$SLURM_ARRAY_TASK_ID

#ulimit -n 5000

python -u xspec_all.py -N 32 --fname="maps/thesis/range/nfreqs32.npy" --path="xspecs/thesis/range/nfreqs32" --shell_idx=$SLURM_ARRAY_TASK_ID

