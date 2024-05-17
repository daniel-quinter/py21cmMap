#!/bin/bash

# Batch job to run the single shell mapping code in parallel on a set of shells. Saves each mapped shell as its own file.

#SBATCH -p bigmem
#SBATCH -J map_allshells

#SBATCH -t 5:00:00

#SBATCH --array=0-31

#SBATCH -e output-files/map_allshells-%a.err
#SBATCH -o output-files/map_allshells-%a.out

#SBATCH -N 1
#SBATCH -c 2

#SBATCH --mem=40G
module load miniconda3/23.11.0s
source /oscar/runtime/software/external/miniconda3/23.11.0/etc/profile.d/conda.sh

conda activate dq21cm

echo "Running job array number: "$SLURM_ARRAY_TASK_ID

#ulimit -n 5000

python -u map_shell.py -s 1.4e8 -e 2e8 -N 32 --nside=1024 --len=1e3 -i=$SLURM_ARRAY_TASK_ID --fname="z7_45_res100_len1000.npy" --path=maps/thesis/range/nfreqs32

