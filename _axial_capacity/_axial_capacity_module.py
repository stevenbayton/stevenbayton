# python modules
import numpy as np
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

# multiconsult modules
import _background_calculations_base as b_calc_base
import _background_calculations_shaft as b_calc_shaft
import _background_setup as b_setup


def calc(capacity_dict, sections_input, foundation_list, calculation_method_i, l_s,
         f_direction_i, pf_load_perm_fav, pf_load_perm_unfav, pf_soil_mat, clay_reconsolidation_time,
         d_z, soil_data_i, soil_data_dis_dict, dl_s, dl_b,
         structure_sw_factor,
         conductor,
         d_cpt=0.0356,
         results_dict_total={},
         calc_type="capacity"):
    
    depth_i = soil_data_i['depth']

    z_in_soil_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2)) & (np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    
    if f_direction_i == 'compression':
        pf_load_perm = pf_load_perm_unfav
    elif f_direction_i == 'tension':
        pf_load_perm = pf_load_perm_fav
        
    W_foundation, section_dimensions = b_setup.section_setup(depth_i, z_in_soil_dis, depth_i, sections_input, foundation_list, d_z, pf_load_perm, calc_type)
    W_foundation = W_foundation*structure_sw_factor

    a_base_annulus_dis = section_dimensions["a_base_annulus"]
    a_base_bo_dis = section_dimensions["a_base_bo"]
    a_base_bi_dis = section_dimensions["a_base_bi"]
    b_outer_dis = section_dimensions["b_outer"]
    t_dis = section_dimensions["thickness"]
    a_shaft_outer_dis = section_dimensions["a_shaft_bo"]
    a_shaft_inner_dis = section_dimensions["a_shaft_bi"]

    a_base_diff_dis = [[depth_i, a_base_annulus_dis[-1], a_base_bo_dis[-1], a_base_bi_dis[-1], b_outer_dis[-1], t_dis[-1]]]
    a_base_global_dis = [[depth_i, a_base_annulus_dis[-1], a_base_bo_dis[-1], a_base_bi_dis[-1], b_outer_dis[-1], t_dis[-1]]]
    for idx, (i1, i2, i3, i4, i5, i6) in enumerate(zip(z_in_soil_dis[-2::-1], a_base_annulus_dis[-2::-1], a_base_bo_dis[-2::-1], a_base_bi_dis[-2::-1], b_outer_dis[-2::-1], t_dis[-2::-1])):
        if i2 - a_base_global_dis[-1][1] > 0:
            a_base_diff_dis.append([i1, i2 - a_base_global_dis[-1][1], i3 - a_base_global_dis[-1][2], i4 - a_base_global_dis[-1][3], i5 - a_base_global_dis[-1][4], i6 - a_base_global_dis[-1][5]])
            a_base_global_dis.append([i1, i2, i3, i4, i5, i6])

    a_shaft_diff_dis = [[depth_i, a_shaft_outer_dis[-1], a_shaft_inner_dis[-1], b_outer_dis[-1], t_dis[-1]]]
    a_shaft_global_dis = [[depth_i, a_shaft_outer_dis[-1], a_shaft_inner_dis[-1], b_outer_dis[-1], t_dis[-1]]]
    for idx, (i1, i2, i3, i4, i5) in enumerate(zip(z_in_soil_dis[-2::-1], a_shaft_outer_dis[-2::-1], a_shaft_inner_dis[-2::-1], b_outer_dis[-2::-1], t_dis[-2::-1])):
        if abs((i2 + i3) - (a_shaft_global_dis[-1][1] + a_shaft_global_dis[-1][2])) > 0:
            a_shaft_diff_dis.append([i1, i2, i3, i4, i5])
            a_shaft_global_dis.append([i1, i2, i3, i4, i5])

    soil_type_i = np.array(soil_data_dis_dict['Soil_Type'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2))][-1]
    
    if soil_type_i.lower() in ['s', 's_c', 'si']:
        l_s += d_z

    results_dict_shaft = b_calc_shaft.shaft_resistance(depth_i, soil_data_dis_dict, dl_s,
                                                       capacity_dict, f_direction_i, pf_soil_mat, clay_reconsolidation_time,
                                                       a_shaft_diff_dis, a_shaft_global_dis,
                                                       calculation_method_i, calc_type, d_z,
                                                       d_cpt,
                                                       conductor=conductor)
    
    Q_s_inner_clay = 0

    for shaft_parameter_inc_i in results_dict_shaft["shaft_parameter_inc"]:
        if l_s > 8:
            for section_i in range(1, 10):
                if any(['section_'+str(section_i) in key for key in shaft_parameter_inc_i.keys()]):
                    if shaft_parameter_inc_i[next(k for k in  shaft_parameter_inc_i if k.startswith('soil_type_s_section_' + str(section_i) + '[input_s]'))] in ['c', 'c_s']:
                        inner_ratio = shaft_parameter_inc_i[next(k for k in  shaft_parameter_inc_i if k.startswith('di_do_ratio_section_' + str(section_i) + '[geometry_s]'))]
                        Q_s_inner_clay += inner_ratio*shaft_parameter_inc_i[next(k for k in  shaft_parameter_inc_i if k.startswith('Q_s_outer_section_' + str(section_i) + '[calc_s]'))]
 
    results_dict_base, plug_output_base = b_calc_base.base_resistance(depth_i, soil_data_dis_dict, dl_b,
                                                                      capacity_dict, f_direction_i, pf_soil_mat, 
                                                                      a_base_diff_dis, a_base_global_dis,
                                                                      calculation_method_i, calc_type,
                                                                      d_z,
                                                                      d_cpt,
                                                                      conductor=conductor,
                                                                      l_s=l_s,
                                                                      Q_s_inner_clay=Q_s_inner_clay)  
                    
    Q_b_total = results_dict_base[next(k for k in results_dict_base if k.startswith("Q_b_total[output_b]"))]

    Q_s_total = results_dict_shaft[next(k for k in results_dict_shaft if k.startswith("Q_s_total[output_s]"))]
    Q_t_total = max(1e-10, Q_b_total + Q_s_total)

    results_dict_total["Q_t_total[output_t]# Q<sub>t</sub> (MN) ? Total ? 2"] = Q_t_total
    
    if plug_output_base.lower() == 'cored':
        W_plug = 0
    else:
        W_plug = depth_i * a_base_bi_dis[-1] * 1000 * pf_load_perm * 9.81/1e6 # maybe update with actually soil weight

    if 'conductor_analysis' in conductor:
        if conductor['conductor_analysis']:
            W_plug = 0
    
    if f_direction_i.lower() == 'compression':
        W_t_total = W_foundation + W_plug
        
    elif f_direction_i.lower() == 'tension':
        W_t_total = -W_foundation - W_plug

    results_dict_total["W_t_total[output_t][output_t]# W (MN) ? Total ? 2"] = W_t_total

    Q_t_net_total = Q_t_total - W_t_total
    results_dict_total["Q_t_net_total[output_t]# Q<sub>t,net</sub> (MN) ? Total ? 2"] = Q_t_net_total

    results_dict = {'z[input]# z (m) ? -': depth_i, 
                    'soil_type[input]# - ? -': soil_type_i, 
                    **results_dict_base, 
                    **results_dict_shaft,
                    **results_dict_total}
                
    return results_dict, l_s, plug_output_base
          

