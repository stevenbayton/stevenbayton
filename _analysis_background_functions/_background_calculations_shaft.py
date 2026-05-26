# python modules
import math
import numpy as np
import re

# multiconsult modules
import _background_functions as bf

# %% --- SHAFT CLAY ---

def cpt_shaft_clay(q_c, sbt, case, calculation_dict, kf_p=0.03, kf_h=0.05):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1

    if 'most_probable' in case.lower():
        k_f = kf_p
    elif 'highest' in case.lower():
        k_f = kf_h
    elif 'tailored' in case.lower():
        match = re.search(r'\[([0-9.+-eE]+)\]', case)
        k_f = float(match.group(1))
    elif 'sbt' in case.lower():
        if 'be' in case.lower():
            matrix = {'SD': 0.0011,
                      'CD': 0.028,
                      'TD': 0.018,
                      'SC': 0.13,
                      'CC': 0.019,
                      'TC': 0.005}
        elif 'le' in case.lower():
            matrix = {'SD': 0.00095,
                      'CD': 0.015,
                      'TD': 0.005,
                      'SC': 0.05,
                      'CC': 0.019,
                      'TC': 0.074}
        elif 'he' in case.lower():
            matrix = {'SD': 0.0012,
                      'CD': 0.045,
                      'TD': 0.038,
                      'SC': 0.25,
                      'CC': 0.1,
                      'TC': 0.35}
        if sbt in matrix:
            k_f = matrix[sbt]
        else:
            k_f = matrix['CD']

    q_s = q_c*k_f
    
    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_f[calc_s]# k<sub>s</sub> (-) ? -': k_f}
        
    return q_s, inner_ratio, save_parameter


def almhamre_shaft_clay(q_c, f_s_cpt, sigv0_, z, z_tip, case, calculation_dict, k_sc=0.004, b=0.0025):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1
    
    if 'be' in case.lower():
        multiplier = 1
    elif 'he' in case.lower():
        multiplier = 1.25

    q_c = max(0.001, q_c)
    f_s_cpt = max(0.001, f_s_cpt)
    
    k = np.power(1000*q_c/sigv0_, 0.5)/80
    qs_res = k_sc*q_c*(1 - b*1000*q_c/sigv0_)
    qs_res = max(0.001, qs_res)

    qs_init = f_s_cpt
    h = z_tip - z
    q_s = multiplier*(qs_res + (qs_init - qs_res)*math.exp(-k*h))

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      'f_s[input_s]# f<sub>s</sub> (MPa) ? -': f_s_cpt,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'k[calc_s]# k (-) ? -': k,
                      'b[calc_s]# b (-) ? -': b,
                      'qs_res[calc_s]# q<sub>s,res</sub> (MPa) ? -': qs_res,
                      'qs_init[calc_s]# q<sub>s,ini</sub> (MPa) ? -': qs_init,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'mult[calc_s]# mult (-) ? -': multiplier}
    
    return q_s, inner_ratio, save_parameter


def alpha_dnv_shaft_clay(s_u_c, alpha, dss_suc, calculation_dict):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1

    s_u_dss = s_u_c*dss_suc
    
    q_s = 0.001*alpha*s_u_dss

    save_parameter = {'s_u_c[input_s]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      'alpha[calc_s]# α (-) ? -': alpha,
                      'dss_suc[input_s]# s<sub>u,d</sub>/s<sub>u,c</sub> (-) ? -': dss_suc,
                      's_u_dss[input_s]# s<sub>u,d</sub> (kPa) ? -': s_u_dss}
        
    return q_s, inner_ratio, save_parameter


def alpha_iso_api_shaft_clay(s_u_c, sigv0_, dss_suc, calculation_dict, alpha_lim=1):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1

    s_u_dss = s_u_c*dss_suc
    
    if s_u_dss != 0:
        if s_u_dss/max(1e-10, sigv0_) > 1:
            alpha = 0.5*(s_u_dss/max(1e-10, sigv0_))**-0.25
        else:
            alpha = 0.5*(s_u_dss/max(1e-10, sigv0_))**-0.5
            
    else:
        alpha = 1

    if alpha > alpha_lim:
        alpha = alpha_lim

    q_s = 0.001*alpha*s_u_dss
        
    save_parameter = {'s_u_c[input_s]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'dss_suc[input_s]# s<sub>u,d</sub>/s<sub>u,c</sub> (-) ? -': dss_suc,
                      's_u_dss[input_s]# s<sub>u,d</sub> (kPa) ? -': s_u_dss,
                      'alpha[calc_s]# α (-) ? -': alpha}
             
    return q_s, inner_ratio, save_parameter


def ucpt_shaft_clay(q_t, z, z_tip, calculation_dict, Fst=1, beta=0.25):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']
    
    h = z_tip - z
    D_ = np.power(np.power(D, 2) - np.power(D_i, 2), 0.5)
    h_D_ = max(h/D_, 1)

    q_s = 0.07*Fst*q_t*np.power(h_D_, -beta)

    save_parameter = {'q_t[input_s]# q<sub>t</sub> (MPa) ? -': q_t,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'D_[calc_s]# D<sub>eff</sub> (m) ? -': D_,
                      'h_D_[calc_s]# h/D<sub>eff</sub> (-) ? -': h_D_,
                      'Fst[calc_s]# F<sub>st</sub> (-) ? -': Fst,
                      'beta[calc_s]# β (-) ? -': beta}
    
    return q_s, inner_ratio, save_parameter


