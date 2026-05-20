# python modules
import copy
import numpy as np
import pandas as pd
import os
from pathlib import Path
import re
import shutil

# multiconsult modules
import _background_pdf as pdf


def extract_dict_inc(data, threshold, type):

    extracted = {}

    for data_i in data:

        for key_i in data_i.keys():
            
            if type == "shaft":
                z_inc_name = 'z_s_section'

            elif type == "base":
                z_inc_name = 'z_b_section'

            elif type == "plug_bearing_base":
                z_inc_name = 'z_pb_section'

            elif type == "plug_bearing_shaft":
                z_inc_name = 'z_ps_section'
            
            elif type == "p_ult":
                z_inc_name = 'z_section'

            elif type == "springs":
                z_inc_name = 'z_section'

            elif type == "grl":
                z_inc_name = 'z_grl_section'

            else:
                z_inc_name = 'z'

            if z_inc_name in key_i:

                z_inc = data_i[key_i]

                if z_inc <= threshold:
                    extracted[z_inc] = data_i

    return extracted


def split_col(col):
                
        match = re.match(r"(.*?)\[(.*?)\]", str(col))
        
        if match:
            return match.group(1), match.group(2)
        
        return col, ""


def col_with_blanks(col_idx, blank_after):
        
        return col_idx + sum(col_idx > b for b in blank_after)


def custom_sort_key(col, param_priority, method_priority):

    param, method = col

    try:
        method = float(method)
    except Exception:
        method = method

    param_pri = param_priority.get(param, 999)

    method_pri = method_priority.get(method, 999)

    method_alpha = method

    param_alpha = param

    return (param_pri, method_pri, method_alpha, param_alpha)


def export_param_method_pdf(df, table_info, calc_symbol_info, parameter_symbol_info, setup_dict, calculation_name, save_file_name, output_folder, method_order, parameter_first=("z")):

    info_pdf = {}
    info_pdf['orientation'] = 'landscape'
    info_pdf['main_title'] = table_info["main_title"]

    if table_info["table_type"] == 'summary':
        extra_title1 = ' (Summary output)'
        extra_save = '_summary'
    elif table_info["table_type"] == 'interval':
        extra_title1 = ' (Detailed input at embedment depth, z = ' + str(round(table_info["table_limit"], 1)) + ')'
        extra_save = '_z_' + str(round(table_info["table_limit"], 1))

    info_pdf['sub_title1'] = table_info.get("sub_title1", "") + extra_title1
    info_pdf['sub_title2'] = table_info.get("sub_title2", "")
    info_pdf['sub_title3'] = table_info.get("sub_title3", "")

    if info_pdf['sub_title3'].lower() == "input":
        info_pdf['sub_title3'] = info_pdf['sub_title3'].strip()

    info_pdf['doc_no'] = table_info.get("doc_no", "")

    if table_info["fig_no"].lower() == "input":
        info_pdf['table_no'] = table_info["fig_no_i"].strip()
    else:
        info_pdf['table_no'] = table_info["fig_no"]

    info_pdf['calc_by'] = table_info["calc_by"]
    info_pdf['check_by'] = table_info["check_by"]
    info_pdf['approv_by'] = table_info["approv_by"]
    info_pdf['table_type'] = table_info["table_type"]
    
    info_pdf['table_limit'] = table_info["table_limit"]

    info_pdf['pdf_directory'] = Path(setup_dict["parent_input"]["calculations_location"])/setup_dict["parent_input"]["python_calculation_folder"]/setup_dict["parent_input"]["foundation_calculation_folder"]/output_folder/calculation_name/(str(info_pdf['table_no']) + '_' + save_file_name.split('.xlsx')[0] + extra_save + '_' + table_info["table_i"] + '.pdf')
    
    pdf.save_table_pdf(info_pdf, df, calc_symbol_info, parameter_symbol_info, method_order, parameter_first)


