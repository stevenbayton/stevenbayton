# python modules
import numpy as np
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

# multiconsult modules
import _background_calculations_p_y as b_calc_p_y
import _background_setup as b_setup

def calc(capacity_dict, sections_input, foundation_list,
         pf_load_perm_unfav, pf_soil_mat,
         d_z, soil_data_i, soil_data_dis_dict, dl,
         calc_type='capacity'):
    
    depth_i = soil_data_i['depth']

    z_in_soil_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(depth_i, 2)) & (np.round(soil_data_dis_dict['depth'], 2) >= 0)]
    
    pf_load_perm = pf_load_perm_unfav
        
    _, section_dimensions = b_setup.section_setup(depth_i, z_in_soil_dis, depth_i, sections_input, foundation_list, d_z, pf_load_perm, calc_type)

    b_outer_dis = section_dimensions["b_outer"]
    t_dis = section_dimensions["thickness"]
    a_shaft_outer_dis = section_dimensions["a_shaft_bo"]
    a_shaft_inner_dis = section_dimensions["a_shaft_bi"]

    a_shaft_diff_dis = [[depth_i, a_shaft_outer_dis[-1], a_shaft_inner_dis[-1], b_outer_dis[-1], t_dis[-1]]]
    a_shaft_global_dis = [[depth_i, a_shaft_outer_dis[-1], a_shaft_inner_dis[-1], b_outer_dis[-1], t_dis[-1]]]
    for idx, (i1, i2, i3, i4, i5) in enumerate(zip(z_in_soil_dis[-2::-1], a_shaft_outer_dis[-2::-1], a_shaft_inner_dis[-2::-1], b_outer_dis[-2::-1], t_dis[-2::-1])):
        if abs((i2 + i3) - (a_shaft_global_dis[-1][1] + a_shaft_global_dis[-1][2])) > 0:
            a_shaft_diff_dis.append([i1, i2, i3, i4, i5])
            a_shaft_global_dis.append([i1, i2, i3, i4, i5])
    
    results_dict_lateral = b_calc_p_y.p_ult_resistance(depth_i, soil_data_dis_dict, dl, 
                                                       capacity_dict, pf_soil_mat, 
                                                       b_outer_dis, a_shaft_diff_dis, a_shaft_global_dis,   
                                                       d_z)
        

    results_dict = {'z[input]': depth_i, 
                    **results_dict_lateral}
                
    return results_dict
          