def ngi_shaft_clay(s_u_c, sigv0_, uu_suc, i_p, calculation_dict, F_tip=1):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1

    s_u_uu = s_u_c*uu_suc
    psi = s_u_uu/sigv0_
    alpha_nc = min(max(0.32*np.power(i_p-10, 0.3), 0.2), 1)
    
    if psi < 0.25:
        alpha_psi = alpha_nc
    elif psi > 1:
        alpha_psi = 0.5*np.power(psi, -0.3)*F_tip
    else:
        alpha_psi = alpha_nc + (0.5-alpha_nc)*(math.log(psi)-math.log(0.25))/(math.log(1)-math.log(0.25))

    beta_nc = 0.08*np.power(i_p - 10, 0.3)

    q_s = 0.001*max(beta_nc*sigv0_, alpha_psi*s_u_uu)

    save_parameter = {'s_u_c[input_s]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'uu_suc[input_s]# s<sub>u,uu</sub>/s<sub>u,c</sub> (-) ? -': uu_suc,
                      's_u_uu[input_s]# s<sub>u,uu</sub> (kPa) ? -': s_u_uu,
                      'i_p[input_s]# I<sub>p</sub> (%) ? -': i_p,
                      'psi[calc_s]# ψ (-) ? -': psi,
                      'alpha_nc[calc_s]# α<sub>nc</sub> (-) ? -': alpha_nc,
                      'alpha_psi[calc_s]# α<sub>ψ</sub> (-) ? -': alpha_psi,
                      'beta_nc[calc_s]# β<sub>nc</sub> (-) ? -': beta_nc}
    
    return q_s, inner_ratio, save_parameter


def icp_shaft_clay(sigv0_, ocr, z, z_tip, st, delta_int, calculation_dict, K_f_K_c=0.8):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    h = z_tip - z
    R = D/2
    R_i = D_i/2
    R_star = np.power(np.power(R, 2) - np.power(R_i, 2), 0.5)

    if 'plugged' in calculation_dict['calculation_method']:
        h_R = max(h/R, 8)  
    else:
        h_R = max(h/R_star, 8)
                
    dI_vy = np.log10(st)
    
    K_c = (2.2 + 0.016*ocr - 0.87*dI_vy)*np.power(ocr, 0.42)*np.power(h_R, -0.2)
    
    q_s = K_f_K_c*K_c*0.001*sigv0_*math.tan(np.radians(delta_int))

    save_parameter = {"sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'ocr[input_s]# OCR (-) ? -': ocr,
                      'st[input_s]# S<sub>t</sub> (-) ? -': st,
                      'delta_int[input_s]# δ<sub>int</sub> (deg) ? -': delta_int,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'K_f_K_c[calc_s]# K<sub>f</sub>/K<sub>c</sub> (-) ? -': K_f_K_c,
                      'R_star[calc_s]# R* (-) ? -': R_star,
                      'h_R[calc_s]# h/R (-) ? -': h_R,
                      'dI_vy[calc_s]': dI_vy,
                      'K_c[calc_s]': K_c}
            
    return q_s, inner_ratio, save_parameter


def uwa_shaft_clay(q_t, sigv0_, z, z_tip, delta_int, calculation_dict):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    h = z_tip - z
    R = D/2
    R_i = D_i/2
    R_star = np.power(np.power(R, 2) - np.power(R_i, 2), 0.5)

    if 'plugged' in calculation_dict['calculation_method']:
        h_R = max(h/R, 1)  
    else:
        h_R = max(h/R_star, 1)
                        
    q_s = 0.23*q_t*np.power(h_R, -0.2)/np.power(1000*q_t/sigv0_, 0.15)*math.tan(np.radians(delta_int))

    save_parameter = {'q_t[input_s]# q<sub>t</sub> (MPa) ? -': q_t,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'delta_int[input_s]# δ<sub>int</sub> (deg) ? -': delta_int,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'R_star[calc_s]# R* (m) ? -': R_star,
                      'h_R[calc_s]# h/R (-) ? -': h_R}
            
    return q_s, inner_ratio, save_parameter


def fugro_shaft_clay(q_t, sigv0_, sigv0, z, z_tip):

    inner_ratio = 0

    h = z_tip - z

    Q_t = (1000*max(1e-10, q_t) - sigv0)/max(1e-10, sigv0_)
    q_s = min(0.08, 0.16*np.power(max(1e-10, h/1), -0.3)*np.power(Q_t, -0.4))

    save_parameter = {'q_t[input_s]# q<sub>t</sub> (MPa) ? -': q_t,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'sigv0[input_s]# σ<sub>v</sub> (kPa) ? -': sigv0,
                      'Q_t[input_s]# Q<sub>t</sub> (-) ? -': Q_t,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h}
            
    return q_s, inner_ratio, save_parameter

# %% --- SHAFT SAND ---

