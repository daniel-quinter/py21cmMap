#!/usr/bin/env python
# coding: utf-8

import numpy as np
import scipy
from matplotlib import pyplot as plt
import healpy as hp
from astropy.cosmology import Planck18 as cosmo
import astropy.units as unit
import scipy.integrate as integrate
import argparse
import os

f21 = 1.420405751e9 * unit.Hz

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A script to calculate the cross-angular power spectrum for one shell[shell_idx]"
        " with all shells with indices <= shell_idx. Best used in conjunction with a batch script."
    )
    parser.add_argument(
        "-N", "--nfreqs", type=int, required=True, help="Number of frequencies/shells"
    )
    parser.add_argument(
        "--fname", type=str, required=True, help="Input folder path for shell maps"
    )
    parser.add_argument(
        "--path", type=str, required=True, help="Output folder path for the computed cross-power spectra"
    )
    parser.add_argument(
        "--shell_idx", type=int, required=True, help="Index of the current shell"
    )
    
    
    
    args = parser.parse_args()
    
    nfreqs = args.nfreqs
    fname = args.fname
    path = args.path
    shell_idx = args.shell_idx
    
    # reverses the order of the shell cross-power spectra calculations. i.e. rather than starting with
    # C_l(shells[0], shells[0]), we begin with C_l(shells[nfreqs - 1], shells[nfreqs - 1])
    # Frontloading the computation of shells with the largest number of cross-power spectra is more efficient for batch jobs 
    # if all jobs can't be run at once. 
    
    shell_idx = nfreqs - 1 - shell_idx
    
    shells = np.load(fname)
    nside = int(np.sqrt(shells.shape[1] / 12))
    
    cross_spectrum_col = np.zeros((shell_idx + 1, nside * 3))
    for j in np.arange(shell_idx + 1):
        cross_spectrum_col[j] = hp.sphtfunc.anafast(shells[shell_idx], shells[j])
    
    
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as error:
        print(error)
    
    np.save(f"{path}/shell{shell_idx}_arr", cross_spectrum_col)
