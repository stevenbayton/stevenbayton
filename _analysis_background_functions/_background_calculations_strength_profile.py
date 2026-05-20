# python modules
import numpy as np
import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

# multiconsult modules
import _background_functions as bf


def norm_static_sand_undrained(d_r, fines, max_tau_sref=2):
    
    fines = int(fines)
    if d_r < 40:
        d_r = 40

    if d_r > 100:
        d_r = 100

    if fines < 5:
        fines = 5

    if fines > 35:
        fines = 35

    d_r = int(d_r)

    ## Andersen Figure 10.1
    DR_array = np.arange(40, 100+5/10, 5)
    FC5_array = np.array([0.24, 0.26, 0.30, 0.40, 0.55, 0.82, 1.23, 1.90, 2.85, 4.45, 6.80, 10.30, 16.00])
    FC20_array = np.array([0.18, 0.185, 0.19, 0.195, 0.2, 0.21, 0.32, 0.5, 0.8, 1.25, 2, 3.15, 5])
    FC35_array = np.array([0.15, 0.15, 0.151, 0.153, 0.155, 0.157, 0.16, 0.165, 0.22, 0.35, 0.55, 0.92, 1.55])

    FC5 = bf.lin_x_log_y_interp(d_r, DR_array, FC5_array)
    FC20 = bf.lin_x_log_y_interp(d_r, DR_array, FC20_array)
    FC35 = bf.lin_x_log_y_interp(d_r, DR_array, FC35_array)

    tau_sref_static = bf.lin_x_log_y_interp(fines, np.array([5, 20, 35]), np.array([FC5, FC20, FC35]))

    tau_sref_static = min(max_tau_sref, tau_sref_static)
    
    return tau_sref_static


def aniso_static_sand_undrained(d_r, max_aniso=2):
    
    if d_r < 40:
        d_r = 40

    if d_r > 100:
        d_r = 100

    d_r = int(d_r)

    ## Andersen Figure 10.4b
    DR_array = np.arange(40, 100+5/10, 5)
    suc_dss_array = np.array([1.45, 1.45, 1.5, 1.65, 1.8, 2.1, 2.53, 3.05, 3.55, 4.1, 4.65, 5.2, 5.75])
    sue_dss_array = np.array([0.65, 0.65, 0.65, 0.65, 0.65, 0.7, 0.8, 0.95, 1.05, 1.1, 1.15, 1.2, 1.2])

    suc_dss = bf.lin_x_log_y_interp(d_r, DR_array, suc_dss_array)
    sue_dss = bf.lin_x_log_y_interp(d_r, DR_array, sue_dss_array)

    suc_dss = min(max_aniso, suc_dss)
    sue_dss = min(max_aniso, sue_dss)
    
    return suc_dss, sue_dss


def norm_sand_drained(phi, k_0):

    alpha = phi - 5
    suC_sig_v_ = k_0*np.sin(np.radians(phi))/(1 - np.sin(np.radians(phi)))
    suD_sig_v_ = np.tan(np.radians(alpha))
    suE_sig_v_ = np.sin(np.radians(phi))/(1 - np.sin(np.radians(phi)))
    
    return suC_sig_v_, suD_sig_v_, suE_sig_v_


def norm_cyclic_sand_undrained_cy(d_r, fines, max_tau_sref=2):
    
    fines = int(fines)
    if d_r < 40:
        d_r = 40

    if d_r > 100:
        d_r = 100

    if fines < 5:
        fines = 5

    if fines > 35:
        fines = 35

    d_r = int(d_r)

    ## Andersen Figure 12.1, cyc/ave = inf
    DR_array = np.arange(40, 100+5/10, 5)
    FC5_array = np.array([0.155, 0.155, 0.162, 0.172, 0.185, 0.200, 0.215, 0.240, 0.280, 0.365, 0.530, 0.800, 1.200])
    FC20_array = np.array([0.130, 0.130, 0.132, 0.138, 0.145, 0.155, 0.166, 0.184, 0.205, 0.250, 0.350, 0.520, 0.780])
    FC35_array = np.array([0.110, 0.110, 0.112, 0.114, 0.118, 0.122, 0.128, 0.134, 0.145, 0.160, 0.185, 0.210, 0.250])

    FC5 = bf.lin_x_log_y_interp(d_r, DR_array, FC5_array)
    FC20 = bf.lin_x_log_y_interp(d_r, DR_array, FC20_array)
    FC35 = bf.lin_x_log_y_interp(d_r, DR_array, FC35_array)

    tau_cy_sref_cyclic = bf.lin_x_log_y_interp(fines, np.array([5, 20, 35]), np.array([FC5, FC20, FC35]))

    tau_cy_sref_cyclic = min(max_tau_sref, tau_cy_sref_cyclic)
    
    return tau_cy_sref_cyclic


