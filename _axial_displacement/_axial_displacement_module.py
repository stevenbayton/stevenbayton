# python modules
import numpy as np
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

target_folder = os.path.join(parent_dir, '_axial_capacity')
sys.path.append(target_folder)

# multiconsult modules
import _background_calculations_t_z as b_calc_t_z
import _background_setup as b_setup
import _axial_capacity_module as ax_cap

def calc(length_embedment, V, f_direction_i,
         capacity_dict, sections_input, foundation_list, calculation_method_i,
         pf_load_perm_fav, pf_load_perm_unfav, pf_soil_mat,
         d_z, soil_data_dis_array, gdb_params, dl_s, dl_b,
         conductor,
         calc_type="t_z_displacement", 
         global_scour=0,
         l_s=np.inf,
         structure_sw_factor=1,
         clay_reconsolidation_time='long_term'):

    soil_data_dis_dict = dict(zip(gdb_params, soil_data_dis_array))    
    
    for soil_data_i in zip(*soil_data_dis_array):

        soil_data_i = dict(zip(gdb_params, soil_data_i))
        depth_i = soil_data_i['depth']

        if depth_i < 0:
            continue
                
        calculation_method_ii = capacity_dict['plugged']

        results_dict, _, _ = ax_cap.calc(capacity_dict, sections_input, foundation_list, calculation_method_ii, l_s,
                                         f_direction_i, pf_load_perm_fav, pf_load_perm_unfav, pf_soil_mat, clay_reconsolidation_time,
                                         d_z, soil_data_i, soil_data_dis_dict, dl_s, dl_b,
                                         structure_sw_factor,
                                         conductor)
        
    z_dis = np.array(soil_data_dis_dict['depth'])[(np.round(soil_data_dis_dict['depth'], 2) <= round(length_embedment, 2))]
    W_foundation, section_dimensions = b_setup.section_setup(length_embedment, z_dis, length_embedment, sections_input, foundation_list, d_z, pf_load_perm_unfav, calc_type)

    b_outer_dis = section_dimensions["b_outer"]
    a_base_bi_dis = section_dimensions["a_base_bi"]
    a_base_annulus_dis = section_dimensions["a_base_annulus"]

    output_shaft_inc_ii = results_dict['shaft_parameter_inc']
    output_base_inc_ii = results_dict['base_parameter_inc']
    
    Q_s_inner_total = np.zeros(len(z_dis))
    Q_s_outer_total = np.zeros(len(z_dis))
    Q_b_total = np.zeros(len(z_dis))

    for idx, z_i in enumerate(z_dis):
   
        for section_i in range(1, 10, 1):
            z_section = [d['z_s_section_' + str(section_i) + '[input_s]#  z (m) ? Section'+str(section_i)] for d in output_shaft_inc_ii if 'z_s_section_' + str(section_i) + '[input_s]#  z (m) ? Section'+str(section_i) in d]
            Q_s_inner_section = [d['Q_s_inner_section_' + str(section_i) + '[calc_s3]# ΔQ<sub>s,inner</sub> (MN) ? Section'+str(section_i)] for d in output_shaft_inc_ii if 'Q_s_inner_section_' + str(section_i) + '[calc_s3]# ΔQ<sub>s,inner</sub> (MN) ? Section'+str(section_i) in d]
            Q_s_outer_section = [d['Q_s_outer_section_' + str(section_i) + '[calc_s3]# ΔQ<sub>s,outer</sub> (MN) ? Section'+str(section_i)] for d in output_shaft_inc_ii if 'Q_s_outer_section_' + str(section_i) + '[calc_s3]# ΔQ<sub>s,outer</sub> (MN) ? Section'+str(section_i) in d]
            Q_b_section = [d['Q_b_section_' + str(section_i) + '[calc_b3]# Q<sub>b</sub> (MN) ? Section'+str(section_i)] for d in output_base_inc_ii if 'Q_b_section_' + str(section_i) + '[calc_b3]# Q<sub>b</sub> (MN) ? Section'+str(section_i) in d]   
            for z_ii, Q_s_inner_section_ii, Q_s_outer_section_ii, Q_b_section_ii in zip(z_section, Q_s_inner_section, Q_s_outer_section, Q_b_section):
                if z_ii == z_i:
                    Q_s_inner_total[idx] += Q_s_inner_section_ii
                    Q_s_outer_total[idx] += Q_s_outer_section_ii
                    Q_b_total[idx] += Q_b_section_ii

    if f_direction_i == 'compression':
        pf_load_perm = pf_load_perm_unfav
    elif f_direction_i == 'tension':
        pf_load_perm = pf_load_perm_fav

    results_dict = b_calc_t_z.t_z_deflection(soil_data_dis_dict, pf_soil_mat, capacity_dict, calculation_method_ii,
                                             length_embedment, V, calculation_method_i, pf_load_perm,
                                             a_base_annulus_dis, b_outer_dis, a_base_bi_dis, global_scour,
                                             d_z,
                                             Q_s_inner_total, Q_s_outer_total, Q_b_total,
                                             conductor)
                        
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
    pf_load_perm_fav = setup_input['load_factor_permanent_fav']
    pf_load_perm_unfav = setup_input['load_factor_permanent_unfav']
    
    pf_soil_mat = setup_input['soil_material_factor']

    utilisation_ratio = setup_input['utilisation_ratio']

    z_gs = setup_input["z_gs"]
            
    capacity_dict = {'sand': setup_input['calculation_method_sand'],
                     'clay': setup_input['calculation_method_clay'],
                     'sand_shaft': setup_input['calculation_method_capacity_sand_shaft'],
                     'sand_base': setup_input['calculation_method_capacity_sand_base'],
                     'clay_shaft': setup_input['calculation_method_capacity_clay_shaft'],
                     'clay_base': setup_input['calculation_method_capacity_clay_base'],
                     'plugged': setup_input['calculation_plugged']}
    
    f_c_var_v = setup_input['characteristic_load_variable_Fz']
    f_c_perm_v = setup_input['characteristic_load_permanent_Fz']
    f_c_var_mx = setup_input['characteristic_load_variable_Mx']
    f_c_perm_mx = setup_input['characteristic_load_permanent_Mx']
    f_c_var_my = setup_input['characteristic_load_variable_My']
    f_c_perm_my = setup_input['characteristic_load_permanent_My']
    
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
    
    soil_data_dis_array, gdb_params = b_setup.extract_design_soil_profile(gdb_df_scour, d_z, z_max, sections_input, foundation_list)
    
    pile_coords_raw = setup_input['pile_coords']

    if type(pile_coords_raw) is str:
        pile_coords_raw = [pile_coords_raw]

    pile_coords = {}
    for pile_i, data_i in enumerate(pile_coords_raw):
        vals = re.findall(r'-?\d+(?:\.\d+)?', data_i)
        pile_coords[pile_i] = [float(val) for val in vals]
    
    output_dict = {}
                    
    output_dict['capacity_dict'] = capacity_dict

    f_d_var_v = f_c_var_v * pf_load_var
    f_d_perm_v = f_c_perm_v * pf_load_perm_unfav
    f_d_total_v = f_d_var_v + f_d_perm_v

    f_d_var_mx = f_c_var_mx * pf_load_var
    f_d_perm_mx = f_c_perm_mx * pf_load_perm_unfav
    f_d_total_mx = f_d_var_mx + f_d_perm_mx

    f_d_var_my = f_c_var_my * pf_load_var
    f_d_perm_my = f_c_perm_my * pf_load_perm_unfav
    f_d_total_my = f_d_var_my + f_d_perm_my

    if f_d_total_v < 0:
        f_direction_i = 'tension'
    else:
        f_direction_i = 'compression'

    for pile_i, data_i in pile_coords.items():

        f_d_total_v = f_d_total_v / len(pile_coords)

        if data_i[1] != 0:
            f_d_total_v += f_d_total_mx/len(pile_coords)/(data_i[1])

        if data_i[0] != 0:
            f_d_total_v -= f_d_total_my/len(pile_coords)/(data_i[1]) 

        # f_d_total_v_array = np.array([0, 0.2, 0.4, 0.6, 0.8, 1, 1.25, 1.5]) * f_d_total_v
        f_d_total_v_array = np.array([0, 0.8, 1]) * f_d_total_v
    
        for calculation_method_i in calculation_method_list:

            output_result_plot = {}
            output_result_save = {}
            output_result_save_breakdown = {}
            
            output_dict[calculation_method_i] = {}

            for f_d_total_v_i in f_d_total_v_array:

                f_d_total_v_i = round(f_d_total_v_i, 2)

                output_result_plot[f_d_total_v_i] = {}
                output_result_save[f_d_total_v_i] = {}
                output_result_save_breakdown[f_d_total_v_i] = {}

                results_dict = calc(length_embedment, f_d_total_v_i, f_direction_i,
                                    capacity_dict, sections_input, foundation_list, calculation_method_i,
                                    pf_load_perm_fav, pf_load_perm_unfav, pf_soil_mat,
                                    d_z, soil_data_dis_array, gdb_params, dl_s, dl_b,
                                    conductor,
                                    global_scour=z_gs)
            
                for key, value in results_dict.items():
                    key_red = key.split('[')[0]
                    output_result_plot[f_d_total_v_i][key_red] = value
                    if key in ["save_parameter_inc"]:
                        output_result_save_breakdown[f_d_total_v_i][key] = value
                    else:
                        output_result_save[f_d_total_v_i][key] = value

            output_result_plot['length_embedment'] = length_embedment
            output_result_plot['design_load'] = round(f_d_total_v, 2)
            output_result_save['design_load'] = round(f_d_total_v, 2)

            output_dict[calculation_method_i]['plot_output'] = output_result_plot
            output_dict[calculation_method_i]['save_output'] = output_result_save
            output_dict[calculation_method_i]['save_breakdown'] = output_result_save_breakdown

    return output_dict
