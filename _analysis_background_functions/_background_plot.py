# python modules
import copy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
from scipy.interpolate import griddata
import pandas as pd

matplotlib.use('QtAgg')


def parse_manual(entry):

    # entry = entry.strip()[1:-1]

    left, right = entry.split("],")

    left = left.strip()[1:]
    right = right.strip()[1:-1]

    x = [float(v) for v in left.split(",")]
    y = [float(v) for v in right.split(",")]

    return x, y


def execute_plot(input_heading, gdb_df, gdb_df_scour, scour_gdb, cpt_dict, setup_dict, output_dict, calculation_name, foundation_location_name):
    
    if len(setup_dict['location_details'][setup_dict['location_details']['design_grouping'] == foundation_location_name]) > 0:
        location_id_array = np.array(setup_dict['location_details']['Borehole'][setup_dict['location_details']['design_grouping'] == foundation_location_name])
    elif len(setup_dict['location_details'][setup_dict['location_details']['Borehole'] == foundation_location_name]) > 0:
        location_id_array = np.array(setup_dict['location_details']['Borehole'][setup_dict['location_details']['Borehole'] == foundation_location_name])
    else:
        location_id_array = []

    cpts = {}

    for loc_i in location_id_array:
        if loc_i in cpt_dict:
            cpts[loc_i] = cpt_dict[loc_i]
                    
    input = output_dict['input']
    output = output_dict['output']

    if calculation_name in ['_caisson_capacity']:
        plot_caisson_output(input_heading, output, setup_dict, calculation_name, foundation_location_name)

    if calculation_name in ['_axial_displacement', '_lateral_displacement']:
        plot_spring_output(input_heading, output, setup_dict, calculation_name, foundation_location_name)
        plot_global_spring_output(input_heading, output, setup_dict, calculation_name, foundation_location_name)

    if calculation_name in ['_installation']:
        if 'driven' in setup_dict[calculation_name][input_heading]['calculation_method']:
            plot_stress_fatigue(input_heading, output, setup_dict, calculation_name, foundation_location_name)
    
    plot_axes_task(cpts, input_heading, input, output, setup_dict, gdb_df, gdb_df_scour, scour_gdb, calculation_name, foundation_location_name)
                

