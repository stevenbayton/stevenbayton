# python modules
import numpy as np
import pandas as pd

# multiconsult modules
import _background_functions as b_func


def extract_design_soil_profile(gdb_df, d_z, z_max, sections, foundation_list):

    soil_data_dis_dict = {}

    depth = depth_orig = np.array(gdb_df['depth'].astype(float))

    z_min = 0
    for foundation_i in sections.keys():
        if foundation_i in foundation_list:
            for section_i in sections[foundation_i].keys():
                data_i = sections[foundation_i][section_i]
                z_min = min(z_min, data_i['z1_from_soil_surface'])

    if z_max in depth:
        z_max_ex = True
        idx_lim_row_1 = [row for row in depth].index(z_max)
        depth = depth[:idx_lim_row_1 + 1]
    else:
        z_max_ex = False
        if z_max > max(depth):
            depth = np.append(depth, max(depth))
            row_to_repeat = len(gdb_df) - 1
            gdb_df = pd.concat([gdb_df.iloc[:row_to_repeat + 1], gdb_df.iloc[[row_to_repeat]], gdb_df.iloc[row_to_repeat + 1:]], ignore_index=True)
            depth_orig = np.array(gdb_df['depth'].astype(float))

        idx_lim_row_2 = len([row for row in depth if row < z_max])-1              
        depth_app = z_max
        depth = depth[:idx_lim_row_2 + 1]        
        depth = np.append(depth, depth_app)
        # add_depth_row = gdb_df.iloc[-1].copy()
        # add_depth_row["depth"] = depth_app
        # gdb_df = pd.concat([gdb_df, pd.DataFrame([add_depth_row])], ignore_index=True)
            
    if d_z is not None:
        z_dis = np.round(np.arange(z_min, z_max+d_z, d_z), 2)
        
    else:
        z_dis = np.array(depth)

    soil_data_dis_dict['depth'] = z_dis

    gdb_params = gdb_df.columns

    for param_i in gdb_params:

        if param_i != 'depth':
            param_data_i = gdb_df[param_i].to_numpy()
            if z_max_ex:
                param_data_i = param_data_i[:idx_lim_row_1 + 1]
            if any(isinstance(param_data_ii, str) for param_data_ii in param_data_i):
                if param_i == 'sbt':
                    param_data_i[np.where(param_data_i.astype(str) == str(np.nan))] = ""
                if not z_max_ex:
                    param_data_app_i = param_data_i[idx_lim_row_2]
                    param_data_i = param_data_i[:idx_lim_row_2 + 1]
                    param_data_i = np.append(param_data_i, param_data_app_i)
                if d_z is not None:
                    soil_data_dis_dict[param_i] = b_func.param_fill(z_dis, depth, param_data_i)
                else:
                    soil_data_dis_dict[param_i] = param_data_i
            else:
                param_data_i = np.array(param_data_i.astype(float))
                if not z_max_ex:

                    if z_max > max(depth_orig):
                        gR = (param_data_i[-3]-param_data_i[-2])/(depth_orig[-3]-depth_orig[-2])
                        param_data_app_i = gR*(z_max - depth_orig[-3]) + param_data_i[-3]
                        if np.isnan(param_data_app_i):
                            param_data_app_i = np.interp(z_max, depth_orig, param_data_i)
                    else:
                        param_data_app_i = np.interp(z_max, depth_orig, param_data_i)

                    param_data_i = param_data_i[:idx_lim_row_2 + 1]
                    param_data_i = np.append(param_data_i, param_data_app_i)

                if d_z is not None:
                    soil_data_dis_dict[param_i] = np.interp(z_dis, depth, param_data_i)
                    soil_data_dis_dict[param_i] = b_func.param_mask(soil_data_dis_dict[param_i])
                else:
                    soil_data_dis_dict[param_i] = param_data_i

            soil_data_dis_dict[param_i][np.round(z_dis, 2) < 0] = np.nan

    soil_data_dis_array = [soil_data_dis_dict[param_i] for param_i in gdb_params]
   
    return soil_data_dis_array, gdb_params