def task(calculation_name, 
         foundation_location_name,
         gdb_df, 
         gdb_df_scour,
         sections_input, 
         setup_input, 
         parent_input,
         input_heading):
    
    foundation_list = [x.strip() for x in setup_input['foundation'].split(';')]
    if type(foundation_list) is not list:
        foundation_list = [foundation_list]
            
    d_z = setup_input['d_z']
    z_max = setup_input['z_max']
    length_embedment = setup_input['length_embedment']
    punch_through_factor = setup_input['punch_through_factor']

    pf_load_var = setup_input['load_factor_variable']    
    pf_load_perm_fav = setup_input['load_factor_permanent_fav']
    pf_load_perm_unfav = setup_input['load_factor_permanent_unfav']
    
    pf_soil_mat = setup_input['soil_material_factor']

    structure_sw_factor  = setup_input['structure_sw_factor']

    utilisation_ratio = setup_input['utilisation_ratio']
            
    capacity_dict = {'sand_shaft': setup_input['calculation_method_sand_shaft'],
                     'sand_base': setup_input['calculation_method_sand_base'],
                     'clay_shaft': setup_input['calculation_method_clay_shaft'],
                     'clay_base': setup_input['calculation_method_clay_base']}
    
    f_c_var_v = setup_input['characteristic_load_variable_Fz']
    f_c_perm_v = setup_input['characteristic_load_permanent_Fz']

    calculation_method_list = [x.strip() for x in setup_input['calculation_method'].split(';')]
    if type(calculation_method_list) is not list:
        calculation_method_list = [calculation_method_list]

    if 'conductor_analysis' in setup_input:
        if setup_input['conductor_analysis']:
            conductor = {"conductor_analysis": setup_input['conductor_analysis'],
                         "conductor_borehole_diameter": setup_input['conductor_borehole_diameter'],
                         "conductor_grout_strength_limit": setup_input['conductor_grout_strength_limit'],
                         "conductor_interface_reduction_factor": setup_input['conductor_interface_reduction_factor']}
        else:
            conductor = {}
    else:
        conductor = {}

    dl_s = setup_input['design_line_shaft']
    dl_b = setup_input['design_line_base']
    
    clay_reconsolidation_time = setup_input['clay_reconsolidation_time']

    soil_data_dis_array, gdb_params = b_setup.extract_design_soil_profile(gdb_df_scour, d_z, z_max, sections_input, foundation_list)
    output_dict = {}
                            
    output_dict = {}
    output_dict['capacity_dict'] = capacity_dict

    f_d_var_v = f_c_var_v * pf_load_var
    f_d_perm_v = f_c_perm_v * pf_load_perm_unfav
    f_d_total_v = f_d_var_v + f_d_perm_v

    if f_d_total_v < 0:
        f_direction_i = 'tension'
    else:
        f_direction_i = 'compression'

    for calculation_method_i in calculation_method_list:

        output_result_plot = {}
        output_result_save = {}
        output_result_save_breakdown = {}

        calculation_save_i = calculation_method_i
        output_dict[calculation_save_i] = {}

        # plug_criteria uwa & fugro ## HERE
        l_s = 0
                                
        for soil_data_i in zip(*soil_data_dis_array):

            soil_data_i = dict(zip(gdb_params, soil_data_i))
            depth_i = soil_data_i['depth']

            if depth_i < 0:
                continue
            
            output_result_save[depth_i] = {}
            output_result_save[depth_i]['structure_sw_factor[input]# Gross/Net (-) ? -'] = structure_sw_factor
            output_result_save_breakdown[depth_i] = {}
            output_result_save_breakdown[depth_i]["total_save_parameter"] = {}
            output_result_save_breakdown[depth_i]["total_save_parameter"]['z[input]# z (m) ? -'] = depth_i
                                                                                                                                    
            results_dict, l_s, plug_output_base = calc(capacity_dict, sections_input, foundation_list, calculation_method_i, l_s, 
                                                       f_direction_i, pf_load_perm_fav, pf_load_perm_unfav, pf_soil_mat, clay_reconsolidation_time,
                                                       d_z, soil_data_i, dict(zip(gdb_params, soil_data_dis_array)), dl_s, dl_b,
                                                       structure_sw_factor,
                                                       conductor)
            

            calculation_method_i = plug_output_base
                            
            for key, value in results_dict.items():
                key_red = key.split('[')[0]
                if key_red not in output_result_plot:
                    output_result_plot[key_red] = []
                output_result_plot[key_red].append(value)
                if key in ["base_parameter_inc", "shaft_parameter_inc"]:
                    output_result_save_breakdown[depth_i][key] = value
                else:
                    output_result_save[depth_i][key] = value

            output_result_plot.setdefault("Q_t_total_design", []).append(f_d_total_v + results_dict[next(k for k in results_dict if k.startswith("W_t_total[output_t]"))])
            output_result_plot.setdefault("Q_t_net_design", []).append(f_d_total_v)  
            output_result_plot.setdefault("utilisation_ratio", []).append((f_d_total_v + results_dict[next(k for k in results_dict if k.startswith("W_t_total[output_t]"))])/results_dict[next(k for k in results_dict if k.startswith("Q_t_total[output_t]"))])
            output_result_save[depth_i]["Q_t_total_design[output_t]# Q<sub>v,total</sub> (MN) ? -"] = f_d_total_v + results_dict[next(k for k in results_dict if k.startswith("W_t_total[output_t]"))]
            output_result_save[depth_i]["Q_t_net_design[output_t]# Q<sub>v,net,total</sub> (MN) ? -"] = f_d_total_v
            output_result_save[depth_i]["utilisation_ratio[output]# UR (-) ? -"] = (f_d_total_v + results_dict[next(k for k in results_dict if k.startswith("W_t_total[output_t]"))])/results_dict[next(k for k in results_dict if k.startswith("Q_t_total[output_t]"))]

        # --- FIND OPTIMAL FOUNDATION LENGTH ---
        if "optimise" in str(length_embedment):   
            if len([i for i in range(len(output_result_plot['Q_t_total'])) if (abs((f_d_total_v + output_result_plot["W_t_total"][i])/output_result_plot['Q_t_total'][i]) <= utilisation_ratio) and (output_result_plot['plug_output'][i] != 'fail')]) == 0:
                length_embedment_i = z_max
                length_emb_punch_through = z_max
                output_result_plot['length_embedment'] = length_embedment_i
                output_result_plot['length_embedment_punch_through'] = length_emb_punch_through
                output_result_plot['utilisation_ratio_length_emb'] = np.inf
                idx_pass = len(output_result_plot["z"])-1
            
            else:
                index_pass = [i for i in range(len(output_result_plot['Q_t_total'])) if (abs((f_d_total_v + output_result_plot["W_t_total"][i])/output_result_plot['Q_t_total'][i]) <= utilisation_ratio) and (output_result_plot['plug_output'][i] != 'fail')]

                for idx_pass in index_pass:
                    first_pass_depth_i = output_result_plot["z"][idx_pass]
                    base_influence_i = output_result_plot['base_influence'][idx_pass]
                    base_influence_depth_i = punch_through_factor * base_influence_i
                    required_second_pass_depth_i = first_pass_depth_i + base_influence_depth_i
                    idx_pass_2 = [i for i, j in enumerate(output_result_plot["z"]) if j > required_second_pass_depth_i][0]

                    if all([abs((f_d_total_v + output_result_plot["W_t_total"][i])/output_result_plot['Q_t_total'][i]) <= utilisation_ratio for i in range(idx_pass, idx_pass_2)]):
                        length_embedment_i = output_result_plot["z"][idx_pass]
                        length_emb_punch_through = output_result_plot["z"][idx_pass_2]
                        output_result_plot['length_embedment'] = length_embedment_i
                        output_result_plot['length_embedment_punch_through'] = length_emb_punch_through
                        output_result_plot['utilisation_ratio_length_emb'] = (f_d_total_v + output_result_plot["W_t_total"][idx_pass])/output_result_plot["Q_t_total"][idx_pass]
                        break
        else:
            idx_pass = [i for i, j in enumerate(output_result_plot["z"]) if j >= length_embedment][0]
            first_pass_depth_i = output_result_plot["z"][idx_pass]
            base_influence_i = output_result_plot['base_influence'][idx_pass]
            base_influence_depth_i = punch_through_factor * base_influence_i
            required_second_pass_depth_i = first_pass_depth_i + base_influence_depth_i
            idx_pass_2 = [i for i, j in enumerate(output_result_plot["z"]) if j >= required_second_pass_depth_i][0]

            length_embedment_i = output_result_plot["z"][idx_pass]
            length_emb_punch_through = output_result_plot["z"][idx_pass_2]
            output_result_plot['length_embedment'] = length_embedment_i
            output_result_plot['length_embedment_punch_through'] = length_emb_punch_through
            output_result_plot['utilisation_ratio_length_emb'] = (f_d_total_v + output_result_plot["W_t_total"][idx_pass])/output_result_plot["Q_t_total"][idx_pass]
        
        output_result_plot['Design_utilisation'] = utilisation_ratio
        output_result_plot['Q_t_net_design_utilisation'] = f_d_total_v/utilisation_ratio
        output_result_plot['Q_t_total_design_utilisation'] = (f_d_total_v + output_result_plot['W_t_total'][idx_pass])/utilisation_ratio
                    
        output_dict[calculation_save_i]['plot_output'] = output_result_plot
        output_dict[calculation_save_i]['save_output'] = output_result_save
        output_dict[calculation_save_i]['save_breakdown'] = output_result_save_breakdown
                  
    return output_dict