def plot_axes_task(cpts, input_heading, input, output, setup_dict, gdb_df, gdb_df_scour, scour_gdb, calculation_name, foundation_location_name, output_folder='output'):

    default_ls = '-'
    default_marker = 'None'
    default_color = 'darkblue'
    
    colors_calculation_method = ['darkblue', 'darkred', 'darkgreen', 'grey', 'grey', 'grey', 'grey', 'grey']

    plots_for_input = setup_dict[calculation_name][input_heading]['plot'].replace(" ", "").split(";")
    
    for plot_i in setup_dict['plotting']:

        if plot_i not in plots_for_input:
            continue

        axes = copy.deepcopy(setup_dict['plotting'][plot_i])
        
        fig, ax = plt.subplots(1, len([title for title in axes.keys() if 'Depth' not in title]), figsize=(22, 12))
        plt.subplots_adjust(wspace=0.1)

        ylim = axes['Depth']['limit'].replace(" ", "").split(",")
        
        ### CLEAN 
        length_embedment = 0
        length_embedment_governing = None
        for key in output.keys():
            if key not in ['capacity_dict', 'url_info']:
                if 'length_embedment' in output[key]['plot_output']:
                    if output[key]['plot_output']['length_embedment'] >= length_embedment:
                        length_embedment_governing = key
                        length_embedment = output[key]['plot_output']['length_embedment']
                        
        if 'length_embedment_punch_through' in output[length_embedment_governing]['plot_output']:
            length_embedment_punch_through = output[length_embedment_governing]['plot_output']['length_embedment_punch_through']

        sw_depth = 0
        for key in output.keys():
            if key not in ['capacity_dict', 'url_info']:
                if 'sw_depth' in output[key]['plot_output']:
                    if output[key]['plot_output']['sw_depth'] >= sw_depth:
                        sw_depth = output[key]['plot_output']['sw_depth']

        sw_total = 0
        for key in output.keys():
            if key not in ['capacity_dict', 'url_info']:
                if 'sw_total' in output[key]['plot_output']:
                    if output[key]['plot_output']['sw_total'] >= sw_total:
                        sw_total = output[key]['plot_output']['sw_total']
       
        ### CLEAN 
        
        for idx_ax, (ax_i, info_i) in enumerate(axes.items()):

            ax_i = ax_i.replace("\\n", "\n")

            if 'depth' in ax_i.lower():
                ax[idx_ax].set_ylabel(f"${ax_i.replace(" ", "\\ ")}$" + '\n(' + info_i['unit'] + ')')
                continue
            else:
                ax_no = idx_ax - 1
                if ax_no != 0:
                    ax[ax_no].set_yticklabels([])

            params = info_i['params'].replace(" ", "").split(";")
            xlim = info_i['limit'].replace(" ", "").split(",")

            if info_i['data_type'] == 'input':
                printed_params = []
                for param_i in params:
                    for cpt_name_i, cpt_data_i in cpts.items():
                        if cpt_name_i in setup_dict['cpt_map']:
                            cpt_color_i = setup_dict['cpt_map'][cpt_name_i]['plot_color']
                        else:
                            cpt_color_i = 'grey'
                        if '_low' in param_i:
                            param_ii = param_i.split('_low')[0]
                        elif '_best' in param_i:
                            param_ii = param_i.split('_best')[0]
                        elif '_high' in param_i:
                            param_ii = param_i.split('_high')[0]
                        else:
                            param_ii = param_i
                        if param_ii not in printed_params:
                            if param_ii in cpt_data_i:
                                ax[ax_no].plot(cpt_data_i[param_ii], cpt_data_i['depth'], ls='-', color=cpt_color_i, alpha=0.5)
                            elif param_ii in setup_dict['param_map']:
                                if setup_dict['param_map'][param_ii]['plot_param'] in cpt_data_i:
                                    ax[ax_no].plot(cpt_data_i[setup_dict['param_map'][param_ii]['plot_param']], cpt_data_i['depth'], ls='-', color=cpt_color_i, alpha=0.5)

                    if gdb_df is not None:

                        if scour_gdb and param_i in [x + y for x in ['qc', 'qt'] for y in ['', '_low', '_best', '_high']]:
                            alpha = 0.5
                        else:
                            alpha = 1

                        print_gdb = False

                        clay_unique = ['suc']
                        sand_unique = ['phi']

                        clay_unique = [x + y for x in clay_unique for y in ['', '_low', '_best', '_high']]
                        sand_unique = [x + y for x in sand_unique for y in ['', '_low', '_best', '_high']]
                        soil_type = np.array(gdb_df['Soil_Type'])

                        if param_i in gdb_df and 'low' in param_i:
                            x_plot = np.array(gdb_df[param_i])                            
                            ls_gdb = '--'
                            color_gdb = 'r'
                            label_gdb = 'LE'
                            print_gdb = True

                        elif param_i in gdb_df and 'high' in param_i:
                            x_plot = np.array(gdb_df[param_i])                            
                            ls_gdb = '--'
                            color_gdb = 'g'
                            label_gdb = 'HE'
                            print_gdb = True

                        elif param_i in gdb_df and 'best' in param_i:
                            x_plot = np.array(gdb_df[param_i])                            
                            ls_gdb = '-'
                            color_gdb = 'k'
                            label_gdb = 'BE'
                            print_gdb = True

                        elif param_i in gdb_df:
                            x_plot = np.array(gdb_df[param_i])                            
                            ls_gdb = '--'
                            color_gdb = 'k'
                            label_gdb = 'None'
                            print_gdb = True

                        if print_gdb:
                            y_plot = np.array(gdb_df['depth'])
                            
                            if param_i in clay_unique:
                                x_plot = [np.nan if st_i.lower() not in ['c', 'clay', 'si'] else x_i for x_i, st_i in zip(x_plot, soil_type)]
                            if param_i in sand_unique:
                                x_plot = [np.nan if st_i.lower() not in ['s', 'sand', 'si'] else x_i for x_i, st_i in zip(x_plot, soil_type)]
                                                
                            nan_condition = np.array([str(x) == 'nan' for x in x_plot])
                            x_plot_red = np.array([np.nan if nan_i else x_i for x_i, nan_i in zip(x_plot, nan_condition)])
                            y_plot_red = np.array([np.nan if nan_i else y_i for y_i, nan_i in zip(y_plot, nan_condition)])
                            ax[ax_no].plot(x_plot_red, y_plot_red, ls=ls_gdb, color=color_gdb, label=label_gdb, alpha=alpha)
                        
                    if gdb_df_scour is not None and scour_gdb and param_i in [x + y for x in ['qc', 'qt'] for y in ['', '_low', '_best', '_high']]:
                        if param_i + '_low' in gdb_df_scour:
                            x_plot = np.array(gdb_df_scour[param_i + '_low'])
                            y_plot = np.array(gdb_df_scour['depth'])
                            nan_condition = np.array([str(x) == 'nan' for x in x_plot])
                            x_plot_red = np.array([np.nan if nan_i else x_i for x_i, nan_i in zip(x_plot, nan_condition)])
                            y_plot_red = np.array([np.nan if nan_i else y_i for y_i, nan_i in zip(y_plot, nan_condition)]) 
                            ax[ax_no].plot(x_plot_red, y_plot_red, ls='--', color='r', label="LE w/ scour")

                        if param_i + '_best' in gdb_df_scour:
                            x_plot = np.array(gdb_df_scour[param_i + '_best'])
                            y_plot = np.array(gdb_df_scour['depth'])
                            nan_condition = np.array([str(x) == 'nan' for x in x_plot])
                            x_plot_red = np.array([np.nan if nan_i else x_i for x_i, nan_i in zip(x_plot, nan_condition)])
                            y_plot_red = np.array([np.nan if nan_i else y_i for y_i, nan_i in zip(y_plot, nan_condition)])
                            ax[ax_no].plot(x_plot_red, y_plot_red, ls='-', color='k', label="BE w/ scour")

                        if param_i + '_high' in gdb_df_scour:
                            x_plot = np.array(gdb_df_scour[param_i + '_high'])
                            y_plot = np.array(gdb_df_scour['depth'])
                            nan_condition = np.array([str(x) == 'nan' for x in x_plot])
                            x_plot_red = np.array([np.nan if nan_i else x_i for x_i, nan_i in zip(x_plot, nan_condition)])
                            y_plot_red = np.array([np.nan if nan_i else y_i for y_i, nan_i in zip(y_plot, nan_condition)])
                            ax[ax_no].plot(x_plot_red, y_plot_red, ls='--', color='g', label="HE w/ scour")

                        if param_i in gdb_df_scour:
                            x_plot = np.array(gdb_df_scour[param_i])
                            y_plot = np.array(gdb_df_scour['depth'])
                            nan_condition = np.array([str(x) == 'nan' for x in x_plot])
                            x_plot_red = np.array([np.nan if nan_i else x_i for x_i, nan_i in zip(x_plot, nan_condition)])
                            y_plot_red = np.array([np.nan if nan_i else y_i for y_i, nan_i in zip(y_plot, nan_condition)]) 
                            ax[ax_no].plot(x_plot_red, y_plot_red, ls='--', color='k')

            elif info_i['data_type'] == 'output':

                if 'line_style' not in info_i:
                    info_i['line_style'] = [default_ls]*len(params)
                else:
                    info_i['line_style'] = info_i['line_style'].replace(" ", "").split(";")
                    if len(info_i['line_style']) < len(params):
                        info_i['line_style'].append(default_ls)

                if 'marker_style' not in info_i:
                    info_i['marker_style'] = [default_marker]*len(params)
                else:
                    info_i['marker_style'] = info_i['marker_style'].replace(" ", "").split(";")
                    if len(info_i['marker_style']) < len(params):
                        info_i['marker_style'].append(default_marker)

                if 'color_override' not in info_i:
                    info_i['color_override'] = [None]*len(params)
                else:
                    info_i['color_override'] = info_i['color_override'].replace(" ", "").split(";")
                    if len(info_i['color_override']) < len(params):
                        info_i['color_override'].append(default_color)

                if 'legend_override' not in info_i:
                    info_i['legend_override'] = [None]*len(params)
                else:
                    info_i['legend_override'] = info_i['legend_override'].split(";")
                    if len(info_i['legend_override']) < len(params):
                        info_i['legend_override'].append('_nolegend_')

                if 'multiplier' not in info_i:
                    info_i['multiplier'] = [1]*len(params)
                else:
                    info_i['multiplier'] = str(info_i['multiplier']).split(";")
                    if len(info_i['legend_override']) < len(params):
                        info_i['legend_override'].append(1)

                for param_i, multiplier_i, color_override_i, ls_i, ms_i, legend_override_i in zip(params, info_i['multiplier'], info_i['color_override'], info_i['line_style'], info_i['marker_style'], info_i['legend_override']):

                    calculation_method_total = []
                    count_color = 0
                    
                    for calculation_method_i in output.keys():

                        if calculation_method_i in ['capacity_dict', 'url_info']:
                            continue
                        
                        if 'plot_input' in output[calculation_method_i]:
                            input_dict = output[calculation_method_i]['plot_input']
                            for key_red in ['[input]', '[input_s]', '[input_b]', '[input_pb]', '[input_ps]', '[input_t]']:
                                input_dict = {key.replace(key_red, ""): value for key, value in input_dict.items()}
                            for key_red in ['[output]', '[output_s]', '[output_b]', '[input_pb]', '[input_ps]', '[output_t]']:
                                input_dict = {key.replace(key_red, ""): value for key, value in input_dict.items()}
                        else:
                            input_dict = {}

                        output_dict_ = output[calculation_method_i]['plot_output']

                        if calculation_name in ['_lateral_displacement', '_axial_displacement']:
                            design_load = output_dict_['design_load']
                            output_dict_array = []

                            for key, val in output_dict_.items():
                                if isinstance(key, np.float64):
                                    output_dict_array.append([key, val])
                                
                        else:
                            design_load = None
                            output_dict_array = [[None, output_dict_]]

                        for output_dict_i in output_dict_array:
                            
                            plot_load = output_dict_i[0]
                            output_dict = output_dict_i[1]

                            if 'foundation_b_outer' in output_dict:
                                foundation_b_outer = output_dict['foundation_b_outer']
                            else:
                                foundation_b_outer = None

                            for key_red in ['[output]', '[output_s]', '[output_b]', '[output_pb]', '[output_ps]', '[output_t]', '[output_grl]']:
                                output_dict = {key.replace(key_red, ""): value for key, value in output_dict.items()}
                            for key_red in ['[output]', '[output_s]', '[output_b]', '[output_pb]', '[output_ps]', '[output_t]', '[output_grl]']:
                                output_dict = {key.replace(key_red, ""): value for key, value in output_dict.items()}

                            if param_i in input_dict:
                                output_i = input_dict
                            else:
                                output_i = output_dict
                            
                            if calculation_name not in ['_cap_capacity', '_caisson_capacity']:
                                index_length = [i for i, j in enumerate(output_i['z']) if j >= length_embedment][0]
                            
                            else:
                                index_length = len(output_i['z']) - 1

                            if 'incremental' in info_i:

                                if 'grl' in param_i:
                                    z_inc_param = 'z_grl'
                                    calc_suf = '[output_grl]'
                                    if any(param_i + '_section_1' + calc_suf in d for sub in output_i['grl_soil_resistance_inc'] for d in sub):
                                        output_inc_i = output_i['grl_soil_resistance_inc']
                                    elif any(param_i + '_section_1' + calc_suf in d for sub in output_i['grl_pile_stress_inc'] for d in sub):
                                        output_inc_i = output_i['grl_pile_stress_inc']
                                    else:
                                        output_inc_i = {}

                                elif '_b' in param_i:
                                    z_inc_param = 'z_b'
                                    calc_suf = '[calc_b]'
                                    output_inc_i = output_i['base_parameter_inc']

                                elif '_s' in param_i:
                                    z_inc_param = 'z_s'
                                    calc_suf = '[calc_s]'
                                    output_inc_i = output_i['shaft_parameter_inc']

                                elif 'p_ult' in param_i:
                                    z_inc_param = 'z'
                                    calc_suf = '[calc]'
                                    output_inc_i = output_i['p_ult_parameter_inc']
                                                            
                                plot_interval = input["incremental_save_plot"]
                                d_z = input["d_z"]

                                if str(plot_interval) != 'None':
                                    n_interval = plot_interval/d_z
                                else:
                                    n_interval = index_length - 1

                                if calculation_method_i not in calculation_method_total:
                                    calculation_method_total.append(calculation_method_i)
                                    color_i = colors_calculation_method[count_color]
                                    count_color += 1
                                    legend_toggle = True
                                
                                else:
                                    legend_toggle = False

                                x_total = []
                                y_total = []
                            
                                for idx2 in range(len(output_inc_i)):
                                    output_inc_ii = output_inc_i[idx2]

                                    for section_i in range(1, 10, 1):
                                        x_data = [float(multiplier_i)*d[param_i + '_section_' + str(section_i) + calc_suf] for d in output_inc_ii if param_i + '_section_' + str(section_i) + calc_suf in d]
                                        y_data = [d[z_inc_param + '_section_' + str(section_i) + calc_suf] for d in output_inc_ii if z_inc_param + '_section_' + str(section_i) + calc_suf in d]
                                        x_total += x_data
                                        y_total += y_data

                                        if idx2 % n_interval == 0 and idx2 != 0:
                                            ax[ax_no].plot(x_data, y_data, ls='-', marker='None', color=color_i, alpha=0.1)
                                
                                if color_override_i is not None:
                                    color_i = color_override_i

                                if legend_override_i is not None:
                                    legend_i = legend_override_i.strip()
                                else:
                                    legend_i = calculation_method_i
                                
                                y_print = list(set(y_total))
                                y_print = sorted(y_print)
                                
                                x_print = []

                                for y_i in y_print:
                                    x_i = max(x_ii for x_ii, y_ii in zip(x_total, y_total) if abs(y_ii - y_i) < 1e-9)
                                    x_print.append(x_i)

                                if legend_toggle:
                                    ax[ax_no].plot(x_print, y_print, ls='--', marker='None', color=color_i, alpha=0.5, label=f"${legend_i.replace(' ', '\\ ')}$" + ' (max)')
                                else:
                                    ax[ax_no].plot(x_print, y_print, ls='--', marker='None', color=color_i, alpha=0.5)
                                        

                                if 'grl' not in param_i:
                                    output_inc_ii = output_inc_i[index_length]
                                    for section_i in range(1, 10, 1):
                                        x_plot = [float(multiplier_i)*d[param_i + '_section_' + str(section_i) + calc_suf] for d in output_inc_ii if param_i + '_section_' + str(section_i) + calc_suf in d]
                                        y_plot = [d[z_inc_param + '_section_' + str(section_i) + calc_suf] for d in output_inc_ii if z_inc_param + '_section_' + str(section_i) + calc_suf in d]
                                        if legend_toggle:
                                            ax[ax_no].plot(x_plot, y_plot, ls='-', marker='None', color=color_i, label=f"${legend_i.replace(' ', '\\ ')}$" + ' (embedment)')
                                        else:
                                            ax[ax_no].plot(x_plot, y_plot, ls='-', marker='None', color=color_i)

                            else:
                                
                                if plot_load == design_load:
                                    alpha_i = 1
                                else:
                                    alpha_i = 0.25

                                if calculation_method_i not in calculation_method_total:
                                    calculation_method_total.append(calculation_method_i)
                                    color_i = colors_calculation_method[count_color]
                                    count_color += 1
                                    legend_toggle = True
                                
                                else:
                                    if plot_load == design_load:
                                        legend_toggle = True
                                    else:
                                        legend_toggle = False

                                if color_override_i is not None:
                                    color_i = color_override_i

                                if legend_override_i is not None:
                                    if '[method]' in legend_override_i:
                                        legend_i = calculation_method_i + ' ' + legend_override_i.split(']')[-1]
                                    else:
                                        if plot_load == design_load and calculation_name in ['_lateral_displacement', '_axial_displacement']:
                                            legend_i = legend_override_i + ' (design load)'
                                        else:
                                            legend_i = legend_override_i
                                else:
                                    if plot_load == design_load and calculation_name in ['_lateral_displacement', '_axial_displacement']:
                                        legend_i = calculation_method_i + ' (design load)'
                                    else:
                                        legend_i = calculation_method_i

                                if 'grl' in param_i:
                                    x_plot1 = [float(multiplier_i)*i for i in output_i[param_i]][0:index_length+1]
                                    y_plot1 = output_i['z_grl'][0:index_length+1]
                                    x_plot2 = [float(multiplier_i)*i for i in output_i[param_i]][index_length:]
                                    y_plot2 = output_i['z_grl'][index_length:]
                                else:
                                    x_plot1 = [float(multiplier_i)*i for i in output_i[param_i]][0:index_length+1]
                                    y_plot1 = output_i['z'][0:index_length+1]
                                    x_plot2 = [float(multiplier_i)*i for i in output_i[param_i]][index_length:]
                                    y_plot2 = output_i['z'][index_length:]

                                    if calculation_name in ['_cap_capacity'] and param_i == 'SF' and length_embedment == 0:
                                        x_plot1 = x_plot1[1:]
                                        y_plot1 = y_plot1[1:]

                                if legend_toggle:                    
                                    ax[ax_no].plot(x_plot1, y_plot1, ls=ls_i, marker=ms_i, color=color_i, label=f"${legend_i.replace(' ', '\\ ')}$", alpha=alpha_i)
                                    ax[ax_no].plot(x_plot2, y_plot2, ls=ls_i, marker=ms_i, color=color_i, alpha=0.25)
                                else:
                                    ax[ax_no].plot(x_plot1, y_plot1, ls=ls_i, marker=ms_i, color=color_i, alpha=alpha_i)
                                    ax[ax_no].plot(x_plot2, y_plot2, ls=ls_i, marker=ms_i, color=color_i, alpha=0.25)

                                if calculation_name in ['_cap_capacity'] and param_i == 'SF':
                                    min_SF = np.min(x_plot1)
                                    index_SF = np.where(x_plot1 == min_SF)[0][0]
                                    depth_SF = y_plot1[index_SF]
                                    ax[ax_no].plot(min_SF, depth_SF, color=color_i, marker='o', ms=5)
                                    ax[ax_no].text(min_SF-(float(xlim[1])-float(xlim[0]))/50, depth_SF, str(round(min_SF, 2)), color=color_i, ha='right', va='center', fontsize=8)              

                                if calculation_name in ['_caisson_capacity'] and param_i == 'su_ave':                               
                                    alpha_d_su = input_dict['alpha_d_su']                             
                                    su_ave_l = input_dict['su_ave_l']                             
                                    su_ave_end_bear = input_dict['su_ave_end_bear']
                                    ax[ax_no].plot([float(xlim[0]), float(xlim[1])], [length_embedment, length_embedment], color='darkred', ls='--')
                                    ax[ax_no].plot([su_ave_l, su_ave_l], [0, length_embedment], color='darkred', ls='--')
                                    ax[ax_no].text(float(xlim[1])-(float(xlim[1])-float(xlim[0]))/50, length_embedment + (float(ylim[-1])-float(ylim[0]))/100, "Embedment length = " + str(round(length_embedment, 1)) + " m \n Average strength = " + str(round(su_ave_l, 1)) + " kPa", color='darkred', ha='right', va='top', fontsize=7)  
                                    ax[ax_no].plot([float(xlim[0]), float(xlim[1])], [length_embedment + alpha_d_su*foundation_b_outer, length_embedment + alpha_d_su*foundation_b_outer], color='darkblue', ls='--')
                                    ax[ax_no].plot([su_ave_end_bear, su_ave_end_bear], [length_embedment, length_embedment + alpha_d_su*foundation_b_outer], color='darkblue', ls='--')
                                    ax[ax_no].text(float(xlim[1])-(float(xlim[1])-float(xlim[0]))/50, length_embedment + alpha_d_su*foundation_b_outer + (float(ylim[-1])-float(ylim[0]))/100, "Plug bearing influence depth (" + str(round(alpha_d_su, 2)) + "*D) = " + str(round(length_embedment + alpha_d_su*foundation_b_outer, 1)) + " m \n Average strength = " + str(round(su_ave_end_bear, 1)) + " kPa", color='darkblue', ha='right', va='top', fontsize=7)  


            if 'manual_line' not in info_i:
                manual_line_list = []
            else:
                manual_line = [manual_line_i.strip() for manual_line_i in info_i['manual_line'].replace("; ", ";").split(";")]
                manual_line_list = [parse_manual(manual_line_i) for manual_line_i in manual_line]

            if 'manual_line_legend' not in info_i:
                manual_line_legend_list = []
            else:
                manual_line_legend_list = info_i['manual_line_legend'].replace("; ", ";").split(";")

            if 'manual_line_color' not in info_i:
                manual_line_color_list = []
            else:
                manual_line_color_list = info_i['manual_line_color'].replace(" ", "").split(";")

            if 'manual_line_style' not in info_i:
                manual_line_style_list = []
            else:
                manual_line_style_list = info_i['manual_line_style'].replace(" ", "").split(";")

            for manual_line_i, manual_line_legend_i, manual_line_color_i, manual_line_style_i in zip(manual_line_list, manual_line_legend_list, manual_line_color_list, manual_line_style_list):
                ax[ax_no].plot(manual_line_i[1], manual_line_i[0], color=manual_line_color_i, ls=manual_line_style_i, label=f"${manual_line_legend_i.replace(" ", "\\ ")}$")
                
            ax[ax_no].set_xlim([float(xlim[0]), float(xlim[-1])])
            ax[ax_no].set_ylim([float(ylim[-1]), float(ylim[0])])  
            ax[ax_no].set_xlabel(f"${ax_i.replace(" ", "\\ ")}$" + '\n(' + info_i['unit'] + ')') 

            ax[ax_no].grid('on')

            handles, labels = ax[ax_no].get_legend_handles_labels()
            handles_final = []
            labels_final = []

            for handle_i, label_i in zip(handles, labels):
                if label_i not in labels_final:
                    handles_final.append(handle_i)
                    labels_final.append(label_i)

            if info_i['legend'] and len(labels) > 0:
                ax[ax_no].legend(handles=handles_final, labels=labels_final, loc='upper right', fontsize=6)

            if 'vlines' in info_i or 'hlines' in info_i:

                keys = ['vlines', 'hlines', 'hlines_ex', 'vlines_ex', 'hlines_text', 'vlines_text']

                for key in keys:
                    if key not in info_i:
                        info_i[key] = [None]

                lists = {key: str(info_i[key]).replace(" ", "").split(";") if info_i[key] != [None] else info_i[key] for key in keys}

                list_length = max(len(lst) for lst in lists.values())
            
                for lst in lists.values():
                    lst.extend([None] * (list_length - len(lst)))

                vlines_i, hlines_i, hlines_ex_i, vlines_ex_i, hlines_text_i, vlines_text_i = [lists[k] for k in keys]

                for vline_ii, hline_ii, hline_ex_ii, vline_ex_ii, hline_text_ii, vline_text_ii in zip(vlines_i, hlines_i, hlines_ex_i, vlines_ex_i, hlines_text_i, vlines_text_i):

                    ### CLEAN 
                    if hline_ii == 'length_embedment':
                        hline_ii = float(length_embedment)
                    elif hline_ii == 'length_embedment_punch_through':
                        hline_ii = float(length_embedment_punch_through)
                    elif hline_ii == 'sw_depth':
                        hline_ii = float(sw_depth)

                    if vline_ii == 'sw_total':
                        vline_ii = float(sw_total)
                    elif vline_ii in output_i:
                        vline_ii = output_i[vline_ii]
                    else:
                        vline_ii = None

                    ### CLEAN 
                    
                    if vline_ii is not None and hline_ii is not None:
                        ax[ax_no].vlines(x=vline_ii, ymin=float(ylim[0]), ymax=hline_ii, color='purple', linestyle='dashed')
                        if vline_ex_ii is not None:
                            ax[ax_no].vlines(x=vline_ii, ymin=hline_ii, ymax=float(ylim[-1]), color='purple', linestyle='dashed', alpha=0.5)
                        if vline_text_ii is not None:
                            ax[ax_no].text(vline_ii, float(float(ylim[0])), '$' + vline_text_ii + ' ' + str(round(float(multiplier_i)*vline_ii, 2)) + ' ' + info_i['unit'] + '$', ha='left', va='bottom', color='purple')

                        ax[ax_no].hlines(y=hline_ii, xmin=float(info_i['limit'].split(",")[0]), xmax=vline_ii, color='purple', linestyle='dashed')
                        if hline_ex_ii is not None:
                            ax[ax_no].hlines(y=hline_ii, xmin=vline_ii, xmax=float(info_i['limit'].split(",")[-1]), color='purple', linestyle='dashed', alpha=0.5)
                        if hline_text_ii is not None:
                            ax[ax_no].text(float(info_i['limit'].split(",")[-1]), hline_ii, '$' + hline_text_ii + ' ' + str(round(hline_ii, 2)) + ' ' + axes['Depth']['unit'] + '$', ha='right', va='bottom', color='purple')

                    elif vline_ii is not None:
                        ax[ax_no].vlines(x=vline_ii, ymin=float(ylim[0]), ymax=float(ylim[-1]), color='purple', linestyle='dashed')
                        if vline_text_ii is not None:
                            ax[ax_no].text(vline_ii, float(ylim[0]), '$' + vline_text_ii + ' ' + str(round(float(multiplier_i)*vline_ii, 2)) + ' ' + info_i['unit'] + '$', ha='left', va='bottom', color='purple')

                    elif hline_ii is not None:
                        ax[ax_no].hlines(y=hline_ii, xmin=float(info_i['limit'].split(",")[0]), xmax=float(info_i['limit'].split(",")[-1]), color='purple', linestyle='dashed')
                        if hline_text_ii is not None:
                            ax[ax_no].text(float(info_i['limit'].split(",")[-1]), hline_ii, '$' + hline_text_ii + ' ' + str(round(hline_ii, 2)) + ' ' + axes['Depth']['unit'] + '$', ha='right', va='bottom', color='purple')

        # if calculation_name not in ['_cap_capacity', '_caisson_capacity']:
        #     try:
        #         sand_shaft = input['calculation_method_sand_shaft']
        #         sand_base = input['calculation_method_sand_base']
        #         clay_shaft = input['calculation_method_clay_shaft']
        #         clay_base = input['calculation_method_clay_base']
        #     except Exception:
        #         sand = input['calculation_method_sand']
        #         clay = input['calculation_method_clay']

        method_text_title = ''
        method_text_save = ''
        
        if input_heading is not None:
            method_text_title += ' (' + input_heading + ')'
            method_text_save += '_' + input_heading.lower()
        if foundation_b_outer is not None:
            method_text_title += ' (' + str(foundation_b_outer) + 'm)'
            method_text_save += '_' + str(foundation_b_outer)

        method_text_save += '_' + str(plot_i)
      
        # if calculation_name not in ['_cap_capacity', '_caisson_capacity']:
        #     try:
        #         extra_title = foundation_location_name + method_text_title + ' (Sand: ' + sand_shaft + '/' + sand_base + ', Clay: ' + clay_shaft + '/' + clay_base + ')'
        #     except Exception:
        #         extra_title = foundation_location_name + method_text_title + ' (Sand: ' + sand + ', Clay: ' + clay + ')'
        # else:
        #     extra_title = foundation_location_name + method_text_title

        save_file_name = foundation_location_name.lower() + method_text_save

        os.makedirs(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name, exist_ok=True)
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.svg'), bbox_inches='tight', pad_inches=0.1)

        # fig.suptitle(extra_title + '\n L = ' + str(round(length_embedment , 1)) + ' m')      
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.png'), bbox_inches='tight', pad_inches=0.1)

        plt.close()


