# python modules
import numpy as np

# %% --- SUCTION UNDERPRESSURE, UREQ

def suction_underpressure_setup(depth, 
                                soil_type, 
                                depth_dis, 
                                soil_type_dis, 
                                b_outer, 
                                t, 
                                no_flow_materials=['c', 'c_s']):

    no_flow_layering = []
    count_no_flow = 0
    count_flow = 0
    for depth_i, soil_type_i in zip(depth_dis, soil_type_dis):
        if count_no_flow == 0 and soil_type_i.lower() in no_flow_materials:
            no_flow_layering.append([depth_i, np.nan])
            count_no_flow += 1
            count_flow = 0
        elif soil_type_i.lower() in no_flow_materials and len(no_flow_layering) > 0:
            no_flow_layering[-1][1] = depth_i
            count_flow = 0
        elif count_flow == 0 and soil_type_i.lower() not in no_flow_materials and len(no_flow_layering) > 0:
            no_flow_layering[-1][1] = depth_i
            count_flow += 1
            count_no_flow = 0
        else:
            count_no_flow = 0

    if len(no_flow_layering) == 0:
        no_flow_layering = [[np.inf, np.inf]]
    
    z_no_flow_below = None

    for data in no_flow_layering:
        if depth <= data[0]:
            z_no_flow_below = data[0]
            break

    if z_no_flow_below is None:
        z_no_flow_below = 1e10

    flow_condition = None

    if soil_type.lower() in no_flow_materials:
        flow_condition = 'no_flow'
        z = depth
        z_t = 0
        z_t_index = 0

    elif depth < no_flow_layering[0][0]:
        flow_condition = 'full_flow'
        z = depth
        z_t = 0
        z_t_index = 0
        
    else:
        flow_condition = 'partial_flow'
        for data in no_flow_layering:
            if depth >= data[1]:
                z_t = data[1]
        z = depth - z_t
        z_t_index = np.where(depth_dis == z_t)[0][0]

    z_b = z_no_flow_below - depth
    z_b_div_D = min(max(1e-10, z_b/b_outer), 2)
    z_div_D =  max(1e-10, z/b_outer)
    z_div_t =  max(1e-10, z/t)

    return z, z_t, z_t_index, z_b, z_b_div_D, z_div_D, z_div_t, flow_condition