def cpt_shaft_sand(q_c, sbt, case, calculation_dict, kf_p=0.001, kf_h=0.003):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1
    
    if 'most_probable' in case.lower():
        k_f = kf_p
    elif 'highest' in case.lower():
        k_f = kf_h
    elif 'tailored' in case.lower():
        match = re.search(r'\[([0-9.+-eE]+)\]', case)
        k_f = float(match.group(1))
    elif 'sbt' in case.lower():
        if 'be' in case.lower():
            matrix = {'SD': 0.0011,
                      'CD': 0.028,
                      'TD': 0.018,
                      'SC': 0.13,
                      'CC': 0.019,
                      'TC': 0.005}
        elif 'le' in case.lower():
            matrix = {'SD': 0.00095,
                      'CD': 0.015,
                      'TD': 0.005,
                      'SC': 0.05,
                      'CC': 0.019,
                      'TC': 0.074}
        elif 'he' in case.lower():
            matrix = {'SD': 0.0012,
                      'CD': 0.045,
                      'TD': 0.038,
                      'SC': 0.25,
                      'CC': 0.1,
                      'TC': 0.35}
        if sbt in matrix:
            k_f = matrix[sbt]
        else:
            k_f = matrix['SD']

    q_s = q_c*k_f

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_f[calc_s]# k<sub>s</sub> (-) ? -': k_f}
        
    return q_s, inner_ratio, save_parameter


def almhamre_shaft_sand(q_c, sigv0_, z, z_tip, d_r, case, calculation_dict, k_ss=0.2, patm=100):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1
    
    if 'be' in case:
        multiplier = 1
    elif 'he' in case:
        multiplier = 1.25

    q_c = max(0.001, q_c)
    sigv0_ = max(0.001, sigv0_)

    if d_r < 15:
        delta_int = 15
    elif d_r < 35:
        delta_int = 20
    elif d_r < 65:
        delta_int = 25
    elif d_r < 85:
        delta_int = 30
    else:
        delta_int = 35
        
    k = np.power(1000*q_c/sigv0_, 0.5)/80
    K = 0.0066*1000*q_c*(sigv0_/patm)**0.13/sigv0_

    qs_init = 0.001*K*sigv0_*math.tan(math.radians(delta_int))
    qs_res = k_ss*qs_init
    h = z_tip - z
    q_s = multiplier*(qs_res + (qs_init - qs_res)*math.exp(-k*h))
    
    q_s = max(0, q_s)

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      'd_r[input_s]# D<sub>r</sub> (%) ? -': d_r,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'delta_int[calc_s]': delta_int,
                      'k[calc_s]# k (-) ? -': k,
                      'K[calc_s]# K (-) ? -': K,
                      'k_ss[calc_s]# k<sub>ss</sub> (-) ? -': k_ss,
                      'qs_res[calc_s]# q<sub>s,res</sub> (MPa) ? -': qs_res,
                      'qs_init[calc_s]# q<sub>s,ini</sub> (MPa) ? -': qs_init,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'mult[calc_s]# mult (-) ? -': multiplier}
    
    return q_s, inner_ratio, save_parameter


def beta_dnv_shaft_sand(phi, phi_rep, sigv0_, calculation_dict, c=0, r=0.66):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1
    
    tan_phi = math.tan(math.radians(phi))
    tan_delta_int = r*tan_phi
    delta_int = np.degrees(np.atan(tan_delta_int))

    # if calc_type in ['installation']:
    #     K = np.interp(min(45, max(26.6, phi_rep)), [26.6, 28.8, 31, 33, 35, 36.9, 38.7, 40.4, 42, 43.5, 45], [4.1, 4.7, 5.5, 6.3, 7.3, 8.6, 9.9, 10.7, 13.2, 15.3, 17.8])
    # elif calc_type in ['capacity'] or calc_type == 'plug_bearing_installation':
    #     K = 0.8

    K = 0.8

    a = c * 1 / np.tan(np.radians(phi))
    q_s = 0.001*(a + K*sigv0_*tan_delta_int) ## HERE ##
        
    save_parameter = {'phi[input_s]# φ (deg) ? -': phi,
                      'tan_phi[calc_s]#  tan(φ) (-) ? -': tan_phi,
                      'r[calc_s]# r (-) ? -': r,
                      'tan_delta_int[calc_s]# tan(δ) (-) ? -': tan_delta_int,
                      'delta_int[calc_s]# δ (deg) ? -': delta_int,
                      'K[calc_s]# K (-) ? -': K,
                      'a[calc_s]# a (-) ? -': a}
        
    return q_s, inner_ratio, save_parameter


def beta_iso_api_shaft_sand(d_r, sigv0_, calculation_dict):

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 1
    
    if d_r >= 85:
        q_s_lim = 0.115
        beta = 0.56
    elif d_r >= 65:
        q_s_lim = 0.096
        beta = 0.46
    elif d_r >= 35:
        q_s_lim = 0.081
        beta = 0.37
    else:
        q_s_lim = 0.067
        beta = 0.29
        
    q_s = 0.001*sigv0_*beta
    
    if q_s > q_s_lim:
        q_s = q_s_lim

    save_parameter = {'d_r[input_s]# D<sub>r</sub> (%) ? -': d_r,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'q_s_lim[calc_s]# q<sub>s,lim</sub> (MPa) ? -': q_s_lim,
                      'beta[calc_s]# β (-) ? -': beta}
    
    return q_s, inner_ratio, save_parameter