def plot_caisson_output(input_heading, output_dict, setup_dict, calculation_name, foundation_location_name, output_folder='output'):

    length_embedment = 0
    for key in output_dict.keys():
        if key not in ['capacity_dict', 'url_info']:
            if 'length_embedment' in output_dict[key]['plot_output']:
                if output_dict[key]['plot_output']['length_embedment'] > length_embedment:
                    length_embedment = output_dict[key]['plot_output']['length_embedment']

    for calculation_method_i in output_dict.keys():

        if calculation_method_i in ['capacity_dict', 'url_info']:
            continue
        
        output_dict_output_i = output_dict[calculation_method_i]['plot_output']

        fos_results = pd.DataFrame(output_dict_output_i['fos_results'][0], columns=['ilc', 'icgeom', 'D', 'L', 'FOS', 'row', 'V', 'H', 'M', 'ilc'])
        FOS_caisson = fos_results['FOS'].iloc[0]
        H_design = fos_results['H'].iloc[0]
        M_design = fos_results['M'].iloc[0]
        V_design = fos_results['V'].iloc[0]

        hvm_results = pd.DataFrame(output_dict_output_i['hvm_results'][0], columns=['Hx', 'My', 'Vz', 'H*', 'M*', 'V*', 'it', 'iv', 'row'])

        if 'foundation_b_outer' in output_dict_output_i:
            foundation_b_outer = output_dict_output_i['foundation_b_outer']
        else:
            foundation_b_outer = None

        method_text_title = ''
        method_text_save = ''

        if input_heading is not None:
            method_text_title += ' (' + input_heading + ')'
            method_text_save += '_' + input_heading.lower()
        if foundation_b_outer is not None:
            method_text_title += ' (' + str(foundation_b_outer) + 'm)'
            method_text_save += '_' + str(foundation_b_outer)

        # extra_title = foundation_location_name + method_text_title
        os.makedirs(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name, exist_ok=True)
                
        load_dict = {0: {"x_val": "Hx",
                        "x_design": H_design,
                        "x_label": "H",
                        "x_unit": "kN",
                        "y_val": "Vz",
                        "y_design": V_design,
                        "y_label": "V",
                        "y_unit": "kN",
                        "z_val": "My",
                        "z_design": M_design,
                        "z_label": "M",
                        "z_unit": "kNm",
                        "z_interp": "iv",
                        "z_plot": "it"},
                    1:  {"x_val": "My",
                        "x_design": M_design,
                        "x_label": "M",
                        "x_unit": "kNm",
                        "y_val": "Vz",
                        "y_design": V_design,
                        "y_label": "V",
                        "y_unit": "kN",
                        "z_val": "Hx",
                        "z_design": H_design,
                        "z_label": "H",
                        "z_unit": "kN",
                        "z_interp": "iv",
                        "z_plot": "it"},
                    2:  {"x_val": "Hx",
                        "x_design": H_design,
                        "x_label": "H",
                        "x_unit": "kN",
                        "y_val": "My",
                        "y_design": M_design,
                        "y_label": "M",
                        "y_unit": "kNm",
                        "z_val": "Vz",
                        "z_design": V_design,
                        "z_label": "V",
                        "z_unit": "kN",
                        "z_interp": "it",
                        "z_plot": "iv"}}

        H_limit_array = [H_design]
        M_limit_array = [M_design]
        V_limit_array = [V_design]

        error = 1e10
        count = 0

        while error > 0.1 and count <= 10:

            for key, val in load_dict.items():

                x_val = val["x_val"]
                x_design = val["x_design"]
                y_val = val["y_val"]
                y_design = val["y_design"]
                z_val = val["z_val"]
                ii_interp = val["z_interp"]
                ii_interp_array = np.array(hvm_results[ii_interp].unique())
                    
                x_vals_lim_neg = []
                y_vals_lim_neg = []
                x_vals_lim_pos = []
                y_vals_lim_pos = []

                for ii in ii_interp_array:

                    x = np.array(hvm_results[x_val][(hvm_results[ii_interp] == ii)])
                    y = np.array(hvm_results[y_val][(hvm_results[ii_interp] == ii)])
                    z = np.array(hvm_results[z_val][(hvm_results[ii_interp] == ii)])

                    if z_val == 'Hx':
                        z_plot = H_limit_array[-1]
                    elif z_val == 'My':
                        z_plot = M_limit_array[-1]
                    elif z_val == 'Vz':
                        z_plot = V_limit_array[-1]
                
                    for idx, (z1i, z2i) in enumerate(zip(z, z[1:])):

                        if (z1i <= z_plot and z2i >= z_plot):
                            z_input = np.array([z[idx], z[idx+1]])
                            x_input = np.array([x[idx], x[idx+1]])
                            y_input = np.array([y[idx], y[idx+1]])

                            sort_z_indices = np.argsort(z_input)
                            z_sorted = z_input[sort_z_indices]
                            x_sorted = x_input[sort_z_indices]
                            y_sorted = y_input[sort_z_indices]

                            x_vals_lim_neg.append(np.interp(z_plot, z_sorted, x_sorted))
                            y_vals_lim_neg.append(np.interp(z_plot, z_sorted, y_sorted))

                        if (z1i >= z_plot and z2i <= z_plot):
                            z_input = np.array([z[idx], z[idx+1]])
                            x_input = np.array([x[idx], x[idx+1]])
                            y_input = np.array([y[idx], y[idx+1]])

                            sort_z_indices = np.argsort(z_input)
                            z_sorted = z_input[sort_z_indices]
                            x_sorted = x_input[sort_z_indices]
                            y_sorted = y_input[sort_z_indices]

                            x_vals_lim_pos.append(np.interp(z_plot, z_sorted, x_sorted))
                            y_vals_lim_pos.append(np.interp(z_plot, z_sorted, y_sorted))

                load_dict[key]["x_vals_lim_pos"] = x_vals_lim_pos
                load_dict[key]["x_vals_lim_neg"] = x_vals_lim_neg
                load_dict[key]["y_vals_lim_pos"] = y_vals_lim_pos
                load_dict[key]["y_vals_lim_neg"] = y_vals_lim_neg
                        
                m = y_design / x_design
                c = 0

                x_data_positive = np.array(x_vals_lim_pos)
                y_data_positive = np.array(y_vals_lim_pos)
                line = m * x_data_positive + c
                diff = y_data_positive - line
                idx = np.where(np.diff(np.sign(diff)))[0]
                x_int_positive = x_data_positive[idx] - diff[idx] * (x_data_positive[idx+1] - x_data_positive[idx]) / (diff[idx+1] - diff[idx])
                y_int_positive = m * x_int_positive + c

                if len(x_int_positive) > 0:
                    if key == 0:
                        H_limit_array.append(x_int_positive[0])
                        V_limit_array.append(y_int_positive[0])
                    elif key == 1:
                        M_limit_array.append(x_int_positive[0])
                        V_limit_array.append(y_int_positive[0])
                    elif key == 2:
                        H_limit_array.append(x_int_positive[0])
                        M_limit_array.append(y_int_positive[0])
                    
                x_data_negative = np.array(x_vals_lim_neg)
                y_data_negative = np.array(y_vals_lim_neg)
                line = m * x_data_negative + c
                diff = y_data_negative - line
                idx = np.where(np.diff(np.sign(diff)))[0]
                x_int_negative = x_data_negative[idx] - diff[idx] * (x_data_negative[idx+1] - x_data_negative[idx]) / (diff[idx+1] - diff[idx])
                y_int_negative = m * x_int_negative + c

                if len(x_int_negative) > 0:
                    if key == 0:
                        H_limit_array.append(x_int_negative[0])
                        V_limit_array.append(y_int_negative[0])
                    elif key == 1:
                        M_limit_array.append(x_int_negative[0])
                        V_limit_array.append(y_int_negative[0])
                    elif key == 2:
                        H_limit_array.append(x_int_negative[0])
                        M_limit_array.append(y_int_negative[0])

            error = np.sum(abs(H_limit_array[-2]-H_limit_array[-1]) + abs(M_limit_array[-2]-M_limit_array[-1]) + abs(V_limit_array[-2]-V_limit_array[-1]))
            count += 1

        SF_3d = np.sqrt(np.power(H_limit_array[-1], 2) + np.power(M_limit_array[-1], 2) + np.power(V_limit_array[-1], 2)) / np.sqrt(np.power(H_design, 2) + np.power(M_design, 2) + np.power(V_design, 2))

        fig, ax = plt.subplots(1, 3, figsize=(25, 14))

        for key, val in load_dict.items():

            x_val = val["x_val"]
            x_design = val["x_design"]
            x_label = val["x_label"]
            x_unit = val["x_unit"]
            y_val = val["y_val"]
            y_design = val["y_design"]
            y_label = val["y_label"]
            y_unit = val["y_unit"]
            z_val = val["z_val"]
            z_label = val["z_label"]

            x_vals_lim_pos = load_dict[key]["x_vals_lim_pos"]
            x_vals_lim_neg = load_dict[key]["x_vals_lim_neg"]
            y_vals_lim_pos = load_dict[key]["y_vals_lim_pos"]
            y_vals_lim_neg = load_dict[key]["y_vals_lim_neg"]

            ii_plot = val["z_plot"]
            ii_plot_array = np.array(hvm_results[ii_plot].unique())

            for ii in ii_plot_array:
                x = np.array(hvm_results[x_val][(hvm_results[ii_plot] == ii)])
                y = np.array(hvm_results[y_val][(hvm_results[ii_plot] == ii)])
                z = np.array(hvm_results[z_val][(hvm_results[ii_plot] == ii)])
                ax[key].plot(x, y, linestyle='-', alpha=0.5, color='darkgrey')

            if key == 0:
                x_limit = H_limit_array[-1]
                y_limit = V_limit_array[-1]
                z_limit = M_limit_array[-1]
                
            elif key == 1:
                x_limit = M_limit_array[-1]
                y_limit = V_limit_array[-1]
                z_limit = H_limit_array[-1]

            elif key == 2:
                x_limit = H_limit_array[-1]
                y_limit = M_limit_array[-1]
                z_limit = V_limit_array[-1]
                            
            ax[key].plot(x_vals_lim_neg, y_vals_lim_neg, linestyle='--', color='k')
            ax[key].plot(x_vals_lim_pos, y_vals_lim_pos, linestyle='--', color='k', label=z_label + "$_{lim}$ = " + str(int(z_limit)) + " kN")

            ax[key].plot([0, x_design], [0, y_design], color='b', ls='-', label="Design load combination")
            ax[key].plot([x_design, x_limit], [y_design, y_limit], color='r', ls='--', label="Load combination limit")
            ax[key].plot([x_design], [y_design], marker='o', markersize=6, color='b')
            ax[key].plot([x_limit], [y_limit], marker='o', markersize=6, color='r')
            ax[key].text(x_design, y_design, "  Design loads: \n  " + str(x_label) + "$_{d}$ = " + str(int(x_design)) + " " + x_unit + "\n  " + str(y_label) + "$_{d}$ = " + str(int(y_design)) + " " + y_unit + "\n  SF = " + str(round(SF_3d, 2)), color='b', fontsize=6, ha='left', va='center')
            ax[key].text(x_limit, y_limit, "  Envelope limit: \n  " + str(x_label) + "$_{lim}$ = " + str(int(x_limit)) + " " + x_unit + "\n  " + str(y_label) + "$_{lim}$ = " + str(int(y_limit)) + " " + y_unit, color='r', fontsize=6, ha='left', va='center')

            ax[key].set_xlabel(f"${x_label.replace(" ", "\\ ")}$" + ' (' + x_unit + ')')
            ax[key].set_ylabel(f"${y_label.replace(" ", "\\ ")}$" + ' (' + y_unit + ')')
            
            ax[key].grid('on')

            ax[key].legend(loc="upper right", fontsize=6)

        
        save_file_name = foundation_location_name.lower() + method_text_save + '_HVM_red'
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.svg'), bbox_inches='tight', pad_inches=0.1)

        # fig.suptitle(extra_title + '\n L = ' + str(round(length_embedment , 1)) + ' m')
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.png'), bbox_inches='tight', pad_inches=0.1)
        plt.close()
                                
        fig = plt.figure(figsize=(15, 15))

        Hx = hvm_results['Hx'].values
        My = hvm_results['My'].values
        Vz = hvm_results['Vz'].values

        grid_hx, grid_my = np.mgrid[Hx.min():Hx.max():500j, My.min():My.max():500j]
        grid_vz = griddata((Hx, My), Vz, (grid_hx, grid_my), method='linear')
        grid_vz = np.nan_to_num(grid_vz, nan=0)
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(grid_hx, grid_my, grid_vz, rstride=9, cstride=9, alpha=0.3, color='darkgrey', label='Envelope limit')

        ax.set_zlim(bottom=0)
        ax.set_xlabel(f"$H$ (kN)")
        ax.set_ylabel(f"$M$ (kNm)")
        ax.set_zlabel(f"$V$ (kN)")
        plt.tight_layout()

        ax.plot([0, H_design], [0, M_design], [0, V_design], color='b', ls='-', label="Design load combination")
        ax.plot(H_design, M_design, V_design, color='b', marker='o')
        ax.text(H_design, M_design, V_design, "  Design loads: \n  H$_{d}$ = " + str(int(H_design)) + " kN\n  M$_{d}$ = " + str(int(M_design)) + " kNm\n  V$_{d}$ = " + str(int(V_design)) + " kN\n  SF = " + str(round(SF_3d, 2)), color='b', fontsize=6, ha='left', va='center')
        ax.plot([H_design, H_limit_array[-1]], [M_design, M_limit_array[-1]], [V_design, V_limit_array[-1]], color='r', ls='--', label="Load combination limit")
        ax.plot(H_limit_array[-1], M_limit_array[-1], V_limit_array[-1], color='r', marker='o')
        ax.text(H_limit_array[-1], M_limit_array[-1], V_limit_array[-1], "  Envelope limit: \n  H$_{lim}$ = " + str(int(H_limit_array[-1])) + " kN\n  M$_{lim}$ = " + str(int(M_limit_array[-1])) + " kNm\n  V$_{lim}$ = " + str(int(V_limit_array[-1])) + " kN", color='r', fontsize=6, ha='left', va='center')

        ax.legend(loc="upper right", fontsize=6)
        
        save_file_name = foundation_location_name.lower() + method_text_save + '_HVM'
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name+'.svg'), bbox_inches='tight', pad_inches=0.1)

        # fig.suptitle(extra_title + '\n L = ' + str(round(length_embedment , 1)) + ' m')
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name+'.png'), bbox_inches='tight', pad_inches=0.1)
        plt.close()


