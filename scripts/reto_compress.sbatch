#!/bin/bash
#
#SBATCH --partition=all
#SBATCH --job-name=reto_compress
#SBATCH --output=%j.reto_compress.out
#SBATCH --ntasks=24
#

OUTPUT_PATH=./dirkbig

time prun ./super_bz2 ejemplo_file $OUTPUT_PATH -p 24