def section_setup(depth_i, z_dis, length_dimension, sections, foundation_list, d_z, pf_load_perm, calc_type, uw_s_steel=6850, add_section=False):

    b_outer_dis = np.zeros(len(z_dis))
    t_dis = np.zeros(len(z_dis))
    base_area_annulus_dis = np.zeros(len(z_dis))
    base_area_outer_dis = np.zeros(len(z_dis))
    base_area_inner_dis = np.zeros(len(z_dis))
    shaft_area_outer_dis = np.zeros(len(z_dis))
    shaft_area_inner_dis = np.zeros(len(z_dis))

    W_foundation = 0
    count = 0
    stick_up_total = 0

    sections_final = {}

    for foundation_i in sections.keys():

        if foundation_i in foundation_list:

            sections_final[foundation_i] = {}

            for section_i in sections[foundation_i].keys():

                data_i = sections[foundation_i][section_i]

                z1 = round(data_i['z1_from_soil_surface'], 2)
                z2 = round(data_i['z2_from_soil_surface'], 2)

                if (z1 < 0 or z2 < 0) and calc_type not in ['p_y_displacement', 't_z_displacement']:
                    sections_final[foundation_i]['stick_up'] = sections[foundation_i][section_i]
                    sections_final[foundation_i]['stick_up']['z1'] = data_i['z1_from_soil_surface']
                    sections_final[foundation_i]['stick_up']['z2'] = data_i['z2_from_soil_surface']
                    stick_up_total += abs(data_i['z1_from_soil_surface'] - data_i['z2_from_soil_surface'])
            
                else:
                    sections_final[foundation_i][section_i] = sections[foundation_i][section_i]

                    if calc_type == 'installation':
                        sections_final[foundation_i][section_i]['z1'] = length_dimension - round(min(data_i['z2_from_soil_surface'], max(length_dimension, data_i['z1_from_soil_surface'])), 2)
                        sections_final[foundation_i][section_i]['z2'] = length_dimension - round(data_i['z1_from_soil_surface'], 2)
                    else:
                        sections_final[foundation_i][section_i]['z1'] = round(data_i['z1_from_soil_surface'], 2)
                        sections_final[foundation_i][section_i]['z2'] = round(min(data_i['z2_from_soil_surface'], max(z_dis[-1], data_i['z1_from_soil_surface'])), 2)
        
            sections_final[foundation_i] = dict(sorted(sections_final[foundation_i].items(), key=lambda item: item[1]['z1']))

    for foundation_i in sections_final.keys():

        for section_i in sections_final[foundation_i].keys():

            data_i = sections_final[foundation_i][section_i]
            geometry_shape_i = data_i['shape']

            if section_i == 'stick_up':  

                W_section = 0

                t_1 = data_i['t1']
                if not np.isnan(data_i['t2']):
                    t_2 = data_i['t2']
                    m_t_wall = (t_2 - t_1) / (data_i['z2'] - data_i['z1'])
                else:
                    t_2 = t_1
                    m_t_wall = 0
                c_t_wall = t_1 - m_t_wall*data_i['z1']
                t_over_soil = np.average([m_t_wall*z_i + c_t_wall for z_i in [data_i['z2'], data_i['z1']]])

                if geometry_shape_i == 'circle':
                    b_inner_over_soil = b_func.bi(data_i['b_outer'], t_over_soil)
                    base_area_annulus_over_soil = b_func.a_annulus_circle(data_i['b_outer'], b_inner_over_soil)

                elif geometry_shape_i == 'rectangle':
                    b_outer_over_soil = data_i['b_outer']
                    l_outer_over_soil = data_i['l_outer']         
                    b_inner_over_soil = b_func.bi(b_outer_over_soil, t_over_soil)
                    l_inner_over_soil = b_func.bi(l_outer_over_soil, t_over_soil)
                    base_area_annulus_over_soil = b_func.a_annulus_rectangle(b_outer_over_soil, l_outer_over_soil, b_inner_over_soil, l_inner_over_soil)

                if data_i['include_submerged_mass']:
                    d_z_stick_up = abs(data_i['z2'] - data_i['z1'])
                    W_section += d_z_stick_up * base_area_annulus_over_soil * uw_s_steel * pf_load_perm * 9.81/1e6

                W_foundation += W_section 

                continue

            z_section = []

            z1 = round(data_i['z1'], 2)
            z2 = round(data_i['z2'], 2)

            if z1 <= z_dis[-1]:
                z_section.append(z1)

                if z2 <= z_dis[-1] and z2 != z_section[-1]:
                    z_section.append(z2)
                elif z2 != z_section[-1]:
                    z_section.append(z_dis[-1])
                        
            if calc_type not in ['p_y_displacement', 't_z_displacement']:
                if len(z_section) > 1:
                    if z_section[0] <= 0:
                        z_section[0] = 0
                    if z_section[-1] <= 0:
                        z_section[-1] = 0
                    if z_section[0] != z_section[-1]:
                        if d_z is not None:
                            z_section_update = np.arange(z_section[0], z_section[1]+d_z/10, d_z)
                        else:
                            z_section_update = z_section
                    else:
                        z_section_update = [z_section[0]] # []

                elif len(z_section) > 0:
                    z_section_update = z_section
                else:
                    z_section_update = []

                if len(z_section_update) > 0:
                    if z_section_update[0] != 0:
                        z_section_update = np.delete(z_section_update, 0)

            else:
                z_section_update = np.arange(z_section[0], z_section[1]+d_z/10, d_z)
            
            if depth_i == 0:
                idx_add = 0
            else:
                idx_add = 1
            
            if len(z_section_update) > 0:

                t_1 = data_i['t1']
                if not np.isnan(data_i['t2']):
                    t_2 = data_i['t2']
                    m_t_wall = (t_2 - t_1) / (data_i['z2'] - data_i['z1'])
                else:
                    t_2 = t_1
                    m_t_wall = 0
                c_t_wall = t_1 - m_t_wall*data_i['z1']
                t_section = np.array([m_t_wall*z_i + c_t_wall for z_i in z_section_update])

                if not np.isnan(data_i['base_reduction']):
                    base_reduction = np.array([data_i['base_reduction'] for z_i in z_section_update])
                else:
                    base_reduction = np.array([1 for z_i in z_section_update])

                if not np.isnan(data_i['friction_reduction']):
                    friction_reduction = np.array([data_i['friction_reduction'] for z_i in z_section_update])
                else:
                    friction_reduction = np.array([1 for z_i in z_section_update])

                if geometry_shape_i == 'circle':
                    b_outer_section = np.array([data_i['b_outer'] for z_i in z_section_update])
                    b_inner_section = np.array([b_func.bi(b_outer_i, t_i) for b_outer_i, t_i in zip(b_outer_section, t_section)])

                    base_area_annulus_section = np.array([base_reduction_i*b_func.a_annulus_circle(b_outer_i, b_inner_i) for b_outer_i, b_inner_i, base_reduction_i in zip(b_outer_section, b_inner_section, base_reduction)])
                    base_area_outer_section = np.array([base_reduction_i*b_func.a_circle(b_outer_i) for b_outer_i, base_reduction_i in zip(b_outer_section, base_reduction)])
                    base_area_inner_section = np.array([b_func.a_circle(b_inner_i) for b_inner_i in b_inner_section])
                    shaft_area_outer_section = np.array([friction_reduction_i*b_func.circumference_circle(b_outer_i) for b_outer_i, friction_reduction_i in zip(b_outer_section, friction_reduction)])
                    shaft_area_inner_section = np.array([friction_reduction_i*b_func.circumference_circle(b_inner_i) for b_inner_i, friction_reduction_i in zip(b_inner_section, friction_reduction)])

                elif geometry_shape_i == 'rectangle':
                    b_outer_section = np.array([data_i['b_outer'] for z_i in z_section_update])
                    l_outer_section = np.array([data_i['l_outer'] for z_i in z_section_update])            
                    b_inner_section = np.array([b_func.bi(b_outer_i, t_i) for b_outer_i, t_i in zip(b_outer_section, t_section)])
                    l_inner_section = np.array([b_func.bi(l_outer_i, t_i) for l_outer_i, t_i in zip(l_outer_section, t_section)])

                    base_area_annulus_section = np.array([base_reduction_i*b_func.a_annulus_rectangle(b_outer_i, l_outer_i, b_inner_i, l_inner_i) for b_outer_i, l_outer_i, b_inner_i, l_inner_i, base_reduction_i in zip(b_outer_section, l_outer_section, b_inner_section, l_inner_section, base_reduction)])
                    base_area_outer_section = np.array([base_reduction_i*b_func.a_rectangle(b_outer_i, l_outer_i) for b_outer_i, l_outer_i, base_reduction_i in zip(b_outer_section, l_outer_section, base_reduction)])
                    base_area_inner_section = np.array([b_func.a_rectangle(b_inner_i, l_inner_i) for b_inner_i, l_inner_i in zip(b_inner_section, l_inner_section)])
                    shaft_area_outer_section = np.array([friction_reduction_i*b_func.circumference_rectangle(b_outer_i, l_outer_i) for b_outer_i, l_outer_i, friction_reduction_i in zip(b_outer_section, l_outer_section, friction_reduction)])
                    shaft_area_inner_section = np.array([friction_reduction_i*b_func.circumference_rectangle(b_inner_i, l_inner_i) for b_inner_i, l_inner_i, friction_reduction_i in zip(b_inner_section, l_inner_section, friction_reduction)])

                W_section = 0

                if data_i['include_submerged_mass']:
                    d_z_section = abs(data_i['z1'] - data_i['z2'])
                    W_section += d_z_section * base_area_annulus_section[0] / base_reduction[0] * uw_s_steel * pf_load_perm * 9.81/1e6

                W_foundation += W_section
                
                if any(np.round(z_dis, 2) >= round(z_section_update[0], 2)) and any(np.round(z_dis, 2) <= round(z_section_update[-1], 2)):
                    
                    add_section = True
                    z1_section_idx = np.where(np.round(z_dis, 2) >= round(z_section_update[0], 2))[0][0]
                    z2_section_idx = np.where(np.round(z_dis, 2) <= round(z_section_update[-1], 2))[0][-1]
        
                    b_outer_dis[z1_section_idx:z2_section_idx+1] = b_outer_section
                    t_dis[z1_section_idx:z2_section_idx+1] = t_section

                    if count == 0:
                        base_area_annulus_dis[z1_section_idx:z2_section_idx+1] = base_area_annulus_section
                        base_area_outer_dis[z1_section_idx:z2_section_idx+1] = base_area_outer_section
                        base_area_inner_dis[z1_section_idx:z2_section_idx+1] = base_area_inner_section
                        shaft_area_outer_dis[z1_section_idx:z2_section_idx+1] = shaft_area_outer_section
                        shaft_area_inner_dis[z1_section_idx:z2_section_idx+1] = shaft_area_inner_section
                    else:
                        base_area_annulus_dis[z1_section_idx:z2_section_idx+1] = np.array([i + j for i, j in zip(base_area_annulus_dis[z1_section_idx:z2_section_idx+1], base_area_annulus_section)])
                        base_area_outer_dis[z1_section_idx:z2_section_idx+1] = np.array([i + j for i, j in zip(base_area_outer_dis[z1_section_idx:z2_section_idx+1], base_area_outer_section)])
                        base_area_inner_dis[z1_section_idx:z2_section_idx+1] = base_area_inner_section
                        shaft_area_outer_dis[z1_section_idx:z2_section_idx+1] = np.array([i + j for i, j in zip(shaft_area_outer_dis[z1_section_idx:z2_section_idx+1], shaft_area_outer_section)])
                        shaft_area_inner_dis[z1_section_idx:z2_section_idx+1] = np.array([i + j for i, j in zip(shaft_area_inner_dis[z1_section_idx:z2_section_idx+1], shaft_area_inner_section)])

            count += 1

        if add_section:
            b_outer_dis[z2_section_idx+idx_add:] = b_outer_dis[z2_section_idx]
            t_dis[z2_section_idx+idx_add:] = t_dis[z2_section_idx]
            base_area_annulus_dis[z2_section_idx+idx_add:] = base_area_annulus_dis[z2_section_idx]
            base_area_outer_dis[z2_section_idx+idx_add:] = base_area_outer_dis[z2_section_idx]
            base_area_inner_dis[z2_section_idx+idx_add:] = base_area_inner_dis[z2_section_idx]
            shaft_area_outer_dis[z2_section_idx+idx_add:] = shaft_area_outer_dis[z2_section_idx]
            shaft_area_inner_dis[z2_section_idx+idx_add:] = shaft_area_inner_dis[z2_section_idx]
            
    section_dimensions = {"b_outer": b_outer_dis,
                          "thickness": t_dis,
                          "a_base_bo": base_area_outer_dis,
                          "a_base_bi": base_area_inner_dis,
                          "a_base_annulus": base_area_annulus_dis,
                          "a_shaft_bo": shaft_area_outer_dis,
                          "a_shaft_bi": shaft_area_inner_dis,
                          "stick_up": stick_up_total}
    
    return W_foundation, section_dimensions