def plot_spring_output(input_heading, output_dict, setup_dict, calculation_name, foundation_location_name, output_folder='output', no_rows=2, no_cols=3, kN=True):

    length_embedment = 0
    for key in output_dict.keys():
        if key not in ['capacity_dict']:
            if 'length_embedment' in output_dict[key]['plot_output']:
                if output_dict[key]['plot_output']['length_embedment'] > length_embedment:
                    length_embedment = output_dict[key]['plot_output']['length_embedment']

    for calculation_method_i in output_dict.keys():

        if calculation_method_i in ['capacity_dict', 'url_info']:
            continue
        
        output_dict_output_i = output_dict[calculation_method_i]['plot_output']
        max_load = 0
        for key in output_dict_output_i:
            try:
                max_load = max(max_load, key)
            except Exception:
                continue

        x_background = output_dict_output_i[max_load]['x_background']
        y_background = output_dict_output_i[max_load]['y_background']
        z_background = output_dict_output_i[max_load]['z']
        
        spring_depth_intervals = setup_dict[calculation_name][input_heading]['spring_depths_to_plot_individual']
        spring_depth_intervals_combined = setup_dict[calculation_name][input_heading]['spring_depths_to_plot_combined']

        if '[' in str(spring_depth_intervals):
            spring_depth_intervals = spring_depth_intervals.strip()[1:-1].split(',')
            spring_depth_intervals = [float(v) for v in spring_depth_intervals]
        else:
            spring_depth_intervals = np.arange(0, length_embedment+spring_depth_intervals, spring_depth_intervals)

        if '[' in str(spring_depth_intervals_combined):
            spring_depth_intervals_combined = spring_depth_intervals_combined.strip()[1:-1].split(',')
            spring_depth_intervals_combined = [float(v) for v in spring_depth_intervals_combined]
        else:
            spring_depth_intervals_combined = np.arange(0, length_embedment+spring_depth_intervals_combined, spring_depth_intervals_combined)

        xlim = setup_dict[calculation_name][input_heading]['spring_x_limit'].replace(" ", "").split(",")

        if calculation_name == '_lateral_displacement':
            base_spring = False
            x_calc = output_dict_output_i[max_load]['y_calc']            
            
        elif calculation_name == '_axial_displacement':
            x_calc = output_dict_output_i[max_load]['z_calc']
            if setup_dict[calculation_name][input_heading]['calculation_method'] == 'free_tip':
                base_spring = False
            elif setup_dict[calculation_name][input_heading]['calculation_method'] == 'q_z_tip':
                base_spring = True
                    
        max_y = 0
        max_y_main = 0

        if kN:
            y_mult = 1000
            unit = 'kN'
        else:
            y_mult = 1
            unit = 'MN'

        for spring_depth_interval_i in spring_depth_intervals:
            idx_diff = np.abs(z_background - spring_depth_interval_i)
            idx_depth = np.argmin(idx_diff)
            y_data = y_background[idx_depth]
            max_y = max(max_y, y_mult*max(y_data))

        for spring_depth_interval_i in spring_depth_intervals_combined:
            idx_diff = np.abs(z_background - spring_depth_interval_i)
            idx_depth = np.argmin(idx_diff)
            y_data = y_background[idx_depth]
            max_y_main = max(max_y_main, y_mult*max(y_data))

        fig_main, ax_main = plt.subplots(1, 2, figsize=(22, 12))

        if base_spring:
            no_plots = int(np.ceil((len(spring_depth_intervals)+1) / (no_rows*no_cols)))
        else:
            no_plots = int(np.ceil((len(spring_depth_intervals)) / (no_rows*no_cols)))

        count_spring = 0

        for idx_fig in range(no_plots):

            fig, ax = plt.subplots(no_rows, no_cols, figsize=(22, 12))
            ax = ax.flatten()
            plt.subplots_adjust(wspace=0.1)
         
            for idx_ax, spring_depth_interval_i in enumerate(spring_depth_intervals[:(no_rows*no_cols)]):

                x_data = x_background

                idx_diff = np.abs(z_background - spring_depth_interval_i)
                idx_depth = np.argmin(idx_diff)
                depth_extract = z_background[idx_depth]
                y_data = y_background[idx_depth]

                x_limit_mob = abs(x_calc[idx_depth])

                ax[idx_ax].plot(x_data, [y_mult*y_i for y_i in y_data], ls='--', color='darkblue', label="Background curve")
                ax[idx_ax].plot([abs(x_i) for x_i in x_data if x_i <= x_limit_mob], [y_mult*abs(y_i) for x_i, y_i in zip(x_data, y_data) if x_i <= x_limit_mob], ls='-', color='darkblue', label="Mobilised at design load")
                
                if spring_depth_interval_i in spring_depth_intervals_combined:
                    if count_spring == 0:
                        ax_main[0].plot(x_data, [y_mult*y_i for y_i in y_data], ls='--', color='darkblue', label="Background curve")
                        ax_main[0].plot([abs(x_i) for x_i in x_data if x_i <= x_limit_mob], [y_mult*abs(y_i) for x_i, y_i in zip(x_data, y_data) if x_i <= x_limit_mob], ls='-', color='darkblue', label="Mobilised at design load")
                    else:
                        ax_main[0].plot(x_data, [y_mult*y_i for y_i in y_data], ls='--', color='darkblue')
                        ax_main[0].plot([abs(x_i) for x_i in x_data if x_i <= x_limit_mob], [y_mult*abs(y_i) for x_i, y_i in zip(x_data, y_data) if x_i <= x_limit_mob], ls='-', color='darkblue')
                    ax_main[0].text(float(xlim[-1]), y_mult*y_data[np.abs(np.array(x_data) - float(xlim[-1])).argmin()], str(round(depth_extract, 1))+" m", ha='right', va='bottom')
                    count_spring += 1

                ax[idx_ax].grid('on')
                ax_main[0].grid('on')

                ax[idx_ax].legend(loc='upper right', fontsize=6)
                if spring_depth_interval_i in spring_depth_intervals_combined:
                    ax_main[0].legend(loc='upper right', fontsize=6)

                ax[idx_ax].set_xlim([float(xlim[0]), float(xlim[-1])])
                ax[idx_ax].set_ylim(0, 1.05*max_y)

                ax_main[0].set_xlim([float(xlim[0]), float(xlim[-1])])
                ax_main[0].set_ylim(0, 1.05*max_y_main)
                                                
                if calculation_name == '_lateral_displacement':
                    ax[idx_ax].set_xlabel(f"$Displacement,\\ y$ (m)")
                    ax[idx_ax].text(0.05*(float(xlim[-1])-float(xlim[0])), 0.95*1.05*max_y, "p-y curve at " + str(round(depth_extract, 1))+" m", ha='left', va='top')
                    if idx_ax % no_cols == 0:
                        ax[idx_ax].set_ylabel(f"$SLateral\\ resistance,\n p$ (" + unit +"/m)")

                    ax_main[0].set_xlabel(f"$Displacement,\\ y$ (m)")
                    ax_main[0].set_ylabel(f"$SLateral\\ resistance,\n p$ (" + unit +"/m)")

                elif calculation_name == '_axial_displacement':
                    ax[idx_ax].set_xlabel(f"$Displacement,\\ z$ (m)")
                    ax[idx_ax].text(0.05*(float(xlim[-1])-float(xlim[0])), 0.95*1.05*max_y, "t-z curve at " + str(round(depth_extract, 1))+" m", ha='left', va='top')
                    if idx_ax % no_cols == 0:
                        ax[idx_ax].set_ylabel(f"$Shaft\\ axial\\ resistance,\n t$ (" + unit +"/m)")
                    
                    ax_main[0].set_xlabel(f"$Displacement,\\ z$ (m)")
                    ax_main[0].set_ylabel(f"$Shaft\\ axial\\ resistance,\n t$ (" + unit +"/m)")
                
            if calculation_name == '_axial_displacement' and base_spring:

                x_data = x_background
                y_data = y_background[-1]

                x_limit_mob = abs(x_calc[idx_depth])

                if idx_fig == 0:
                    ax_main[1].plot(x_data, [y_mult*y_i for y_i in y_data], ls='--', color='darkblue', label="Background curve")
                    ax_main[1].plot([abs(x_i) for x_i in x_data if x_i <= x_limit_mob], [y_mult*abs(y_i) for x_i, y_i in zip(x_data, y_data) if x_i <= x_limit_mob], ls='-', color='darkblue', label="Mobilised at design load")
                    
                    ax_main[1].grid('on')
                    ax_main[1].legend(loc='upper right', fontsize=6)

                    ax_main[1].set_xlim([float(xlim[0]), float(xlim[-1])])
                    ax_main[1].set_ylim(bottom=0)

                    ax_main[1].set_xlabel(f"$Displacement,\\ z$ (m)")
                    ax_main[1].set_ylabel(f"$Base\\ axial\\ resistance,\n Q$ (" + unit +")")
                    ax_main[1].text(x_data[-1], [y_mult*y_i for y_i in y_data][-1], str(round(z_background[-1], 1))+" m", ha='left', va='top')

                if idx_ax < (no_rows*no_cols) - 1:

                    ax[idx_ax+1].plot(x_data, [y_mult*y_i for y_i in y_data], ls='--', color='darkblue', label="Background curve")
                    ax[idx_ax+1].plot([abs(x_i) for x_i in x_data if x_i <= x_limit_mob], [y_mult*abs(y_i) for x_i, y_i in zip(x_data, y_data) if x_i <= x_limit_mob], ls='-', color='darkblue', label="Mobilised at design load")

                    ax[idx_ax+1].grid('on')
                    
                    ax[idx_ax+1].legend(loc='upper right', fontsize=6)
                    
                    ax[idx_ax+1].set_xlim([float(xlim[0]), float(xlim[-1])])
                    ax[idx_ax+1].set_ylim(bottom=0)
                    _, max_y = ax[idx_ax+1].get_ylim()
                                                    
                    ax[idx_ax+1].set_xlabel(f"$Displacement,\\ z$ (m)")
                    ax[idx_ax+1].set_ylabel(f"$Base\\ axial\\ resistance,\n Q$ (" + unit +")")
                    ax[idx_ax+1].text(0.05*(float(xlim[-1])-float(xlim[0])), 0.95*max_y, "Q-z curve at " + str(round(z_background[-1], 1))+" m", ha='left', va='top')

                    ax[idx_ax+1].yaxis.tick_right()
                    ax[idx_ax+1].yaxis.set_label_position("right")

                    for idx_ax2 in range(idx_ax+2, (no_rows*no_cols)):
                        ax[idx_ax2].set_axis_off()

                elif len(spring_depth_intervals) == 0:

                    ax[0].plot(x_data, [y_mult*y_i for y_i in y_data], ls='--', color='darkblue', label="Background curve")
                    ax[0].plot([abs(x_i) for x_i in x_data if x_i <= x_limit_mob], [y_mult*abs(y_i) for x_i, y_i in zip(x_data, y_data) if x_i <= x_limit_mob], ls='-', color='darkblue', label="Mobilised at design load")

                    ax[0].grid('on')

                    ax[0].legend(loc='upper right', fontsize=6)

                    ax[0].set_xlim([float(xlim[0]), float(xlim[-1])])
                    ax[0].set_ylim(bottom=0)
                    _, max_y = ax[0].get_ylim()
                                                    
                    ax[0].set_xlabel(f"$Displacement,\\ z$ (m)")
                    ax[0].set_ylabel(f"$Base\\ axial\\ resistance,\n Q$ (" + unit +")")
                    ax[0].text(0.05*(float(xlim[-1])-float(xlim[0])), 0.95*max_y, "Q-z curve at " + str(round(z_background[-1], 1))+" m", ha='left', va='top')

                    for idx_ax2 in range(1, (no_rows*no_cols)):
                        ax[idx_ax2].set_axis_off()

            else:

                if idx_ax < (no_rows*no_cols) - 1:

                    for idx_ax2 in range(idx_ax+1, (no_rows*no_cols)):
                        ax[idx_ax2].set_axis_off()

            spring_depth_intervals = spring_depth_intervals[(no_rows*no_cols):]

            # extra_title = foundation_location_name + ' (' + input_heading + ')'
            save_file_name = foundation_location_name.lower() + '_' + input_heading.lower() + '_' + calculation_method_i + '_springs' + str(idx_fig)

            os.makedirs(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name, exist_ok=True)
            fig.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.svg'), bbox_inches='tight', pad_inches=0.1)
            
            # fig.suptitle(extra_title + '\n L = ' + str(round(length_embedment , 1)) + ' m')      
            fig.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name+'.png'), bbox_inches='tight', pad_inches=0.1)

            # extra_title = foundation_location_name + ' (' + input_heading + ')'
            save_file_name = foundation_location_name.lower() + '_' + input_heading.lower() + '_' + calculation_method_i + '_all_springs'

            os.makedirs(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name, exist_ok=True)
            fig_main.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.svg'), bbox_inches='tight', pad_inches=0.1)
            
            # fig_main.suptitle(extra_title + '\n L = ' + str(round(length_embedment , 1)) + ' m')      
            fig_main.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name+'.png'), bbox_inches='tight', pad_inches=0.1)

            plt.close(fig)
            plt.close(fig_main)


