# python modules
import numpy as np

# multiconsult modules
import _background_functions as bf

# %% --- T-Z ---

def t_z_static(z, t_ult, t_res_norm, D, z_ult_norm=0.01):

    if z < 0:
        mult = -1
    else:
        mult = 1

    z = abs(z)
    z_ult = z_ult_norm*D

    if z <= 0.16*z_ult:
        z1 = 0
        z2 = 0.16
        t1 = 0
        t2 = 0.3
    elif z <= 0.31*z_ult:
        z1 = 0.16
        z2 = 0.31
        t1 = 0.3
        t2 = 0.5
    elif z <= 0.57*z_ult:
        z1 = 0.31
        z2 = 0.57
        t1 = 0.5
        t2 = 0.75
    elif z <= 0.80*z_ult:
        z1 = 0.57
        z2 = 0.80
        t1 = 0.75
        t2 = 0.9
    elif z <= z_ult:
        z1 = 0.80
        z2 = 1
        t1 = 0.9
        t2 = 1
    elif z <= 2.0*z_ult:
        z1 = 1
        z2 = 2
        t1 = 1
        t2 = t_res_norm
    else:
        z1 = 2
        z2 = 1e10
        t1 = t_res_norm
        t2 = t_res_norm

    m = ((t2 - t1)*t_ult)/((z2 - z1)*z_ult)
    t = mult*(m*z + t1*t_ult - m*z1*z_ult)

    save_parameter = {'t_ult[calc_tz]# t<sub>ult</sub> (MN/m) ? -': t_ult,
                      'z_ult[calc_tz]# z<sub>ult</sub> (m) ? -': z_ult,
                      't_calc[calc_tz]# t (MN/m) ? -': t,
                      'z_calc[input_tz]# z (m) ? -': z}
    
    return t, t_ult, save_parameter


# %% --- Q-Z ---

def q_z_static(z, q_ult, D, z_ult=0.1):

    if z < 0:
        mult = -1
    else:
        mult = 1

    z = abs(z)
    z_ult = z_ult*D

    if z <= 0.02*z_ult:
        z1 = 0
        z2 = 0.02
        q1 = 0
        q2 = 0.3
    elif z <= 0.13*z_ult:
        z1 = 0.02
        z2 = 0.13
        q1 = 0.3
        q2 = 0.5
    elif z <= 0.42*z_ult:
        z1 = 0.13
        z2 = 0.42
        q1 = 0.5
        q2 = 0.75
    elif z <= 0.73*z_ult:
        z1 = 0.42
        z2 = 0.73
        q1 = 0.75
        q2 = 0.9
    elif z <= z_ult:
        z1 = 0.73
        z2 = 1
        q1 = 0.9
        q2 = 1
    else:
        z1 = 1
        z2 = 1e10
        q1 = q_ult
        q2 = q_ult

    m = ((q2 - q1)*q_ult)/((z2 - z1)*z_ult)
    q = mult*(m*z + q1*q_ult - m*z1*z_ult)

    save_parameter = {'q_ult[calc_qz]# Q<sub>ult</sub> (MN) ? -': q_ult,
                      'z_ult[calc_qz]# z<sub>ult</sub> (m) ? -': z_ult,
                      'q[calc_qz]# qQ (MN) ? -': q,
                      'z_calc[calc_qz]# z (m) ? -': z}
    
    save_parameter = {**save_parameter}

    return q, q_ult, save_parameter


# %% --- T-Z DEFLECTION

