# python modules
import math
import numpy as np
import re

# multiconsult modules
import _background_functions as bf

# %% --- BASE CLAY ---

def cpt_base_clay(q_c, sbt, case, calculation_dict, kp_p=0.4, kp_h=0.6):
    
    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    if 'most_probable' in case.lower():
        k_p = kp_p
    elif 'highest' in case.lower():
        k_p = kp_h
    elif 'tailored' in case.lower():
        match = re.search(r'\[([0-9.+-eE]+)\]', case)
        k_p = float(match.group(1))
    elif 'sbt' in case.lower():
        if 'be' in case.lower():
            matrix = {'SD': 0.12,
                      'CD': 0.66,
                      'TD': 0.47,
                      'SC': 1.1,
                      'CC': 4.6,
                      'TC': 2.5}
        elif 'le' in case.lower():
            matrix = {'SD': 0.1,
                      'CD': 0.3,
                      'TD': 0.3,
                      'SC': 0.25,
                      'CC': 0.1,
                      'TC': 1}
        elif 'he' in case.lower():
            matrix = {'SD': 0.13,
                      'CD': 0.9,
                      'TD': 0.6,
                      'SC': 2.5,
                      'CC': 8,
                      'TC': 5}
        if sbt in matrix:
            k_p = matrix[sbt]
        else:
            k_p = matrix['CD']

    q_b = q_c*k_p

    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_p[calc_b]# k<sub>p</sub> (-) ? -': k_p,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def almhamre_base_clay(q_c, case, calculation_dict, k_tc=0.6):
    
    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    if 'be' in case.lower():
        multiplier = 1
    elif 'he' in case.lower():
        multiplier = 1.25

    q_c = max(0.001, q_c)
    
    q_b = multiplier*k_tc*q_c

    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_tc[calc_b]# k<sub>t,c</sub> (-) ? -': k_tc,
                      'mult[calc_b]# mult (-) ? -': multiplier,
                      'plug_output[output_b]# - ? -': plug_output}
        
    return q_b, a_base, base_influence, plug_output, save_parameter


# def bc_dnv_base_shallow_clay(z, s_u_c, dss_suc, sue_suc, sigv0_, D, calculation_dict, N_c_0=6.2, N_c_lim=9):

# TO BE UPDATED
    
#     N_c = N_c_0*(1 + 0.34*math.atan(z/D))
#     a_base = calculation_dict['area_plug_diff']
#     base_influence = calculation_dict['b_outer_diff']
#     N_c = min(N_c, N_c_lim)

#     s_u_dss = s_u_c*dss_suc
#     s_u_e = s_u_c*sue_suc
#     s_u_ave = (s_u_c + s_u_dss + s_u_e)/3
    
#     if calculation_dict['calc_type'] != 'plug_bearing_installation':
#         q_b = 0.001*(N_c*s_u_c + sigv0_)
#     else:
#         q_b = 0.001*N_c*s_u_c*0.9

#     save_parameter = {'s_u_c[input_b]': s_u_c,
#                       's_u_dss[input_b]': s_u_dss,
#                       'dss_suc[input_b]': dss_suc,
#                       's_u_e[input_b]': s_u_e,
#                       'sue_suc[input_b]': sue_suc,
#                       's_u_ave[input_b]': s_u_ave,
#                       'sigv0_[input_b]': sigv0_,
#                       'N_c[bc_dnv_shallow_clay_b]': N_c}
    
#     return q_b, a_base, base_influence, save_parameter