def plot_global_spring_output(input_heading, output_dict, setup_dict, calculation_name, foundation_location_name, output_folder='output'):

    colors_calculation_method = ['darkblue', 'darkred', 'darkgreen', 'grey', 'grey', 'grey', 'grey', 'grey']

    length_embedment = 0
    for key in output_dict.keys():
        if key not in ['capacity_dict']:
            if 'length_embedment' in output_dict[key]['plot_output']:
                if output_dict[key]['plot_output']['length_embedment'] > length_embedment:
                    length_embedment = output_dict[key]['plot_output']['length_embedment']

    for calculation_method_i in output_dict.keys():

        if calculation_method_i in ['capacity_dict', 'url_info']:
            continue
        
        output_dict_output_i = output_dict[calculation_method_i]['plot_output']

        spring_depth_intervals = setup_dict[calculation_name][input_heading]['global_spring_depth_to_plot']

        if '[' in str(spring_depth_intervals):
            spring_depth_intervals = spring_depth_intervals.strip()[1:-1].split(',')
        else:
            spring_depth_intervals = np.arange(0, length_embedment+spring_depth_intervals, spring_depth_intervals)

        if calculation_name == '_lateral_displacement':
            no_sub_plots = 3
        
        elif calculation_name == '_axial_displacement':
            no_sub_plots = 2
        
        fig, ax = plt.subplots(1, no_sub_plots, figsize=(22, 12))
        ax = ax.flatten()
        plt.subplots_adjust(wspace=0.1)

        param_array = []

        design_load = output_dict_output_i['design_load']
        output_dict_array = []

        for key, val in output_dict_output_i.items():
            if isinstance(key, np.float64):
                output_dict_array.append([key, val])

        for idx, output_dict_i in enumerate(output_dict_array):

            if calculation_name == '_lateral_displacement':

                plot_load = output_dict_i[0]
                output_dict = output_dict_i[1]

                if plot_load == design_load:
                    alpha_i = 1
                else:
                    alpha_i = 0.25

                if idx == 0:
                    legend_toggle = True        
                    legend_i = 'M'        
                else:
                    if plot_load == design_load:
                        legend_toggle = True
                        legend_i = 'M (design load)'
                    else:
                        legend_toggle = False

                param_name = 'M'
                depth = output_dict['z']
                param = output_dict[param_name]
                max_param = min(param)
                max_param_depth = depth[np.argmin(param)]
                
                param_array.append([max_param_depth, max_param])

                if legend_toggle:   
                    ax[0].plot(param, depth, ls='-', color='darkblue', alpha=alpha_i, label=f"${legend_i.replace(' ', '\\ ')}$")
                else:
                    ax[0].plot(param, depth, ls='-', color='darkblue', alpha=alpha_i)

        if calculation_name == '_lateral_displacement':

            ax[0].plot([param_i[1] for param_i in param_array[1:]], [param_i[0] for param_i in param_array[1:]], ls='--', color='red', label='Depth to maximum moment')
            ax[0].text(1.02*param_array[-1][1], param_array[-1][0], str(round(param_array[-1][0], 1)) + ' m', ha='right', va='center', fontsize=6, color='red')

            ax[0].grid('on')
            ax[0].legend(loc='upper right', fontsize=6)

            plots_for_input = setup_dict[calculation_name][input_heading]['plot'].replace(" ", "").split(";")

            for plot_i in setup_dict['plotting']:

                if plot_i not in plots_for_input:
                    continue

                axes = copy.deepcopy(setup_dict['plotting'][plot_i])

                if any(param_name in [p.strip() for p in sub.get("params", "").split(";")]for sub in axes.values()):
                    moment_axis = {param_name: sub for key, sub in axes.items() if param_name in [p.strip() for p in sub.get("params", "").split(";")]}
                    xlim = moment_axis[param_name]['limit'].replace(" ", "").split(",")
                    ax[0].set_xlim([float(xlim[0]), float(xlim[-1])])

                ylim = axes['Depth']['limit'].replace(" ", "").split(",")

                ax[0].set_ylim([float(ylim[-1]), float(ylim[0])])  
                ax[0].set_xlabel(f"$Moment$\n(MNm)")
                ax[0].set_ylabel(f"$Depth\\ from\\ mudline$ (m)")

        max_disp = 0

        for idx, spring_depth_interval_i in enumerate(spring_depth_intervals):

            load_array = []
            displacement_array = []
            secant_stiffness_array = []
            tangent_stiffness_array = []
            
            for key in output_dict_output_i:

                if key in ['length_embedment', 'design_load']:
                    continue

                if calculation_name == '_lateral_displacement':
                    x_calc = output_dict_output_i[key]['y_calc']
                
                elif calculation_name == '_axial_displacement':
                    x_calc = output_dict_output_i[key]['z_calc']

                load_array.append(key)

                depth = output_dict_output_i[key]['z']

                if calculation_name == '_lateral_displacement' and 'max_moment' in str(spring_depth_interval_i):
                    spring_depth_interval_i = param_array[-1][0]
                else:
                    spring_depth_interval_i = float(spring_depth_interval_i)

                idx_diff = np.abs(depth - spring_depth_interval_i)
                idx_depth = np.argmin(idx_diff)
                
                displacement_array.append(x_calc[idx_depth])

                if len(displacement_array) > 1:
                    secant_stiffness_array.append(abs((load_array[-1] - load_array[0])/(displacement_array[-1] - displacement_array[0])))
                    tangent_stiffness_array.append(abs((load_array[-1] - load_array[-2])/(displacement_array[-1] - displacement_array[-2])))

            color_i = colors_calculation_method[idx]

            ax[-2].plot(displacement_array, load_array, ls='-', color=color_i, label="Load-displacement at depth " + str(round(spring_depth_interval_i, 1)) + ' m')
            
            ax[-1].plot(displacement_array[1:], secant_stiffness_array, ls='-', color=color_i, label="Secant stiffness at depth " + str(round(spring_depth_interval_i, 1)) + ' m')
            ax[-1].plot(displacement_array[1:], tangent_stiffness_array, ls='--', color=color_i, label="Tangent stiffness at depth " + str(round(spring_depth_interval_i, 1)) + ' m')

            max_disp = max(max_disp, max(displacement_array))
        
        ax[-2].plot([0, max_disp], [design_load, design_load], ls='--', color='r', label="Design load")

        ax[-2].grid('on')
        ax[-2].legend(loc='upper right', fontsize=6)
        ax[-2].set_ylim(bottom=0)
        ax[-2].set_xlim(left=0)

        ax[-1].grid('on')
        ax[-1].legend(loc='upper right', fontsize=6)
        ax[-1].set_yscale('log')
        ax[-1].set_xlim(left=0)
                                        
        if calculation_name == '_lateral_displacement':
            ax[-2].set_xlabel(f"$Displacement,\\ y$ (m)")
            ax[-1].set_xlabel(f"$Displacement,\\ y$ (m)")
            ax[-2].set_ylabel(f"$Lateral\\ load,\\ H$ (MN)")
            ax[-1].set_ylabel(f"$Lateral\\ stiffness,\\ K_h$ (MN/m)")
        elif calculation_name == '_axial_displacement':
            ax[-2].set_xlabel(f"$Displacement,\\ z$ (m)")
            ax[-1].set_xlabel(f"$Displacement,\\ z$ (m)")
            ax[-2].set_ylabel(f"$Axial\\ load,\\ V$ (MN)")
            ax[-1].set_ylabel(f"$Axial\\ stiffness,\\ K_v$ (MN/m)")
                    
        # extra_title = foundation_location_name + ' (' + input_heading + ')'
        save_file_name = foundation_location_name.lower() + '_' + input_heading.lower() + '_' + calculation_method_i + '_global_spring'

        os.makedirs(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name, exist_ok=True)
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.svg'), bbox_inches='tight', pad_inches=0.1)
        
        # fig.suptitle(extra_title + '\n L = ' + str(round(length_embedment , 1)) + ' m')      
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name+'.png'), bbox_inches='tight', pad_inches=0.1)

        plt.close()



