#!/usr/bin/env python

# Program to generate a 2D beam and the corresponding 1D line 
# of sight profiles at varying frequency.



import beamModel as bm
import numpy as np
import argparse
import matplotlib.pyplot as plt

#==============================================================================================================================================
#                                          IMPORTANT FUNCTION:
#==============================================================================================================================================
def generateBeam(P, alpha, beta, freq, dm, heights, npatch, snr, do_ab, iseed, fanBeam):
    """Function to plot the patches for a given rotation period.
    
       A rgs:
       -----
       P       : rotational period (seconds)
       alpha   : inclination angle (degrees)
       beta    : impact parameter (degrees)
       heights : emission heights (in km)
       centerx : the patch center projection on the x-axis 
       centery : the patch center projection on the y-axis
       snr     : signal to noise ratio       
       iseed   : seed for the random number generator
       do_ab   : option to include abberration effects
       fanBeam : option to use fan beam model 

       Returns:
       --------
       prof    : an array containing 1D profile
       Z       : a 2D beam 
    
    """    
    
#   initialize parameters:
    xmin = -180.
    xmax = 180.
    res = 1e3 #resolution
    ymin = -180.
    ymax = 180.
    dx = (xmax - xmin)/res
    dy = (ymax - ymin)/res
    x = np.linspace(xmin, xmax, num=res, endpoint=True)
    y = np.linspace(ymin, ymax, num=res, endpoint=True)
    X,Y = np.meshgrid(x,y)
    gauss = np.zeros(len(x))
    Z = np.zeros_like(X)
    prof_los = np.zeros_like(gauss)

#   find the width of the patches:
    patchwidths = bm.patch_width(P, heights)
#   An arbitrary peak of the profile:
    peakAmp = 1.
#   Get the line of sight:
    xlos, ylos, thetalos = bm.los(alpha, beta, res)
#   Get the centre of the emission patches on the xy-plane
    centerx, centery = bm.patch_center(P, heights, npatch, iseed, fanBeam)
#   Get the ofset due to abberation:
    ab_xofset, ab_yofset = bm.aberration(heights, P, alpha)

#   Find the 1D and 2D profile:
    for cid, comp in enumerate(heights):
#       widths for circular patches:        
        sigmax = patchwidths[cid]
        sigmay = patchwidths[cid]

#       center of the patch:
        patchCenterX = centerx[cid]
        patchCenterY = centery[cid]

#       2D patch (including aberation):
        for pc in zip(patchCenterX, patchCenterY):
            #if distance of current box from the patch center is
            #larger than 3 times the patchwidth, I do not want any
            #power contributed
            # first compute a grid of distance from the center of the patch, in units of the width
            distance = (np.sqrt((X - pc[0])**2 + (Y - pc[1])**2))/sigmax
            distance[np.where(distance > 3.0)] = 0.0
            distance[np.where(distance != 0.0)] = peakAmp
            if do_ab == None:
                Z += distance * np.exp(-((X - pc[0])**2 / (2 * sigmax**2) + (Y - pc[1])**2 / (2 * sigmay**2)))
            else:
                Z += distance * np.exp(-((X - pc[0] - ab_xofset[cid])**2 / (2 * sigmax**2) + (Y - pc[1] - ab_yofset[cid])**2 / (2 * sigmay**2)))

#   1D profile from 2D patch, closest to the line of sight (select nearest neighbors):
    ZxIdx = np.array((xlos-xmin)/dx, dtype=int) # x index
    ZyIdx = np.array((ylos-ymin)/dy, dtype=int) # y index
    prof = Z[ZxIdx, ZyIdx]

    return prof, Z

#===============================================================================================================================================
#                                       MAIN:
#===============================================================================================================================================

parser = argparse.ArgumentParser(description='Plot the patchy emission region as well as the line of sight profile.\
                                 Running the file without specified argument will produce an output beam and profile from default parameters.')
parser.add_argument('-alpha', metavar="<alpha>", type=float, default='45', help='inclination angle in degrees (default = 45)')
parser.add_argument('-beta', metavar="<beta>", type=float, default='5', help='impact parameter in degrees (default = 5)')
parser.add_argument('-p', metavar="<p>", type=float, default='0.16', help='period in seconds (default = 0.16 s)')
parser.add_argument('-hmin', metavar="<hmin>", type=float, default=None, help='minimum emission height in km\
                    (default = {20 km for P > 0.15 s}, and {950 km for P < 0.15 s})')
parser.add_argument('-hmax', metavar="<hmax>", type=float, default=None, help='maximum emission height in km (default = 1000 km)')
parser.add_argument('-nc', metavar="<ncomp>", type=int, default='4', help='integer number of components (default = 4)')
parser.add_argument('-npatch', metavar="<npatch>", type=int, default='10', help='number of emission patches (default= 10)' )
parser.add_argument('-min_freq', metavar="<minfreq>", type=float, default='0.2', help='min frequency in GHz (default = 0.2 GHz)')
parser.add_argument('-chbw', metavar="<chanbw>", type=float, default='0.8', help='channel bandwidth in GHz (default = 0.8 GHz)')
parser.add_argument('-nch', metavar="<nch>", type=int, default='5', help='number of channels (default = 5)')
parser.add_argument('-iseed', metavar="<iseed>", type=int, default='4', help='integer seed for a pseudo-random number generator (default = 4)')
parser.add_argument('-snr', metavar="<snr>", type=float, default=None, help='signal to noise ratio (default = None)')
parser.add_argument('-dm', metavar="<dm>", type=float, default=1, help='dispersion measure in cm^-3 pc (default = 1)')
parser.add_argument('-outfile', metavar="<output file>", help="Write to file.")
parser.add_argument('-do_ab', default=None, help='include aberration ofset (default = None)')
parser.add_argument('-scatter', default=None, help='include scattering (default = None)')
parser.add_argument('-doFan', default=None, help='Fan beam - default: patchy beam')
args = parser.parse_args()
P = args.p
ncomp = args.nc
npatch = args.npatch
iseed = args.iseed
hmin = args.hmin
hmax = args.hmax
alpha = args.alpha
beta = args.beta
snr = args.snr
dm = args.dm
do_ab = args.do_ab
nch = args.nch
min_freq = args.min_freq
chbw = args.chbw
scr = args.scatter
fanBeam = args.doFan
fileName = args.outfile

