# python modules
import numpy as np
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

# multiconsult modules
import _background_calculations_p_y as b_calc_p_y
import _background_setup as b_setup


def calc(length_embedment, H, V,
         capacity_dict, sections_input, foundation_list, calculation_method_i,
         pf_load_perm_unfav, pf_soil_mat,
         d_z, soil_data_dis_dict, dl_p_y,
         steel_yield_strength, pf_steel_mat,
         calc_type="p_y_displacement", global_scour=0):
                            
    z_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment, 2))]
    W_foundation, section_dimensions = b_setup.section_setup(length_embedment, z_dis, length_embedment, sections_input, foundation_list, d_z, pf_load_perm_unfav, calc_type)

    b_outer_dis = section_dimensions["b_outer"]
    thickness_dis = section_dimensions["thickness"]

    results_dict = b_calc_p_y.p_y_deflection(soil_data_dis_dict, dl_p_y, pf_soil_mat, capacity_dict,
                                             length_embedment, H, V, calculation_method_i,
                                             b_outer_dis, thickness_dis, global_scour,
                                             steel_yield_strength, pf_steel_mat,
                                             d_z)
                    
    return results_dict
         

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
    z_max = setup_input['length_embedment']
    length_embedment = setup_input['length_embedment']

    pf_load_var = setup_input['load_factor_variable']    
    pf_load_perm_unfav = setup_input['load_factor_permanent_unfav']
    
    pf_soil_mat = setup_input['soil_material_factor']

    utilisation_ratio = setup_input['utilisation_ratio']
    steel_yield_strength = setup_input['steel_yield_strength']
    pf_steel_mat = setup_input['steel_material_factor']

    z_gs = setup_input["z_gs"]
            
    capacity_dict = {'sand': setup_input['calculation_method_sand'],
                     'clay': setup_input['calculation_method_clay'],}
    
    f_c_var_v = setup_input['characteristic_load_variable_Fz']
    f_c_perm_v = setup_input['characteristic_load_permanent_Fz']
    f_c_var_hx = setup_input['characteristic_load_variable_Fx']
    f_c_perm_hx = setup_input['characteristic_load_permanent_Fx']
    f_c_var_hy = setup_input['characteristic_load_variable_Fy']
    f_c_perm_hy = setup_input['characteristic_load_permanent_Fy']
    f_c_var_mz = setup_input['characteristic_load_variable_Mz']
    f_c_perm_mz = setup_input['characteristic_load_permanent_Mz']
    f_c_var_mx = setup_input['characteristic_load_variable_Mx']
    f_c_perm_mx = setup_input['characteristic_load_permanent_Mx']
    f_c_var_my = setup_input['characteristic_load_variable_My']
    f_c_perm_my = setup_input['characteristic_load_permanent_My']
    
    calculation_method_list = [x.strip() for x in setup_input['calculation_method'].split(';')]
    if type(calculation_method_list) is not list:
        calculation_method_list = [calculation_method_list]
        
    pile_coords_raw = setup_input['pile_coords']

    if type(pile_coords_raw) is str:
        pile_coords_raw = [pile_coords_raw]

    pile_coords = {}
    for pile_i, data_i in enumerate(pile_coords_raw):
        vals = re.findall(r'-?\d+(?:\.\d+)?', data_i)
        pile_coords[pile_i] = [float(val) for val in vals]

    dl_p_y = setup_input['design_line'] 
    
    soil_data_dis_array, gdb_params = b_setup.extract_design_soil_profile(gdb_df_scour, d_z, z_max, sections_input, foundation_list)
    soil_data_dis_dict = dict(zip(gdb_params, soil_data_dis_array))
    
    output_dict = {}
                          
    output_dict = {}
    output_dict['capacity_dict'] = capacity_dict

    f_d_var_v = f_c_var_v * pf_load_var
    f_d_perm_v = f_c_perm_v * pf_load_perm_unfav
    f_d_total_v = f_d_var_v + f_d_perm_v

    f_d_var_hx = f_c_var_hx * pf_load_var
    f_d_perm_hx = f_c_perm_hx * pf_load_perm_unfav
    f_d_total_hx = f_d_var_hx + f_d_perm_hx

    f_d_var_hy = f_c_var_hy * pf_load_var
    f_d_perm_hy = f_c_perm_hy * pf_load_perm_unfav
    f_d_total_hy = f_d_var_hy + f_d_perm_hy

    f_d_var_mz = f_c_var_mz * pf_load_var
    f_d_perm_mz = f_c_perm_mz * pf_load_perm_unfav
    f_d_total_mz = f_d_var_mz + f_d_perm_mz

    f_d_var_mx = f_c_var_mx * pf_load_var
    f_d_perm_mx = f_c_perm_mx * pf_load_perm_unfav
    f_d_total_mx = f_d_var_mx + f_d_perm_mx

    f_d_var_my = f_c_var_my * pf_load_var
    f_d_perm_my = f_c_perm_my * pf_load_perm_unfav
    f_d_total_my = f_d_var_my + f_d_perm_my

    for pile_i, data_i in pile_coords.items():

        f_d_total_h1 = f_d_total_hx / len(pile_coords)
        f_d_total_h2 = f_d_total_hy / len(pile_coords)
        f_d_total_v = f_d_total_v / len(pile_coords)

        if data_i[1] != 0:
            f_d_total_h1 -= f_d_total_mz/len(pile_coords)/(2*data_i[1])
            f_d_total_v += f_d_total_mx/len(pile_coords)/(data_i[1])

        if data_i[0] != 0:
            f_d_total_h2 += f_d_total_mz/len(pile_coords)/(2*data_i[1])
            f_d_total_v -= f_d_total_my/len(pile_coords)/(data_i[1]) 

        f_d_total_hr = np.sqrt(np.power(f_d_total_h1, 2)+np.power(f_d_total_h2, 2))

        f_d_total_hr_array = np.array([0, 0.2, 0.4, 0.6, 0.8, 1, 1.25, 1.5, 2, 3, 4]) * f_d_total_hr
        # f_d_total_hr_array = np.array([0.9, 1, 1.1]) * f_d_total_hr
    
        for calculation_method_i in calculation_method_list:

            output_result_plot = {}
            output_result_save = {}
            output_result_save_breakdown = {}
            
            output_dict[calculation_method_i] = {}

            for f_d_total_hr_i in f_d_total_hr_array:

                f_d_total_hr_i = round(f_d_total_hr_i, 2)

                output_result_plot[f_d_total_hr_i] = {}
                output_result_save[f_d_total_hr_i] = {}
                output_result_save_breakdown[f_d_total_hr_i] = {}                

                results_dict = calc(length_embedment, f_d_total_hr_i, f_d_total_v,
                                    capacity_dict, sections_input, foundation_list, calculation_method_i,
                                    pf_load_perm_unfav, pf_soil_mat,
                                    d_z, soil_data_dis_dict, dl_p_y,
                                    steel_yield_strength, pf_steel_mat,
                                    global_scour=z_gs)
                
                for key, value in results_dict.items():
                    key_red = key.split('[')[0]
                    output_result_plot[f_d_total_hr_i][key_red] = value
                    if key in ["p_y_parameter_inc"]:
                        output_result_save_breakdown[f_d_total_hr_i][key] = value
                    else:
                        output_result_save[f_d_total_hr_i][key] = value

            output_result_plot['length_embedment'] = length_embedment
            output_result_plot['design_load'] = round(f_d_total_hr, 2)
            output_result_save['design_load'] = round(f_d_total_hr, 2)

            output_dict[calculation_method_i]['plot_output'] = output_result_plot
            output_dict[calculation_method_i]['save_output'] = output_result_save
            output_dict[calculation_method_i]['save_breakdown'] = output_result_save_breakdown

    return output_dict
