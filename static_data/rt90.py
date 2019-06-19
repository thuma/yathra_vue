# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Arnold Andreasson, info@mellifica.se
# Copyright (c) 2007-2016 Arnold Andreasson 
# License: MIT License as follows:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# =============================================================================
# Javascript-implementation of "Gauss Conformal Projection 
# (Transverse Mercator), Krügers Formulas".
# - Parameters for SWEREF99 lat-long to/from RT90 and SWEREF99 
#   coordinates (RT90 and SWEREF99 are used in Swedish maps).
# Source: http:#www.lantmateriet.se/geodesi/
 
#axis = null; # Semi-major axis of the ellipsoid.
#flattening = null; # Flattening of the ellipsoid.
#central_meridian = null; # Central meridian for the projection.
#lat_of_origin = null; # Latitude of origin.
#scale = null; # Scale on central meridian.
#false_northing = null; # Offset for origo.
#false_easting = null; # Offset for origo.
import math

axis = 6378137.0 # GRS 80.
flattening = 1.0 / 298.257222101# GRS 80.
lat_of_origin = 0.0
central_meridian = 15.0 + 48.0/60.0 + 22.624306/3600.0
scale = 1.00000561024
false_northing = -667.711
false_easting = 1500064.274

def geodetic_to_grid(latitude, longitude):
	x_y = [0,0];
	# Prepare ellipsoid-based stuff.
	e2 = flattening * (2.0 - flattening);
	n = flattening / (2.0 - flattening);
	a_roof = axis / (1.0 + n) * (1.0 + n*n/4.0 + n*n*n*n/64.0);
	A = e2;
	B = (5.0*e2*e2 - e2*e2*e2) / 6.0;
	C = (104.0*e2*e2*e2 - 45.0*e2*e2*e2*e2) / 120.0;
	D = (1237.0*e2*e2*e2*e2) / 1260.0;
	beta1 = n/2.0 - 2.0*n*n/3.0 + 5.0*n*n*n/16.0 + 41.0*n*n*n*n/180.0;
	beta2 = 13.0*n*n/48.0 - 3.0*n*n*n/5.0 + 557.0*n*n*n*n/1440.0;
	beta3 = 61.0*n*n*n/240.0 - 103.0*n*n*n*n/140.0;
	beta4 = 49561.0*n*n*n*n/161280.0;
	
	# Convert.
	deg_to_rad = math.pi / 180.0;
	phi = latitude * deg_to_rad;
	lambda_v = longitude * deg_to_rad;
	lambda_zero = central_meridian * deg_to_rad;
	
	phi_star = phi - math.sin(phi) * math.cos(phi) * (A + 
					B*(math.sin(phi)**2) + 
					C*(math.sin(phi)**4) + 
					D*(math.sin(phi)**6));
	delta_lambda = lambda_v - lambda_zero;
	xi_prim = math.atan(math.tan(phi_star) / math.cos(delta_lambda));
	eta_prim = math.atanh(math.cos(phi_star) * math.sin(delta_lambda));
	x = (scale * a_roof * (xi_prim +
					beta1 * math.sin(2.0*xi_prim) * math.cosh(2.0*eta_prim) +
					beta2 * math.sin(4.0*xi_prim) * math.cosh(4.0*eta_prim) +
					beta3 * math.sin(6.0*xi_prim) * math.cosh(6.0*eta_prim) +
					beta4 * math.sin(8.0*xi_prim) * math.cosh(8.0*eta_prim)) + 
					false_northing);
	y = (scale * a_roof * (eta_prim +
					beta1 * math.cos(2.0*xi_prim) * math.sinh(2.0*eta_prim) +
					beta2 * math.cos(4.0*xi_prim) * math.sinh(4.0*eta_prim) +
					beta3 * math.cos(6.0*xi_prim) * math.sinh(6.0*eta_prim) +
					beta4 * math.cos(8.0*xi_prim) * math.sinh(8.0*eta_prim)) + 
					false_easting);
	x_y[0] = round(x * 1000.0) / 1000.0;
	x_y[1] = round(y * 1000.0) / 1000.0;
	return x_y;