import numpy as np
from astropy import cosmology
import astropy_healpix
from astropy_healpix import HEALPix
import astropy.cosmology
from astropy.cosmology import Planck18 as cosmo
import astropy.units as unit
import argparse
import os
import pickle
from matplotlib import pyplot as plt

f21 = 1.420405751e9 * unit.Hz

# round_base(x, prec, base):
#    Rounds value x to the nearest integer multiple of base, with precision prec
def round_base(x, prec, base):     
    return (base * (np.array(x) / base).round()).round(prec)


#  nearest_cube_pt(x, y, z, cube_length, cube_res):
#      Input : 
#           x (float), y (float), z (float): coordinates of the shell point being mapped onto, units of [Mpc]
#           cube_length (int): comoving length of one side of the input data cube, units of [Mpc]
#           cube_res (int): number of points per side of the input data cube
#
#      Returns the nearest point of a cube with cube_length and cube_res
#      to point on the shell with coordinates (x, y, z).
# 
#      Assumes that cubes are uniformly tiled throughout the larger volume, such that (x y z) % cube_length is guaranteed
#      to give the coordinates of the input sphere point relative to the origin of the cube.

def nearest_cube_pt(x, y, z, cube_length, cube_res): 
    
    arr = np.array([x, y, z]) % cube_length
    nearest = round_base(arr, 5, cube_length / cube_res)
    nearest = (nearest * (cube_res / cube_length)).astype(int)
    
    # Imposes periodicity: if the index of any of the coordinates of the nearest cube point equals the max index + 1,
    #    set this index to 0, effectively "wrapping around" the cube
    nearest[nearest == cube_res] = 0
    
    return nearest

# cosm_plot(redshift, nside, cube_length, data_cube):
#      Input: 
#           redshift (float)
#           nside (int): desired shell resolution. Must be a power of 2, # of pixels on a shell = nside ^ 2 * 12
#           cube_length (int): comoving length of one side of the input data cube, units of [Mpc]
#           data_cube (numpy array, shape = (cube_res, cube_res, cube_res))
#
#      Returns a numpy array of the value of each point in the data cube nearest to each point on the shell, 
#           shape = (npix, 1)

def cosm_plot(redshift, nside, cube_length, data_cube):
    # cube_length in Mpc
    
    cube_res = data_cube.shape[0]
    
    hp = HEALPix(nside=nside)
    x, y, z = astropy_healpix.healpix_to_xyz(np.arange(hp.npix), nside = hp.nside)

    r_s = cosmology.Planck18.comoving_distance(redshift)
    xs = np.array(x * r_s)
    ys = np.array(y * r_s)
    zs = np.array(z * r_s)
    shell = np.array([xs, ys, zs]).T
    
    nearest_arr = nearest_cube_pt(xs, ys, zs, cube_length, cube_res)
    
    return data_cube[nearest_arr[0], nearest_arr[1], nearest_arr[2]]

if __name__ == "__main__":
    # When run as a script, construct a noiselike skymodel for the MWA frequency channels.

    parser = argparse.ArgumentParser(
        description="A command-like script to map a cube onto a single shell in a set of shells."
        "Best used in conjunction with a batch script."
    )

    parser.add_argument(
        "-s", "--start_freq", type=float, required=True, help="Start frequency (in Hz)"
    )
    parser.add_argument(
        "-e", "--end_freq", type=float, required=True, help="End frequency (in Hz)"
    )
    parser.add_argument(
        "-N", "--nfreqs", type=int, required=True, help="Number of frequencies/shells"
    )
    parser.add_argument(
        "--nside",
        type=int,
        required=True,
        help="HEALPix NSIDE parameter. Must be a power of 2",
    )
    parser.add_argument(
        "--len",
        type=float,
        required=True,
        help="Length of one cube (in Mpc)",
    )
    parser.add_argument(
        "-i", "--index",
        type=int,
        required=True,
        help="Index of the shell being mapped in the range [0, Nfreqs)",
    )
    parser.add_argument(
        "--fname",
        type=str,
        required=str,
        help="Path + file name of input data cube",
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Output path",
    )

    


    args = parser.parse_args()


    
    nside = args.nside
    start_freq = args.start_freq
    end_freq = args.end_freq
    Nfreqs = args.nfreqs
    
    cube_len = args.len
    idx = args.index
    fname = args.fname
    path = args.path
    
    start_freq *= unit.Hz
    end_freq *= unit.Hz

    freqs = np.linspace(start_freq, end_freq, Nfreqs)
    
    redshifts = (f21 / freqs) - 1

    # must sort so that redshifts go in ascending order (opposite freq order)
    z_order = np.argsort(redshifts)
    redshifts = redshifts[z_order]
    redshifts = redshifts.to_value()
    
    data_cube = np.load(fname)
   # data_cube = np.random.normal(scale = np.sqrt(1), size=(100, 100, 100))    
    shell = cosm_plot(redshifts[idx], nside, cube_len, data_cube)
    
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as error:
        print(error)
    
    np.save(f"{path}/shell{idx}", shell)
    