def ucpt_shaft_sand(q_c, sigv0_, z, z_tip, I_c, delta_int, calculation_dict, f_direction, d_cpt):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    if f_direction.lower() == 'compression':
        ft_fc = 1
    elif f_direction.lower() == 'tension':
        ft_fc = 0.75
        
    PLR = math.tanh(0.3*np.power(D_i/d_cpt, 0.5))
        
    A_r_eff = 1 - PLR*np.power(D_i/D, 2)
            
    h = z_tip - z
    h_D = h/D
    
    q_c = max(0.001, q_c)

    if sigv0_ == 0:
        sigv0_ = 1e-10

    if I_c > 2.05 and I_c < 2.5:
        i_c_corr = 3.93*np.power(I_c, 2) - 14.78*I_c + 14.78
    else:
        i_c_corr = 1
    
    sig_rc_ = (i_c_corr*q_c/44)*np.power(A_r_eff, 0.3)*np.power(max(1, h_D), -0.4)
    
    dsig_rd_ = (i_c_corr*q_c/10)*np.power(1000*i_c_corr*q_c/sigv0_, -0.33)*d_cpt/D
        
    q_s = (ft_fc)*(sig_rc_ + dsig_rd_)*np.tan(np.radians(delta_int))

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'I_c[input_s]# I<sub>c</sub> (-) ? -': I_c,
                      'delta_int[input_s]# δ<sub>int</sub> (deg) ? -': delta_int,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'PLR[calc_s]# PLR (-) ? -': PLR,
                      'A_r_eff[calc_s]# A<sub>r,eff</sub> (m<super>2</super>) ? -': A_r_eff,
                      'i_c_corr[calc_s]# I<sub>c,corr</sub> (-) ? -': i_c_corr,
                      'ft_fc[calc_s]# f<sub>t</sub>/f<sub>c</sub> (-) ? -': ft_fc,
                      "sig_rc_[calc_s]# σ'<sub>rc</sub> (kPa) ? -": sig_rc_,
                      "dsig_rd_[calc_s]# dσ'<sub>rd</sub> (kPa) ? -": dsig_rd_}
    
    return q_s, inner_ratio, save_parameter


def ngi_shaft_sand(q_c, sigv0_, z, z_tip, calculation_dict, f_direction, material='steel'):

    d_r_ngi = max(0.1, 0.4*math.log(1000*max(1e-10, q_c) / (22*np.power(max(1e-10, sigv0_)*100, 0.5))))
    F_dr = 2.1*np.power(d_r_ngi - 0.1, 1.7)
    F_sig = np.power(sigv0_/100, 0.25)

    if f_direction.lower() == 'compression':
        F_load = 1.3
    elif f_direction.lower() == 'tension':
        F_load = 1.0

    F_tip = 1

    if 'plugged' in calculation_dict['calculation_method']:
        inner_ratio = 0
    else:
        inner_ratio = 3
    
    if material.lower() == 'steel':
        F_mat = 1.0
    elif material.lower() == 'concrete':
        F_mat = 1.2

    q_s = max(0.001*0.1*sigv0_ (z/max(1e-10, z_tip))*0.1*F_dr*F_sig*F_tip*F_load*F_mat)

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'd_r_ngi[calc_s]# D<sub>r,NGI</sub> (%) ? -': 100*d_r_ngi,
                      'F_dr[calc_s]# F<sub>dr</sub> (-) ? -': F_dr,
                      'F_sig[calc_s]# F<sub>σ</sub> (-) ? -': F_sig,
                      'F_load[calc_s]# F<sub>load</sub> (-) ? -': F_load,
                      'F_tip[calc_s]# F<sub>tip</sub> (-) ? -': F_tip,
                      'F_mat[calc_s]# F<sub>mat</sub> (-) ? -': F_mat}
    
    return q_s, inner_ratio, save_parameter


def icp_shaft_sand(q_c, sigv0_, z, z_tip, delta_int, calculation_dict, f_direction, dr=2e-5):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']
    
    if f_direction.lower() == 'compression':
        a = 1
        b = 1
    elif f_direction.lower() == 'tension':
        if 'plugged' in calculation_dict['calculation_method']:
            a = 1
        else:
            a = 0.9
        b = 0.8
                        
    h = z_tip - z
    R = D/2
    R_i = D_i/2
    R_star = np.power(np.power(R, 2) - np.power(R_i, 2), 0.5)
    
    if 'plugged' in calculation_dict['calculation_method']:
        h_R = max(h/R, 8)  
    else:
        h_R = max(h/R_star, 8)
        
    sig_rc_ = 0.029*max(0.001, q_c)*np.power(sigv0_/100, 0.13)*np.power(h_R, -0.38)

    A = 0.0203
    B = 0.00125
    C = 1.216e-6
    nu = q_c*np.power(0.1*max(1e-10, sigv0_)/1000, -0.5)
    G = q_c*np.power(A + B*nu - C*np.power(nu, 2), -1)
        
    dsig_rd_ = 2*G*dr/R
            
    q_s = a*(b*sig_rc_ + dsig_rd_)*math.tan(np.radians(delta_int))

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'R_star[calc_s]# R* (-) ? -': R_star,
                      'G[calc_s]# G (MPa) ? -': G,
                      'h_R[calc_s]# h/R (-) ? -': h_R,
                      "sig_rc_[calc_s]# σ'<sub>rc</sub> (kPa) ? -": sig_rc_,
                      "dsig_rd_[calc_s]# dσ'<sub>rd</sub> (kPa) ? -": dsig_rd_,
                      'dr[calc_s]# d<sub>r</sub> (-) ? -': dr,
                      'a[calc_s]# a (-) ? -': a,
                      'b[calc_s]# b (-) ? -': b}
            
    return q_s, inner_ratio, save_parameter