def aniso_cyclic_sand_undrained(d_r):
    
    if d_r < 40:
        d_r = 40

    if d_r > 100:
        d_r = 100

    d_r = int(d_r)

    d_r_lower = 60
    d_r_upper = 80

    suc_dss_lower = 1.25
    suc_dss_upper = 2.0

    sue_dss_lower = 0.3
    sue_dss_upper = 0.5

    if d_r < d_r_lower:
        suc_dss = suc_dss_lower
        sue_dss = sue_dss_lower
    elif d_r < d_r_upper:
        m_suc = (suc_dss_upper - suc_dss_lower)/(d_r_upper - d_r_lower)
        c_suc = -m_suc*d_r_lower + suc_dss_upper
        suc_dss = m_suc*d_r + c_suc

        m_sue = (sue_dss_upper - sue_dss_lower)/(d_r_upper - d_r_lower)
        c_sue = -m_sue*d_r_lower + sue_dss_upper
        sue_dss = m_sue*d_r + c_sue
    else:
        suc_dss = suc_dss_upper
        sue_dss = sue_dss_upper
    
    return suc_dss, sue_dss


def norm_n_cyclic_ratio(n):

    n_array = np.arange([1, 3, 10, 30, 100, 300, 1000])
    tau_cyc_ratio_array = np.array([1.450, 1.200, 1.000, 0.850, 0.730, 0.650, 0.550])

    n_tau_cyc_ratio = bf.lin_x_log_y_interp(n, n_array, tau_cyc_ratio_array)

    return n_tau_cyc_ratio


def param_extract(col, soil_data, soil_data_length):

    if col in soil_data:
        s = soil_data[col]
    else:
        s = pd.Series(np.nan, index=range(soil_data_length))

    return s


