# python modules
import math
import numpy as np


def bi(b, tw):

    bi = b - 2*tw

    return bi


def a_annulus_circle(b, bi):

    a_annulus_circle = np.pi/4 * (np.power(b, 2) - np.power(bi, 2))

    return a_annulus_circle


def a_circle(b):

    a_circle = np.pi/4*np.power(b, 2)

    return a_circle


def circumference_circle(b):

    circumference_circle = np.pi*b

    return circumference_circle


def i_annulus_circle(b, bi):

    i_annulus_circle = np.pi/64 * (np.power(b, 4) - np.power(bi, 4))

    return i_annulus_circle


def a_annulus_rectangle(b, l, bi, li):

    a_annulus_rectangle = b * l - bi * li

    return a_annulus_rectangle


def a_rectangle(b, l):

    a_rectangle = b * l

    return a_rectangle


def circumference_rectangle(b, l):

    circumference_rectangle = 2 * (b + l)

    return circumference_rectangle


def phi_adjust(sig_v_, sig_under, phi, Dr):

    sig_v_ = max(0.001, sig_v_)
    sig_under = max(0.001, sig_under)
    
    thres = [20, 40, 60, 80, 100] 
    a = [37.2240, 41.0914, 45.0320, 48.9110, 52.8392]
    b = [-0.0189, -0.0278, -0.0337, -0.0365, -0.0372]
                
    if Dr <= thres[0]:
        phi_sigv = a[0]*math.pow(sig_v_, b[0])
        phi_sig_under = a[0]*math.pow(sig_under, b[0])
        ratio = phi_sig_under/phi_sigv
        phi = phi*ratio
    elif Dr > thres[0] and Dr <= thres[1]:
        phi_sigv_xx1 = a[0]*math.pow(sig_v_, b[0])
        phi_sigv_xx2 = a[1]*math.pow(sig_v_, b[1])
        phi_sig_under_xx1 = a[0]*math.pow(sig_under, b[0])
        phi_sig_under_xx2 = a[1]*math.pow(sig_under, b[1])
        phi_sigv = np.interp(Dr, [thres[0], thres[1]], [phi_sigv_xx1, phi_sigv_xx2])
        phi_sig_under = np.interp(Dr, [thres[0], thres[1]], [phi_sig_under_xx1, phi_sig_under_xx2])
        ratio = phi_sig_under/phi_sigv
        phi = phi*ratio
    elif Dr > thres[1] and Dr <= thres[2]:
        phi_sigv_xx1 = a[1]*math.pow(sig_v_, b[1])
        phi_sigv_xx2 = a[2]*math.pow(sig_v_, b[2])
        phi_sig_under_xx1 = a[1]*math.pow(sig_under, b[1])
        phi_sig_under_xx2 = a[2]*math.pow(sig_under, b[2])
        phi_sigv = np.interp(Dr, [thres[1], thres[2]], [phi_sigv_xx1, phi_sigv_xx2])
        phi_sig_under = np.interp(Dr, [thres[1], thres[2]], [phi_sig_under_xx1, phi_sig_under_xx2])
        ratio = phi_sig_under/phi_sigv
        phi = phi*ratio
    elif Dr > thres[2] and Dr <= thres[3]:
        phi_sigv_xx1 = a[2]*math.pow(sig_v_, b[2])
        phi_sigv_xx2 = a[3]*math.pow(sig_v_, b[3])
        phi_sig_under_xx1 = a[2]*math.pow(sig_under, b[2])
        phi_sig_under_xx2 = a[3]*math.pow(sig_under, b[3])
        phi_sigv = np.interp(Dr, [thres[2], thres[3]], [phi_sigv_xx1, phi_sigv_xx2])
        phi_sig_under = np.interp(Dr, [thres[2], thres[3]], [phi_sig_under_xx1, phi_sig_under_xx2])
        ratio = phi_sig_under/phi_sigv
        phi = phi*ratio
    elif Dr > thres[3] and Dr <= thres[4]:
        phi_sigv_xx1 = a[3]*math.pow(sig_v_, b[3])
        phi_sigv_xx2 = a[4]*math.pow(sig_v_, b[4])
        phi_sig_under_xx1 = a[3]*math.pow(sig_under, b[3])
        phi_sig_under_xx2 = a[4]*math.pow(sig_under, b[4])
        phi_sigv = np.interp(Dr, [thres[3], thres[4]], [phi_sigv_xx1, phi_sigv_xx2])
        phi_sig_under = np.interp(Dr, [thres[3], thres[4]], [phi_sig_under_xx1, phi_sig_under_xx2])
        ratio = phi_sig_under/phi_sigv
        phi = phi*ratio
    elif Dr > thres[4]:
        phi_sigv = a[4]*math.pow(sig_v_, b[4])
        phi_sig_under = a[4]*math.pow(sig_under, b[4])
        ratio = phi_sig_under/phi_sigv
        phi = phi*ratio
        
    return phi
    

def param_mask(param_dis):

    if not np.isnan(param_dis).all():
        mask = np.isnan(param_dis)
        param_dis[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), param_dis[~mask])
    
    return param_dis


def param_fill(z_dis, z_array, param_array):

    param_dis = np.array(['nan']*len(z_dis))

    for zi, parami in zip(z_array, param_array):
        param_dis = np.where((np.round(z_dis, 2) < round(zi, 2))&(param_dis == 'nan'), parami, param_dis)

    param_dis = np.where((param_dis == 'nan'), parami, param_dis)

    return param_dis


def extract_array_from_dl(data, key, mask=None, length=0):

    if key not in data:
        return np.full(length, np.nan)
    
    arr = np.asarray(data[key])

    return arr[mask] if mask is not None else arr


def extract_bearing(x_array, y_array):

    theta = []
    mult = []

    for xi, yi in zip(x_array, y_array):
        if xi >= 0 and yi >= 0:
            theta.append(np.atan(abs(yi)/max(1e-10, abs(xi))))
            mult.append(1)
        elif yi >= 0:
            theta.append(np.pi - np.atan(abs(yi)/max(1e-10, abs(xi))))
            mult.append(1)
        elif xi >= 0:
            theta.append(2*np.pi - np.atan(abs(yi)/max(1e-10, abs(xi))))
            mult.append(-1)
        else:
            theta.append(np.pi + np.atan(abs(yi)/max(1e-10, abs(xi))))
            mult.append(-1)

    return theta, mult


def nan_helper(y):

    return np.isnan(y), lambda z: z.nonzero()[0]


def lin_x_log_y_interp(x, xx, yy):

    logyy = np.log10(yy)

    interp = np.power(10.0, np.interp(x, xx, logyy))

    return interp