def suction_underpressure(depth_i, soil_data_dis_dict, dl_b,
                          calculation_method_i,
                          a_base_diff_dis,
                          W_t_total,
                          Q_s_inner_array, Q_s_outer_array, Q_b_total, Q_t_total,
                          t_ss_array,
                          d_z_gdb,
                          gamma_w=10,
                          T_ss=10):
    
    base_area_outer_i = a_base_diff_dis[0][2]
    base_area_inner_i = a_base_diff_dis[0][3]
    b_outer_diff_i = a_base_diff_dis[0][4]
    t_diff_i = a_base_diff_dis[0][5]

    depth_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    qc_dis = np.array(soil_data_dis_dict['qc_' + dl_b])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    p_0__dis = np.array(soil_data_dis_dict['sigveff_rep'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    soil_type_dis = np.array(soil_data_dis_dict['Soil_Type'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    gamma__dis = np.array(soil_data_dis_dict['effunitweight_rep'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    ki_ko_dis = np.array(soil_data_dis_dict['ki_ko'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    k_v_dis = np.array(soil_data_dis_dict['kv_rep'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    k_h_dis = np.array(soil_data_dis_dict['kh_rep'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    M_dis = np.array(soil_data_dis_dict['consmodulus_rep'])[(np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    
    z_index = np.where(depth_dis == depth_i)
    soil_type_i = soil_type_dis[z_index][0]
    gamma__i = gamma__dis[z_index][0]
    p_0__i = p_0__dis[z_index][0]
    ki_ko_i = ki_ko_dis[z_index][0]
    k_v_i = k_v_dis[z_index][0]
    k_h_i = k_h_dis[z_index][0]
    k_o_i = (k_v_i + k_h_i)/2
    k_i_i = k_o_i*ki_ko_i
    M_i = M_dis[z_index][0]*1000
    
    if np.isnan(gamma__i):
        gamma__i = 10

    if np.isnan(p_0__i):
        p_0__dis = np.array([z_i*gamma__i for z_i in depth_dis])
        p_0__i = gamma__i*depth_i
        
    if np.isnan(ki_ko_i):
        if soil_type_i.lower() in ['c', 'c_s']:
            ki_ko_i = 1
        else:
            ki_ko_i = 4
        
    z, z_t, z_t_index, z_b, z_b_div_D, z_div_D, z_div_t, flow_condition = suction_underpressure_setup(depth_i, soil_type_i, depth_dis, soil_type_dis, b_outer_diff_i, t_diff_i)

    if 'no_flow' in calculation_method_i or 'removal' in calculation_method_i:
        flow_condition = 'no_flow'

    if flow_condition in ['no_flow']:
        Q_t_installation = Q_t_total
        S_n_cr = np.nan
        add_dict = {'flow_condition[calc_t]# - ? -': flow_condition}

    elif flow_condition in ['full_flow']:
        p_0_z = p_0__i

        alpha = 4.8623 / (16.1833*z_b_div_D) + 0.9701
        beta = 1.9338 - np.tanh((z_b_div_D + 0.1273)/0.2282)
        chi = -0.4163 + np.tanh((z_b_div_D + 0.0498)/0.4026)
        delta = 0.8350 / (4.6850*z_b_div_D) + 0.5159

        W_eq = W_t_total
        Q_t_total_z = Q_t_total
        W_soil_F = 0.001*(base_area_inner_i*p_0_z)

    elif flow_condition in ['partial_flow']:
        Q_s_inner_zt = Q_s_inner_array[z_t_index]
        Q_s_outer_zt = Q_s_outer_array[z_t_index]

        Q_s_inner_z = Q_s_inner_array[-1] - Q_s_inner_zt
        Q_s_outer_z = Q_s_outer_array[-1] - Q_s_outer_zt

        p_0_zt = p_0__dis[z_t_index]
        p_0_z = p_0__i - p_0_zt

        Q_b_z = Q_b_total

        alpha = 1.8981 - np.tanh((z_b_div_D - 0.1377)/0.3883)
        beta = 0.45285
        chi = 0.2315 + np.tanh((z_b_div_D - 0.0306)/0.8673)
        delta = -0.9150 + np.tanh((z_b_div_D + 0.6402)/0.3472)

        W_soil_eq = 0.001*(base_area_inner_i*p_0_zt)
        W_eq = max(0, W_t_total + W_soil_eq - Q_s_outer_zt)
        Q_t_total_z = Q_s_inner_z + Q_s_outer_z + Q_b_z
        W_soil_F = 0.001*(base_area_inner_i*p_0_z)      

    if flow_condition in ['full_flow', 'partial_flow']:
        off = W_eq / max(1e-10, Q_t_total_z)
        S_n_cr = alpha * gamma_w/gamma__i * ((np.pi/4*ki_ko_i + beta + 11/4*z_div_D*chi)/(11/4*z_div_D + delta))
        gR =  W_soil_F * S_n_cr / max(1e-10, Q_t_total_z)

        z_div_t = min(500, z_div_t)
        x = np.linspace(0, 1, 1001)
        line = gR*x + off
        ellipse = np.power(1 - np.power(x, 0.05*z_div_t), 1/(0.0017*np.power(z_div_t, 2) + 0.2))
        diff = line - ellipse
        idx = np.where(np.sign(diff[:-1]) != np.sign(diff[1:]))[0]
        x_intersections = []
        y_intersections = []

        for i in idx:
            x0, x1 = x[i], x[i+1]
            y0, y1 = diff[i], diff[i+1]

            xi = x0 - y0 * (x1 - x0) / (y1 - y0)
            yi = gR*xi + off

            x_intersections.append(xi)
            y_intersections.append(yi)

        x_intersections = np.array(x_intersections)
        y_intersections = np.array(y_intersections)
        
        S_n_div_S_n_cr = 0
        Q_t_flow_Q_div_t_total = 1
        if len(y_intersections) > 0:
            S_n_div_S_n_cr = x_intersections[0]
            Q_t_flow_Q_div_t_total = y_intersections[0]

        z, z_t, z_t_index, z_b, z_b_div_D, z_div_D, z_div_t, flow_condition

        add_dict = {'z_perm[calc_t]# z<sub>perm</sub> (m) ? -': z,
                    'z_perm/D[calc_t]# z<sub>perm</sub>/D (-) ? -': z_div_D,
                    'z_nonperm[calc_t]# z<sub>non-perm</sub> (m) ? -': z_t,
                    'z_perm/t[calc_t]# z<sub>perm</sub>/t (-) ? -': z_div_t,
                    'z_to_next_nonperm[calc_t]# z<sub>to non-perm</sub> (m) ? -': z_b,
                    'z_to_next_nonperm/D[calc_t]# z<sub>to non-perm</sub>/D (-) ? -': z_b_div_D,
                    'flow_condition[calc_t]# Flow condition (-) ? -': flow_condition,
                    'W_eq[calc_t]# W<sub>eq</sub> (MN) ? -': W_eq,
                    'W_soil[calc_t]# W<sub>soil</sub> (MN) ? -': W_soil_F,
                    'Q_t_PF[calc_t]# Q<sub>t,PF</sub> (MN) ? -': Q_t_total_z,
                    'W_eq/P_f_NF[calc_t]# W<sub>eq</sub>/P<sub>f,NF</sub> (-) ? -': off,
                    'W_soil/P_f_NF[calc_t]# W<sub>soil</sub>/P<sub>f,NF</sub> (-) ? -': gR,
                    'S_n/S_n_cr[calc_t]# S<sub>n</sub>/S<sub>n,cr</sub> (-) ? -': S_n_div_S_n_cr,
                    'P_f_PF/P_f_NF[calc_t]# P<sub>f,PF</sub>/P<sub>f,NF</sub> (-) ? -': Q_t_flow_Q_div_t_total,}
        
    if flow_condition in ['full_flow']:
        Q_t_flow = Q_t_total_z*Q_t_flow_Q_div_t_total
        Q_t_installation = Q_t_flow
        U_req = max(0, (Q_t_installation - W_t_total)*1000/base_area_outer_i)
        t_ss = 0
        d_heave_klinkvort = 0

    elif flow_condition in ['partial_flow']:
        Q_t_flow = Q_t_total_z*Q_t_flow_Q_div_t_total
        U_eq = 1000*(Q_t_flow - W_eq)/base_area_outer_i
        Q_t_installation = Q_t_flow + Q_s_inner_zt + Q_s_outer_zt
        U_req = max(0, U_eq + 1000*(W_soil_eq + Q_s_inner_zt)/base_area_outer_i)

        add_dict['U_eq[output_t]# U<sub>eq</sub> (kPa) ? -'] = U_eq

        H_eq = max(0, U_eq / gamma_w)

        alpha_w = 1.997 - np.tanh((z_b_div_D - 0.3505)/0.7270)
        beta_w = -0.7928 + np.tanh((z_b_div_D + 0.9277)/0.9068)
        chi_w = 1
        delta_w = -1.000 + np.tanh((z_b_div_D + 6.4375)/0.6643)

        q_i_div_k_i = H_eq / max(1e-10, z) * ((11/4*z_div_D + delta_w)/(alpha_w*(np.pi/4*ki_ko_i + beta_w + 11/4*z_div_D*chi_w)))
        q_i = q_i_div_k_i * k_i_i
        add_dict['q/ki[output_t]# q/k<sub>i</sub> (-) ? -'] = q_i_div_k_i
        add_dict['q[output_t]# q (-) ? -'] = q_i

        t_ss = (gamma__i*np.power(z+2*b_outer_diff_i, 2))/(k_i_i*M_i)*T_ss
        d_t_ss = t_ss - t_ss_array[-1]
        add_dict['d_t_ss[output_t]# d<sub>t,ss</sub> (-) ? -'] = d_t_ss
        d_heave_klinkvort = d_t_ss*q_i

    else:
        U_req = max(0, (Q_t_installation - W_t_total)*1000/base_area_outer_i)
        t_ss = 0
        d_heave_klinkvort = 0
    
    if U_req == 0:
        inner_outer_heave_ratio = 0.5
    else:
        if soil_type_i.lower() in ['s', 's_c', 'si']:
            inner_outer_heave_ratio = 1
        else:
            inner_outer_heave_ratio = 1

    d_heave_klinkvort += 4*t_diff_i*(b_outer_diff_i - t_diff_i)*d_z_gdb/np.power(b_outer_diff_i - 2*t_diff_i, 2)*inner_outer_heave_ratio
    add_dict['t_ss[output_t]# t<sub>ss</sub> (s) ? -'] = t_ss
    add_dict['d_heave_klinkvort[output_t]# d<sub>heave,klinkvort</sub> (m) ? -'] = d_heave_klinkvort
    
    S_n = U_req / max(1e-10, p_0__i)

    sum_w = 0
    sum_w_q_c = 0

    for z_ii, q_c_ii, soil_type_ii in zip(depth_dis, qc_dis, soil_type_dis):
        if z_ii <= depth_i and soil_type_ii.lower() in ['s', 's_c', 'si']:
            w_ii = (depth_i - z_ii)/t_diff_i
            w_q_c_ii = w_ii*q_c_ii
            sum_w += w_ii
            sum_w_q_c += w_q_c_ii

    q_c_w_ave = sum_w_q_c/max(1e-10, sum_w)
    
    alpha = inner_outer_heave_ratio + (227.4*U_req + 1000*q_c_w_ave)/(830*100)
    d_heave_gunawan = 4*t_diff_i*(b_outer_diff_i - t_diff_i)*d_z_gdb/np.power(b_outer_diff_i - 2*t_diff_i, 2) * alpha
    add_dict['d_heave_gunawan[output_t]# d<sub>heave,gunawan</sub> (-) ? -'] = d_heave_gunawan

    results_dict_underpressure = {'U_req[output_t]# U<sub>req</sub> (kPa) ? -': U_req,
                                  'S_n[output_t]# S<sub>n</sub> (-) ? -': S_n,
                                  'S_n_cr[output_t]# S<sub>n,cr</sub> (-) ? -': S_n_cr,
                                  'Q_t_ins[output_t]# Q<sub>t,ins</sub> (MN) ? -': Q_t_installation}
    
    results_dict_underpressure = {**results_dict_underpressure, **add_dict}

    return results_dict_underpressure