def input_limit_equilibrium_design_profile(length_dimension_i, 
                                           soil_data, gdb_params, dl_capacity, dl_override,
                                           b_outer, l_outer, f_d_perm_fav_v_i,
                                           pf_soil_mat, pf_soil_mat_application,
                                           executable=None,
                                           ratio_load_tip=0):
    
    depth = depth_orig = soil_data['depth']

    if length_dimension_i != 0:
                
        if not any([(length_dimension_i - 0.005 < i and length_dimension_i + 0.005 > i) for i in depth]):
            if executable == 'cap_family':
                z_ins_array = [length_dimension_i + 0.01, length_dimension_i]
            elif executable == 'caisson':
                z_ins_array = [length_dimension_i, length_dimension_i]

            for z_ins in z_ins_array:
                
                idx_ins = len([row for row in depth if row < length_dimension_i])
                depth = np.insert(depth, idx_ins, z_ins)

                for param_i in gdb_params:
                    
                    if param_i != 'depth':
                        param_data_i = soil_data[param_i]

                        if any(isinstance(param_data_ii, str) for param_data_ii in param_data_i):
                            param_data_ins_i = param_data_i[idx_ins]
                            param_data_i = np.insert(param_data_i, idx_ins, param_data_ins_i)
                        else:
                            param_data_i = np.array(param_data_i.astype(float))
                            param_data_ins_i = np.interp(z_ins, depth_orig, param_data_i)
                            param_data_i = np.insert(param_data_i, idx_ins, param_data_ins_i)

                        soil_data[param_i] = param_data_i

                depth_orig = depth

    soil_data['depth'] = depth

    soil_data_length = len(depth)

    dsig_found = 1000*max(0, f_d_perm_fav_v_i)/((b_outer + 2*(depth - length_dimension_i)/3)*(l_outer + 2*(depth - length_dimension_i)/3))
    if length_dimension_i > 0:
        dsig_found = np.where(depth <= length_dimension_i, 0, ratio_load_tip*dsig_found)

    eff_uw = soil_data['effunitweight_rep']
    sig_v_ = soil_data['sigveff_rep']
    sig_found = np.nan_to_num(sig_v_) + dsig_found
    soil_type = soil_data['Soil_Type']

    s_u_c = param_extract('suc_'+dl_capacity, soil_data, soil_data_length)
    s_u_c = np.array([s_u_c_i if soil_type_i.lower() in ["c", "c_s"] else np.nan  for s_u_c_i, soil_type_i in zip(s_u_c, soil_type)])
    phi_is = param_extract('phi_'+dl_capacity, soil_data, soil_data_length)
    phi_is = np.array([phi_is_i if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan  for phi_is_i, soil_type_i in zip(phi_is, soil_type)])
    d_r = param_extract('dr_'+dl_capacity, soil_data, soil_data_length)
    d_r = np.array([d_r_i if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan  for d_r_i, soil_type_i in zip(d_r, soil_type)])
    k_0 = param_extract('K0_rep', soil_data, soil_data_length)
    k_0 = np.array([k_0_i if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan  for k_0_i, soil_type_i in zip(k_0, soil_type)])
    phi_adj = np.array([bf.phi_adjust(sig_v__i, sig_under_i, phi_i, d_r_i) if not np.isnan(phi_i) else np.nan for sig_v__i, sig_under_i, phi_i, d_r_i in zip(sig_v_, sig_found, phi_is, d_r)])
        
    if dl_override is None or str(dl_override) == 'nan':
        
        if pf_soil_mat_application == 'local':
            phi_adj = np.array([np.degrees(np.atan(np.tan(np.radians(phi_i))/pf_soil_mat)) if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan for phi_i, soil_type_i in zip(phi_adj, soil_type)])
            pf_soil_mat_global = 1
        else:
            pf_soil_mat_global = pf_soil_mat

        tau_C_sv_sand = np.array([norm_sand_drained(phi_i, k_0_i)[0] if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan for phi_i, k_0_i, soil_type_i in zip(phi_adj, k_0, soil_type)])
        tau_D_sv_sand = np.array([norm_sand_drained(phi_i, k_0_i)[1] if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan for phi_i, k_0_i, soil_type_i in zip(phi_adj, k_0, soil_type)])
        tau_E_sv_sand = np.array([norm_sand_drained(phi_i, k_0_i)[2] if soil_type_i.lower() in ["s", "s_c", "si"] else np.nan for phi_i, k_0_i, soil_type_i in zip(phi_adj, k_0, soil_type)])

        su_C_sand_found = np.array([tau_i*sig_under_i/pf_soil_mat_global for tau_i, sig_under_i in zip(tau_C_sv_sand, sig_found)])
        su_D_sand_found = np.array([tau_i*sig_under_i/pf_soil_mat_global for tau_i, sig_under_i in zip(tau_D_sv_sand, sig_found)])
        su_E_sand_found = np.array([tau_i*sig_under_i/pf_soil_mat_global for tau_i, sig_under_i in zip(tau_E_sv_sand, sig_found)])

        su_C_sand = np.array([tau_i*sig_v_i/pf_soil_mat_global for tau_i, sig_v_i in zip(tau_C_sv_sand, sig_v_)])
        su_D_sand = np.array([tau_i*sig_v_i/pf_soil_mat_global for tau_i, sig_v_i in zip(tau_D_sv_sand, sig_v_)])
        su_E_sand = np.array([tau_i*sig_v_i/pf_soil_mat_global for tau_i, sig_v_i in zip(tau_E_sv_sand, sig_v_)])

        su_C_clay = np.array([su_i/pf_soil_mat if soil_type_i.lower() in ["c", "c_s"] else np.nan for su_i, soil_type_i in zip(s_u_c, soil_type)])
        dss_suc = param_extract('sud-suc_rep', soil_data, soil_data_length)
        sue_suc = param_extract('sue-suc_rep', soil_data, soil_data_length)

        su_D_clay = np.array([su_i*dss_suc_i if soil_type_i.lower() in ["c", "c_s"] else np.nan for su_i, dss_suc_i, soil_type_i in zip(su_C_clay, dss_suc, soil_type)])
        su_E_clay = np.array([su_i*sue_suc_i if soil_type_i.lower() in ["c", "c_s"] else np.nan for su_i, sue_suc_i, soil_type_i in zip(su_C_clay, sue_suc, soil_type)])

        su_C_found = np.array([su_sand_i if np.isnan(su_clay_i) else su_clay_i if np.isnan(su_sand_i) else min(su_sand_i, su_clay_i) for su_sand_i, su_clay_i in zip(su_C_sand_found, su_C_clay)])
        su_D_found = np.array([su_sand_i if np.isnan(su_clay_i) else su_clay_i if np.isnan(su_sand_i) else min(su_sand_i, su_clay_i) for su_sand_i, su_clay_i in zip(su_D_sand_found, su_D_clay)])
        su_E_found = np.array([su_sand_i if np.isnan(su_clay_i) else su_clay_i if np.isnan(su_sand_i) else min(su_sand_i, su_clay_i) for su_sand_i, su_clay_i in zip(su_E_sand_found, su_E_clay)])
        
        su_C = np.array([su_sand_i if np.isnan(su_clay_i) else su_clay_i if np.isnan(su_sand_i) else min(su_sand_i, su_clay_i) for su_sand_i, su_clay_i in zip(su_C_sand, su_C_clay)])
        su_D = np.array([su_sand_i if np.isnan(su_clay_i) else su_clay_i if np.isnan(su_sand_i) else min(su_sand_i, su_clay_i) for su_sand_i, su_clay_i in zip(su_D_sand, su_D_clay)])
        su_E = np.array([su_sand_i if np.isnan(su_clay_i) else su_clay_i if np.isnan(su_sand_i) else min(su_sand_i, su_clay_i) for su_sand_i, su_clay_i in zip(su_E_sand, su_E_clay)])

        nans, x = bf.nan_helper(su_C_found)
        su_C_found[nans] = np.interp(x(nans), x(~nans), su_C_found[~nans])
        nans, x = bf.nan_helper(su_D_found)
        su_D_found[nans] = np.interp(x(nans), x(~nans), su_D_found[~nans])
        nans, x = bf.nan_helper(su_E_found)
        su_E_found[nans] = np.interp(x(nans), x(~nans), su_E_found[~nans])

        nans, x = bf.nan_helper(su_C)
        su_C[nans] = np.interp(x(nans), x(~nans), su_C[~nans])
        nans, x = bf.nan_helper(su_D)
        su_D[nans] = np.interp(x(nans), x(~nans), su_D[~nans])
        nans, x = bf.nan_helper(su_E)
        su_E[nans] = np.interp(x(nans), x(~nans), su_E[~nans])

        save_parameter = {'z[input]# z (m) ? -': depth,
                        'soil_type[input]# - ? -': soil_type,
                        "sig_v_[input]# σ'<sub>v</sub> (kPa) ? -": sig_v_,
                        'B[input]# B<sub>eq</sub> (m) ? -': b_outer,
                        'L[input]# L<sub>eq</sub> (m) ? -': l_outer,
                        'z_emb[input]# z<sub>emb</sub> (m) ? -': length_dimension_i,
                        's_u_c[input]# s<sub>u,c</sub> (kPa) ? -': s_u_c,
                        'd_r[input]# D<sub>r</sub> (%) ? -': d_r,
                        'k_0[input]# K<sub>0</sub> (-) ? -': k_0,
                        'phi_is[input]# φ<sub>in situ</sub> (deg) ? -': phi_is,
                        'pf_soil_mat[input]# γ<sub>m</sub> (-) ? -': pf_soil_mat,
                        "dsig_found[output]# dσ'<sub>v,found</sub> (kPa) ? -": dsig_found,
                        "sig_found[output]# σ'<sub>found</sub> (kPa) ? -": sig_found,
                        'phi_adj[output]# φ<sub>adj</sub> (deg) ? -': phi_adj,
                        'su_C_clay[output]# s<sub>u,c,clay</sub> (kPa) ? -': su_C_clay,
                        'dss_suc[input]# s<sub>u,d</sub>/s<sub>u,c</sub> (-) ? -': dss_suc,
                        'su_D_clay[output]# s<sub>u,d,clay</sub> (kPa) ? -': su_D_clay,
                        'sue_suc[input]# s<sub>u,e</sub>/s<sub>u,c</sub> (-) ? -': sue_suc,
                        'su_E_clay[output]# s<sub>u,e,clay</sub> (kPa) ? -': su_E_clay,}
                
        save_parameter_sand = {"tau_C_sv_sand[output]# τ<sub>c,sand</sub>/σ'<sub>v</sub> (-) ? -": tau_C_sv_sand,
                               "tau_D_sv_sand[output]# τ<sub>d,sand</sub>/σ'<sub>v</sub> (-) ? -": tau_D_sv_sand,
                               "tau_E_sv_sand[output]# τ<sub>e,sand</sub>/σ'<sub>v</sub> (-) ? -": tau_E_sv_sand,
                               'su_C_sand_found[output]# s<sub>u,c,sand found</sub> (kPa) ? -': su_C_sand_found,
                               'su_D_sand_found[output]# s<sub>u,d,sand found</sub> (kPa) ? -': su_D_sand_found,
                               'su_E_sand_found[output]# s<sub>u,e,sand found</sub> (kPa) ? -': su_E_sand_found,
                               'su_C_sand[output]# s<sub>u,c,sand</sub> (kPa) ? -': su_C_sand,
                               'su_D_sand[output]# s<sub>u,d,sand</sub> (kPa) ? -': su_D_sand,
                               'su_E_sand[output]# s<sub>u,e,sand</sub> (kPa) ? -': su_E_sand}

    else:

        su_ave = np.array([su_eq_i/pf_soil_mat for su_eq_i in param_extract(dl_override+'_'+dl_capacity, soil_data, soil_data_length)])
        su_C_found = su_D_found = su_E_found = su_C = su_D = su_E = su_ave
        
        save_parameter = {'z[input]# z (m) ? -': depth,
                          'soil_type[input]# - ? -': soil_type,
                          "sig_v_[input]# σ'<sub>v</sub> (kPa) ? -": sig_v_,
                          'B[input]# B<sub>eq</sub> (m) ? -': b_outer,
                          'L[input]# L<sub>eq</sub> (m) ? -': l_outer,
                          'z_emb[input]# z<sub>emb</sub> (m) ? -': length_dimension_i,
                          'su_ave[output]# s<sub>u,ave</sub> (kPa) ? -': su_ave,
                          'pf_soil_mat[input]# γ<sub>m,pb</sub> (-) ? -': pf_soil_mat}
        
        save_parameter_sand = {}
    
    save_parameter_2 = {'su_C_found[output]# s<sub>u,c found</sub> (kPa) ? -': su_C_found,
                        'su_D_found[output]# s<sub>u,d found</sub> (kPa) ? -': su_D_found,
                        'su_E_found[output]# s<sub>u,e found</sub> (kPa) ? -': su_E_found,
                        'su_ave[output]# s<sub>u,ave</sub> (kPa) ? -': (su_C_found + su_D_found + su_E)/3,
                        'su_C[output]# s<sub>u,c</sub> (kPa) ? -': su_C,
                        'su_D[output]# s<sub>u,d</sub> (kPa) ? -': su_D,
                        'su_E[output]# s<sub>u,e</sub> (kPa) ? -': su_E}
    
    save_parameter = {**save_parameter, **save_parameter_sand, **save_parameter_2}

    su_input = (su_C_found + su_D_found + su_E)/3
    
    input_dict = {'z': depth,
                  'eff_uw': eff_uw,
                  'su_C_found': su_C_found,
                  'su_D_found': su_D_found,
                  'su_E_found': su_E_found,
                  'su_C': su_C,
                  'su_D': su_D,
                  'su_E': su_E,
                  'su_input': su_input}
            
    return input_dict, save_parameter
