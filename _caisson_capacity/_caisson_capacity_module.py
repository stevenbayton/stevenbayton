# python modules
import numpy as np
import os
import sys

# multiconsult modules
import _caisson_capacity._navigate_caisson as caisson

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

# multiconsult modules
import _background_calculations_strength_profile as b_calc_strength
import _background_setup as b_setup


def task(calculation_name, 
         foundation_location_name, 
         gdb_df, 
         gdb_df_scour, 
         sections_input, 
         setup_input, 
         parent_input,
         input_heading, 
         output_dict={}, d_z=None, url_main="https://app.casksoftware.com/home"):

    output_dict = {}

    foundation_list = [x.strip() for x in setup_input['foundation'].split(';')]
    if type(foundation_list) is not list:
        foundation_list = [foundation_list]

    z_max = setup_input['z_max']
    length_embedment = setup_input['length_embedment']
    
    pf_load_var = setup_input['load_factor_variable']
    pf_load_perm_fav = setup_input['load_factor_permanent_fav']
    pf_load_perm_unfav = setup_input['load_factor_permanent_unfav']

    pf_soil_mat = float(setup_input['soil_material_factor'])
    pf_soil_mat_application = setup_input['soil_material_factor_application']

    utilisation_ratio = setup_input['utilisation_ratio']
    structure_sw_factor  = setup_input['structure_sw_factor']

    f_c_var_v = setup_input['characteristic_load_variable_Fz']
    f_c_perm_v = setup_input['characteristic_load_permanent_Fz']
    f_c_var_h = setup_input['characteristic_load_variable_Fx']
    f_c_perm_h = setup_input['characteristic_load_permanent_Fx']
    f_c_var_m = setup_input['characteristic_load_variable_My']
    f_c_perm_m = setup_input['characteristic_load_permanent_My']
    f_c_var_t = setup_input['characteristic_load_variable_Mz']
    f_c_perm_t = setup_input['characteristic_load_permanent_Mz']

    calculation_method = setup_input['calculation_method']
    
    alpha_fo = setup_input['alpha_fo']
    alpha_fi = setup_input['alpha_fi']
    eta_fo = setup_input['eta_fo']
    eta_reb = setup_input['eta_reb']
    alpha_d_su = setup_input['alpha_d_su']
    iplug_vmode = setup_input['iplug_vmode']

    dl_capacity = setup_input['design_line']
    dl_override = setup_input.get('design_line_override', None)
    ratio_load_tip = setup_input.get('ratio_load_tip', 0)

    soil_data_dis_array_sections, gdb_params = b_setup.extract_design_soil_profile(gdb_df, 0.1, z_max, sections_input, foundation_list)
    soil_data_dis_dict_sections = dict(zip(gdb_params, soil_data_dis_array_sections))
                         
    soil_data_dis_array, gdb_params = b_setup.extract_design_soil_profile(gdb_df, d_z, z_max, sections_input, foundation_list)
    soil_data_dis_dict = dict(zip(gdb_params, soil_data_dis_array))

    for foundation_i in sections_input.keys():
        if foundation_i in foundation_list:
            section_foundation = foundation_i
            section_section = next(iter(sections_input[section_foundation]))
            break

    if sections_input[section_foundation][section_section]['shape'] == 'circle':
        b_outer = l_outer = sections_input[section_foundation][section_section]['b_outer']
    elif sections_input[section_foundation][section_section]['shape'] == 'rectangle':
        b_outer = sections_input[section_foundation][section_section]['b_outer']
        l_outer = sections_input[section_foundation][section_section]['l_outer']

    output_dict = {}
    output_dict['capacity_dict'] = None

    f_d_var_v = f_c_var_v * pf_load_var
    f_d_perm_unfav_v = f_c_perm_v * pf_load_perm_unfav
    f_d_perm_fav_v = f_c_perm_v * pf_load_perm_fav
    f_d_total_v = f_d_var_v + f_d_perm_unfav_v

    f_d_var_h = f_c_var_h * pf_load_var
    f_d_perm_h = f_c_perm_h * pf_load_perm_unfav
    f_d_total_h = f_d_var_h + f_d_perm_h

    f_d_var_m = f_c_var_m * pf_load_var
    f_d_perm_m = f_c_perm_m * pf_load_perm_unfav
    f_d_total_m = f_d_var_m + f_d_perm_m

    f_d_var_t = f_c_var_t * pf_load_var
    f_d_perm_t = f_c_perm_t * pf_load_perm_unfav
    f_d_total_t = f_d_var_t + f_d_perm_t

    if "optimise" in str(length_embedment): 

        length_embedment_min = 10 # to update
        length_embedment_max = 10 # to update
        length_embedment_diff = 0 # to update

        length_embedment_array = np.arange(length_embedment_min, length_embedment_max+length_embedment_diff, length_embedment_diff)

    else:

        length_embedment_array = np.array([length_embedment])

    output_result_plot_input = {}
    output_result_save_input = {}
    output_result_plot_output = {}
    output_result_save_output = {}

    for length_embedment_i in length_embedment_array:

        z_foundation_dis = np.array(soil_data_dis_dict_sections['depth'])[(np.round(soil_data_dis_dict_sections['depth'], 2) <= round(length_embedment_i, 2)) & (np.round(soil_data_dis_dict_sections['depth'], 2) >= 0)]      
        W_foundation_fav, section_dimensions = b_setup.section_setup(length_embedment_i, z_foundation_dis, length_embedment_i, sections_input, foundation_list, 0.1, pf_load_perm_fav, "capacity")   
        W_foundation_unfav, _ = b_setup.section_setup(length_embedment_i, z_foundation_dis, length_embedment_i, sections_input, foundation_list, 0.1, pf_load_perm_unfav, "capacity")

        t_wall = np.average(section_dimensions['thickness'])
        f_d_perm_fav_v_i = f_d_perm_fav_v + W_foundation_fav*structure_sw_factor
        f_d_total_v_i = f_d_total_v + W_foundation_unfav*structure_sw_factor

        input_dict, save_parameter = b_calc_strength.input_limit_equilibrium_design_profile(length_embedment_i,
                                                                                            soil_data_dis_dict, gdb_params, dl_capacity, dl_override,
                                                                                            b_outer, l_outer, f_d_perm_fav_v_i,
                                                                                            pf_soil_mat, pf_soil_mat_application, 
                                                                                            xecutable="caisson",
                                                                                            ratio_load_tip=ratio_load_tip)
        
        
        output_dict[calculation_method] = {}

        mode_vhm = calculation_method.split('_')[-1]
    
        input_file, output_file, input_dict = caisson.write_caisson_file(foundation_location_name, 
                                                                         input_heading, 
                                                                         input_dict, 
                                                                         b_outer, length_embedment_i, t_wall, 
                                                                         f_d_total_v_i, f_d_total_h, f_d_total_m, f_d_total_t, 
                                                                         mode_vhm, alpha_fo, alpha_fi, eta_fo, eta_reb, alpha_d_su, iplug_vmode)
        
        save_parameter["alpha_d_su"] = input_dict["alpha_d_su"]
        save_parameter["alpha_updated"] = input_dict["alpha_updated"]
        save_parameter["su_ave_l"] = input_dict["su_ave_l"]
        save_parameter["su_ave_end_bear"] = input_dict["su_ave_end_bear"]
        output_result_save_input[length_embedment_i] = save_parameter

        for key, value in save_parameter.items():
            if key not in output_result_plot_input:
                output_result_plot_input[key] = value

        output_dict[calculation_method]['input_file'] = input_file
        output_dict[calculation_method]['output_file'] = output_file
         
    output_result_plot_output['foundation_b_outer'] = b_outer
    output_result_plot_output['length_embedment'] = length_embedment_i
    output_dict[calculation_method]['plot_input'] = output_result_plot_input
    output_dict[calculation_method]['save_input'] = output_result_save_input  
    output_dict[calculation_method]['plot_output'] = output_result_plot_output
    output_dict[calculation_method]['save_output'] = output_result_save_output     
  
    return output_dict, calculation_method