def bc_dnv_base_deep_clay(s_u_c, dss_suc, sue_suc, sigv0_, calculation_dict):

    # TO BE CHECKED
    
    N_c = 7.5
    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    s_u_dss = s_u_c*dss_suc
    s_u_e = s_u_c*sue_suc
    s_u_ave = (s_u_c + s_u_dss + s_u_e)/3
    
    if 'plug_bearing' in calculation_dict['calc_type']:
        q_b = 0.001*(N_c*s_u_c + sigv0_)
    else:
        q_b = 0.001*N_c*s_u_c*0.9

    save_parameter = {'s_u_c[input_b]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      's_u_dss[input_b]# s<sub>u,d</sub> (kPa) ? -': s_u_dss,
                      'dss_suc[input_b]# s<sub>u,d</sub>/s<sub>u,c</sub> (-) ? -': dss_suc,
                      's_u_e[input_b]# s<sub>u,e</sub> (kPa) ? -': s_u_e,
                      'sue_suc[input_b]# s<sub>u,e</sub>/s<sub>u,c</sub> (-) ? -': sue_suc,
                      's_u_ave[input_b]# s<sub>u,ave</sub> (kPa) ? -': s_u_ave,
                      "sigv0_[input_b]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'N_c[calc_b]# N<sub>c</sub> (-) ? -': N_c,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


# def bc_iso_base_shallow_clay(s_u_c, dss_suc, sue_suc, sigv0_, calculation_dict, N_c=9):

# TO BE UPDATED
        
#     if 'plugged' in calculation_dict['calculation_method']:
#         a_base = calculation_dict['area_plug_diff']
#         base_influence = calculation_dict['b_outer_diff']
#     else:
#         a_base = calculation_dict['area_core_diff']
#         base_influence = calculation_dict['t_diff']

#     s_u_dss = s_u_c*dss_suc
#     s_u_e = s_u_c*sue_suc
#     s_u_ave = (s_u_c + s_u_dss + s_u_e)/3
    
#     q_b = 0.001*N_c*s_u_c*0.9

#     save_parameter = {'s_u_c[input_b]': s_u_c,
#                       's_u_dss[input_b]': s_u_dss,
#                       'dss_suc[input_b]': dss_suc,
#                       's_u_e[input_b]': s_u_e,
#                       'sue_suc[input_b]': sue_suc,
#                       's_u_ave[input_b]': s_u_ave,
#                       'sigv0_[input_b]': sigv0_,
#                       'N_c[bc_iso_deep_clay_b]': N_c}
    
#     return q_b, a_base, base_influence, save_parameter
    

def bc_iso_base_deep_clay(s_u_c, dss_suc, sue_suc, calculation_dict, N_c=9):
        
    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    s_u_dss = s_u_c*dss_suc
    s_u_e = s_u_c*sue_suc
    s_u_ave = (s_u_c + s_u_dss + s_u_e)/3
    
    q_b = 0.001*N_c*s_u_c*0.9

    save_parameter = {'s_u_c[input_b]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      's_u_dss[input_b]# s<sub>u,dss</sub> (kPa) ? -': s_u_dss,
                      'dss_suc[input_b]# s<sub>u,d</sub>/s<sub>u,c</sub> (-) ? -': dss_suc,
                      's_u_e[input_b]# s<sub>u,e</sub> (kPa) ? -': s_u_e,
                      'sue_suc[input_b]# s<sub>u,e</sub>/s<sub>u,c</sub> (-) ? -': sue_suc,
                      's_u_ave[input_b]# s<sub>u,ave</sub> (kPa) ? -': s_u_ave,
                      'N_c[calc_b]# N<sub>c</sub> (-) ? -': N_c,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


# def bc_api_base_shallow_clay(s_u_c, dss_suc, sue_suc, calculation_dict, N_c=9):

# TO BE UPDATED

#     a_base = calculation_dict['area_plug_diff']
#     base_influence = calculation_dict['b_outer_diff']

#     s_u_dss = s_u_c*dss_suc
#     s_u_e = s_u_c*sue_suc
#     s_u_ave = (s_u_c + s_u_dss + s_u_e)/3
    
#     q_b = 0.001*N_c*s_u_ave

#     save_parameter = {'s_u_c[input_b]': s_u_c,
#                       's_u_dss[input_b]': s_u_dss,
#                       'dss_suc[input_b]': dss_suc,
#                       's_u_e[input_b]': s_u_e,
#                       'sue_suc[input_b]': sue_suc,
#                       's_u_ave[input_b]': s_u_ave,
#                       'N_c[bc_api_shallow_clay_b]': N_c}
    
#     return q_b, a_base, base_influence, save_parameter


def bc_api_base_deep_clay(s_u_c, dss_suc, sue_suc, calculation_dict, N_c=9):

    # TO BE CHECKED

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    s_u_dss = s_u_c*dss_suc
    s_u_e = s_u_c*sue_suc
    s_u_ave = (s_u_c + s_u_dss + s_u_e)/3
    
    q_b = 0.001*N_c*s_u_ave

    save_parameter = {'s_u_c[input_b]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      's_u_dss[input_b]# s<sub>u,dss</sub> (kPa) ? -': s_u_dss,
                      'dss_suc[input_b]# s<sub>u,d</sub>/s<sub>u,c</sub> (-) ? -': dss_suc,
                      's_u_e[input_b]# s<sub>u,e</sub> (kPa) ? -': s_u_e,
                      'sue_suc[input_b]# s<sub>u,e</sub>/s<sub>u,c</sub> (-) ? -': sue_suc,
                      's_u_ave[input_b]# s<sub>u,ave</sub> (kPa) ? -': s_u_ave,
                      'N_c[calc_b]# N<sub>c</sub> (-) ? -': N_c,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def ucpt_base_clay(q_t_tot, z, z_tot, soil_type_tot, calculation_dict):

    a_base = calculation_dict['area_plug_diff']
    base_influence = calculation_dict['b_outer_diff']

    if 'plugged' in calculation_dict['calculation_method']:
        plug_output = 'plugged'
    else:
        plug_output = 'cored'
    
    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']
    t = calculation_dict['t']

    D_ = np.power(np.power(D, 2) - np.power(D_i, 2), 0.5)

    q_p = np.average(q_t_tot[(z_tot <= z+20*t) & (z_tot >= z) & (soil_type_tot == 'C') & (z_tot >= 0)])
    q_b = (0.2 + 0.6*np.power(D_/D, 2))*q_p

    save_parameter = {'q_p[input_b]# q<sub>p</sub> (MPa) ? -': q_p,
                      'D_[calc_b]# D<sub>eff</sub> (m) ? -': D_,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def ngi_base_clay(s_u_c, uu_suc, calculation_dict, N_c=9):

    a_base = calculation_dict['area_plug_diff']
    base_influence = calculation_dict['b_outer_diff']

    if 'plugged' in calculation_dict['calculation_method']:
        plug_output = 'plugged'
    else:
        plug_output = 'cored'
        
    s_u_uu = s_u_c*uu_suc
    
    q_b = 0.001*N_c*s_u_uu

    save_parameter = {'s_u_c[input_b]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                      'uu_suc[input_b]# s<sub>u,uu</sub>/s<sub>u,c</sub> (-) ? -': uu_suc,
                      's_u_uu[input_b]# s<sub>u,uu</sub> (kPa) ? -': s_u_uu,
                      'N_c[calc_b]# N<sub>c</sub> (-) ? -': N_c,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def icp_base_clay(q_c, calculation_dict, d_cpt, drainage='undrained'):

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        if drainage.lower() == 'undrained':
            k_b = 0.4
        else:
            k_b = 0.65
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        if drainage.lower() == 'undrained':
            k_b = 1
        else:
            k_b = 1.6
        
    q_b = k_b*q_c

    D_i = calculation_dict['b_inner']

    if (D_i/d_cpt + 0.45*q_c/0.1) < 36:
        plug_output = 'plugged'
    else:
        plug_output = 'cored'
    
    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_b[calc_b]# k<sub>b</sub> (-) ? -': k_b,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def uwa_base_clay(q_c, calculation_dict, d_cpt, drainage='undrained'):

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        if drainage.lower() == 'undrained':
            k_b = 0.4
        else:
            k_b = 0.65
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        if drainage.lower() == 'undrained':
            k_b = 1
        else:
            k_b = 1.6
        
    q_b = k_b*q_c

    D_i = calculation_dict['b_inner']

    if (D_i/d_cpt + 0.45*q_c/0.1) < 36:
        plug_output = 'plugged'
    else:
        plug_output = 'cored'
    
    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_b[calc_b]# k<sub>b</sub> (-) ? -': k_b,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def fugro_base_clay(q_t_tot, p_0_tot, z, z_tot, calculation_dict):

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    D = calculation_dict['b_outer']

    q_n_tot = q_t_tot - 0.001*p_0_tot
    q_p = np.average(q_n_tot[(z_tot >= z-1.5*D) & (z_tot <= z+1.5*D) & (z_tot >= 0)])
    q_b = 0.7*q_p

    save_parameter = {'q_p[input_b]# q<sub>p</sub> (MPa) ? -': q_p,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter

# %% --- BASE SAND ---

def cpt_base_sand(q_c, sbt, case, calculation_dict, kp_p=0.3, kp_h=0.6):

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    if 'most_probable' in case.lower():
        k_p = kp_p
    elif 'highest' in case.lower():
        k_p = kp_h
    elif 'tailored' in case.lower():
        match = re.search(r'\[([0-9.+-eE]+)\]', case)
        k_p = float(match.group(1))
    elif 'sbt' in case.lower():
        if 'be' in case.lower():
            matrix = {'SD': 0.12,
                      'CD': 0.66,
                      'TD': 0.47,
                      'SC': 1.1,
                      'CC': 4.6,
                      'TC': 2.5}
        elif 'le' in case.lower():
            matrix = {'SD': 0.1,
                      'CD': 0.3,
                      'TD': 0.3,
                      'SC': 0.25,
                      'CC': 0.1,
                      'TC': 1}
        elif 'he' in case.lower():
            matrix = {'SD': 0.13,
                      'CD': 0.9,
                      'TD': 0.6,
                      'SC': 2.5,
                      'CC': 8,
                      'TC': 5}
        if sbt in matrix:
            k_p = matrix[sbt]
        else:
            k_p = matrix['SD']
    
    q_b = q_c*k_p

    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      'k_p[calc_b]# k<sub>p</sub> (-) ? -': k_p,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


def almhamre_base_sand(q_c, sigv0_, case, calculation_dict, k_ts=0.15, beta=0.2):
    
    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    if 'be' in case.lower():
        multiplier = 1
    elif 'he' in case.lower():
        multiplier = 1.25

    q_c = max(0.001, q_c)
    sigv0_ = max(0.001, sigv0_)
    
    q_b = multiplier*k_ts*q_c*(1000*q_c/sigv0_)**beta

    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_b]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'k_ts[calc_b]': k_ts,
                      'beta[calc_b]': beta,
                      'mult[calc_b]# mult (-) ? -': multiplier,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


# def bc_dnv_base_shallow_sand(z, phi, sigv0_, calc_type, calculation_dict):

# TO BE UPDATED

#     a_base = calculation_dict['area_plug_diff']
#     base_influence = calculation_dict['b_outer_diff']

#     if calc_type in ['installation']:
#         r = 0.66
#         alpha_f = 1
#         tan_phi = math.tan(math.radians(phi))
#         tan_delta = r*tan_phi
#         delta = np.degrees(np.atan(tan_delta))
#         K = 0.8
#         q_ = sigv0_*(1 + alpha_f*K*np.tan(np.radians(delta)))

#     elif calc_type in ['capacity'] or calc_type == 'plug_bearing_installation':
#         q_ = sigv0_

#     N_q = np.exp(np.pi * np.tan(np.radians(phi))) * np.power(np.tan(np.pi/4 + np.radians(phi)/2), 2)
#     N_g = 2 * (N_q + 1)*np.tan(np.radians(phi))
    
#     q_b = 0.001 * (0.5 * (sigv0_/max(1e-10, z)) * base_influence * N_g + q_ * N_q)

#     save_parameter = {'phi[input_b]': phi,
#                       'sigv0_[input_b]': sigv0_,
#                       'q_[input_b]': q_,
#                       'N_q[bc_dnv_sand_b]': N_q,
#                       'N_g[bc_dnv_sand_b]': N_g,
#                       'b_eff[bc_dnv_sand_b]': base_influence}
    
#     return q_b, a_base, base_influence, save_parameter


def bc_dnv_base_deep_sand(z, phi, sigv0_, calculation_dict):

    # TO BE CHECKED

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'

    N_q = np.exp(np.pi * np.tan(np.radians(phi))) * np.power(np.tan(np.pi/4 + np.radians(phi)/2), 2)
    N_g = 2 * (N_q + 1)*np.tan(np.radians(phi))
    
    q_b = 0.001 * (0.5 * (sigv0_/max(1e-10, z)) * base_influence * N_g + sigv0_ * N_q)

    save_parameter = {'phi[input_b]# φ (deg) ? -': phi,
                      "sigv0_[input_b]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'N_q[calc_b]# N<sub>q</sub> (-) ? -': N_q,
                      'N_g[calc_b]# N<sub>γ</sub> (-) ? -': N_g,
                      'b_eff[calc_b]# b<sub>eff</sub> (m) ? -': base_influence,
                      'plug_output[output_b]# - ? - ': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


# def bc_api_base_shallow_sand(d_r, sigv0_, calculation_dict):

# TO BE UPDATED

#     if 'plugged' in calculation_dict['calculation_method']:
#         a_base = calculation_dict['area_plug_diff']
#         base_influence = calculation_dict['b_outer_diff']
#     else:
#         a_base = calculation_dict['area_core_diff']
#         base_influence = calculation_dict['t_diff']
    
#     if d_r >= 85:
#         q_b_lim = 12
#         N_q = 50
#     elif d_r >= 65:
#         q_b_lim = 10
#         N_q = 40
#     elif d_r >= 35:
#         q_b_lim = 5
#         N_q = 20
#     else:
#         q_b_lim = 3
#         N_q = 12

#     q_b = 0.001*sigv0_*N_q

#     if q_b > q_b_lim:
#         q_b = q_b_lim

#     save_parameter = {'d_r[input_b]': d_r,
#                       'sigv0_[input_b]': sigv0_,
#                       'N_q[bc_api_sand_b]': N_q,
#                       'q_b_lim[bc_api_sand_b]': q_b_lim}
    
#     return q_b, a_base, base_influence, save_parameter


def bc_api_base_deep_sand(d_r, sigv0_, calculation_dict):

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        plug_output = 'cored'
    
    if d_r >= 85:
        q_b_lim = 12
        N_q = 50
    elif d_r >= 65:
        q_b_lim = 9.6
        N_q = 40
    elif d_r >= 35:
        q_b_lim = 4.8
        N_q = 20
    else:
        q_b_lim = 2.9
        N_q = 12

    q_b = 0.001*sigv0_*N_q

    if q_b > q_b_lim:
        q_b = q_b_lim

    save_parameter = {'d_r[input_b]': d_r,
                      "sigv0_[input_b]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'N_q[calc_b]': N_q,
                      'q_b_lim[calc_b]': q_b_lim,
                      'plug_output[output_b]# - ? -': plug_output}
    
    return q_b, a_base, base_influence, plug_output, save_parameter


# def bc_iso_base_shallow_sand(d_r, sigv0_, calculation_dict):

#     if 'plugged' in calculation_dict['calculation_method']:
#         a_base = calculation_dict['area_plug_diff']
#         base_influence = calculation_dict['b_outer_diff']
#     else:
#         a_base = calculation_dict['area_core_diff']
#         base_influence = calculation_dict['t_diff']
    
#     if d_r >= 85:
#         q_b_lim = 12
#         N_q = 50
#     elif d_r >= 65:
#         q_b_lim = 10
#         N_q = 40
#     elif d_r >= 35:
#         q_b_lim = 5
#         N_q = 20
#     else:
#         q_b_lim = 3
#         N_q = 12

#     q_b = 0.001*sigv0_*N_q

#     if q_b > q_b_lim:
#         q_b = q_b_lim

#     save_parameter = {'d_r[input_b]': d_r,
#                       'sigv0_[input_b]': sigv0_,
#                       'N_q[bc_api_sand_b]': N_q,
#                       'q_b_lim[bc_api_sand_b]': q_b_lim}
    
#     return q_b, a_base, base_influence, save_parameter

### No ISO base deep sand exists, uCPT recommended

def ucpt_base_sand(q_c_tot, z, z_tot, I_c, calculation_dict, d_cpt):

    a_base = calculation_dict['area_plug_diff']
    base_influence = calculation_dict['b_outer_diff']

    if 'plugged' in calculation_dict['calculation_method']:
        plug_output = 'plugged'
    else:
        plug_output = 'cored'

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']
    
    PLR = math.tanh(0.3*np.power(D_i/d_cpt, 0.5))
        
    A_r_eff = 1 - PLR*np.power(D_i/D, 2)

    if I_c > 2.05 and I_c < 2.5:
        i_c_corr = 3.93*np.power(I_c, 2) - 14.78*I_c + 14.78
    else:
        i_c_corr = 1
    
    q_p = np.average(q_c_tot[(z_tot >= z-1.5*D) & (z_tot <= z+1.5*D) & (z_tot >= 0)])
    q_b = (0.12 + 0.38*A_r_eff)*i_c_corr*q_p

    save_parameter = {'I_c[input_b]': I_c,
                      'PLR[calc_b]': PLR,
                      'A_r_eff[calc_b]': A_r_eff,
                      'i_c_corr[calc_b]': i_c_corr,
                      'q_p[calc_b]': q_p,
                      'plug_output[output_b]# - ? -': plug_output}
            
    return q_b, a_base, base_influence, plug_output, save_parameter


def ngi_base_sand(q_c, sigv0_, calculation_dict):

    d_r_ngi = max(0.1, 0.4*math.log(1000*max(1e-10, q_c) / (22*np.power(max(1e-10, sigv0_)*100, 0.5))))

    if 'plugged' in calculation_dict['calculation_method']:
        a_base = calculation_dict['area_plug_diff']
        base_influence = calculation_dict['b_outer_diff']
        q_b = 0.7*q_c/(1 + 3*np.power(d_r_ngi, 2))  
        plug_output = 'plugged'
    else:
        a_base = calculation_dict['area_core_diff']
        base_influence = calculation_dict['t_diff']
        q_b = q_c    
        plug_output = 'cored'

    save_parameter = {'q_c[input_b]# q<sub>c</sub> (MPa) ? -': q_c,
                      "sigv0_[input_b]# σ'<sub>v</sub> (kPa) ? -": sigv0_,
                      'd_r_ngi[calc_b]# D<sub>r,NGI</sub> (-) ? -': d_r_ngi,
                      'plug_output[output_b]# - ? -': plug_output}
            
    return q_b, a_base, base_influence, plug_output, save_parameter


def icp_base_sand(q_c_tot, z, z_tot, sigv0_, calculation_dict, d_cpt):

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    q_p = np.average(q_c_tot[(z_tot >= z-1.5*D) & (z_tot <= z+1.5*D) & (z_tot >= 0)])
    A_r = 1 - np.power(D_i/D, 2)

    a_base = calculation_dict['area_plug_diff']
    base_influence = calculation_dict['b_outer_diff']

    if 'plugged' in calculation_dict['calculation_method']:
        q_b = max(A_r, 0.15 (0.5-0.25*np.log10(D/d_cpt)))*q_p
    else:
        q_b = A_r*q_p

    d_r_icp = max(0.1, min(1, 0.4*math.log(1000*max(1e-10, q_p) / (22*np.power(max(1e-10, sigv0_)*100, 0.5)))))

    if D_i < 0.02*(d_r_icp - 30) and D_i/d_cpt < 0.083*q_p/0.1:
        plug_output = 'plugged'
    else:
        plug_output = 'cored'

    save_parameter = {'q_p[input_b]# q<sub>p</sub> (MPa) ? -': q_p,
                      'd_cpt[calc_b]# d<sub>CPT</sub> (m) ? -': d_cpt,
                      'd_r_icp[calc_b]# D<sub>r,ICP</sub> (-) ? -': d_r_icp,
                      'A_r[calc_b]# A<sub>r</sub> (m<super>2</super>) ? -': A_r,
                      'plug_output[output_b]# - ? -': plug_output}
        
    return q_b, a_base, base_influence, plug_output, save_parameter


def uwa_base_sand(q_c_tot, z, z_tot, calculation_dict, l_s, Q_s_inner_clay, q_b_clay_limit=np.nan):

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    # q_i = np.average(q_c_tot[(z_tot <= z+1.5*D) & (z_tot >= 0)])
    # q_ii = np.min(q_c_tot[(z_tot <= z+1.5*D) & (z_tot >= 0)])
    # q_iii = np.average(q_c_tot[(z_tot >= z-8*D) & (z_tot >= 0)])

    # q_p = 0.5*(0.5*(q_i + q_ii) + q_iii)
    
    a_base = calculation_dict['area_plug_diff']
    base_influence = calculation_dict['b_outer_diff']

    FFR = min(1, np.power(D_i/1.5, 0.2))
    A_rb = 1 - FFR*np.power(D_i/D, 2)
    D_star = D*np.power(A_rb, 0.5)

    q_p = np.average(q_c_tot[(z_tot >= z-1.5*D_star) & (z_tot <= z+1.5*D_star) & (z_tot >= 0)])
    q_b = (0.15 + 0.45*A_rb)*q_p

    if l_s > 8:
        plug_output = 'plugged'
        if Q_s_inner_clay > 0:
            q_b_clay_limit = Q_s_inner_clay*np.exp(l_s/D)/a_base
            q_b = min(q_b, q_b_clay_limit)
    else:
        plug_output = 'fail'

    save_parameter = {'q_p[input_b]# q<sub>p</sub> (MPa) ? -': q_p,
                      'FFR[calc_b]# FFR (-) ? -': FFR,
                      'D_star[calc_b]# D* (m) ? -': D_star,
                      'A_rb[calc_b]# A<sub>rb</sub> (m<super>2</super>) ? -': A_rb,
                      'l_s[calc_b]# L<sub>sand</sub> (m) ? -': l_s,
                      'q_b_clay_limit[calc_b]# q<sub>b,limit clay</sub> (MPa) ? -': q_b_clay_limit,
                      'plug_output[output_b]# - ? -': plug_output}
        
    return q_b, a_base, base_influence, plug_output, save_parameter


def fugro_base_sand(q_c_tot, z, z_tot, calculation_dict, l_s, Q_s_inner_clay, q_b_clay_limit=np.nan):

    D = calculation_dict['b_outer']
    D_i = calculation_dict['b_inner']

    q_p = np.average(q_c_tot[(z_tot >= z-1.5*D) & (z_tot <= z+1.5*D) & (z_tot >= 0)])

    R = D/2
    R_i = D_i/2
    R_star = np.power(np.power(R, 2) - np.power(R_i, 2), 0.5)

    a_base = calculation_dict['area_plug_diff']
    base_influence = calculation_dict['b_outer_diff']

    q_b = 0.1*8.5*np.power(q_p/0.1, 0.5)*np.power(R_star/R, 0.5)

    if l_s > 8:
        plug_output = 'plugged'
        if Q_s_inner_clay > 0:
            q_b_clay_limit = Q_s_inner_clay*np.exp(l_s/D)/a_base
            q_b = min(q_b, q_b_clay_limit)
    else:
        plug_output = 'fail'

    save_parameter = {'q_p[input_b]# q<sub>p</sub> (MPa) ? -': q_p,
                      'R_star[calc_b]# R* (m) ? -': R_star,
                      'l_s[calc_b]# L<sub>sand</sub> (m) ? -': l_s,
                      'q_b_clay_limit[calc_b]# q<sub>b,limit clay</sub> (MPa) ? -': q_b_clay_limit,
                      'plug_output[output_b]# - ? -': plug_output}
        
    return q_b, a_base, base_influence, plug_output, save_parameter


def base_resistance(depth_i, soil_data_dis_dict, dl_b,
                    capacity_dict, f_direction, pf_soil_mat,
                    a_base_diff_dis, a_base_global_dis,
                    calculation_method, calc_type,
                    d_z_gdb,
                    d_cpt,
                    removal=False,
                    conductor={},
                    l_s=None,
                    Q_s_inner_clay=None):  
    
    base_parameter_inc = []

    for idx, (a_base_diff_dis_i, a_base_global_dis_i) in enumerate(zip(a_base_diff_dis, a_base_global_dis)):

        z_end_section_i, a_base_core_diff_i, a_base_o_diff_i, a_base_i_diff_i, b_outer_diff_i, t_diff_i = a_base_diff_dis_i[0], a_base_diff_dis_i[1], a_base_diff_dis_i[2], a_base_diff_dis_i[3], a_base_diff_dis_i[4], a_base_diff_dis_i[5]
        b_outer_i, t_i = a_base_global_dis_i[4], a_base_global_dis_i[5]
        b_inner_i = b_outer_i - 2*t_i
       
        try:
            z_start_section_i = a_base_diff_dis[idx + 1][0]
        except Exception:
            z_start_section_i = 0
      
        depth_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'depth')
        soil_type_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'Soil_Type')
        q_c_b_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'qc_'+dl_b)
        q_t_b_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'qt_'+dl_b)
        p0_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sigv_rep')

        mask = ((depth_total_dis <= round(depth_i, 2)) & (depth_total_dis >= round(z_start_section_i, 2)) & (depth_total_dis <= round(z_end_section_i, 2)))
                                
        depth_in_soil_dis = depth_total_dis[mask]
        length = len(depth_in_soil_dis)

        soil_type_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'Soil_Type', mask=mask, length=length)
        sbt_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sbt', mask=mask, length=length)
        i_c_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'ic', mask=mask, length=length)
        p_0__dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sigveff_rep', mask=mask, length=length)
        q_c_b_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'qc_{dl_b}', mask=mask, length=length)
        s_u_c_b_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'suc_{dl_b}', mask=mask, length=length)
        dss_suc_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sud-suc_rep', mask=mask, length=length)
        sue_suc_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sue-suc_rep', mask=mask, length=length)
        uu_suc_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'suuu-suc_rep', mask=mask, length=length)
        phi_b_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'phi_{dl_b}', mask=mask, length=length)
        dr_b_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'dr_{dl_b}', mask=mask, length=length)

        for idx2 in range(len(depth_in_soil_dis)):
            
            depth_ii_1 = depth_in_soil_dis[idx2]
            soil_type_ii = soil_type_dis[idx2]
            p_0__ii = p_0__dis[idx2]
            q_c_b_ii = q_c_b_dis[idx2]
            sbt_ii = sbt_dis[idx2]
            s_u_c_b_ii = s_u_c_b_dis[idx2]
            dss_suc_ii = dss_suc_dis[idx2]
            sue_suc_ii = sue_suc_dis[idx2]
            uu_suc_ii = uu_suc_dis[idx2]
            phi_b_ii = phi_b_dis[idx2]
            dr_b_ii = dr_b_dis[idx2]
            i_c_ii = i_c_dis[idx2]
                      
            calculation_dict = {'calculation_method': calculation_method.lower(),
                                'area_core_diff': a_base_core_diff_i,
                                'area_plug_diff': a_base_o_diff_i,
                                'b_outer_diff': b_outer_diff_i,
                                't_diff': t_diff_i,
                                'b_outer': b_outer_i,
                                'b_inner': b_inner_i,
                                't': t_i,
                                'calc_type': calc_type}
                        
            if f_direction.lower() == 'compression':
                                                    
                if soil_type_ii.lower() in ['c', 'c_s']:

                    sub_capacity_entry = 'clay_base'             
                    
                    # BEARING CAPACITY METHOD, DEEP FOUNDATION, DNV, CLAY
                    if 'bc_deep_dnv' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = bc_dnv_base_deep_clay(s_u_c_b_ii, dss_suc_ii, sue_suc_ii, p_0__ii, calculation_dict)

                    # BEARING CAPACITY METHOD, DEEP FOUNDATION, API, CLAY
                    elif 'bc_deep_api' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = bc_api_base_deep_clay(s_u_c_b_ii, dss_suc_ii, sue_suc_ii, calculation_dict)

                    # BEARING CAPACITY METHOD, DEEP FOUNDATION, ISO, CLAY
                    elif 'bc_deep_iso' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = bc_iso_base_deep_clay(s_u_c_b_ii, dss_suc_ii, sue_suc_ii, calculation_dict)

                    # ALM & HAMRE METHOD, CLAY
                    elif 'alm_hamre' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = almhamre_base_clay(q_c_b_ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)

                    # UNIFIED CPT METHOD, CLAY
                    elif 'ucpt' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = ucpt_base_clay(q_t_b_total_dis, depth_ii_1, depth_total_dis, soil_type_total_dis, calculation_dict)
                    
                    # CPT METHOD, CLAY
                    elif 'cpt' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = cpt_base_clay(q_c_b_ii, sbt_ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)

                    # NGI-05 METHOD, CLAY
                    elif 'ngi' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = ngi_base_clay(s_u_c_b_ii, uu_suc_ii, calculation_dict)

                    # ICP METHOD, CLAY
                    elif 'icp' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = icp_base_clay(q_c_b_ii, calculation_dict, d_cpt)

                    # UWA METHOD, CLAY
                    elif 'uwa' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = uwa_base_clay(q_c_b_ii, calculation_dict, d_cpt)

                    # FUGRO METHOD, CLAY
                    elif 'fugro' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = fugro_base_clay(q_t_b_total_dis, p0_total_dis, depth_ii_1, depth_total_dis, calculation_dict)
                                        
                    else:
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = 0, 0, 0, calculation_method.lower(), {}
                        print(f'Error at q_b for {capacity_dict[sub_capacity_entry].lower()}')

                elif soil_type_ii.lower() in ['s', 's_c', 'si']:

                    sub_capacity_entry = 'sand_base'               

                    # BEARING CAPACITY METHOD, DEEP FOUNDATION, DNV, SAND
                    if 'bc_deep_dnv' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = bc_dnv_base_deep_sand(depth_ii_1, phi_b_ii, p_0__ii, calculation_dict)
                    
                    # BEARING CAPACITY METHOD, DEEP FOUNDATION, API, SAND
                    elif 'bc_deep_api' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = bc_api_base_deep_sand(dr_b_ii, p_0__ii, calculation_dict)

                    # BEARING CAPACITY METHOD, DEEP FOUNDATION, ISO, SAND
                    ### No ISO base deep sand exists, uCPT recommended

                    # ALM & HAMRE METHOD, SAND
                    elif 'alm_hamre' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = almhamre_base_sand(q_c_b_ii, p_0__ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)

                    # UNIFIED CPT METHOD, SAND
                    elif 'ucpt' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = ucpt_base_sand(q_c_b_total_dis, depth_ii_1, depth_total_dis, i_c_ii, calculation_dict, d_cpt)
                    
                    # CPT METHOD, SAND
                    elif 'cpt' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = cpt_base_sand(q_c_b_ii, sbt_ii, capacity_dict[sub_capacity_entry].lower(), calculation_dict)

                    # NGI-99 METHOD, SAND
                    elif 'ngi' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = ngi_base_sand(q_c_b_ii, p_0__ii, calculation_dict)

                    # ICP METHOD, SAND
                    elif 'icp' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = icp_base_sand(q_c_b_total_dis, depth_ii_1, depth_total_dis, p_0__ii, calculation_dict, d_cpt)

                    # UWA METHOD, SAND
                    elif 'uwa' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = uwa_base_sand(q_c_b_total_dis, depth_ii_1, depth_total_dis, calculation_dict, l_s, Q_s_inner_clay)

                    # FUGRO METHOD, SAND
                    elif 'fugro' in capacity_dict[sub_capacity_entry].lower():
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = fugro_base_sand(q_c_b_total_dis, depth_ii_1, depth_total_dis, calculation_dict, l_s, Q_s_inner_clay)

                    else:
                        q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = 0, 0, 0, calculation_method.lower(), {}
                        print(f'Error at q_b for {capacity_dict[sub_capacity_entry].lower()}')

            else:
                q_b_ii, a_base_ii, base_influence_ii, plug_output_ii, save_parameter_ii = 0, 0, 0, calculation_method.lower(), {}

            if calc_type in ['plug_bearing_installation']: 
                if soil_type_ii.lower() in ['c', 'c_s']:
                    q_b_ii = q_b_ii
                elif soil_type_ii.lower() in ['s', 's_c', 'si'] and np.all(np.isin(np.char.lower(soil_type_dis), ['s', 's_c', 'si'])):
                    q_b_ii = 0
                a_base_ii = a_base_i_diff_i
            elif calc_type in ['plug_bearing_removal']: 
                a_base_ii = a_base_i_diff_i

            if removal:
                q_b_ii = 0
            
            if 'conductor_analysis' in conductor:
                if conductor['conductor_analysis']:
                    q_b_ii = 0

            if idx2 != len(depth_in_soil_dis) - 1:
                a_base_ii = 0
                base_influence_ii = 0

            if calc_type in ['capacity', 'plug_bearing_installation', 'plug_bearing_removal']: 
                q_b_ii = q_b_ii/pf_soil_mat
            elif calc_type in ['installation']:
                q_b_ii = q_b_ii*pf_soil_mat

            Q_b_i = a_base_ii*q_b_ii                       

            if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
                save_parameter_ii = {key.replace('_b]', '_pb]'): value for key, value in save_parameter_ii.items()}
                save_parameter_ii['soil_type_pb_section_' + str(idx+1) + '[input_pb]# - ? Section'+str(idx+1)] = soil_type_ii
                save_parameter_ii['z_pb_section_' + str(idx+1) + '[input_pb]# z (m) ? Section'+str(idx+1)] = float(depth_ii_1)
                save_parameter_ii['q_pb_section_' + str(idx+1) + '[calc_pb2]# q<sub>b,pb</sub> (MPa) ? Section'+str(idx+1)] = float(q_b_ii)
                save_parameter_ii['a_pb_section_' + str(idx+1) + '[geometry_pb]# A<sub>b,pb</sub> (m<super>2</super>) ? Section'+str(idx+1)] = a_base_ii
                save_parameter_ii['Q_pb_section_' + str(idx+1) + '[calc_pb3]# Q<sub>b,pb</sub> (MN) ? Section'+str(idx+1)] = float(Q_b_i)

            else:
                save_parameter_ii['soil_type_b_section_' + str(idx+1) + '[input_b]# - ? Section'+str(idx+1)] = soil_type_ii
                save_parameter_ii['z_b_section_' + str(idx+1) + '[input_b]# z (m) ? Section'+str(idx+1)] = float(depth_ii_1)
                save_parameter_ii['q_b_section_' + str(idx+1) + '[calc_b2]# q<sub>b</sub> (MPa) ? Section'+str(idx+1)] = float(q_b_ii)
                save_parameter_ii['a_b_section_' + str(idx+1) + '[geometry_b]# A<sub>b</sub> (m<super>2</super>) ? Section'+str(idx+1)] = a_base_ii
                save_parameter_ii['base_influence_section_' + str(idx+1) + '[output_b]# t<sub>b</sub> (m) ? Section'+str(idx+1)] = base_influence_ii
                save_parameter_ii['Q_b_section_' + str(idx+1) + '[calc_b3]# Q<sub>b</sub> (MN) ? Section'+str(idx+1)] = Q_b_i
            
            base_parameter_inc.append(save_parameter_ii)

            if depth_ii_1 == depth_i:
                plug_output_base = plug_output_ii

    Q_b_total = 0

    if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
        Q_pb_total = 0

    for save_parameter_ii in base_parameter_inc:
        for key in save_parameter_ii:
            if 'Q_b' in key:
                Q_b_total = Q_b_total + save_parameter_ii[key]
            if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
                if 'Q_pb' in key:
                    Q_pb_total = Q_pb_total + save_parameter_ii[key]
    
    if calc_type in ['plug_bearing_installation', 'plug_bearing_removal']: 
        results_dict_base = {'Q_pb_total[output_pb]# Q<sub>b,pb</sub> (MN) ? -': Q_pb_total,
                             'plug_output[output_pb]# - ? - ': plug_output_base,
                             'base_parameter_inc_plug_bearing': base_parameter_inc,
                             'pf_soil_mat[input_pb]# γ<sub>m,pb</sub> (-) ? -': pf_soil_mat}
        
    else:
        results_dict_base = {'Q_b_total[output_b]# Q<sub>b</sub> (MN) ? -': Q_b_total,
                             'plug_output[output_b]# - ? - ': plug_output_base,
                             'base_parameter_inc': base_parameter_inc,
                             'base_influence': base_influence_ii,
                             'pf_soil_mat[input_b]# γ<sub>m</sub> (-) ? -': pf_soil_mat}
                
    return results_dict_base, plug_output_base