# python modules
import numpy as np
import os
import sys
import time

import _installation._navigate_grlweap as grl

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

# multiconsult modules
import _background_calculations_base as b_calc_base
import _background_calculations_shaft as b_calc_shaft
import _background_calculations_suction as b_calc_suction
import _background_setup as b_setup


def calc(capacity_dict, sections_input, foundation_list, calculation_method_i, length_embedment,
         pf_load_perm, pf_soil_mat, pf_load_plug_bearing, clay_reconsolidation_time,
         d_z, soil_data_i, soil_data_dis_dict, dl_s, dl_b,
         f_d_total_v_i, structure_sw_factor,
         calculation_name,
         Q_s_inner_array, Q_s_outer_array,
         t_ss_array,
         parent_input,
         hammer_dict,
         quake_damp_dict,
         d_cpt=0.0356,
         results_dict_total={},
         results_dict_base_plug_bearing = {},
         results_dict_shaft_plug_bearing = {},
         results_dict_underpressure = {},
         results_dict_grl={},
         calc_type="installation", f_direction_i="compression"):
    
    depth_i = soil_data_i['depth']
    soil_type_i = soil_data_i['Soil_Type']

    z_in_soil_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2)) & (np.round(soil_data_dis_dict['depth'], 2) >= 0)]   
    soil_type_dis = np.array(soil_data_dis_dict['Soil_Type'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2)) & (np.round(soil_data_dis_dict['depth'], 2) >= 0)]       
    _, section_dimensions = b_setup.section_setup(depth_i, z_in_soil_dis, length_embedment, sections_input, foundation_list, d_z, pf_load_perm, calc_type)
    
    z_foundation_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment, 2)) & (np.round(soil_data_dis_dict['depth'], 2) >= 0)]      
    W_foundation, _ = b_setup.section_setup(depth_i, z_foundation_dis, length_embedment, sections_input, foundation_list, d_z, pf_load_perm, calc_type)

    if structure_sw_factor is None:
        structure_sw_factor = 1

    W_foundation = W_foundation*structure_sw_factor

    if calculation_name == '_removal':
        W_foundation = 0
    
    a_base_annulus_dis = section_dimensions["a_base_annulus"]
    a_base_bo_dis = section_dimensions["a_base_bo"]
    a_base_bi_dis = section_dimensions["a_base_bi"]
    b_outer_dis = section_dimensions["b_outer"]
    t_dis = section_dimensions["thickness"]
    a_shaft_outer_dis = section_dimensions["a_shaft_bo"]
    a_shaft_inner_dis = section_dimensions["a_shaft_bi"]
        
    a_base_diff_dis = [[depth_i, a_base_annulus_dis[0], a_base_bo_dis[0], a_base_bi_dis[0], b_outer_dis[0], t_dis[0]]]
    a_base_global_dis = [[depth_i, a_base_annulus_dis[0], a_base_bo_dis[0], a_base_bi_dis[0], b_outer_dis[0], t_dis[0]]]
    for idx, (i1, i2, i3, i4, i5, i6) in enumerate(zip(z_in_soil_dis[1:], a_base_annulus_dis[1:], a_base_bo_dis[1:], a_base_bi_dis[1:], b_outer_dis[1:], t_dis[1:])):
        if i2 - a_base_global_dis[-1][1] > 0:
            a_base_diff_dis.append([min(length_embedment - i1, depth_i - i1), i2 - a_base_global_dis[-1][1], i3 - a_base_global_dis[-1][2], i4 - a_base_global_dis[-1][3], i5 - a_base_global_dis[-1][4], i6 - a_base_global_dis[-1][5]])
            a_base_global_dis.append([min(length_embedment - i1, depth_i - i1), i2, i3, i4, i5, i6])

    a_shaft_diff_dis = [[depth_i, a_shaft_outer_dis[0], a_shaft_inner_dis[0], b_outer_dis[0], t_dis[0]]]
    a_shaft_global_dis = [[depth_i, a_shaft_outer_dis[0], a_shaft_inner_dis[0], b_outer_dis[0], t_dis[0]]]

    for idx, (i1, i2, i3, i4, i5) in enumerate(zip(z_in_soil_dis[1:], a_shaft_outer_dis[1:], a_shaft_inner_dis[1:], b_outer_dis[1:], t_dis[1:])):
        if abs((i2 + i3) - (a_shaft_global_dis[-1][1] + a_shaft_global_dis[-1][2])) > 0:
            a_shaft_diff_dis.append([min(length_embedment - i1, depth_i - i1), i2, i3, i4, i5])
            a_shaft_global_dis.append([min(length_embedment - i1, depth_i - i1), i2, i3, i4, i5])

    if calculation_name == '_installation':
        removal = False
    elif calculation_name == '_removal':
        removal = True

    results_dict_base, plug_output_base = b_calc_base.base_resistance(depth_i, soil_data_dis_dict, dl_b,
                                                                      capacity_dict, f_direction_i, pf_soil_mat,
                                                                      a_base_diff_dis, a_base_global_dis,
                                                                      calculation_method_i, calc_type,
                                                                      d_z,
                                                                      d_cpt,
                                                                      removal=removal)
        
    results_dict_shaft = b_calc_shaft.shaft_resistance(depth_i, soil_data_dis_dict, dl_s,
                                                       capacity_dict, f_direction_i, pf_soil_mat, clay_reconsolidation_time,
                                                       a_shaft_diff_dis, a_shaft_global_dis,
                                                       calculation_method_i, calc_type,
                                                       d_z,
                                                       d_cpt,
                                                       removal=removal)
    
    Q_b_total = results_dict_base[next(k for k in results_dict_base if k.startswith("Q_b_total[output_b]"))]
    Q_s_inner = results_dict_shaft[next(k for k in results_dict_shaft if k.startswith("Q_s_inner[output_s]"))]
    Q_s_outer = results_dict_shaft[next(k for k in results_dict_shaft if k.startswith("Q_s_outer[output_s]"))]
    Q_s_total = results_dict_shaft[next(k for k in results_dict_shaft if k.startswith("Q_s_total[output_s]"))]
    Q_t_total = max(1e-10, Q_b_total + Q_s_total)

    results_dict_total["Q_t_total[output_t]# Q<sub>t</sub> (MN) ? -"] = Q_t_total

    Q_s_inner_array.append(Q_s_inner)
    Q_s_outer_array.append(Q_s_outer)

    if plug_output_base.lower() == 'cored':
        W_plug = 0        
    else:
        W_plug = depth_i * a_base_bi_dis[-1] * 1000 * pf_load_perm * 9.81/1e6 # maybe update
            
    W_t_total = (W_foundation + W_plug) + f_d_total_v_i
    results_dict_total["W_t_total[output_t]# W (MN) ? -"] = W_t_total

    Q_t_net_total = Q_t_total - W_t_total
    results_dict_total["Q_t_net_total[output_t]# Q<sub>t,net</sub> (MN) ? -"] = Q_t_net_total
    
    if 'suction' in calculation_method_i:
        capacity_dict_plug_bearing = {'sand_base': 'bc_deep_dnv',
                                      'sand_shaft': 'beta_dnv',
                                      'clay_base': 'bc_deep_dnv',
                                      'clay_shaft': 'alpha_dnv',}
        
        a_base_diff_dis_plug_bearing = [a_base_diff_dis[0]]
        a_base_global_dis_plug_bearing = [a_base_global_dis[0]]
        calculation_method_plug_bearing = 'plugged'

        if 'removal' in calculation_method_i:
            calc_type_plug_bearing = 'plug_bearing_removal'
        else:
            calc_type_plug_bearing = 'plug_bearing_installation'
        
        results_dict_base_plug_bearing, _ = b_calc_base.base_resistance(depth_i, soil_data_dis_dict, dl_b,
                                                                        capacity_dict_plug_bearing, f_direction_i, pf_load_plug_bearing,
                                                                        a_base_diff_dis_plug_bearing, a_base_global_dis_plug_bearing,
                                                                        calculation_method_plug_bearing, calc_type_plug_bearing,
                                                                        d_z,
                                                                        d_cpt)
        
        results_dict_shaft_plug_bearing = b_calc_shaft.shaft_resistance(depth_i, soil_data_dis_dict, dl_s,
                                                                        capacity_dict_plug_bearing, f_direction_i, pf_soil_mat, clay_reconsolidation_time,
                                                                        a_shaft_diff_dis, a_shaft_global_dis,
                                                                        calculation_method_i, calc_type_plug_bearing,
                                                                        d_z,
                                                                        d_cpt)

        Q_pb_total = results_dict_base_plug_bearing[next(k for k in results_dict_base_plug_bearing if k.startswith("Q_pb_total[output_pb]"))]
        Q_ps_inner = results_dict_shaft_plug_bearing[next(k for k in results_dict_shaft_plug_bearing if k.startswith("Q_ps_inner[output_ps]"))]
        Q_p_total = max(1e-10, Q_pb_total + Q_ps_inner)
        U_allowable_plug = 1000*Q_p_total/a_base_diff_dis[0][3]
        results_dict_total["U_allowable_plug[output_u]# U<sub>allow</sub> (kPa) ? -"] = U_allowable_plug

        results_dict_underpressure = b_calc_suction.suction_underpressure(depth_i, soil_data_dis_dict, dl_b,
                                                                          calculation_method_i,
                                                                          a_base_diff_dis,
                                                                          W_t_total,
                                                                          Q_s_inner_array, Q_s_outer_array, Q_b_total, Q_t_total,
                                                                          t_ss_array,
                                                                          d_z)
        
        t_ss_append = results_dict_underpressure[next(k for k in results_dict_underpressure if k.startswith("t_ss[output_u]"))]
        t_ss_array.append(t_ss_append)
        U_req = results_dict_underpressure[next(k for k in results_dict_underpressure if k.startswith("U_req[output_u]"))]
        U_utilisation_plug = min(100, U_allowable_plug/max(1e-10, U_req))
        results_dict_total["U_utilisation_plug[output_u]# UR<sub>plug</sub> (-) ? -"] = U_utilisation_plug
                    
    elif 'driven' in calculation_method_i:

        if hammer_dict['run_grl_weap']:

            drive_depth_intervals = hammer_dict['drive_depth_intervals']

            if depth_i in drive_depth_intervals and depth_i != 0 and depth_i <= length_embedment:

                tic = time.time()

                idx_depth = np.where(hammer_dict['drive_depth_intervals'] == depth_i)[0][0]
                efficiency_i = hammer_dict['drive_efficiency_intervals'][idx_depth]
                
                ### Update for pile sections
                b_outer = b_outer_dis[-1]
                a_base_annulus = a_base_annulus_dis[-1]      
                a_base_bo = a_base_bo_dis[-1]  
                a_shaft_inner = a_shaft_inner_dis[-1]
                a_shaft_outer = a_shaft_outer_dis[-1]
                # a_base_global_dis
                # a_shaft_global_dis
                ###

                total_pile_length = length_embedment + section_dimensions['stick_up']

                file_location_name = grl.save_grl_weap_gwwb(depth_i,
                                                            efficiency_i,
                                                            hammer_dict,
                                                            calculation_name, 
                                                            parent_input, 
                                                            results_dict_base, 
                                                            results_dict_shaft, 
                                                            z_in_soil_dis, 
                                                            soil_type_dis, 
                                                            quake_damp_dict,
                                                            b_outer, 
                                                            a_base_annulus,
                                                            a_base_bo, 
                                                            a_shaft_inner, 
                                                            a_shaft_outer, 
                                                            total_pile_length,
                                                            plug_output_base)
                
                ###
                # b_calc.save_grl_weap_srp(calculation_name, parent_input, results_dict_base, results_dict_shaft, z_in_soil_dis, soil_type_dis, quake_damp_dict, a_base_annulus, a_base_bo, a_shaft_inner, a_shaft_outer, plug_output_base)
                ###
                results_dict_grl = grl.run_grl_weap(file_location_name, efficiency_i)
                toc = time.time()
                print(f" ---- Executed GRLWEAP at depth = {depth_i} m [{round(toc - tic, 1)} s]")

                ############ DELETE
                # driving_data_complete = driving_data['output_complete']
                # if depth_i in list(driving_data_complete['z_grl']):
                #     driving_data_depth = driving_data_complete[driving_data_complete['z_grl'] == depth_i]                        
                #     summary_blow = {"z_grl[output_grl]": depth_i,
                #                     "Q_t_grl[output_grl]": float(driving_data_depth['Q_t_grl'].iloc[0]),
                #                     "Q_s_grl[output_grl]": float(driving_data_depth['Q_s_grl'].iloc[0]),
                #                     "Q_b_grl[output_grl]": float(driving_data_depth['Q_b_grl'].iloc[0]),
                #                     "blc_grl[output_grl]": float(driving_data_depth['blc_grl'].iloc[0]),
                #                     "efficiency_grl[output_grl]": float(driving_data_depth['efficiency_grl'].iloc[0]),}

                # else:
                #     summary_blow = {}
                
                # if 'grl_stress_' + str(round(depth_i, 1)) in driving_data:
                #     grl_pile_stress_inc = driving_data['grl_stress_'+str(round(depth_i, 1))]

                #     grl_pile_stress_inc_re_save = []
                #     for idx, datai in grl_pile_stress_inc.iterrows():
                #         if datai["z_grl_section_1"] == 'output_grl':
                #             continue
                #         grl_pile_stress_inc_re_save.append({"z_grl_section_1[output_grl]": datai["z_grl_section_1"],
                #                                             "T_max_grl_section_1[output_grl]": datai["T_max_grl_section_1"],
                #                                             "C_max_grl_section_1[output_grl]": datai["C_max_grl_section_1"],
                #                                             "t_max_grl_section_1[output_grl]":datai["t_max_grl_section_1"],
                #                                             "c_max_grl_section_1[output_grl]": datai["c_max_grl_section_1"],
                #                                             "v_max_grl_section_1[output_grl]": datai["v_max_grl_section_1"],
                #                                             "d_max_grl_section_1[output_grl]": datai["d_max_grl_section_1"],
                #                                             "E_grl_section_1[output_grl]": datai["E_grl_section_1"],})
                    
                #     results_dict_grl = {"grl_pile_stress_inc": grl_pile_stress_inc_re_save,}

                # results_dict_grl = {**results_dict_grl, **summary_blow}
                
                #########

    results_dict = {'z[input]# z (m) ? -': depth_i, 
                    'soil_type[input]# - ? -': soil_type_i, 
                    **results_dict_base, 
                    **results_dict_shaft, 
                    **results_dict_base_plug_bearing, 
                    **results_dict_shaft_plug_bearing, 
                    **results_dict_underpressure,
                    **results_dict_total,
                    **results_dict_grl} 
                        
    return results_dict, t_ss_array, a_base_global_dis, a_shaft_global_dis