def uwa_shaft_sand(q_c, sigv0_, z, z_tip, delta_int, calculation_dict, f_direction, dr=2e-5):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    if f_direction.lower() == 'compression':
        ft_fc = 1
    elif f_direction.lower() == 'tension':
        ft_fc = 0.75
        
    IFR = min(1, np.power(D_i/1.5, 0.2))
        
    A_r_eff = 1 - IFR*np.power(D_i/D, 2)
            
    h = z_tip - z
    h_D = max(2, h/D)
    
    sig_rc = 0.03*q_c*np.power(A_r_eff, 0.3)*np.power(h_D, -0.5)
    
    q_c1N = (max(1e-10, q_c)/0.1)/np.power(max(1e-10, sigv0_)/100, 0.5)
    G = q_c*185*np.power(q_c1N, -0.7)
        
    dsig_rd_ = 4*G*dr/D

    tan_delta = min(0.55, np.tan(np.radians(delta_int)))
        
    q_s = (ft_fc)*(sig_rc + dsig_rd_)*tan_delta

    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'delta_int[input_s]# δ<sub>int</sub> (deg) ? -': delta_int,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'h_D[calc_s]# h/D (-) ? -': h_D,
                      'IFR[calc_s]# IFR (-) ? -': IFR,
                      'A_r_eff[calc_s]# A<sub>r,eff</sub> (m<super>2</super>) ? -': A_r_eff,
                      'ft_fc[calc_s]# f<sub>t</sub>/<sub>c</sub> (-) ? -': ft_fc,
                      "sig_rc[calc_s]# σ'<sub>rc</sub> (kPa) ? -": sig_rc,
                      "dsig_rd_[calc_s]# dσ'<sub>rd</sub> (kPa) ? -": dsig_rd_}
    
    return q_s, inner_ratio, save_parameter


def fugro_shaft_sand(q_c, sigv0_, z, z_tip, calculation_dict, f_direction, min_h_D=0.1):

    inner_ratio = 0

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    h = z_tip - z
    R = D/2
    R_i = D_i/2
    R_star = np.power(np.power(R, 2) - np.power(R_i, 2), 0.5)
    h_R_star = max(min_h_D, h/R_star)

    if f_direction.lower() == 'compression':
        if h_R_star >= 4:
            q_s = 0.08*q_c*np.power(sigv0_/100, 0.05)*np.power(h_R_star, -0.9)
        else:
            q_s = 0.08*q_c*np.power(sigv0_/100, 0.05)*np.power(4, -0.9)*(h_R_star/4)

    elif f_direction.lower() == 'tension':
        q_s = 0.045*q_c*np.power(sigv0_/100, 0.15)*np.power(max(h_R_star, 4), -0.85)
       
    save_parameter = {'q_c[input_s]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_s]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'z_tip[calc_s]# z<sub>tip</sub> (m) ? -': z_tip,
                      'h[calc_s]# h (m) ? -': h,
                      'R_star[calc_s]# R* (-) ? -': R_star,
                      'h_R_star[calc_s]# h/R (-) ? -': h_R_star}
    
    return q_s, inner_ratio, save_parameter

# %% --- SHAFT RESISTANCE, QS