def t_z_deflection(soil_data_dis_dict, pf_soil_mat, capacity_dict, calculation_method_ii,
                   length_embedment_i, V, calculation_method_i, pf_load_perm,
                   a_base_annulus_dis, b_outer_dis, a_base_bi_dis, z_gs, 
                   d_z_gdb,
                   Q_s_inner_total, Q_s_outer_total, Q_b_total,
                   conductor,
                   t_t_max_clay=0.9, t_t_max_sand=1, uw_s_steel=6850,
                   count_lim=1000, T_s_0=100, Q_s_0=100, E_pile=210e3):
    
    '''
    Update to have AI(i) with depth
    '''
       
    depth_dis = soil_data_dis_dict['depth'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
    soil_type_dis = soil_data_dis_dict['Soil_Type'][(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment_i, 2))]
   
    N = len(depth_dis)
    K = np.zeros((N, N))
    B = np.zeros(N)
    z = [np.zeros(N)]
   
    N_ax = np.zeros(N)

    T_s = [np.array([0 if depth_i < 0 else T_s_0 for depth_i in depth_dis])]
    Q_s = [np.array([0 if depth_i < 0 else Q_s_0 for depth_i in depth_dis])]
    pf_soil_mat_dis = np.array([pf_soil_mat for depth_i in depth_dis])

    count = 1
    Err = [1]

    A_annulus_ave = np.average(a_base_annulus_dis)
    W_pile_dis = a_base_annulus_dis * uw_s_steel * pf_load_perm * 9.81/1e6

    if calculation_method_ii.lower() == 'cored':
        W_plug_dis = np.zeros(len(W_pile_dis))
    else:
        W_plug_dis = a_base_bi_dis * 1000 * pf_load_perm * 9.81/1e6 # maybe update with actually soil weight

    if 'conductor_analysis' in conductor:
        if conductor['conductor_analysis']:
            W_plug_dis = np.zeros(len(W_pile_dis))
            W_pile_dis = np.zeros(len(W_pile_dis))

    while Err[-1] > 1e-6 and count < count_lim:

        save_parameter_inc = []

        B[0] = 2*V*d_z_gdb
        K[0,0] = (2*E_pile*A_annulus_ave) + (T_s[count-1][0]*d_z_gdb**2)
        K[0,1] = (-2*E_pile*A_annulus_ave)

        for i in range(1, N-1):
            depth_i = depth_dis[i]
            if depth_i < 0:
                B[i] = W_pile_dis[i]*d_z_gdb**2
            else:
                B[i] = (W_pile_dis[i] + W_plug_dis[i])*d_z_gdb**2
            K[i,i-1] = (-E_pile*A_annulus_ave) 
            K[i,i]   = (2*E_pile*A_annulus_ave) + (T_s[count-1][i]*d_z_gdb**2) 
            K[i,i+1] = (-E_pile*A_annulus_ave) 

        B[-1] = (W_pile_dis[-1] + W_plug_dis[-1])*d_z_gdb**2
        if calculation_method_i == 'free_tip':
            K[-1,-2] = (-2*E_pile*A_annulus_ave) 
            K[-1,-1] = (2*E_pile*A_annulus_ave) + (T_s[count-1][-1]*d_z_gdb**2) 
        elif calculation_method_i == 'q_z_tip':
            K[-1,-2] = (-2*E_pile*A_annulus_ave) 
            K[-1,-1] = (2*E_pile*A_annulus_ave) + (2*Q_s[count-1][-1]*d_z_gdb) + (T_s[count-1][-1]*d_z_gdb**2) 
        
        z_i = np.linalg.solve(K, B) # m
        z_i = np.array([1e-10 if zi == 0 else zi for zi in z_i])
        
        t_ult = np.zeros(N)
        t_i = np.zeros(N)
        q_ult = np.zeros(N)
        q_i = np.zeros(N)
        
        for idx in range(len(depth_dis)):
            depth_i = depth_dis[idx]
            soil_type_ii = soil_type_dis[idx]
            b_outer_diff_ii = b_outer_dis[idx]

            Q_s_inner_i = Q_s_inner_total[idx]
            Q_s_outer_i = Q_s_outer_total[idx]
            Q_s_total_i = (Q_s_inner_i + Q_s_outer_i)/d_z_gdb
            Q_b_i = Q_b_total[idx]

            if soil_type_ii.lower() in ['c', 'c_s']:

                sub_capacity_entry = 'clay'

                if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                    t_ii, t_ult_ii, save_parameter_tz_ii = t_z_static(z_i[idx], Q_s_total_i, t_t_max_clay, b_outer_diff_ii)
                    t_ult[idx] = t_ult_ii
                    t_i[idx] = t_ii

                if depth_i == length_embedment_i:

                    if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                        q_ii, q_ult_ii, save_parameter_qz_ii = q_z_static(z_i[idx], Q_b_i, b_outer_diff_ii)
                        q_ult[idx] = q_ult_ii
                        q_i[idx] = q_ii

                else:
                    q_ii, q_ult_ii, save_parameter_qz_ii = 0, 0, {}
                    q_ult[idx] = q_ult_ii
                    q_i[idx] = q_ii

            elif soil_type_ii.lower() in ['s', 's_c', 'si']:

                sub_capacity_entry = 'sand'

                if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                    t_ii, t_ult_ii, save_parameter_tz_ii = t_z_static(z_i[idx], Q_s_total_i, t_t_max_sand, b_outer_diff_ii)
                    save_parameter_tz_ii = {f"{key}${"t_z_static"}": value for key, value in save_parameter_tz_ii.items()}
                    t_ult[idx] = t_ult_ii
                    t_i[idx] = t_ii

                if depth_i == length_embedment_i:

                    if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                        q_ii, q_ult_ii, save_parameter_qz_ii = q_z_static(z_i[idx], Q_b_i, b_outer_diff_ii)
                        save_parameter_qz_ii = {f"{key}${"q_z_static"}": value for key, value in save_parameter_qz_ii.items()}
                        q_ult[idx] = q_ult_ii
                        q_i[idx] = q_ii

                else:
                    q_ii, q_ult_ii, save_parameter_qz_ii = 0, 0, {}
                    q_ult[idx] = q_ult_ii
                    q_i[idx] = q_ii

            else:
                t_ii, t_ult_ii, save_parameter_tz_ii = 0, 0, {}
                q_ii, q_ult_ii, save_parameter_qz_ii = 0, 0, {}

            save_parameter_tz_ii['z_tz_section_1[input_tz]'] = float(depth_i)
            save_parameter_tz_ii['soil_type_tz_section_1[input_tz]# - ? -'] = soil_type_ii
            save_parameter_tz_ii['pf_soil_mat[input_tz]# γ<sub>m</sub> (-) ? -'] = pf_soil_mat
            save_parameter_ii = {**save_parameter_tz_ii, **save_parameter_qz_ii}
            save_parameter_inc.append(save_parameter_ii)
        
        T_s_i = np.array([t_i[i]/z_i[i] for i in range(N)])
        T_s_i = np.array([0 if (zi - z_gs) < 0 else T_s_ii for zi, T_s_ii in zip(depth_dis, T_s_i)])
        T_s.append(T_s_i)

        Q_s_i = np.array([q_i[i]/z_i[i] for i in range(N)])
        Q_s.append(Q_s_i)

        Err.append(np.sum(np.abs(z_i - z[-1])))
        z.append(z_i)

        count += 1

    if count == count_lim:
        print(f' ----- Reached count limit = {count_lim} at {V} kN')
   
    for i in range(N):
        if i == 0:
            N_ax[i] = -E_pile*A_annulus_ave/d_z_gdb*(z_i[i+1] - z_i[i])
        elif i == N-1:
            N_ax[i] = -E_pile*A_annulus_ave/d_z_gdb*(z_i[i] - z_i[i-1])
        else:
            N_ax[i] = -E_pile*A_annulus_ave/2/d_z_gdb*(z_i[i+1] - z_i[i-1])

    part1 = np.linspace(0, 0.005 * b_outer_dis[-1], 200, endpoint=False)
    part2 = np.linspace(0.005 * b_outer_dis[-1], 0.01 * b_outer_dis[-1], 100, endpoint=False)
    part3 = np.linspace(0.01 * b_outer_dis[-1], 0.1 * b_outer_dis[-1], 100)

    x_background = list(np.concatenate([part1, part2, part3]))
    y_background = []

    for idx in range(len(depth_dis)):
        depth_i = depth_dis[idx]
        soil_type_ii = soil_type_dis[idx]
        b_outer_diff_ii = b_outer_dis[idx]

        Q_s_inner_i = Q_s_inner_total[idx]
        Q_s_outer_i = Q_s_outer_total[idx]
        Q_s_total_i = (Q_s_inner_i + Q_s_outer_i)/d_z_gdb
        Q_b_i = Q_b_total[idx]

        if soil_type_ii.lower() in ['c', 'c_s']:

            sub_capacity_entry = 'clay'

            if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                y_background.append([t_z_static(x_ii, Q_s_total_i, t_t_max_clay, b_outer_diff_ii)[0] for x_ii in x_background])

            if depth_i == length_embedment_i:

                if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([q_z_static(x_ii, Q_b_i, b_outer_diff_ii)[0] for x_ii in x_background])

        elif soil_type_ii.lower() in ['s', 's_c', 'si']:

            sub_capacity_entry = 'sand'

            if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                y_background.append([t_z_static(x_ii, Q_s_total_i, t_t_max_sand, b_outer_diff_ii)[0] for x_ii in x_background])

            if depth_i == length_embedment_i:

                if 'api' in capacity_dict[sub_capacity_entry].lower() or 'iso' in capacity_dict[sub_capacity_entry].lower():
                    y_background.append([q_z_static(x_ii, Q_b_i, b_outer_diff_ii)[0] for x_ii in x_background])

        else:
            y_background.append(list(np.zeros(len(x_background))))
            
    results_dict = {'z[input]# z (m) ? -': depth_dis,
                    'soil_type[input]# - ? -': soil_type_dis,
                    'pf_soil_mat[input]# γ<sub>m</sub> (-) ? -': pf_soil_mat_dis,
                    't_ult[output_tz]# t<sub>ult</sub> (MN/m) ? -': t_ult,
                    'q_ult[output_tz]# Q<sub>ult</sub> (MN) ? -': q_ult,
                    't_calc[output_tz]# t (MN/m) ? -': t_i,
                    'q_calc[output_tz]# Q (MN) ? -': q_i,
                    'z_calc[output_tz]# z (m) ? -': z_i,
                    'T_s[output_tz]# T<sub>s</sub> (MPa) ? -': T_s_i,
                    'Q_s[output_tz]# Q<sub>s</sub> (MN/m) ? -': Q_s_i,
                    'N_ax[output_tz]# N (MN) ? -': N_ax,
                    'x_background': x_background,
                    'y_background': y_background}
                                
    return results_dict