def task(calculation_name, 
         foundation_location_name,
         gdb_df, 
         gdb_df_scour,
         sections_input, 
         setup_input, 
         parent_input,
         input_heading):
    
    foundation_list = setup_input['foundation'].split(";")
    if type(foundation_list) is not list:
        foundation_list = [foundation_list]
            
    d_z = setup_input['d_z']
    z_max = setup_input['z_max']
    length_embedment = setup_input['length_embedment']

    pf_load_var = setup_input['load_factor_variable']    
    pf_load_perm_unfav = setup_input['load_factor_permanent_unfav']
    
    pf_soil_mat = setup_input['soil_material_factor']

    utilisation_ratio = setup_input['utilisation_ratio']
            
    capacity_dict = {'sand': setup_input['calculation_method_sand'],
                     'clay': setup_input['calculation_method_clay']}
    
    f_c_var_hx = setup_input['characteristic_load_variable_Fx']
    f_c_perm_hx = setup_input['characteristic_load_permanent_Fx']
    f_c_var_hy = setup_input['characteristic_load_variable_Fy']
    f_c_perm_hy = setup_input['characteristic_load_permanent_Fy']

    calculation_method_list = ['lateral']

    dl = setup_input['design_line']
    
    soil_data_dis_array, gdb_params = b_setup.extract_design_soil_profile(gdb_df_scour, d_z, z_max, sections_input, foundation_list)

    output_dict = {}
                            
    output_dict = {}
    output_dict['capacity_dict'] = capacity_dict

    f_d_var_hx = f_c_var_hx * pf_load_var
    f_d_perm_hx = f_c_perm_hx * pf_load_perm_unfav
    f_d_total_hx = f_d_var_hx + f_d_perm_hx

    f_d_var_hy = f_c_var_hy * pf_load_var
    f_d_perm_hy = f_c_perm_hy * pf_load_perm_unfav
    f_d_total_hy = f_d_var_hy + f_d_perm_hy

    f_d_total_h = np.sqrt(np.power(f_d_total_hx, 2) + np.power(f_d_total_hy, 2))

    for calculation_method_i in calculation_method_list:

        output_result_plot = {}
        output_result_save = {}
        output_result_save_breakdown = {}

        calculation_save_i = calculation_method_i
        output_dict[calculation_save_i] = {}
                                
        for soil_data_i in zip(*soil_data_dis_array):

            soil_data_i = dict(zip(gdb_params, soil_data_i))
            depth_i = soil_data_i['depth']

            if depth_i < 0:
                continue
            
            output_result_save[depth_i] = {}
            output_result_save_breakdown[depth_i] = {}
            output_result_save_breakdown[depth_i]["total_save_parameter"] = {}
            output_result_save_breakdown[depth_i]["total_save_parameter"]['z[input]'] = depth_i
                                                                       
            results_dict = calc(capacity_dict, sections_input, foundation_list,
                                pf_load_perm_unfav, pf_soil_mat,
                                d_z, soil_data_i, dict(zip(gdb_params, soil_data_dis_array)), dl)
                                        
            for key, value in results_dict.items():
                key_red = key.split('[')[0]
                if key_red not in output_result_plot:
                    output_result_plot[key_red] = []
                output_result_plot[key_red].append(value)
                if key in ["p_ult_parameter_inc"]:
                    output_result_save_breakdown[depth_i][key] = value
                else:
                    output_result_save[depth_i][key] = value

            output_result_plot.setdefault("Utilisation_ratio", []).append(f_d_total_h/results_dict["P_ult[output]"])
            output_result_save[depth_i]["Utilisation_ratio[output]"] = f_d_total_h/max(1e-10, results_dict["P_ult[output]"])

        # --- FIND OPTIMAL FOUNDATION LENGTH ---
        if "optimise" in str(length_embedment):   
            if len([i for i in range(len(output_result_plot['P_ult'])) if (abs(f_d_total_h/output_result_plot['P_ult'][i]) <= utilisation_ratio)]) == 0:
                length_embedment_i = z_max
                output_result_plot['length_embedment'] = length_embedment_i
                output_result_plot['Utilisation_ratio_length_emb'] = np.inf
                idx_pass = len(output_result_plot["z"])-1
            
            else:
                index_pass = [i for i in range(len(output_result_plot['P_ult'])) if (abs(f_d_total_h/output_result_plot['P_ult'][i]) <= utilisation_ratio)]

                for idx_pass in index_pass:
                    first_pass_depth_i = output_result_plot["z"][idx_pass]
                    required_second_pass_depth_i = first_pass_depth_i
                    idx_pass_2 = [i for i, j in enumerate(output_result_plot["z"]) if j > required_second_pass_depth_i][0]

                    if all([abs(f_d_total_h/output_result_plot['P_ult'][i]) <= utilisation_ratio for i in range(idx_pass, idx_pass_2)]):
                        length_embedment_i = output_result_plot["z"][idx_pass]
                        output_result_plot['length_embedment'] = length_embedment_i
                        break
        else:
            idx_pass = [i for i, j in enumerate(output_result_plot["z"]) if j >= length_embedment][0]
            first_pass_depth_i = output_result_plot["z"][idx_pass]
            required_second_pass_depth_i = first_pass_depth_i
            idx_pass_2 = [i for i, j in enumerate(output_result_plot["z"]) if j >= required_second_pass_depth_i][0]

            length_embedment_i = output_result_plot["z"][idx_pass]
            length_emb_punch_through = output_result_plot["z"][idx_pass_2]
            output_result_plot['length_embedment'] = length_embedment_i
        
        output_result_plot['Design_utilisation'] = utilisation_ratio
        output_result_plot['P_ult_design_utilisation'] = f_d_total_h/utilisation_ratio
                    
        output_dict[calculation_save_i]['plot_output'] = output_result_plot
        output_dict[calculation_save_i]['save_output'] = output_result_save
        output_dict[calculation_save_i]['save_breakdown'] = output_result_save_breakdown
                  
    return output_dict
