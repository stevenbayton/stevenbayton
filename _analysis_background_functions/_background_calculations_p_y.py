# python modules
import numpy as np

# multiconsult modules
import _background_functions as bf

# %% --- P-Y CLAY ---

def p_ult_clay_iso_old_static(D, z, su, p_0_, J=0.25):

    if z <= 0:
        p_ult = 0
    else:
        p_ult1 = (3*su + p_0_)*D + J*su*z
        p_ult2 = 9*su*D

        p_ult = 0.001*min(p_ult1, p_ult2)

    save_parameter = {'s_u_p_y[input]': su,
                      'p_0_[input]': p_0_,
                      'J[input]': J}

    return p_ult, save_parameter


def p_y_clay_iso_old_static(y, D, z, su, p_0_, ep_c=0.01):

    p_ult, save_parameter_p_ult = p_ult_clay_iso_old_static(D, z, su, p_0_)

    y_c = 2.5*ep_c*D

    if y < 0:
        mult = -1
    else:
        mult = 1

    y = abs(y)

    if y <= 0.1*y_c:
        y1 = 0
        y2 = 0.1
        p1 = 0
        p2 = 0.23
    elif y <= 0.3*y_c:
        y1 = 0.1
        y2 = 0.3
        p1 = 0.23
        p2 = 0.33
    elif y <= 1*y_c:
        y1 = 0.3
        y2 = 1
        p1 = 0.33
        p2 = 0.5
    elif y <= 3*y_c:
        y1 = 1
        y2 = 3
        p1 = 0.5
        p2 = 0.72
    elif y <= 8*y_c:
        y1 = 3
        y2 = 8
        p1 = 0.72
        p2 = 1
    else:
        y1 = 8
        y2 = 1e10
        p1 = 1
        p2 = 1

    m = ((p2 - p1)*p_ult)/((y2 - y1)*y_c)
    p = mult*(m*y + p1*p_ult - m*y1*y_c)
    
    save_parameter = {'ep_c[input]': ep_c,
                      'p_ult[calc_py]': p_ult,
                      'y_c[calc_py]': y_c,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter


# def p_ult_clay_iso_static(D, z, su, alpha_ave):

#     ##### NEEDS TO BE UPDATED WITH CLAY FROM SURFACE

#     if z <= 0:
#         p_ult = 0
#     else:
#         N_pd = 9 + 3*alpha_ave
#         p_ult = 0.001*N_pd*su*D

#     save_parameter = {'s_u_p_y[input]': su,
#                       'alpha_ave[calc_py]': alpha_ave,
#                       'N_pd[calc_py]': N_pd}

#     return p_ult, save_parameter


def p_ult_clay_iso_static(D, z, su, p_0_, alpha_ave, start_clay_s_u, start_clay_depth, gapping=False):

    if z <= 0:
        p_ult = 0
    else:
        N_pd = 9 + 3*alpha_ave

        if start_clay_depth <= D:
            N_1 = 12
            N_2 = 3.22
            su_1 = max(1e-10, (su - start_clay_s_u)/z)
            lam = max(1e-10, start_clay_s_u / (su_1 * D))
            d = max(14.5, 16.8 - 2.3*np.log10(lam))
            N_p0 = min(N_pd, N_1 - (1 - alpha_ave) - (N_1 - N_2)*np.power(max(0, 1 - np.power(z/(d*D), 0.6)), 1.35))

            if gapping:
                N_p = min(N_p0 + z*p_0_/su, N_pd)
            else:
                N_p = min(2*N_p0, N_pd)
        else:
            N_p = N_pd

        p_ult = 0.001*N_p*su*D

    save_parameter = {'s_u_p_y[input]': su,
                      'alpha_ave[calc_py]': alpha_ave,
                      'N_p[calc_py]': N_p}

    return p_ult, save_parameter


def p_y_clay_iso_static(y, D, z, su, p_0_, Ip, OCR, alpha_ave, start_clay_s_u, start_clay_depth):

    p_ult, save_parameter_p_ult = p_ult_clay_iso_static(D, z, su, p_0_, alpha_ave, start_clay_s_u, start_clay_depth)

    if y < 0:
        mult = -1
    else:
        mult = 1

    y = abs(y)

    Ip_gr_30_OCR_leq_2 = [0.0003, 0.003, 0.0053, 0.009, 0.014, 0.022, 0.032, 0.05, 0.082, 0.15, 0.25, 1e10]
    Ip_gr_30_OCR_4 = [0.0004, 0.004, 0.008, 0.015, 0.024, 0.036, 0.055, 0.084, 0.14, 0.23, 0.30, 1e10]
    Ip_gr_30_OCR_10 = [0.0005, 0.005, 0.011, 0.021, 0.034, 0.052, 0.078, 0.12, 0.19, 0.30, 0.40, 1e10]

    Ip_leq_30_OCR_leq_2 = [0.0001, 0.001, 0.0018, 0.003, 0.0048, 0.0073, 0.011, 0.017, 0.027, 0.05, 0.083, 1e10]
    Ip_leq_30_OCR_4 = [0.0002, 0.002, 0.004, 0.0075, 0.012, 0.018, 0.027, 0.042, 0.07, 0.11, 0.15, 1e10]
    Ip_leq_30_OCR_10 = [0.0003, 0.0033, 0.0073, 0.014, 0.023, 0.035, 0.052, 0.08, 0.13, 0.20, 0.27, 1e10]

    if Ip <= 30:
        p_y_shape = [np.interp(OCR, [2, 4, 10], [x1, x2, x3], left=x1, right=x3) for x1, x2, x3 in zip(Ip_leq_30_OCR_leq_2, Ip_leq_30_OCR_4, Ip_leq_30_OCR_10)]
    else:
        p_y_shape = [np.interp(OCR, [2, 4, 10], [x1, x2, x3], left=x1, right=x3) for x1, x2, x3 in zip(Ip_gr_30_OCR_leq_2, Ip_gr_30_OCR_4, Ip_gr_30_OCR_10)]

    if y/D <= p_y_shape[0]:
        y1 = 0
        y2 = p_y_shape[0]
        p1 = 0
        p2 = 0.05
    elif y/D <= p_y_shape[1]:
        y1 = p_y_shape[0]
        y2 = p_y_shape[1]
        p1 = 0.05
        p2 = 0.2
    elif y/D <= p_y_shape[2]:
        y1 = p_y_shape[1]
        y2 = p_y_shape[2]
        p1 = 0.2
        p2 = 0.3
    elif y/D <= p_y_shape[3]:
        y1 = p_y_shape[2]
        y2 = p_y_shape[3]
        p1 = 0.3
        p2 = 0.4
    elif y/D <= p_y_shape[4]:
        y1 = p_y_shape[3]
        y2 = p_y_shape[4]
        p1 = 0.4
        p2 = 0.5
    elif y/D <= p_y_shape[5]:
        y1 = p_y_shape[4]
        y2 = p_y_shape[5]
        p1 = 0.5
        p2 = 0.6
    elif y/D <= p_y_shape[6]:
        y1 = p_y_shape[5]
        y2 = p_y_shape[6]
        p1 = 0.6
        p2 = 0.7
    elif y/D <= p_y_shape[7]:
        y1 = p_y_shape[6]
        y2 = p_y_shape[7]
        p1 = 0.7
        p2 = 0.8
    elif y/D <= p_y_shape[8]:
        y1 = p_y_shape[7]
        y2 = p_y_shape[8]
        p1 = 0.8
        p2 = 0.9
    elif y/D <= p_y_shape[9]:
        y1 = p_y_shape[8]
        y2 = p_y_shape[9]
        p1 = 0.9
        p2 = 0.975
    elif y/D <= p_y_shape[10]:
        y1 = p_y_shape[9]
        y2 = p_y_shape[10]
        p1 = 0.975
        p2 = 1
    else:
        y1 = p_y_shape[10]
        y2 = p_y_shape[11]
        p1 = 1
        p2 = 1

    m = ((p2 - p1)*p_ult)/((y2 - y1))
    p = mult*(m*y/D + p1*p_ult - m*y1)
    
    save_parameter = {'OCR[input]': OCR,
                      'Ip[input]': Ip,
                      'p_ult[calc_py]': p_ult,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter


def p_ult_soft_clay_api_static(D, z, su, p_0_, J=0.25):

    if z <= 0:
        p_ult = 0
    else:
        p_ult1 = (3*su + p_0_)*D + J*su*z
        p_ult2 = 9*su*D

        p_ult = 0.001*min(p_ult1, p_ult2)

    save_parameter = {'s_u_p_y[input]': su,
                      'p_0_[input]': p_0_,
                      'J[input]': J}
    
    return p_ult, save_parameter


def p_y_soft_clay_api_static(y, D, z, su, p_0_, ep_c=0.01):

    p_ult, save_parameter_p_ult = p_ult_soft_clay_api_static(D, z, su, p_0_)

    y_c = 2.5*ep_c*D

    if y < 0:
        mult = -1
    else:
        mult = 1

    y = abs(y)

    if y <= 1*y_c:
        y1 = 0
        y2 = 1
        p1 = 0
        p2 = 0.5
    elif y <= 3*y_c:
        y1 = 1
        y2 = 3
        p1 = 0.5
        p2 = 0.72
    elif y <= 8*y_c:
        y1 = 3
        y2 = 8
        p1 = 0.72
        p2 = 1
    else:
        y1 = 8
        y2 = 1e10
        p1 = 1
        p2 = 1

    m = ((p2 - p1)*p_ult)/((y2 - y1)*y_c)
    p = mult*(m*y + p1*p_ult - m*y1*y_c)

    save_parameter = {'ep_c[input]': ep_c,
                      'p_ult[calc_py]': p_ult,
                      'y_c[calc_py]': y_c,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter


def p_ult_stiff_clay_api_static(D, z, su, su_tot, z_tot, p_0_):

    if z < 0:
        s_u_ave = np.nan
        p_ult = 0
    else:
        s_u_ave = np.average(np.array(su_tot)[(np.round(np.array(z_tot), 2) <= round(z, 2)) & (np.round(np.array(z_tot), 2) >= 0)])
        p_ult1 = (2*s_u_ave + p_0_)*D + 2.83*s_u_ave*z
        p_ult2 = 11*su*D

        p_ult = 0.001*min(p_ult1, p_ult2)

    save_parameter = {'s_u_p_y[input]': su,
                      's_u_ave_p_y[input]': s_u_ave,
                      'p_0_[input]': p_0_}
        
    return p_ult, save_parameter


def p_y_stiff_clay_api_static(y, D, z, su, su_tot, z_tot, p_0_):

    p_ult, save_parameter_p_ult = p_ult_stiff_clay_api_static(D, z, su, su_tot, z_tot, p_0_)

    if su < 100:
        ep_50 = 0.007
    elif su < 200:
        ep_50 = 0.005
    else:
        ep_50 = 0.004

    y_50 = ep_50*D

    a = -2.778E-04
    b = 8.420E-03
    c = -7.764E-02
    d = 2.940E-01
    e = 1.981E-01

    z_D = z/D

    if z <= 4:
        A = a*np.power(z_D, 4) + b*np.power(z_D, 3) + c*np.power(z_D, 2) + d*z_D + e
    else:
        A = 0.6

    if su < 100:
        k = 130e3
    elif su < 200:
        k = 270e3
    else:
        k = 540e3

    if y < 0:
        mult = -1
    else:
        mult = 1

    y = abs(y)

    y_k = np.power(p_ult, 2)/y_50/np.power(2*k*max(0.001, z), 2)

    if y <= A*y_50:

        if y_k < A*y_50:
            p = 0.5*p_ult*np.power(y/y_50, 0.5)

            if p > k*z*y:
                p = k*z*y
        else:
            p = 0.5*p_ult*np.power(y/y_50, 0.5)

    elif y <= 6*A*y_50:
        p_e = 0.5*p_ult*np.power(y/y_50, 0.5)
        p_o = 0.055*p_ult*np.power((y - A*y_50)/(A*y_50), 1.25)

        p = p_e - p_o

    elif y <= 18*A*y_50:
        p_e_lim = 0.5*p_ult*np.power(6*A, 0.5)
        p_o_lim = 0.055*p_ult*np.power(5, 1.25)
        p_lim = p_e_lim - p_o_lim
        p = p_lim - 0.0625*p_ult/y_50*(y - 6*A*y_50)
        
    else:
        p_e_lim = 0.5*p_ult*np.power(6*A, 0.5)
        p_o_lim = 0.055*p_ult*np.power(5, 1.25)

        p_lim = p_e_lim - p_o_lim
        p = p_lim - 0.0625*p_ult*(12*A)

    p = mult*p

    save_parameter = {'ep_50[input]': ep_50,
                      'p_ult[calc_py]': p_ult,
                      'y_50[calc_py]': y_50,
                      'A[calc_py]': A,
                      'k[calc_py]': k,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter

# %% --- P-Y SAND ---

def p_ult_sand_dnv_static(D, z, phi, p_0_):

    a = [3.528E-04, 1.388E-04, 2.920E-02]
    b = [-2.520E-02, -1.112E-02, -2.561E+00]
    c = [7.287E-01, 4.335E-01, 7.871E+01]
    d = [-6.663E+00, -4.055E+00, -8.156E+02]

    C1 = a[0]*np.power(phi, 3) + b[0]*np.power(phi, 2) + c[0]*phi + d[0]
    C2 = a[1]*np.power(phi, 3) + b[1]*np.power(phi, 2) + c[1]*phi + d[1]
    C3 = a[2]*np.power(phi, 3) + b[2]*np.power(phi, 2) + c[2]*phi + d[2]

    z_r = (C3 - C2)*D/C1

    if z < 0:
        p_ult = 1e-10
    elif z < z_r:
        p_ult = 0.001*max(1e-10, (C1*z + C2*D)*p_0_)
    else:
        p_ult = 0.001*C3*D*p_0_

    save_parameter = {'phi_p_y[input]': phi,
                      'p_0_[input]': p_0_,
                      'C1[calc_py]': C1,
                      'C2[calc_py]': C2,
                      'C3[calc_py]': C3}

    return p_ult, save_parameter


def p_y_sand_dnv_static(y, D, z, phi, p_0_):

    p_ult, save_parameter_p_ult = p_ult_sand_dnv_static(D, z, phi, p_0_)

    A = max(0.9, 3 - 0.8*z/D)

    a = 0.0088
    b = -0.684
    c = 18.72
    d = -172.6

    k = (a*np.power(phi, 3) + b*np.power(phi, 2) + c*phi + d)

    p = A*p_ult*np.tanh((k*z/A/max(1e-10, p_ult))*y)

    save_parameter = {'p_ult[calc_py]': p_ult,
                      'A[calc_py]': A,
                      'k[calc_py]': k,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter


def p_ult_sand_iso_static(D, z, phi, p_0_):

    a = [3.528E-04, 1.388E-04, 2.920E-02]
    b = [-2.520E-02, -1.112E-02, -2.561E+00]
    c = [7.287E-01, 4.335E-01, 7.871E+01]
    d = [-6.663E+00, -4.055E+00, -8.156E+02]

    phi = max(30, phi)
    phi = min(phi, 42)

    C1 = a[0]*np.power(phi, 3) + b[0]*np.power(phi, 2) + c[0]*phi + d[0]
    C2 = a[1]*np.power(phi, 3) + b[1]*np.power(phi, 2) + c[1]*phi + d[1]
    C3 = a[2]*np.power(phi, 3) + b[2]*np.power(phi, 2) + c[2]*phi + d[2]

    z_r = (C3 - C2)*D/C1

    if z < 0:
        p_ult = 1e-10
    elif z < z_r:
        p_ult = 0.001*max(1e-10, (C1*z + C2*D)*p_0_)
    else:
        p_ult = 0.001*C3*D*p_0_

    save_parameter = {'phi_p_y[input]': phi,
                      'p_0_[input]': p_0_,
                      'C1[calc_py]': C1,
                      'C2[calc_py]': C2,
                      'C3[calc_py]': C3}

    return p_ult, save_parameter


def p_y_sand_iso_static(y, D, z, phi, p_0_):

    p_ult, save_parameter_p_ult = p_ult_sand_iso_static(D, z, phi, p_0_)

    A = max(0.9, 3 - 0.8*z/D)

    phi = max(30, phi)
    phi = min(phi, 42)

    a = 0.197
    b = -10.163
    c = 136.34

    k = (a*np.power(phi, 2) + b*phi + c)

    p = A*p_ult*np.tanh((k*z/A/max(1e-10, p_ult))*y)

    save_parameter = {'p_ult[calc_py]': p_ult,
                      'A[calc_py]': A,
                      'k[calc_py]': k,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter


def p_ult_sand_api_static(D, z, phi, p_0_):

    a = [3.528E-04, 1.388E-04, 2.920E-02]
    b = [-2.520E-02, -1.112E-02, -2.561E+00]
    c = [7.287E-01, 4.335E-01, 7.871E+01]
    d = [-6.663E+00, -4.055E+00, -8.156E+02] # adjust to equations

    # --- Equations
    # alpha = phi/2 
    # beta = 45 + phi/2

    # phi_r = np.radians(phi)
    # alpha_r = np.radians(alpha)
    # beta_r = np.radians(beta)

    # K0 = 0.4
    # Ka = (1 - np.sin(phi_r))/(1 + np.sin(phi_r))

    # C1 = np.power(np.tan(beta_r), 2) * np.tan(alpha_r) / np.tan(beta_r - phi_r) + K0 * (np.tan(phi_r) * np.sin(beta_r) / (np.cos(alpha_r) * np.tan(beta_r - alpha_r)) + np.tan(beta_r) * (np.tan(phi_r) * np.sin(beta_r) - np.tan(alpha_r)))
    # C2 = np.tan(beta_r) / np.tan(beta_r - phi_r) - Ka
    # C3 = Ka * (np.power(np.tan(beta_r), 8) - 1) + K0 * np.tan(phi_r) * np.power(np.tan(beta_r), 4)

    # --- Figures
    C1 = a[0]*np.power(phi, 3) + b[0]*np.power(phi, 2) + c[0]*phi + d[0]
    C2 = a[1]*np.power(phi, 3) + b[1]*np.power(phi, 2) + c[1]*phi + d[1]
    C3 = a[2]*np.power(phi, 3) + b[2]*np.power(phi, 2) + c[2]*phi + d[2]

    if z < 0:
        p_ult = 1e-10
    else:
        p_ult1 = max(1e-10, (C1*z + C2*D)*p_0_)
        p_ult2 = C3*D*p_0_

        p_ult = 0.001*min(p_ult1, p_ult2)

    save_parameter = {'phi_p_y[input]': phi,
                      'p_0_[input]': p_0_,
                      'C1[calc_py]': C1,
                      'C2[calc_py]': C2,
                      'C3[calc_py]': C3}
    
    return p_ult, save_parameter


def p_y_sand_api_static(y, D, z, phi, p_0_):

    p_ult, save_parameter_p_ult = p_ult_sand_api_static(D, z, phi, p_0_)

    A = max(0.9, 3 - 0.8*z/D)

    if phi <= 30:
        a = 1.019E01
        b = -5.770E02
        c = 8.173E03
        phi = max(29, phi)

    elif phi <= 36:
        a = 4.226E-01
        b = -1.763E01
        c = 1.790E02

    elif phi <= 40:
        a = 8.571E-01
        b = -4.874E01
        c = 7.356E02
    else:
        a = 0
        b = 1.800E01
        c = -5.630E02
        phi = min(43, phi)
        
    k = (a*np.power(phi, 2) + b*phi + c) * 0.271 # 271

    p = A*p_ult*np.tanh((k*z/A/max(1e-10, p_ult))*y)

    save_parameter = {'p_ult[calc_py]': p_ult,
                      'A[calc_py]': A,
                      'k[calc_py]': k,
                      'p_calc[calc_py]': p,
                      'y_calc[calc_py]': y}
    
    save_parameter = {**save_parameter, **save_parameter_p_ult}

    return p, p_ult, save_parameter


# %% --- P-ULT RESISTANCE

def p_ult_resistance(depth_i, soil_data_dis_dict, dl_p_ult, 
                     capacity_dict, pf_soil_mat, 
                     b_outer_dis, a_shaft_diff_dis, a_shaft_global_dis,           
                     d_z_gdb,
                     z_gs=0,
                     su_api_thres=96):
    
    depth_dis = soil_data_dis_dict['depth'][(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2))]
    p_0__dis = soil_data_dis_dict['sigveff_rep'][(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2))]
    soil_type_dis = soil_data_dis_dict['Soil_Type'][(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2))]
    s_u_dis = soil_data_dis_dict['suc_'+dl_p_ult][(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2))]

    start_clay_mask = (np.char.lower(soil_type_dis) == 'clay') | (np.char.lower(soil_type_dis) == 'c') | (np.char.lower(soil_type_dis) == 'c_s')
    start_clay_index = start_clay_mask.argmax()
    start_clay_depth = depth_dis[start_clay_index]
    start_clay_s_u = s_u_dis[start_clay_index]

    L_D_dis = depth_dis/b_outer_dis[-1]
    psi_dis = np.array([s_u_i/max(1e-10, p_0__i) for s_u_i, p_0__i, L_D_i in zip(s_u_dis, p_0__dis, L_D_dis) if (L_D_i <= 20 and L_D_i >= 0)])
    alpha_dis = np.array([0.5*np.power(psi_i, -0.5) if psi_i <= 1 else 0.5*np.power(psi_i, -0.25) for psi_i in psi_dis])
    if len(alpha_dis) > 0:
        if all([str(alpha_i) == 'nan' for alpha_i in alpha_dis]):
            alpha_ave = np.nan
        else:
            alpha_ave = np.nanmean(alpha_dis)
    else:
        alpha_ave = np.nan

    p_ult_parameter_inc = []

    for idx, (a_shaft_diff_dis_i, a_shaft_global_dis_i) in enumerate(zip(a_shaft_diff_dis, a_shaft_global_dis)):
        
        z_end_section_i = a_shaft_diff_dis_i[0]
        b_outer_i = a_shaft_diff_dis_i[3]

        try:
            z_start_section_i = a_shaft_diff_dis[idx + 1][0]
        except Exception:
            z_start_section_i = 0
    
        depth_total_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'depth')
        mask = ((depth_total_dis <= round(depth_i, 2)) & (depth_total_dis >= round(z_start_section_i, 2)) & (depth_total_dis <= round(z_end_section_i, 2)))
        
        depth_in_soil_dis = depth_total_dis[mask]
        length = len(depth_in_soil_dis)

        soil_type_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'Soil_Type', mask=mask, length=length)

        p_0__dis = bf.extract_array_from_dl(soil_data_dis_dict, f'sigveff_rep', mask=mask, length=length)
            
        s_u_c_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'suc_{dl_p_ult}', mask=mask, length=length)
        phi_dis = bf.extract_array_from_dl(soil_data_dis_dict, f'phi_{dl_p_ult}', mask=mask, length=length)

        for idx2 in range(len(depth_in_soil_dis)):
            depth_ii_1 = depth_in_soil_dis[idx2]
            if idx2 != 0:
                depth_ii_2 = depth_in_soil_dis[idx2-1]
                d_z_gdb = depth_ii_1 - depth_ii_2
            else:
                d_z_gdb = d_z_gdb
                
            depth_ii_1 = depth_in_soil_dis[idx2] - z_gs
            soil_type_ii = soil_type_dis[idx2]
            sus_u_c_ii_ii = s_u_c_dis[idx2]
            phi_ii = phi_dis[idx2]
            p_0__ii = p_0__dis[idx2]

            if soil_type_ii.lower() in ['c', 'c_s']:

                sub_capacity_entry = 'clay'
                
                if 'iso_old' in capacity_dict[sub_capacity_entry].lower():
                    p_ult_ii, save_parameter_ii = p_ult_clay_iso_old_static(b_outer_i, depth_ii_1, sus_u_c_ii_ii, p_0__ii)

                elif 'iso' in capacity_dict[sub_capacity_entry].lower():
                    p_ult_ii, save_parameter_ii = p_ult_clay_iso_static(b_outer_i, depth_ii_1, sus_u_c_ii_ii, p_0__ii, alpha_ave, start_clay_s_u, start_clay_depth)

                elif 'api' in capacity_dict[sub_capacity_entry].lower():
                    if sus_u_c_ii_ii <= su_api_thres:
                        p_ult_ii, save_parameter_ii = p_ult_soft_clay_api_static(b_outer_i, depth_ii_1, sus_u_c_ii_ii, p_0__ii)
                    else:
                        p_ult_ii, save_parameter_ii = p_ult_stiff_clay_api_static(b_outer_i, depth_ii_1, sus_u_c_ii_ii, s_u_c_dis, depth_in_soil_dis, p_0__ii)

                else:
                    p_ult_ii, save_parameter_ii = 0, {}
                    print(f'Error at p_ult for {capacity_dict[sub_capacity_entry].lower()}')

            elif soil_type_ii.lower() in ['s', 's_c', 'si']:

                sub_capacity_entry = 'sand'

                if 'dnv' in capacity_dict[sub_capacity_entry].lower():
                    p_ult_ii, save_parameter_ii = p_ult_sand_dnv_static(b_outer_i, depth_ii_1, phi_ii, p_0__ii)

                elif 'api' in capacity_dict[sub_capacity_entry].lower():
                    p_ult_ii, save_parameter_ii = p_ult_sand_api_static(b_outer_i, depth_ii_1, phi_ii, p_0__ii)

                elif 'iso' in capacity_dict[sub_capacity_entry].lower():
                    p_ult_ii, save_parameter_ii = p_ult_sand_iso_static(b_outer_i, depth_ii_1, phi_ii, p_0__ii)

                else:
                    p_ult_ii, save_parameter_ii = 0, {}
                    print(f'Error at p_ult for {capacity_dict[sub_capacity_entry].lower()}')

            p_ult_ii = p_ult_ii/pf_soil_mat

            P_ult_i = b_outer_i*d_z_gdb*p_ult_ii
            
            save_parameter_ii['soil_type_section_' + str(idx+1) + '[input]'] = soil_type_ii
            save_parameter_ii['z_section_' + str(idx+1) + '[calc]'] = float(depth_ii_1)
            save_parameter_ii['p_ult_section_' + str(idx+1) + '[calc]'] = float(p_ult_ii)
            save_parameter_ii['b_outer_section_' + str(idx+1) + '[geometry]'] = b_outer_i
            save_parameter_ii['P_ult_section_' + str(idx+1) + '[calc]'] = P_ult_i

            p_ult_parameter_inc.append(save_parameter_ii)
    
    P_ult = 0

    for save_parameter_ii in p_ult_parameter_inc:
        for key in save_parameter_ii:
            if 'P_ult' in key:
                P_ult = P_ult + save_parameter_ii[key]
        
    results_dict = {'P_ult[output]': P_ult,
                    'p_ult_parameter_inc': p_ult_parameter_inc,
                    'pf_soil_mat[input]': pf_soil_mat}
                        
    return results_dict