def export_param_method_excel(df, writer, sheet_name, method_order, parameter_first=("z")):

    pairs = [split_col(c) for c in df.columns]
    df = df.apply(lambda col: col.explode()).reset_index(drop=True)

    df.columns = pd.MultiIndex.from_tuples(pairs)

    param_priority  = {p: i for i, p in enumerate(parameter_first)}
    method_priority = {m: i for i, m in enumerate(method_order)}
    sorted_cols = sorted(df.columns, key=lambda c: custom_sort_key(c, param_priority, method_priority))
    df = df[sorted_cols]

    target_groups = ["input", "calc_b", "calc_s", "calc_pb", "calc_ps", "calc", "output"]
    last_idx = {g: None for g in target_groups}

    for i, (param, method) in enumerate(df.columns):
        if method in last_idx:
            last_idx[method] = i

    inserts = sorted(idx for idx in last_idx.values() if idx is not None)

    workbook = writer.book
    worksheet = workbook.add_worksheet(sheet_name)
    writer.sheets[sheet_name] = worksheet

    header_format = workbook.add_format({"bold": True,
                                         "border": 1,
                                         "align": "center",
                                         "valign": "vcenter"})

    for col_idx, (param, method) in enumerate(df.columns):
        write_idx = col_with_blanks(col_idx, inserts)
        worksheet.write(0, write_idx, param, header_format)

    for ins in inserts:
        blank_idx = ins + 1 + sum(ins > earlier for earlier in inserts)
        worksheet.write(0, blank_idx, "", header_format)

    for col_idx, (param, method) in enumerate(df.columns):
        write_idx = col_with_blanks(col_idx, inserts)
        worksheet.write(1, write_idx, method, header_format)

    for ins in inserts:
        blank_idx = ins + 1 + sum(ins > earlier for earlier in inserts)
        worksheet.write(1, blank_idx, "", header_format)

    for row_idx, row in enumerate(df.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row):
            write_idx = col_with_blanks(col_idx, inserts)
            if pd.isna(value) or value in (float("inf"), float("-inf")):
                worksheet.write(row_idx, write_idx, "")
            else:
                worksheet.write(row_idx, write_idx, value)

        for ins in inserts:
            blank_idx = ins + 1 + sum(ins > earlier for earlier in inserts)
            worksheet.write_blank(row_idx, blank_idx, None)
   

def execute_save(input_heading, parent_input, setup_dict, output_dict, calculation_name, foundation_location_name):
        
    input = output_dict['input']
    output = output_dict['output']

    save_excel_task(input_heading, input, output, parent_input, setup_dict, calculation_name, foundation_location_name)