#====================================================================================================================================================
#                                                        MAIN BODY: 
#====================================================================================================================================================
#=====================
# initialize params:
#=====================
beam = []
prof = []
peaks = []
w10 = []
res = 1e3
t_res = P/res
phase = np.linspace(-180, 180, num=res)
max_freq = (nch - 1) * chbw + min_freq
freq = np.linspace(min_freq, max_freq, nch) #channel frequency in GHz!!!

#=======================================
#     1. Find the emission height:
#=======================================
H = bm.emission_height(P, ncomp, iseed, hmin, hmax)
#========================================
#     2. Get profile at each frequency:
#========================================
for i in np.arange(len(freq)):
    heights = bm.height_f(H, freq[i]) # frequency dependent H
    pr, Z = generateBeam(P, alpha, beta, freq[i], dm, heights, npatch, snr, do_ab, iseed, fanBeam)
    w10.append(bm.find_width(pr))
    prof.append(pr)
    beam.append(Z)

#==========================================
#     3. Scatter the line of sight profile: 
#==========================================
train = []
bf = []
tau = bm.sc_time(freq, dm, iseed)
if scr == None:
    sc_prof = prof # returns the profile without scattering and store that in sc_prof

else:
    sc_prof = []
    for pid in np.arange(len(prof)):
        train.append(bm.pulsetrain(3, res, prof[pid]))

    for fid in np.arange(len(freq)):
        tau = bm.sc_time(freq[fid], dm, iseed)
        bf = bm.broadening(tau, P, res)
        sc_train = bm.scatter(train[fid], bf)
        sc_prof.append(bm.extractpulse(sc_train, 2, res)) #scattered pulse profile

#===========================================
#     4. Add noise:
#===========================================
for j in np.arange(len(prof)):
    peaks.append(bm.find_peak(sc_prof[j]))

if snr == None:
    profile = sc_prof
else:
    rms = bm.noise_rms(snr, np.max(peaks))
    profile = bm.add_noise(sc_prof, rms, iseed, res)

#======================================================
#      5. Fit a DM Curve:
#======================================================

average_profile = []
peaks_of_average = []
phase_bin0 = bm.find_phase_bin(profile[nch - 1])
phase_bin1 = bm.find_phase_bin(profile[0])
dm_range = bm.find_delta_dm(P, profile, phase, phase_bin0, phase_bin1, freq[nch - 1], freq[0], nch)

for dm_id in range(len(dm_range)):
    shifted_profile = []
    for freq_id in range(nch-1):
        bin_shift = bm.delay(freq[nch - 1], freq[freq_id], dm_range[dm_id], t_res)
        shifted_profile.append(np.roll(profile[freq_id], bin_shift))
    average_profile.append(bm.avg_prof(shifted_profile))
    peaks_of_average.append(bm.find_peak(average_profile[dm_id]))

for i in range(len(peaks_of_average)):
    if peaks_of_average[i] == np.max(peaks_of_average):
       best_dm = dm_range[i]

#=======================================================
#    6. Write out the important parames to a file:
#=======================================================
pulsarParams = np.asarray([P, alpha, beta, w10[0], w10[-1], iseed, best_dm])
f = open(fileName, 'a')
f.write(' '.join([str(item) for item in pulsarParams]) + ' \n')

#==================================================================
#                     PRODUCE PLOTS:
#==================================================================
#===========================================
# 1. SET A ZERO BASELINE AND PLOT THE PROFILE:
#===========================================
fig = plt.figure()
for k in np.arange(len(profile)):
    plt.plot(phase, profile[k] + k, label='frequency = %0.2f GHz' %freq[k])
plt.title('A sequence of %i pulse profile' %nch)
plt.xlabel('phase (degrees)')
plt.xlim(-180,180)
plt.grid()

#============================================
#    2D emission region:
#============================================
meanBeam = np.mean(beam, axis=0)
xlos, ylos, thetalos = bm.los(alpha, beta, res)
plt.figure(figsize=(10,5))
plt.subplot(1, 2, 1)
plt.plot(xlos, ylos, '+r')
plt.imshow(beam[0].T, extent=[-180, 180, 180, -180])
plt.xlabel('X (degrees)')
plt.ylabel('Y (degrees)')
# find zoomed extent for plot
nonZero = np.where(beam[0]!= 0.0)
nzx_min = np.min(np.amin(nonZero,0))
nzy_min = np.min(np.amin(nonZero,1))
nzx_max = np.max(np.amax(nonZero,0))
nzy_max = np.max(np.amax(nonZero,1))
x1 = phase[nzx_min]
x2 = phase[nzx_max]
y1 = phase[nzy_min]
y2 = phase[nzy_max]
plt.xlim(x1,x2)
plt.ylim(y1,y2)
plt.colorbar()
plt.subplot(1, 2, 2)
plt.plot(phase, profile[0])
plt.xlim(-180, 180)
plt.xlabel('Phase (degrees)')
plt.show()
