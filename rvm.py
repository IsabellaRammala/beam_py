#!/usr/bin/env python

import numpy as np 

def rvm(alpha,beta,phi0,psi0,psi,xprof):
    """Function to predict the polarisation position angle (PPA).
       Takes the inputs angles that define the geometry of the rotating vector
       model and predict the position angle swing.
    
       Args: 
    
          alpha   : the magnetic inclination angle in degrees.
          beta    : the impact parameter in degrees.
          phi0    : the rotational phase at the fiducial point in degrees.
          psi0    : the position angle at the fiducial point in degrees.
          xprof   : an array of the baseline points of the profile.  
        
       Outputs:
         
           allpsi : an array of polarisation position angles swing in degrees.
           
    """

    # Converting the input angles to radians:
    angles = alpha, beta, phi0, psi0
    for angle in angles:
        angRad = np.deg2rad(angles)
            
    # Predict the position angle (psi) swing through the observer's sight line:
    zeta = alpha + beta
    numpts = len(xprof)
    points = range(1,numpts + 1)
    
    allpsi = []

    for point in points:
        phi = np.deg2rad(xprof[point - 1])
        numer = np.sin(alpha) * np.sin(phi - phi0)
        denom = np.sin(zeta) * np.cos(alpha) - np.cos(zeta) * np.sin(alpha) * np.cos(phi - phi0)
        
        psi = psi0 + np.arctan(numer/denom)
        
        # restrict psi between [-pi/2, pi/2]
        if psi < -np.pi/2.:
            psi = psi + np.pi
            
        if psi > np.pi/2.:
              psi = psi - np.pi
            
        # Convert psi back to degrees
        allpsi.append(np.rad2deg(psi))
        
    return allpsi

# simple test line
if __name__ == "__main__":
    xprof = np.linspace(-180.,180.,10)
    print rvm(45.,15.,10.,15.,10.,xprof)