def save_excel_task(input_heading, input, output, parent_input, setup_dict, calculation_name, foundation_location_name, output_folder='output'):

    tables_for_input = setup_dict[calculation_name][input_heading]['table'].replace(" ", "").split(";")

    sub_title3_for_input = str(setup_dict[calculation_name][input_heading]['sub_title3']).split(";")

    if len(sub_title3_for_input) == 0:
        sub_title3_for_input = [""]*len(tables_for_input)
    else:
        while len(sub_title3_for_input) < len(tables_for_input):
            sub_title3_for_input.append(sub_title3_for_input[-1])

    fig_no_for_input = str(setup_dict[calculation_name][input_heading]['fig_no']).split(";")
    
    if len(fig_no_for_input) == 0:
        fig_no_for_input = [""]*len(tables_for_input)
    else:
        while len(fig_no_for_input) < len(tables_for_input):
            fig_no_for_input.append(fig_no_for_input[-1])

    method_order = ("input", "input_b", "input_s", "input_pb", "input_ps", 
                    "geometry_b", "geometry_s", "geometry_pb", "geometry_ps", "geometry",
                    "calc_b", "calc_s", "calc_pb", "calc_ps",
                    "calc_b2", "calc_s2", "calc_pb2", "calc_ps2",
                    "calc_b3", "calc_s3", "calc_pb3", "calc_ps3",
                    "calc", "calc_t", 
                    "output_b", "output_s", "output_pb", "output_ps", "output", "output_t", "output_grl")
    
    length_embedment = 0
    for key in output.keys():
        if key not in ['capacity_dict']:
            if 'length_embedment' in output[key]['plot_output']:
                if output[key]['plot_output']['length_embedment'] > length_embedment:
                    length_embedment = output[key]['plot_output']['length_embedment']

    for calculation_method_i in output.keys():

        if calculation_method_i in ['capacity_dict', 'url_info']:
            continue
        
        if 'save_input' in output[calculation_method_i]:
            input_i = output[calculation_method_i]['save_input']
        else:
            input_i = {}

        output_i = output[calculation_method_i]['save_output']

        if 'save_breakdown' in output[calculation_method_i]:
            output_breakdown_i = output[calculation_method_i]['save_breakdown']

        save_intervals = np.abs(np.array(list(output_i.keys())))

        if "incremental_save_plot" in input:
            plot_interval = input["incremental_save_plot"]
        else:
            plot_interval = None

        if "d_z" in input:
            d_z = input["d_z"]
        else:
            d_z = None
        
        if str(plot_interval) != 'None':
            n_interval = plot_interval/d_z
        else:
            n_interval = len(save_intervals) - 1

        if 'foundation_b_outer' in output_i:
            foundation_b_outer = output_i['foundation_b_outer']
        else:
            foundation_b_outer = None

        method_text_save = ''

        if input_heading is not None:
            method_text_save += '_' + input_heading.lower()
        if calculation_method_i is not None:
            method_text_save += '_' + calculation_method_i.lower()
        if foundation_b_outer is not None:
            method_text_save += '_' + str(foundation_b_outer)

        save_file_name = foundation_location_name.lower() + method_text_save + '.xlsx'

        save_folder = Path(parent_input["calculations_location"])/parent_input["python_calculation_folder"]/parent_input["foundation_calculation_folder"]/output_folder
 
        os.makedirs(save_folder/calculation_name, exist_ok=True)
        
        with pd.ExcelWriter(save_folder/calculation_name/save_file_name, engine='xlsxwriter') as writer:

            df = pd.DataFrame()

            for save_interval_i in save_intervals:

                if save_interval_i in input_i:
                    df = pd.DataFrame.from_dict({k: v for k, v in input_i[save_interval_i].items()if k not in ["alpha_d_su", "alpha_updated", "su_ave_l", "su_ave_end_bear"]})
                    export_param_method_excel(df, writer, 'input_' + str(save_interval_i), method_order)

                if save_interval_i in output_i:

                    if calculation_name in ['_cap_capacity']:
                        if calculation_method_i.lower() in ['cap', 'capt']:
                            df = pd.DataFrame.from_dict(output_i[save_interval_i])
                            export_param_method_excel(df, writer, 'output_' + str(save_interval_i), method_order)

                        elif calculation_method_i.lower() in ['carl']:
                            df = pd.DataFrame(output_i[save_interval_i]['SF[output]'], index=output_i[save_interval_i]['z[output]'], columns=output_i[save_interval_i]['x[output]'])
                            df.index.name = "z / x"
                            df.to_excel(writer, sheet_name='output_' + str(save_interval_i), index=True)

                    elif calculation_name in ['_caisson_capacity']:
                        input_file_i = output[calculation_method_i]['save_input']
                        start = 0
                        df0 = pd.DataFrame([{k: round(input_file_i[save_interval_i][k], 3) for k in ["alpha_d_su", "alpha_updated", "su_ave_l", "su_ave_end_bear"]}], columns=['alpha_d_su', 'alpha_updated', "su_ave_l", "su_ave_end_bear"])
                        df0.to_excel(writer, sheet_name='output_' + str(save_interval_i), startrow=start, index=False)
                        start += len(df0) + 2
                        df1 = pd.DataFrame(output_i[save_interval_i]['summary_caisson'][0], columns=['ilc', 'icgeom', 'D', 'L', 'L/D', 'Vmax', 'Hmax', 'H0', 'Bw', 'su_av_L'])
                        df1.to_excel(writer, sheet_name='output_' + str(save_interval_i), startrow=start, index=False)
                        start += len(df1) + 2
                        df2 = pd.DataFrame(output_i[save_interval_i]['fos_results'][0], columns=['ilc', 'icgeom', 'D', 'L', 'FOS', 'row', 'V', 'H', 'M', 'ilc'])
                        df2.to_excel(writer, sheet_name='output_' + str(save_interval_i), startrow=start, index=False)
                        start += len(df2) + 2
                        df3 = pd.DataFrame(output_i[save_interval_i]['hvm_results'][0], columns=['Hx', 'My', 'Vz', 'H*', 'M*', 'V*', 'it', 'iv', 'row'])
                        df3.to_excel(writer, sheet_name='output_' + str(save_interval_i), startrow=start, index=False)

                    elif calculation_name not in ['_lateral_displacement', '_axial_displacement']:
                        extract_dict = output_i[save_interval_i]
                        df2 = pd.Series(extract_dict)
                        df = pd.concat([df, df2.to_frame().T], ignore_index=True)
            
            if calculation_name not in ['_cap_capacity', '_lateral_displacement', '_axial_displacement']:
                export_param_method_excel(df, writer, 'output_complete', method_order)
                
                for table_i, sub_title3_i, fig_no_i in zip(tables_for_input, sub_title3_for_input, fig_no_for_input):

                    if table_i not in setup_dict['tables']:
                        continue

                    axes = copy.deepcopy(setup_dict['tables'][table_i])
                    table_info = axes["table_info"]
                    table_info['table_i'] = table_i
                    table_info['sub_title3_i'] = sub_title3_i
                    table_info['fig_no_i'] = pdf.clean_fig_no(fig_no_i)
                    table_info['table_limit'] = length_embedment
                    table_info['table_type'] = 'summary'

                    calc_symbol_info = axes["calc_symbol_info"]
                    parameter_symbol_info = axes["parameter_symbol_info"]

                    export_param_method_pdf(df, table_info, calc_symbol_info, parameter_symbol_info, setup_dict, calculation_name, save_file_name, output_folder, method_order)

            elif calculation_name in ['_lateral_displacement', '_axial_displacement']:
                for save_interval_i in save_intervals:
                    df = pd.Series(output_i[save_interval_i])
                    df = df.to_frame().T
                    x_background = df['x_background'].iloc[0]
                    y_background = df['y_background'].iloc[0]
                    z_background = df['z[input]'].iloc[0]

                    df = df.drop(["x_background", "y_background"], axis=1)   
                    export_param_method_excel(df, writer, 'Load='+str(save_interval_i), method_order)

                spring_depth_intervals = setup_dict[calculation_name][input_heading]['global_spring_depth_to_plot']

                param_array = []

                for key in output_i:

                    if key in ['length_embedment']:
                        continue

                    if calculation_name == '_lateral_displacement':

                        param_name = 'M[output]'
                        depth = output_i[key]['z[input]']
                        param = output_i[key][param_name]
                        max_param = min(param)
                        max_param_depth = depth[np.argmin(param)]
                        param_array.append([max_param_depth, max_param])

                if '[' in str(spring_depth_intervals):
                    spring_depth_intervals = spring_depth_intervals.strip()[1:-1].split(',')
                    spring_depth_intervals = [param_array[-1][0] if 'max_moment' in str(v) else float(v) for v in spring_depth_intervals]
                else:
                    spring_depth_intervals = np.arange(0, length_embedment+spring_depth_intervals, spring_depth_intervals)

                for spring_depth_interval_i in spring_depth_intervals:

                    load_array = []
                    displacement_array = []
                    secant_stiffness_array = []
                    tangent_stiffness_array = []
                    
                    for key in output_i:

                        if key in ['length_embedment']:
                            continue

                        load_array.append(key)

                        depth = output_i[key]['z[input]']

                        if calculation_name == '_lateral_displacement':
                            x_calc = output_i[key]['y_calc[output]']
                            displacement = 'y_calc[output]'
                        
                        elif calculation_name == '_axial_displacement':
                            x_calc = output_i[key]['z_calc[output]']
                            displacement = 'z_calc[output]'

                        idx_diff = np.abs(depth - spring_depth_interval_i)
                        idx_depth = np.argmin(idx_diff)
                        
                        displacement_array.append(x_calc[idx_depth])

                        if len(displacement_array) > 1:
                            secant_stiffness_array.append(abs((load_array[-1] - load_array[0])/(displacement_array[-1] - displacement_array[0])))
                            tangent_stiffness_array.append(abs((load_array[-1] - load_array[-2])/(displacement_array[-1] - displacement_array[-2])))
                        else:
                            secant_stiffness_array.append(np.nan)
                            tangent_stiffness_array.append(np.nan)

                    df = pd.DataFrame({displacement: displacement_array,
                                    'load[output]': load_array,
                                    'secant_stiffness[output]': secant_stiffness_array,
                                    'tangent_stiffness[output]': tangent_stiffness_array})
                    
                    export_param_method_excel(df, writer, 'global_spring_'+str(round(spring_depth_interval_i, 1)), method_order)

                y_background = np.column_stack(y_background)
                x_y_save = np.column_stack((x_background, y_background))
                
                if calculation_name in ['_lateral_displacement']:
                    df2 = pd.DataFrame(x_y_save, columns=['x / y']+list(z_background))
                elif calculation_name in ['_axial_displacement']:
                    df2 = pd.DataFrame(x_y_save, columns=['x / y']+list(z_background)+[z_background[-1]])
                df2.to_excel(writer, sheet_name='local_springs', index=False)
            
            elif calculation_name not in ['_cap_capacity', '_caisson_capacity']:

                export_param_method_excel(df, writer, 'output_complete', method_order)
                
            else:

                export_param_method_excel(df, writer, 'output_complete', method_order)

            if calculation_name in ['_installation']:

                if 'stress_fatigue_dict' in output[calculation_method_i]:
                    stress_fatigue_dict = output[calculation_method_i]['stress_fatigue_dict']
                    penetration_depth_array = next(iter(stress_fatigue_dict.values()))['penetration_depth']

                    rows = []
                    for depth, values in stress_fatigue_dict.items():
                        row = {"z_pile[geometry]": depth, "acc_damage[output]": float(values["acc_damage"])}
                        
                        for depth_i, t, c in zip(penetration_depth_array, values["t_max"], values["c_max"]):
                            row["t_max[" + str(depth_i) +"]"] = t
                            row["c_max[" + str(depth_i) +"]"] = c
                        
                        rows.append(row)

                    df = pd.DataFrame(rows)
                    export_param_method_excel(df, writer, 'stress_fatigue', method_order)
                    
            if calculation_name not in ['_cap_capacity', '_caisson_capacity', '_lateral_displacement', '_axial_displacement']:
                for idx2, save_interval_i in enumerate(save_intervals[::-1]):

                    if idx2 % n_interval == 0 or round(save_interval_i, 2) == round(length_embedment, 2):

                        if 'base_parameter_inc' in output_breakdown_i[save_interval_i]:
                            extract_dict_base = extract_dict_inc(output_breakdown_i[save_interval_i]['base_parameter_inc'], save_interval_i, "base")
                        else:
                            extract_dict_base = {}

                        if 'shaft_parameter_inc' in output_breakdown_i[save_interval_i]:
                            extract_dict_shaft = extract_dict_inc(output_breakdown_i[save_interval_i]['shaft_parameter_inc'], save_interval_i, "shaft")
                        else:
                            extract_dict_shaft = {}

                        if 'base_parameter_inc_plug_bearing' in output_breakdown_i[save_interval_i]:
                            extract_dict_base_plug_bearing = extract_dict_inc(output_breakdown_i[save_interval_i]['base_parameter_inc_plug_bearing'], save_interval_i, "plug_bearing_base")
                        else:
                            extract_dict_base_plug_bearing = {}

                        if 'shaft_parameter_inc_plug_bearing' in output_breakdown_i[save_interval_i]:
                            extract_dict_shaft_plug_bearing = extract_dict_inc(output_breakdown_i[save_interval_i]['shaft_parameter_inc_plug_bearing'], save_interval_i, "plug_bearing_shaft")
                        else:
                            extract_dict_shaft_plug_bearing = {}

                        if 'p_ult_parameter_inc' in output_breakdown_i[save_interval_i]:
                            extract_dict_p_ult = extract_dict_inc(output_breakdown_i[save_interval_i]['p_ult_parameter_inc'], save_interval_i, "p_ult")
                        else:
                            extract_dict_p_ult = {}

                        if 'grl_soil_resistance_inc' in output_breakdown_i[save_interval_i]:
                            extract_dict_grl_soil_resistance = extract_dict_inc(output_breakdown_i[save_interval_i]['grl_soil_resistance_inc'], save_interval_i, "grl")
                        else:
                            extract_dict_grl_soil_resistance = {}

                        extract_dict = {}

                        for save_interval_ii in save_intervals:

                            if save_interval_ii <= save_interval_i:

                                if save_interval_ii not in extract_dict_base:
                                    extract_dict_base[save_interval_ii] = {}

                                if save_interval_ii not in extract_dict_shaft:
                                    extract_dict_shaft[save_interval_ii] = {}
                                    
                                if save_interval_ii not in extract_dict_base_plug_bearing:
                                    extract_dict_base_plug_bearing[save_interval_ii] = {}

                                if save_interval_ii not in extract_dict_shaft_plug_bearing:
                                    extract_dict_shaft_plug_bearing[save_interval_ii] = {}

                                if save_interval_ii not in extract_dict_p_ult:
                                    extract_dict_p_ult[save_interval_ii] = {}

                                if save_interval_ii not in extract_dict_grl_soil_resistance:
                                    extract_dict_grl_soil_resistance[save_interval_ii] = {}
                                    
                                extract_dict_total = output_breakdown_i[save_interval_ii]['total_save_parameter']
                                extract_dict[save_interval_ii] = {**extract_dict_total, 
                                                                  **extract_dict_base[save_interval_ii], 
                                                                  **extract_dict_shaft[save_interval_ii], 
                                                                  **extract_dict_base_plug_bearing[save_interval_ii], 
                                                                  **extract_dict_shaft_plug_bearing[save_interval_ii], 
                                                                  **extract_dict_p_ult[save_interval_ii],
                                                                  **extract_dict_grl_soil_resistance[save_interval_ii]}
                                
                        df = pd.DataFrame.from_dict(extract_dict, orient='index')#.sort_values(by='z[input]')

                        if round(save_interval_i, 2) == round(length_embedment, 2):
                            sheet_name = "l_emb="+str(save_interval_i)
                            for table_i, sub_title3_i, fig_no_i in zip(tables_for_input, sub_title3_for_input, fig_no_for_input):

                                if table_i not in setup_dict['tables']:
                                    continue

                                axes = copy.deepcopy(setup_dict['tables'][table_i])
                                table_info = axes["table_info"]
                                table_info['table_i'] = table_i
                                table_info['sub_title3_i'] = sub_title3_i
                                table_info['fig_no_i'] = pdf.clean_fig_no(fig_no_i)
                                table_info['table_limit'] = length_embedment
                                table_info['table_type'] = 'interval'

                                export_param_method_pdf(df, table_info, calc_symbol_info, parameter_symbol_info, setup_dict, calculation_name, save_file_name, output_folder, method_order)
                                
                        else:
                            sheet_name = str(save_interval_i)
                        export_param_method_excel(df, writer, sheet_name, method_order)

            if calculation_name in ['_installation']:

                for idx2, save_interval_i in enumerate(save_intervals[::-1]):

                    if round(save_interval_i, 2) == round(length_embedment, 2):
                        sheet_name = "l_emb="+str(save_interval_i)
                    else:
                        sheet_name = str(save_interval_i)

                    if 'grl_pile_stress_inc' in output_breakdown_i[save_interval_i]:
                        extract_dict_grl_pile_stress = extract_dict_inc(output_breakdown_i[save_interval_i]['grl_pile_stress_inc'], np.inf, "grl")

                        try:                                                                                                 
                            df = pd.DataFrame.from_dict(extract_dict_grl_pile_stress, orient='index').sort_values(by='z_grl_section_1[output_grl]')
                            export_param_method_excel(df, writer, "grl_stress_" + sheet_name)
                        except Exception:
                            continue

        if calculation_name in ['_cap_capacity', '_caisson_capacity']:  # HERE
            input_file_i = output[calculation_method_i]['input_file']
            input_file_move_i = os.path.basename(input_file_i)
            shutil.move(input_file_i, save_folder/calculation_name/input_file_move_i)

            output_file_i = output[calculation_method_i]['output_file']
            output_file_move_i = os.path.basename(output_file_i)
            shutil.move(output_file_i, save_folder/calculation_name/output_file_move_i)