def shaft_resistance(depth_i, soil_data_dis_dict, dl_s,
                     capacity_dict, f_direction, pf_soil_mat, clay_reconsolidation_time,
                     a_shaft_diff_dis, a_shaft_global_dis,
                     calculation_method, calc_type,
                     d_z_gdb,
                     d_cpt,
                     removal=False,
                     conductor={}):  
    
    shaft_parameter_inc = []

    for idx, (a_shaft_diff_dis_i, a_shaft_global_dis_i) in enumerate(zip(a_shaft_diff_dis, a_shaft_global_dis)):

        z_end_section_i, a_shaft_outer_diff_i, a_shaft_inner_diff_i, b_outer_diff_i, t_diff_i = a_shaft_diff_dis_i[0], a_shaft_diff_dis_i[1], a_shaft_diff_dis_i[2], a_shaft_diff_dis_i[3], a_shaft_diff_dis_i[4]
        b_outer_i, t_i = a_shaft_diff_dis_i[3], a_shaft_diff_dis_i[4]
        b_inner_i = b_outer_i - 2*t_i
       
        try:
            z_start_section_i = a_shaft_diff_dis[idx + 1][0]
        except Exception:
            z_start_section_i = 0
        
        depth_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'depth')
        mask = ((depth_total_dis <= round(depth_i, 2)) & (depth_total_dis >= round(z_start_section_i, 2)) & (depth_total_dis <= round(z_end_section_i, 2)))
                                
        depth_in_soil_dis = depth_total_dis[mask]
        length = len(depth_in_soil_dis)

        soil_type_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'Soil_Type', mask=mask, length=length)
        sbt_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sbt', mask=mask, length=length)

        p_0__dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sigveff_rep', mask=mask, length=length)
        p_0_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sigv_rep', mask=mask, length=length)

        q_c_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'qc_{dl_s}', mask=mask, length=length)
        f_s_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'fs_{dl_s}', mask=mask, length=length)
        q_t_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'qt_{dl_s}', mask=mask, length=length)

        s_u_c_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'suc_{dl_s}', mask=mask, length=length)
        phi_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'phi_{dl_s}', mask=mask, length=length)
        phi_rep_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'phi_best{dl_s}', mask=mask, length=length)
        d_r_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'dr_{dl_s}', mask=mask, length=length)

        dss_suc_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sud-suc_rep', mask=mask, length=length)
        uu_suc_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'suuu-suc_rep', mask=mask, length=length)

        i_c_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'ic', mask=mask, length=length)
        i_p_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'plasticity_rep', mask=mask, length=length)
        ocr_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'ocr_rep', mask=mask, length=length)
        st_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sensitivity_rep', mask=mask, length=length)
        
        if removal:
            alpha_key = f'alfaavg_{clay_reconsolidation_time}_removal_rep'
        else:
            alpha_key = f'alfaavg_{clay_reconsolidation_time}_rep'

        alpha_s_dis = bf.extract_array_from_dl(soil_data_dis_dict, alpha_key, mask=mask, length=length)
        
        if calc_type in ['capacity']:
            delta_key = 'delta_res_rep'
        elif calc_type in ['installation', 'plug_bearing_installation', 'plug_bearing_removal']:
            delta_key = 'delta_peak_rep'

        delta_int_dis = bf.extract_array_from_dl(soil_data_dis_dict, delta_key, mask=mask, length=length)

        l_s = 0

        for idx2 in range(len(depth_in_soil_dis)):
            depth_ii_1 = depth_in_soil_dis[idx2]
            if idx2 != 0:
                depth_ii_2 = depth_in_soil_dis[idx2-1]
                d_z_gdb = depth_ii_1 - depth_ii_2
            else:
                d_z_gdb = d_z_gdb

            soil_type_ii = soil_type_dis[idx2]
            p_0__ii = p_0__dis[idx2]
            p_0_ii = p_0_dis[idx2]
            q_c_s_ii = q_c_s_dis[idx2]
            f_s_s_ii = f_s_s_dis[idx2]
            q_t_s_ii = q_t_s_dis[idx2]
            sbt_ii = sbt_dis[idx2]
            s_u_c_s_ii = s_u_c_s_dis[idx2]
            phi_s_ii = phi_s_dis[idx2]
            phi_rep_s_ii = phi_rep_s_dis[idx2]
            d_r_s_ii = d_r_s_dis[idx2]
            alpha_s_ii = alpha_s_dis[idx2]
            dss_suc_ii = dss_suc_dis[idx2]
            uu_suc_ii = uu_suc_dis[idx2]
            i_c_ii = i_c_dis[idx2]
            i_p_ii = i_p_dis[idx2]
            ocr_ii = ocr_dis[idx2]
            st_ii = st_dis[idx2]
            delta_int_ii = delta_int_dis[idx2]

            a_shaft_outer_diff_ii = max(1e-10, a_shaft_outer_diff_i)
            a_shaft_inner_diff_ii = a_shaft_inner_diff_i
            b_outer_diff_ii = b_outer_diff_i

            calculation_dict = {'calculation_method': calculation_method.lower(),
                                'b_outer': b_outer_i,
                                'b_inner': b_inner_i,
                                'calc_type': calc_type}
            
            if soil_type_ii.lower() in ['c', 'c_s']:

                sub_capacity_entry = 'clay_shaft'

                # ALPHA METHOD, DNV, CLAY
                if 'alpha_dnv' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = alpha_dnv_shaft_clay(s_u_c_s_ii, alpha_s_ii, dss_suc_ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"alpha_dnv_shaft_clay"}": value for key, value in save_parameter_ii.items()}

                # ALPHA METHOD, ISO + API, CLAY
                elif 'alpha_iso' in capacity_dict[sub_capacity_entry].lower() or 'alpha_api' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = alpha_iso_api_shaft_clay(s_u_c_s_ii, p_0__ii, dss_suc_ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"alpha_iso_api_shaft_clay"}": value for key, value in save_parameter_ii.items()}

                # ALM & HAMRE METHOD, CLAY
                elif 'alm_hamre' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = almhamre_shaft_clay(q_c_s_ii, f_s_s_ii, p_0__ii, depth_ii_1, depth_i, capacity_dict[sub_capacity_entry].lower(), calculation_dict)
                    save_parameter_ii = {f"{key}${"almhamre_shaft_clay"}": value for key, value in save_parameter_ii.items()}
                
                # UNIFIED CPT METHOD, CLAY
                elif 'ucpt' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = ucpt_shaft_clay(q_t_s_ii, depth_ii_1, depth_i, calculation_dict)
                    save_parameter_ii = {f"{key}${"ucpt_shaft_clay"}": value for key, value in save_parameter_ii.items()}
                
                # CPT METHOD, CLAY
                elif 'cpt' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = cpt_shaft_clay(q_c_s_ii, sbt_ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)
                    save_parameter_ii = {f"{key}${"cpt_shaft_clay"}": value for key, value in save_parameter_ii.items()}

                # NGI-05 METHOD, CLAY
                elif 'ngi' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = ngi_shaft_clay(s_u_c_s_ii, p_0__ii, uu_suc_ii, i_p_ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"ngi_shaft_clay"}": value for key, value in save_parameter_ii.items()}

                # ICP METHOD, CLAY
                elif 'icp' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = icp_shaft_clay(p_0__ii, ocr_ii, depth_ii_1, depth_i, st_ii, delta_int_ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"icp_shaft_clay"}": value for key, value in save_parameter_ii.items()}

                # UWA METHOD, CLAY
                elif 'uwa' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = uwa_shaft_clay(q_t_s_ii, p_0__ii, depth_ii_1, depth_i, delta_int_ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"uwa_shaft_clay"}": value for key, value in save_parameter_ii.items()}

                # FUGRO METHOD, CLAY
                elif 'fugro' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = fugro_shaft_clay(q_t_s_ii, p_0__ii, p_0_ii, depth_ii_1, depth_i)
                    save_parameter_ii = {f"{key}${"fugro_shaft_clay"}": value for key, value in save_parameter_ii.items()}
                
                else:
                    q_s_ii, inner_ratio_ii, save_parameter_ii = 0, 0, {}
                    print(f'Error at q_s for {capacity_dict[sub_capacity_entry].lower()}')

            elif soil_type_ii.lower() in ['s', 's_c', 'si']:
                
                if idx2 > 0:
                    l_s += d_z_gdb

                sub_capacity_entry = 'sand_shaft'
                
                # BETA METHOD, DNV, SAND
                if 'beta_dnv' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = beta_dnv_shaft_sand(phi_s_ii, phi_rep_s_ii, p_0__ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"beta_dnv_shaft_sand"}": value for key, value in save_parameter_ii.items()}
                
                # BETA METHOD, ISO + API, SAND
                elif 'beta_iso' in capacity_dict[sub_capacity_entry].lower() or 'beta_api' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = beta_iso_api_shaft_sand(d_r_s_ii, p_0__ii, calculation_dict)
                    save_parameter_ii = {f"{key}${"beta_iso_api_shaft_sand"}": value for key, value in save_parameter_ii.items()}

                # ALM & HAMRE METHOD, SAND
                elif 'alm_hamre' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = almhamre_shaft_sand(q_c_s_ii, p_0__ii, depth_ii_1, depth_i, d_r_s_ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)
                    save_parameter_ii = {f"{key}${"almhamre_shaft_sand"}": value for key, value in save_parameter_ii.items()}

                # UNIFIED CPT METHOD, SAND
                elif 'ucpt' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = ucpt_shaft_sand(q_c_s_ii, p_0__ii, depth_ii_1, depth_i, i_c_ii, delta_int_ii, calculation_dict, f_direction, d_cpt)
                    save_parameter_ii = {f"{key}${"ucpt_shaft_sand"}": value for key, value in save_parameter_ii.items()}
                
                # CPT METHOD, SAND
                elif 'cpt' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = cpt_shaft_sand(q_c_s_ii, sbt_ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)
                    save_parameter_ii = {f"{key}${"cpt_shaft_sand"}": value for key, value in save_parameter_ii.items()}

                # NGI-99 METHOD, SAND
                elif 'ngi' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = ngi_shaft_sand(q_c_s_ii, p_0__ii, depth_ii_1, depth_i, calculation_dict, f_direction)
                    save_parameter_ii = {f"{key}${"ngi_shaft_sand"}": value for key, value in save_parameter_ii.items()}

                # ICP METHOD, SAND
                elif 'icp' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = icp_shaft_sand(q_c_s_ii, p_0__ii, depth_ii_1, depth_i, delta_int_ii, calculation_dict, f_direction)
                    save_parameter_ii = {f"{key}${"icp_shaft_sand"}": value for key, value in save_parameter_ii.items()}

                # UWA METHOD, SAND
                elif 'uwa' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = uwa_shaft_sand(q_c_s_ii, p_0__ii, depth_ii_1, depth_i, delta_int_ii, calculation_dict, f_direction)
                    save_parameter_ii = {f"{key}${"uwa_shaft_sand"}": value for key, value in save_parameter_ii.items()}

                # FUGRO METHOD, SAND
                elif 'fugro' in capacity_dict[sub_capacity_entry].lower():
                    q_s_ii, inner_ratio_ii, save_parameter_ii = fugro_shaft_sand(q_c_s_ii, p_0__ii, depth_ii_1, depth_i, calculation_dict, f_direction)
                    save_parameter_ii = {f"{key}${"fugro_shaft_sand"}": value for key, value in save_parameter_ii.items()}
                
                else:
                    q_s_ii, inner_ratio_ii, save_parameter_ii = 0, 0, {}
                    print(f'Error at q_s for {capacity_dict[sub_capacity_entry].lower()}')

            if 'conductor_analysis' in conductor:
                if conductor['conductor_analysis']:
                    grout_lim = conductor['conductor_grout_strength_limit']
                    b_outer_conductor = conductor['conductor_borehole_diameter']
                    interface_reduction_factor = conductor['conductor_interface_reduction_factor']
                    q_s_ii = interface_reduction_factor*min(q_s_ii, 0.001*grout_lim*b_outer_conductor/b_outer_i)
                    a_shaft_outer_diff_ii = np.pi*conductor['conductor_borehole_diameter']

            if calc_type == 'capacity': 
                q_s_ii = q_s_ii/pf_soil_mat
            elif calc_type == 'installation':
                q_s_ii = q_s_ii*pf_soil_mat
            elif calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
                q_s_ii = q_s_ii/pf_soil_mat

            Q_s_i = a_shaft_outer_diff_ii*d_z_gdb*q_s_ii

            inner_ratio_applied_ii = inner_ratio_ii * (a_shaft_inner_diff_ii/a_shaft_outer_diff_ii)
            Q_s_inner_section_i = Q_s_i*inner_ratio_applied_ii
            Q_s_outer_section_i =  Q_s_i

            if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
                save_parameter_ii = {key.replace('_s]', '_ps]'): value for key, value in save_parameter_ii.items()}
                save_parameter_ii['soil_type_ps_section_' + str(idx+1) + '[input_ps]# - ? Section'+str(idx+1)] = soil_type_ii
                save_parameter_ii['z_ps_section_' + str(idx+1) + '[input_ps]# z (m) ? Section'+str(idx+1)] = float(depth_ii_1)
                save_parameter_ii['q_ps_section_' + str(idx+1) + '[calc_ps2]# q<sub>s,pb</sub> (MPa) ? Section'+str(idx+1)] = float(q_s_ii)
                save_parameter_ii['a_ps_inner_section_' + str(idx+1) + '[geometry_ps]# A<sub>s,pb</sub> (m<super>2</super>) ? Section'+str(idx+1)] = inner_ratio_ii*a_shaft_inner_diff_ii
                save_parameter_ii['Q_ps_inner_section_' + str(idx+1) + '[calc_ps3]# ΔQ<sub>s,pb</sub> (MN ? Section'+str(idx+1)] = Q_s_inner_section_i
                save_parameter_ii['pf_soil_mat[input_ps]# γ<sub>m</sub> (-) ? -'] = pf_soil_mat
            else:
                save_parameter_ii['soil_type_s_section_' + str(idx+1) + '[input_s]# - ? Section'+str(idx+1)] = soil_type_ii
                save_parameter_ii['z_s_section_' + str(idx+1) + '[input_s]#  z (m) ? Section'+str(idx+1)] = float(depth_ii_1)
                save_parameter_ii['q_s_section_' + str(idx+1) + '[calc_s2]# q<sub>s</sub> (MPa) ? Section'+str(idx+1)] = float(q_s_ii)
                save_parameter_ii['di_do_ratio_section_' + str(idx+1) + '[geometry_s]# A<sub>i</sub>/A<sub>o</sub> ? Section'+str(idx+1)] = a_shaft_inner_diff_ii/a_shaft_outer_diff_ii
                save_parameter_ii['a_s_inner_section_' + str(idx+1) + '[geometry_s]# A<sub>s,inner</sub> (m<super>2</super>) ? Section'+str(idx+1)] = inner_ratio_ii*a_shaft_inner_diff_ii
                save_parameter_ii['a_s_outer_section_' + str(idx+1) + '[geometry_s]# A<sub>s,outer</sub> (m<super>2</super>) ? Section'+str(idx+1)] = a_shaft_outer_diff_ii
                save_parameter_ii['a_s_total_section_' + str(idx+1) + '[geometry_s]# A<sub>s</sub> (m<super>2</super>) ? Section'+str(idx+1)] = a_shaft_outer_diff_ii + inner_ratio_ii*a_shaft_inner_diff_ii
                save_parameter_ii['Q_s_inner_section_' + str(idx+1) + '[calc_s3]# ΔQ<sub>s,inner</sub> (MN) ? Section'+str(idx+1)] = Q_s_inner_section_i
                save_parameter_ii['Q_s_outer_section_' + str(idx+1) + '[calc_s3]# ΔQ<sub>s,outer</sub> (MN) ? Section'+str(idx+1)] = Q_s_outer_section_i
                save_parameter_ii['Q_s_total_section_' + str(idx+1) + '[calc_s3]# ΔQ<sub>s</sub> (MN) ? Section'+str(idx+1)] = Q_s_inner_section_i + Q_s_outer_section_i
                save_parameter_ii['pf_soil_mat[input_s]# γ<sub>m</sub> (-) ? -'] = pf_soil_mat
     
            shaft_parameter_inc.append(save_parameter_ii)

    Q_s_inner = 0
    Q_s_outer = 0

    if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
        Q_ps_inner = 0

    for save_parameter_ii in shaft_parameter_inc:
        for key in save_parameter_ii:
            if 'Q_s_inner' in key:
                Q_s_inner = Q_s_inner + save_parameter_ii[key]
            if 'Q_s_outer' in key:
                Q_s_outer = Q_s_outer + save_parameter_ii[key]
            if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
                if 'Q_ps' in key:
                    Q_ps_inner = Q_ps_inner + save_parameter_ii[key]
    
    if calc_type not in ['plug_bearing_installation', 'plug_bearing_removal']: 
        Q_s_total = Q_s_outer + Q_s_inner

    if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
        results_dict_shaft = {'Q_ps_inner[output_ps]# Q<sub>s,pb</sub> (MN) ? -': Q_ps_inner,
                              'shaft_parameter_inc_plug_bearing': shaft_parameter_inc,
                              'pf_soil_mat[input_ps]# γ<sub>m,pb</sub> (-) ? -': pf_soil_mat}
    else:
        results_dict_shaft = {'Q_s_total[output_s]# Q<sub>s</sub> (MN) ? -': Q_s_total,
                              'Q_s_inner[output_s]# Q<sub>s,inner</sub> (MN) ? -': Q_s_inner,
                              'Q_s_outer[output_s]# Q<sub>s,outer</sub> (MN) ? -': Q_s_outer,
                              'shaft_parameter_inc': shaft_parameter_inc,
                              'pf_soil_mat[input]# γ<sub>m</sub> (-) ? -': pf_soil_mat}
    
    return results_dict_shaft