# %% --- P-Y DEFLECTION

def p_y_deflection(soil_data_dis_dict, dl_p_y, pf_soil_mat, capacity_dict,
                   length_embedment_i, H, V, calculation_method_i,
                   b_outer_dis, thickness_dis, z_gs, 
                   d_z_gdb,
                   su_api_thres=96, count_lim=1000, k_M_rot_stiff_factor=-8000, P_s_0=100, E_pile=210e3):
       
    depth_dis = soil_data_dis_dict['depth'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    p_0__dis = soil_data_dis_dict['sigveff_rep'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    soil_type_dis = soil_data_dis_dict['Soil_Type'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    s_u_dis = soil_data_dis_dict['suc_'+dl_p_y][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    phi_dis = soil_data_dis_dict['phi_'+dl_p_y][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    ip_dis = soil_data_dis_dict['plasticity_rep'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    ocr_dis = soil_data_dis_dict['ocr_rep'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]

    start_clay_mask = (np.char.lower(soil_type_dis) == 'clay') | (np.char.lower(soil_type_dis) == 'c') | (np.char.lower(soil_type_dis) == 'c_s')
    start_clay_index = start_clay_mask.argmax()
    start_clay_depth = depth_dis[start_clay_index]
    start_clay_s_u = s_u_dis[start_clay_index]

    L_D_dis = depth_dis/b_outer_dis
    psi_dis = np.array([s_u_i/max(1e-10, p_0__i) for s_u_i, p_0__i, L_D_i in zip(s_u_dis, p_0__dis, L_D_dis) if (L_D_i <= 20 and L_D_i >= 0)])
    alpha_dis = np.array([0.5*np.power(psi_i, -0.5) if psi_i <= 1 else 0.5*np.power(psi_i, -0.25) for psi_i in psi_dis])
    if len(alpha_dis) > 0:
        if all([str(alpha_i) == 'nan' for alpha_i in alpha_dis]):
            alpha_ave = np.nan
        else:
            alpha_ave = np.nanmean(alpha_dis)
    else:
        alpha_ave = np.nan

    N = len(depth_dis)
    K = np.zeros((N, N))
    B = np.zeros(N)
    y = [np.zeros(N)]

    M = np.zeros(N)    
    Q = np.zeros(N)

    P_s = [np.array([0 if depth_i < 0 else P_s_0 for depth_i in depth_dis])]
    pf_soil_mat_dis = np.array([pf_soil_mat for depth_i in depth_dis])

    count = 1
    Err = [1]
    k = k_M_rot_stiff_factor

    I_annulus_dis = np.pi/64*(np.power(b_outer_dis, 4) - np.power(b_outer_dis - 2*thickness_dis, 4))
    I_annulus_ave = np.average(I_annulus_dis)

    while Err[-1] > 1e-6 and count < count_lim:

        save_parameter_inc = []

        if calculation_method_i == 'free_head':
            B[0] = 2*H*d_z_gdb**3
            K[0,0] = (2*E_pile*I_annulus_ave) +  (P_s[count-1][0]*d_z_gdb**4)
            K[0,1] = (-4*E_pile*I_annulus_ave)
            K[0,2] = (2*E_pile*I_annulus_ave)

            K[1,0] = (-2*E_pile*I_annulus_ave) + (V*d_z_gdb**2)
            K[1,1] = (5*E_pile*I_annulus_ave) - (2*V*d_z_gdb**2) + (P_s[count-1][1]*d_z_gdb**4) 
            K[1,2] = (-4*E_pile*I_annulus_ave) + (V*d_z_gdb**2)
            K[1,3] = (E_pile*I_annulus_ave)

        elif calculation_method_i == 'fixed_head':
            B[0] = 2*H*d_z_gdb**3
            K[0,0] = (6*E_pile*I_annulus_ave) - (2*V*d_z_gdb**2) + (P_s[count-1][0]*d_z_gdb**4) 
            K[0,1] = (-8*E_pile*I_annulus_ave) + (2*V*d_z_gdb**2)
            K[0,2] = (2*E_pile*I_annulus_ave)

            K[1,0] = (-4*E_pile*I_annulus_ave) + (V*d_z_gdb**2)
            K[1,1] = (7*E_pile*I_annulus_ave) - (2*V*d_z_gdb**2) + (P_s[count-1][1]*d_z_gdb**4) 
            K[1,2] = (-4*E_pile*I_annulus_ave) + (V*d_z_gdb**2)
            K[1,3] = (E_pile*I_annulus_ave)

        elif calculation_method_i == 'stiff_head':
            B[0] = 2*H*d_z_gdb**3
            K[0,0] = ((6 - 4/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))*E_pile*I_annulus_ave) + ((-2 + 2/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))*V*d_z_gdb**2) + (P_s[count-1][0]*d_z_gdb**4) 
            K[0,1] = ((-6 + 2*(1 + k*d_z_gdb/(2*E_pile*I_annulus_ave))/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))*E_pile*I_annulus_ave) + ((1 - (1 + k*d_z_gdb/(2*E_pile*I_annulus_ave))/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))*V*d_z_gdb**2)
            K[0,2] = (2*E_pile*I_annulus_ave)

            K[1,0] = ((-4 + 2/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))*E_pile*I_annulus_ave) + (V*d_z_gdb**2)
            K[1,1] = ((6 - (1 + k*d_z_gdb/(2*E_pile*I_annulus_ave))/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))*E_pile*I_annulus_ave) - (2*V*d_z_gdb**2) + (P_s[count-1][1]*d_z_gdb**4) 
            K[1,2] = (-4*E_pile*I_annulus_ave) + (V*d_z_gdb**2)
            K[1,3] = (E_pile*I_annulus_ave)

        for i in range(2, N-2):
            K[i,i-2] = (E_pile*I_annulus_ave) 
            K[i,i-1] = (-4*E_pile*I_annulus_ave)  + (V*d_z_gdb**2) 
            K[i,i]   = (6*E_pile*I_annulus_ave) - (2*V*d_z_gdb**2) + (P_s[count-1][i]*d_z_gdb**4) 
            K[i,i+1] = (-4*E_pile*I_annulus_ave)  + (V*d_z_gdb**2) 
            K[i,i+2] = (E_pile*I_annulus_ave) 

        K[-2,-4] = (E_pile*I_annulus_ave) 
        K[-2,-3] = (-4*E_pile*I_annulus_ave) + (V*d_z_gdb**2) 
        K[-2,-2] = (5*E_pile*I_annulus_ave) - (2*V*d_z_gdb**2) + (P_s[count-1][-1]*d_z_gdb**4) 
        K[-2,-1] = (-2*E_pile*I_annulus_ave) + (V*d_z_gdb**2) 

        K[-1,-3] = (2*E_pile*I_annulus_ave) 
        K[-1,-2] = (-4*E_pile*I_annulus_ave) 
        K[-1,-1] = (2*E_pile*I_annulus_ave) + (P_s[count-1][-2]*d_z_gdb**4) 
        
        y_i = np.linalg.solve(K, B) # m
        y_i = np.array([1e-10 if yi == 0 else yi for yi in y_i])
        
        p_ult = np.zeros(N)
        p_i = np.zeros(N)
        P_s_i = np.zeros(N)

        for idx in range(len(depth_dis)):
            z1_ii = depth_dis[idx]
            if round(z1_ii, 2) < 0:
                p_i[idx] = 0
                save_parameter_ii = {}
            else:
                z2_ii = depth_dis[idx] - z_gs
                soil_type_ii = soil_type_dis[idx]
                su_ii = s_u_dis[idx]
                phi_ii = phi_dis[idx]
                ip_ii = ip_dis[idx]
                ocr_ii = ocr_dis[idx]
                p_0__ii = p_0__dis[idx]
                b_outer_diff_ii = b_outer_dis[idx]

                if soil_type_ii.lower() in ['c', 'c_s']:

                    sub_capacity_entry = 'clay'

                    if 'iso_old' in capacity_dict[sub_capacity_entry].lower():
                        p_ii, p_ult_ii, save_parameter_ii = p_y_clay_iso_old_static(y_i[idx], b_outer_diff_ii, z2_ii, su_ii, p_0__ii)
                        p_ult[idx] = p_ult_ii
                        p_i[idx] = p_ii

                    elif 'iso' in capacity_dict[sub_capacity_entry].lower():
                        p_ii, p_ult_ii, save_parameter_ii = p_y_clay_iso_static(y_i[idx], b_outer_diff_ii, z2_ii, su_ii, p_0__ii, ip_ii, ocr_ii, alpha_ave, start_clay_s_u, start_clay_depth)
                        p_ult[idx] = p_ult_ii
                        p_i[idx] = p_ii

                    elif 'api' in capacity_dict[sub_capacity_entry].lower():
                        if su_ii <= su_api_thres:
                            p_ii, p_ult_ii, save_parameter_ii = p_y_soft_clay_api_static(y_i[idx], b_outer_diff_ii, z2_ii, su_ii, p_0__ii)
                            p_ult[idx] = p_ult_ii
                            p_i[idx] = p_ii
                        else:
                            p_ii, p_ult_ii, save_parameter_ii = p_y_stiff_clay_api_static(y_i[idx], b_outer_diff_ii, z2_ii, su_ii, s_u_dis, depth_dis, p_0__ii)
                            p_ult[idx] = p_ult_ii
                            p_i[idx] = p_ii

                elif soil_type_ii.lower() in ['s', 's_c', 'si']:

                    sub_capacity_entry = 'sand'

                    if 'dnv' in capacity_dict[sub_capacity_entry].lower():
                        p_ii, p_ult_ii, save_parameter_ii = p_y_sand_dnv_static(y_i[idx], b_outer_diff_ii, z2_ii, phi_ii, p_0__ii)
                        p_ult[idx] = p_ult_ii
                        p_i[idx] = p_ii

                    elif 'api' in capacity_dict[sub_capacity_entry].lower():
                        p_ii, p_ult_ii, save_parameter_ii = p_y_sand_api_static(y_i[idx], b_outer_diff_ii, z2_ii, phi_ii, p_0__ii)
                        p_ult[idx] = p_ult_ii
                        p_i[idx] = p_ii

                    elif 'iso' in capacity_dict[sub_capacity_entry].lower():
                        p_ii, p_ult_ii, save_parameter_ii = p_y_sand_iso_static(y_i[idx], b_outer_diff_ii, z2_ii, phi_ii, p_0__ii)
                        p_ult[idx] = p_ult_ii
                        p_i[idx] = p_ii

            save_parameter_ii['z_section_1[input]'] = float(z1_ii)
            save_parameter_inc.append(save_parameter_ii)

        p_i = p_i/pf_soil_mat_dis
        
        P_s_i = np.array([p_i[i]/y_i[i] for i in range(N)])
        P_s_i = np.array([0 if (zi - z_gs) < 0 else P_s_ii for zi, P_s_ii in zip(depth_dis, P_s_i)])
        P_s.append(P_s_i)

        Err.append(np.sum(np.abs(y_i - y[-1])))
        y.append(y_i)

        count += 1

    if count == count_lim:
        print(f' ----- Reached count limit = {count_lim} at {H} kN')

    for i in range(N):
        if i == 0:
            if calculation_method_i == 'free_head':
                ya = 2*y_i[i] - y_i[i+1]
                yb = y_i[i]
                yc = y_i[i+1]
            elif calculation_method_i == 'fixed_head':
                ya = y_i[i+1]
                yb = y_i[i]
                yc = y_i[i+1]
            elif calculation_method_i == 'stiff_head':
                ya = y_i[i] * (2 / (1 - k*d_z_gdb/(2*E_pile*I_annulus_ave))) - y_i[i+1] * ((1 + k*d_z_gdb/(2*E_pile*I_annulus_ave))/(1 - k*d_z_gdb/(2*E_pile*I_annulus_ave)))
                yb = y_i[i]
                yc = y_i[i+1]
        elif i == N-1:
            ya = y_i[i-1]
            yb = y_i[i]
            yc = 2*y_i[i] - y_i[i-1]
        else:
            ya = y_i[i-1]
            yb = y_i[i]
            yc = y_i[i+1]

        M[i] = -E_pile*I_annulus_ave/d_z_gdb**2*(ya - 2*yb +yc)

    Q[0] = (1/(2*d_z_gdb))*(-3*M[0] + 4*M[1] - M[2])
    for i in range(1, N-1):
        Q[i] = (1/(2*d_z_gdb))*(M[i+1] - M[i-1])
    Q[-1] = (1/(2*d_z_gdb))*(3*M[-1] - 4*M[-2] + M[-3])

    R = np.zeros(N)
    R[0] = (1/(2*d_z_gdb))*(-3*y_i[0] + 4*y_i[1] - y_i[2])
    for i in range(1, N-1):
        R[i] = (1/(2*d_z_gdb))*(y_i[i+1] - y_i[i-1])
    R[-1] = (1/(2*d_z_gdb))*(3*y_i[-1] - 4*y_i[-2] + y_i[-3])

    part1 = np.linspace(0, 0.01 * b_outer_dis[-1], 200, endpoint=False)
    part2 = np.linspace(0.01 * b_outer_dis[-1], 0.05 * b_outer_dis[-1], 100, endpoint=False)
    part3 = np.linspace(0.05 * b_outer_dis[-1], 0.1 * b_outer_dis[-1], 100)
    part4 = np.linspace(0.1 * b_outer_dis[-1], 0.5 * b_outer_dis[-1], 100)

    x_background = list(np.concatenate([part1, part2, part3, part4]))
    y_background = []
    
    for idx in range(len(depth_dis)):
        z1_ii = depth_dis[idx]
        if round(z1_ii, 2) < 0:
            y_background.append(list(np.zeros(len(x_background))))
        else:
            z2_ii = depth_dis[idx] - z_gs
            soil_type_ii = soil_type_dis[idx]
            su_ii = s_u_dis[idx]
            ip_ii = ip_dis[idx]
            ocr_ii = ocr_dis[idx]
            phi_ii = phi_dis[idx]
            p_0__ii = p_0__dis[idx]
            b_outer_diff_ii = b_outer_dis[idx]

            if soil_type_ii.lower() in ['c', 'c_s']:

                sub_capacity_entry = 'clay'

                if 'iso_old' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([p_y_clay_iso_old_static(x_ii, b_outer_diff_ii, z2_ii, su_ii, p_0__ii)[0] for x_ii in x_background])

                if 'iso' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([p_y_clay_iso_static(x_ii, b_outer_diff_ii, z2_ii, su_ii, p_0__ii, ip_ii, ocr_ii, alpha_ave, start_clay_s_u, start_clay_depth)[0] for x_ii in x_background])
                    
                elif 'api' in capacity_dict[sub_capacity_entry].lower():
                    if su_ii <= su_api_thres:
                        y_background.append([p_y_soft_clay_api_static(x_ii, b_outer_diff_ii, z2_ii, su_ii, p_0__ii)[0] for x_ii in x_background])
                    else:
                        y_background.append([p_y_stiff_clay_api_static(x_ii, b_outer_diff_ii, z2_ii, su_ii, s_u_dis, depth_dis, p_0__ii)[0] for x_ii in x_background])

            elif soil_type_ii.lower() in ['s', 's_c', 'si']:

                sub_capacity_entry = 'sand'

                if 'dnv' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([p_y_sand_dnv_static(x_ii, b_outer_diff_ii, z2_ii, phi_ii, p_0__ii)[0] for x_ii in x_background])

                elif 'api' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([p_y_sand_api_static(x_ii, b_outer_diff_ii, z2_ii, phi_ii, p_0__ii)[0] for x_ii in x_background])

                elif 'iso' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([p_y_sand_iso_static(x_ii, b_outer_diff_ii, z2_ii, phi_ii, p_0__ii)[0] for x_ii in x_background])
                   
    results_dict = {'z[input]': depth_dis,
                    'soil_type[input]': soil_type_dis,
                    'pf_soil_mat[input]': pf_soil_mat_dis,
                    'p_ult[output]': p_ult,
                    'p_calc[output]': p_i,
                    'y_calc[output]': y_i,
                    'P_s[output]': P_s_i,
                    'M[output]': M,
                    'Q[output]': Q,
                    'R[output]': R,
                    'x_background': x_background,
                    'y_background': y_background}
                                
    return results_dict