def plot_stress_fatigue(input_heading, output_dict, setup_dict, calculation_name, foundation_location_name, output_folder='output'):

    length_embedment = 0
    for key in output_dict.keys():
        if key not in ['capacity_dict']:
            if 'length_embedment' in output_dict[key]['plot_output']:
                if output_dict[key]['plot_output']['length_embedment'] > length_embedment:
                    length_embedment = output_dict[key]['plot_output']['length_embedment']

    foundation = setup_dict[calculation_name][input_heading]['foundation']
    stick_up = 0

    for section_i, data_i in setup_dict['sections_input'][foundation].items():
        if data_i['z1_from_soil_surface'] < stick_up:
            stick_up = data_i['z1_from_soil_surface']

    stick_up = abs(stick_up)

    for calculation_method_i in output_dict.keys():

        if calculation_method_i in ['capacity_dict', 'url_info']:
            continue
        
        output_dict_output_i = output_dict[calculation_method_i]['stress_fatigue_dict']

        penetration_depth_array = next(iter(output_dict_output_i.values()))['penetration_depth']
        stress_depth_array = output_dict_output_i.keys()
        t_max = [[] for i in penetration_depth_array]
        c_max = [[] for i in penetration_depth_array]
        fatigue_damage = []

        for stress_depth_i in output_dict_output_i.keys():
            stress_dict_i = output_dict_output_i[stress_depth_i]

            for idx, depth_i in enumerate(penetration_depth_array):
                t_max[idx].append(stress_dict_i['t_max'][idx])
                c_max[idx].append(stress_dict_i['c_max'][idx])
            
            fatigue_damage.append(stress_dict_i['acc_damage'])

        no_axes = 3
        
        fig, ax = plt.subplots(1, no_axes, figsize=(22, 12))
        ax = ax.flatten()
        plt.subplots_adjust(wspace=0.1)

        for t_max_i in t_max:
            ax[0].plot(t_max_i, stress_depth_array, ls='-', color='darkblue', alpha=1)
        
        for c_max_i in c_max:
            ax[1].plot(c_max_i, stress_depth_array, ls='-', color='darkblue', alpha=1)

        ax[2].plot(fatigue_damage, stress_depth_array, ls='-', color='darkblue', alpha=1)
        ax[2].plot([0.1, 0.1], [0, length_embedment+stick_up], ls='--', color='red', alpha=1)

        for ax_idx in range(no_axes):
            ax[ax_idx].grid('on')
            ax[ax_idx].set_xlim(left=0)
            ax[ax_idx].set_ylim([length_embedment + stick_up, 0])

        ax[2].set_xlim([0, 0.15])
                                        
        ax[0].set_xlabel(f"$Maximum\\ tension\\ stress$ (MPa)")
        ax[1].set_xlabel(f"$Maximum\\ compression\\ stress$ (MPa)")
        ax[2].set_xlabel(f"$Fatigue\\ damage$ (-)")

        ax[0].set_ylabel(f"$Length\\ of\\ pile$ (m)")
        ax[1].set_yticklabels([])
        ax[2].set_yticklabels([])
        
        save_file_name = foundation_location_name.lower() + '_' + input_heading.lower() + '_fatigue_damage'

        os.makedirs(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name, exist_ok=True)
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name + '.svg'), bbox_inches='tight', pad_inches=0.1)
          
        plt.savefig(Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(save_file_name+'.png'), bbox_inches='tight', pad_inches=0.1)

        plt.close()