def task(calculation_name, 
         foundation_location_name, 
         gdb_df,
         gdb_df_scour, 
         sections_input, 
         setup_input, 
         parent_input,
         input_heading,
         hammer_dict={},
         quake_damp_dict={}):
    
    foundation_list = [x.strip() for x in setup_input['foundation'].split(';')]
    if type(foundation_list) is not list:
        foundation_list = [foundation_list]
        
    d_z = setup_input['d_z']
    z_max = setup_input['z_max']
    length_embedment = setup_input['length_embedment']

    punch_through_factor = setup_input.get('punch_through_factor', np.inf)

    pf_soil_mat = setup_input['soil_material_factor']
    
    pf_load_perm_fav = setup_input.get('load_factor_permanent_fav', 1)
    pf_load_plug_bearing = setup_input.get('load_factor_plug_bearing', 1)
    structure_sw_factor = setup_input.get('structure_sw_factor', 1)
               
    capacity_dict = {'sand_shaft': setup_input['calculation_method_sand_shaft'],
                     'sand_base': setup_input['calculation_method_sand_base'],
                     'clay_shaft': setup_input['calculation_method_clay_shaft'],
                     'clay_base': setup_input['calculation_method_clay_base']}
    
    if 'characteristic_load_permanent_Fz' in setup_input:
        f_c_perm_v = setup_input['characteristic_load_permanent_Fz']
    else:
        f_c_perm_v = 0
    
    calculation_method_list = [x.strip() for x in setup_input['calculation_method'].split(';')]
    if type(calculation_method_list) is not list:
        calculation_method_list = [calculation_method_list]

    dl_s = setup_input['design_line_shaft']
    dl_b = setup_input['design_line_base']

    clay_reconsolidation_time = setup_input['clay_reconsolidation_time']

    soil_data_dis_array, gdb_params = b_setup.extract_design_soil_profile(gdb_df, d_z, z_max, sections_input, foundation_list)

    output_dict = {}
    
    output_dict = {}
    output_dict['capacity_dict'] = capacity_dict

    pf_load_perm = pf_load_perm_fav

    f_d_perm_v = f_c_perm_v * pf_load_perm
    f_d_total_v = f_d_perm_v

    for calculation_method_i in calculation_method_list:

        if 'driven' in calculation_method_i:
            hammer_id = setup_input.get('hammer_id', None)
            hammer_name = setup_input.get('hammer_name', None)
            hammer_type = setup_input.get('hammer_type', None)
            drive_depth_intervals = setup_input.get('drive_depth_intervals', None)
            drive_efficiency_intervals = setup_input.get('drive_efficiency_intervals', None)
            run_grl_weap = setup_input.get('run_grl_weap', False)
            s_n_curve = setup_input.get('s_n_curve', None)

            if '[' in str(drive_depth_intervals):
                drive_depth_intervals = drive_depth_intervals.strip()[1:-1].split(',')
                drive_depth_intervals = [float(v) for v in drive_depth_intervals]
            else:
                drive_depth_intervals = np.arange(0, length_embedment+drive_depth_intervals, drive_depth_intervals)

            if '[' in str(drive_efficiency_intervals):
                drive_efficiency_intervals = drive_efficiency_intervals.strip()[1:-1].split(',')
                drive_efficiency_intervals = [float(v) for v in drive_efficiency_intervals]
            else:
                drive_efficiency_intervals = np.array([drive_efficiency_intervals for xi in drive_depth_intervals])

            hammer_dict = {'hammer_id': hammer_id,
                           'hammer_name': hammer_name,
                           'hammer_type': hammer_type,
                           'drive_depth_intervals': drive_depth_intervals,
                           'drive_efficiency_intervals': drive_efficiency_intervals,
                           'run_grl_weap': run_grl_weap,
                           "input_heading": input_heading}
            
            quake_damp_dict = {'quake_sand_shaft': setup_input['quake_sand_shaft'],
                               'quake_clay_shaft': setup_input['quake_clay_shaft'],
                               'quake_sand_base': setup_input['quake_sand_base'],
                               'quake_clay_base': setup_input['quake_clay_base'],
                               'damping_sand_shaft': setup_input['damping_sand_shaft'],
                               'damping_clay_shaft': setup_input['damping_clay_shaft'],
                               'damping_sand_base': setup_input['damping_sand_base'],
                               'damping_clay_base': setup_input['damping_clay_base']}

        output_result_plot = {}
        output_result_save = {}
        output_result_save_breakdown = {}

        output_dict[calculation_method_i] = {}

        Q_s_inner_array = []
        Q_s_outer_array = []

        t_ss_array = []
        heave_klinkvort = 0
        heave_gunawan = 0

        #### DELETE ####
        # import pandas as pd
        # driving_data = pd.read_excel(r"C:\STEB\python_projects\python\Eirin_he\output\_installation\eirin_he_input1_driven.xlsx", sheet_name=None)
        ################
                                
        for soil_data_i in zip(*soil_data_dis_array):

            soil_data_i = dict(zip(gdb_params, soil_data_i))
            depth_i = soil_data_i['depth']

            if depth_i < 0:
                continue

            output_result_save[depth_i] = {}
            output_result_save[depth_i]['structure_sw_factor[input]# Gross/Net (-) ? -'] = structure_sw_factor
            output_result_save_breakdown[depth_i] = {}
            output_result_save_breakdown[depth_i]["total_save_parameter"] = {}
            output_result_save_breakdown[depth_i]["total_save_parameter"]['z[input]# z (m) ? here'] = depth_i
                                                                                                                                    
            results_dict, t_ss_array, a_base_global_dis, a_shaft_global_dis = calc(capacity_dict, sections_input, foundation_list, calculation_method_i, length_embedment,
                                                                                   pf_load_perm, pf_soil_mat, pf_load_plug_bearing, clay_reconsolidation_time,
                                                                                   d_z, soil_data_i, dict(zip(gdb_params, soil_data_dis_array)), dl_s, dl_b,
                                                                                   f_d_total_v, structure_sw_factor,
                                                                                   calculation_name,
                                                                                   Q_s_inner_array, Q_s_outer_array,
                                                                                   t_ss_array,
                                                                                   parent_input,
                                                                                   hammer_dict,
                                                                                   quake_damp_dict)
                                                                                #    driving_data) ## DELETE
                            
            for key, value in results_dict.items():
                key_red = key.split('[')[0]
                if key_red not in output_result_plot:
                    output_result_plot[key_red] = []
                output_result_plot[key_red].append(value)
                if key in ["base_parameter_inc", "shaft_parameter_inc", "base_parameter_inc_plug_bearing", "shaft_parameter_inc_plug_bearing", "grl_soil_resistance_inc", "grl_pile_stress_inc"]:
                    output_result_save_breakdown[depth_i][key] = value
                else:
                    output_result_save[depth_i][key] = value

            output_result_plot.setdefault("Q_t_total_design", []).append(output_result_plot['W_t_total'][-1])   
            output_result_save[depth_i]["Q_t_total_design[output_t]# Q<sub>v,total</sub> (MN) ? -"] = output_result_plot['W_t_total'][-1]

            if 'suction' in calculation_method_i:
                d_heave_klinkvort = results_dict[next(k for k in results_dict if k.startswith("d_heave_klinkvort[output_u]"))]
                heave_klinkvort += d_heave_klinkvort
                output_result_save[depth_i]["heave_klinkvort[output_u]# z<sub>heave,Klinkvort</sub> (m) ? -"] = heave_klinkvort
                if "heave_klinkvort" not in output_result_plot:
                    output_result_plot["heave_klinkvort"] = []
                output_result_plot["heave_klinkvort"].append(heave_klinkvort)

                d_heave_gunawan = results_dict[next(k for k in results_dict if k.startswith("d_heave_gunawan[output_u]"))]
                heave_gunawan += d_heave_gunawan
                output_result_save[depth_i]["heave_gunawan[output_u]# z<sub>heave,Gunawan</sub> (m) ? -"] = heave_gunawan
                if "heave_gunawan" not in output_result_plot:
                    output_result_plot["heave_gunawan"] = []
                output_result_plot["heave_gunawan"].append(heave_gunawan)

        if len([i for i in range(len(output_result_plot['Q_t_total'])) if (abs(output_result_plot['W_t_total'][-1]/output_result_plot['Q_t_total'][i]) <= 1)]) == 0:
            sw_depth = 0
            sw_depth_punch_through = 0
            output_result_plot['sw_depth'] = sw_depth
            output_result_plot['sw_depth_punch_through'] = sw_depth_punch_through
        
        else:
            index_pass = [i for i in range(len(output_result_plot['Q_t_total'])) if (abs(output_result_plot['W_t_total'][-1]/output_result_plot['Q_t_total'][i]) <= 1)]

            for idx_pass in index_pass:
                first_pass_depth_i = output_result_plot['z'][idx_pass]
                base_influence_i = output_result_plot['base_influence'][idx_pass]
                base_influence_depth_i = punch_through_factor * base_influence_i
                required_second_pass_depth_i = first_pass_depth_i + base_influence_depth_i
                if any([True for i, j in enumerate(output_result_plot['z']) if j > required_second_pass_depth_i]):
                    idx_pass_2 = [i for i, j in enumerate(output_result_plot['z']) if j > required_second_pass_depth_i][0]
                else:
                    idx_pass_2 = len(output_result_plot['z']) - 1

                if all([abs(output_result_plot['W_t_total'][-1]/output_result_plot['Q_t_total'][i]) <= 1 for i in range(idx_pass, idx_pass_2)]):
                    sw_depth = output_result_plot['z'][idx_pass]
                    sw_depth_punch_through = output_result_plot['z'][idx_pass_2]
                    output_result_plot['sw_depth'] = sw_depth
                    output_result_plot['sw_depth_punch_through'] = sw_depth_punch_through
                    break

        if 'driven' in calculation_method_i:
            output_result_save, count_blow_results_dict = grl.count_blow(output_result_save)
            stress_fatigue_dict = grl.stress_fatigue_analysis(output_result_save_breakdown, count_blow_results_dict, a_base_global_dis, s_n_curve)
            output_dict[calculation_method_i]['stress_fatigue_dict'] = stress_fatigue_dict
                        
        output_result_plot['length_embedment'] = length_embedment
        output_result_plot['sw_total'] = output_result_plot['W_t_total'][-1]

        output_dict[calculation_method_i]['plot_output'] = output_result_plot
        output_dict[calculation_method_i]['save_output'] = output_result_save
        output_dict[calculation_method_i]['save_breakdown'] = output_result_save_breakdown
            
    return output_dict