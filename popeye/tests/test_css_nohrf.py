import os
from itertools import repeat
import ctypes

import numpy as np
import numpy.testing as npt

import popeye.utilities as utils
import popeye.css_nohrf as css
from popeye.visual_stimulus import VisualStimulus, simulate_bar_stimulus, resample_stimulus

def test_css_fit():
    
    viewing_distance = 38
    screen_width = 25
    thetas = np.arange(0,360,90)
    num_blank_steps = 0
    num_bar_steps = 30
    ecc = 10
    tr_length = 1.0
    frames_per_tr = 1.0
    scale_factor = 0.10
    pixels_down = 50
    pixels_across = 50
    dtype = ctypes.c_int16
    Ns = 3
    voxel_index = (1,2,3)
    auto_fit = True
    verbose = 1
    
    # create the sweeping bar stimulus in memory
    bar = simulate_bar_stimulus(pixels_across, pixels_down, viewing_distance, 
                                screen_width, thetas, num_bar_steps, num_blank_steps, ecc)
    
    # create an instance of the Stimulus class
    stimulus = VisualStimulus(bar, viewing_distance, screen_width, scale_factor, tr_length, dtype)
    
    # initialize the gaussian model
    model = css.CompressiveSpatialSummationModel(stimulus, utils.spm_hrf)
    model.hrf_delay = 0.2
    
    # generate a random pRF estimate
    x = -2.24
    y = 1.58
    sigma = 1.23
    n = 0.90
    beta = 1.0
    
    # create the "data"
    data =  model.generate_prediction(x, y, sigma, n, beta)
    
    # set search grid
    x_grid = (-3,2)
    y_grid = (-3,2)
    s_grid = (1/stimulus.ppd,2.75)
    n_grid = (0.1,0.90)
    b_grid = (0.01,1)
    h_grid = (-4.0,4.0)
    
    # set search bounds
    x_bound = (-10,10)
    y_bound =  (-10,10)
    s_bound = (1/stimulus.ppd,10)
    n_bound = (1e-8,1.0)
    b_bound = (1e-8,1e5)
    h_bound = (-5.0,5.0)
    
    # loop over each voxel and set up a GaussianFit object
    grids = (x_grid, y_grid, s_grid, n_grid, b_grid,)
    bounds = (x_bound, y_bound, s_bound, n_bound, b_bound,)
    
    # fit the response
    fit = css.CompressiveSpatialSummationFit(model, data, grids, bounds, Ns=Ns)
    
    # fine
    npt.assert_almost_equal(fit.x, x, 1)
    npt.assert_almost_equal(fit.y, y, 1)
    npt.assert_almost_equal(fit.sigma, sigma, 1)
    npt.assert_almost_equal(fit.n, n, 1)
    npt.assert_almost_equal(fit.beta, beta, 1)
    
    # coarse
    npt.assert_almost_equal(fit.ballpark,[-0.5       , -0.5       ,  0.72833938,  0.9       ,  0.505     ])
    
    # overloaded
    npt.assert_almost_equal(fit.overloaded_estimate,[2.5272803327911109,
                                                     2.741167634420512,
                                                     1.2965338406813691,
                                                     0.90000000004104885,
                                                     1.0000000000009019])