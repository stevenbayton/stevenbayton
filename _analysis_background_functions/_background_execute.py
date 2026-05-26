# python modules
import math
import numpy as np
import pandas as pd
from pathlib import Path
import os


def remove_nan_values(original_dict):

    cleaned_dict = {}
    for key, val in original_dict.items():
        if isinstance(val, dict):
            cleaned_dict[key] = remove_nan_values(val)
        else:
            if not (isinstance(val, float) and math.isnan(val)):
                cleaned_dict[key] = val

    return cleaned_dict


def load_parent_input(calculations_location, python_calculation_folder="python", shared_input_folder="_shared_inputs", parent_input_file="_parent_input.xlsx", setup_dict={}):

    calculations_location = Path(calculations_location)
    parent_input_file = pd.read_excel(os.path.join(calculations_location, python_calculation_folder, shared_input_folder, parent_input_file)).set_index("Parent input")
    
    parent_input_file = parent_input_file.dropna(subset=['Input'])
    
    setup_dict["parent_input"] = parent_input_file['Input'].to_dict()
    setup_dict["parent_input"]["calculations_location"] = calculations_location
    setup_dict["parent_input"]["python_calculation_folder"] = python_calculation_folder

    return setup_dict


def load_gdb_input(setup_dict):
    
    gdb_file_location = setup_dict["parent_input"]["gdb_file_location"]
    gdb_file_name = setup_dict["parent_input"]["gdb_file_name"]

    gdb_dict = pd.read_excel(os.path.join(Path(gdb_file_location), gdb_file_name), sheet_name=None, skiprows=2)
    for sheet, gdb_df in gdb_dict.items():
        try:
            gdb_dict[sheet] = gdb_df.dropna(subset=['depth'])
        except Exception:
            continue

    return gdb_dict


def clean_gdb_df(gdb_df):

    depth_abs = gdb_df["depth"].abs()
    is_unique = depth_abs.map(depth_abs.value_counts()) == 1
    if len(is_unique) > 2:
        is_unique.iloc[[0, -1]] = False
    gdb_df = gdb_df.loc[gdb_df.index.repeat(is_unique.astype(int) + 1)].reset_index(drop=True)

    gdb_df = gdb_df.sort_values("depth")

    cols = gdb_df.columns
    for col in cols:
        if col == 'depth':
            continue
        if gdb_df[col].map(type).eq(str).any():
            gdb_df[col] = (gdb_df.set_index("depth")[col].ffill().bfill().values)
        else:
            gdb_df[col] = pd.to_numeric(gdb_df[col], errors='coerce')
            gdb_df[col] = (gdb_df.set_index("depth")[col].interpolate(method="index", limit_direction="both", limit_area="inside").values)

    gdb_df = gdb_df.dropna(axis=1, how='all')
            
    return gdb_df


def scour_introduce(gdb_df, setup_input, sections_input, overburden_red_depth_constant=6, large_general_scour=False):

    foundation_list = setup_input['foundation'].split(";")
    if type(foundation_list) is not list:
        foundation_list = [foundation_list]

    b_outer = 0
    for foundation_i in sections_input.keys():
        if foundation_i in foundation_list:
            for section_i in sections_input[foundation_i].keys():
                data_i = sections_input[foundation_i][section_i]
                b_outer = max(b_outer, data_i['b_outer'])
    
    gdb_df_scour = gdb_df.copy()
    gdb_df_scour.loc[gdb_df_scour.index[::2], "depth"] += 0.0001

    if 'global_scour'in setup_input:
        z_gs = float(setup_input['global_scour'])
    else:
        z_gs = 0

    if 'local_scour'in setup_input:
        z_ls = float(setup_input['local_scour'])
    else:
        z_ls = 0

    if z_gs != 0 and z_gs not in gdb_df_scour["depth"].values:
        for z_gs_i in [z_gs, z_gs+0.0001]:
            gdb_df_scour = insert_and_fill(gdb_df_scour, z_gs_i)
            
    if z_ls + z_gs != 0 and z_ls + z_gs not in gdb_df_scour["depth"].values:
        for z_ls_i in [z_ls, z_ls+0.0001]:
            gdb_df_scour = insert_and_fill(gdb_df_scour, z_ls_i + z_gs)

    if z_ls != 0:
        overburden_red_depth = round(overburden_red_depth_constant*b_outer, 1)
        if overburden_red_depth + z_gs not in gdb_df_scour["depth"].values:
            for overburden_red_depth_i in [overburden_red_depth, overburden_red_depth+0.0001]:
                gdb_df_scour = insert_and_fill(gdb_df_scour, overburden_red_depth_i + z_gs)
    else:
        overburden_red_depth = 0

    # Vertical stress
    z = np.array(gdb_df_scour['depth'])
    t_uw_gs = np.array([0 if z_i <= z_gs else t_uw_i for z_i, t_uw_i in zip(gdb_df_scour['depth'], gdb_df_scour['totunitweight_rep'])])
    e_uw_gs = np.array([0 if z_i <= z_gs else t_uw_i for z_i, t_uw_i in zip(gdb_df_scour['depth'], gdb_df_scour['effunitweight_rep'])])
    gdb_df_scour['sigv_rep_gs'] = np.append(z[0]*t_uw_gs[0], z[0]*t_uw_gs[0] + np.cumsum(t_uw_gs[1:]*np.diff(z)))
    gdb_df_scour['sigveff_rep_gs'] = np.append(z[0]*e_uw_gs[0], z[0]*e_uw_gs[0] + np.cumsum(e_uw_gs[1:]*np.diff(z)))

    idx_overburden_red = gdb_df_scour.index[gdb_df_scour['depth'] == (z_gs + overburden_red_depth)]
    if overburden_red_depth != 0:
        sigv_overburden_red = gdb_df_scour['sigv_rep_gs'][idx_overburden_red[0]]
        sigveff_overburden_red = gdb_df_scour['sigveff_rep_gs'][idx_overburden_red[0]]
        gdb_df_scour['sigv_rep_ls'] = np.array([0 if (sigv_overburden_red/(overburden_red_depth-z_ls))*(z_i-z_gs-z_ls) < 0 else sigv_gs_i if (sigv_overburden_red/(overburden_red_depth-z_ls))*(z_i-z_gs-z_ls) > sigv_gs_i else (sigv_overburden_red/(overburden_red_depth-z_ls))*(z_i-z_gs-z_ls) for z_i, sigv_gs_i in zip(z, gdb_df_scour['sigv_rep_gs'])])
        gdb_df_scour['sigveff_rep_ls'] = np.array([0 if (sigveff_overburden_red/(overburden_red_depth-z_ls))*(z_i-z_gs-z_ls) < 0 else sigveff_gs_i if (sigveff_overburden_red/(overburden_red_depth-z_ls))*(z_i-z_gs-z_ls) > sigveff_gs_i else (sigveff_overburden_red/(overburden_red_depth-z_ls))*(z_i-z_gs-z_ls) for z_i, sigveff_gs_i in zip(z, gdb_df_scour['sigveff_rep_gs'])])
    else:
        sigv_overburden_red = gdb_df_scour['sigv_rep_gs'][0]
        sigveff_overburden_red = gdb_df_scour['sigveff_rep_gs'][0]
        gdb_df_scour['sigv_rep_ls'] = np.array(gdb_df_scour['sigv_rep_gs'])
        gdb_df_scour['sigveff_rep_ls'] = np.array(gdb_df_scour['sigveff_rep_gs'])
        
    if z_gs != 0 or z_ls != 0:
        if large_general_scour:
            K0 = np.array(gdb_df_scour['K0_rep'])
            gdb_df_scour['chi'] = np.array([0 if z_i <= z_gs else 1/(1+2*K0_i)*np.sqrt(((z_i-z_gs)+2*K0_i*np.sqrt(z_gs*(z_i-z_gs)+np.power(z_i-z_gs, 2)))/(z_gs+(z_i-z_gs))) for z_i, K0_i in zip(z, K0)])
        else:
            gdb_df_scour['chi'] = np.array([sigveff_ls_recalc_i/max(1e-10, sigveff_i) for sigveff_i, sigveff_ls_recalc_i in zip(gdb_df_scour['sigveff_rep'], gdb_df_scour['sigveff_rep_ls'])])
    else:
        gdb_df_scour['chi'] = np.ones(len(gdb_df_scour['sigveff_rep']))

    gdb_df_scour['sigv_rep'] = gdb_df_scour['sigv_rep_ls']
    gdb_df_scour['sigveff_rep'] = gdb_df_scour['sigveff_rep_ls']    

    for param_i in ['qc', 'qt']:
        for dl_i in ['low', 'best', 'high']:
            param_ii = param_i + '_' + dl_i
            if param_ii in gdb_df_scour:
                gdb_df_scour[param_ii] = np.array([chi_i*q_i for q_i, chi_i in zip(gdb_df_scour[param_ii], gdb_df_scour['chi'])])

    gdb_df_scour["depth"] = gdb_df_scour["depth"].round(2)

    if z_gs != 0 or z_ls != 0:
        scour_gdb = True
    else:
        scour_gdb = False
    
    return gdb_df_scour, scour_gdb, z_gs, z_ls


def load_cpt_input(setup_dict):
    
    if "pog_global_location" in setup_dict["parent_input"]:
        pog_global_location = setup_dict["parent_input"]["pog_global_location"]
        cpt_files_location = os.path.join(Path(pog_global_location), "Output", "Data")

        if os.path.exists(cpt_files_location):
            cpt_files = list(filter(lambda f: f.endswith('.csv'), os.listdir(cpt_files_location)))
        else:
            cpt_files = []

        location_details_location = os.path.join(Path(pog_global_location), "Interpretation", "Location_details.xlsx")

        if os.path.exists(location_details_location):
            location_details_file = pd.read_excel(location_details_location).dropna(subset=['Borehole'])
        else:
            location_details_file = None
       
    else:
        cpt_files = []
        location_details_file = None

    setup_dict["location_details"] = location_details_file

    cpt_dict = {}
    for cpt_file_i in cpt_files:
        cpt_name_i = cpt_file_i.split("_CPT_processed")[0]
        cpt_dict[cpt_name_i] = pd.read_csv(os.path.join(cpt_files_location, cpt_file_i), skiprows=[1])
   
    return cpt_dict, setup_dict


def load_sections_input(setup_dict, foundation_location_name, input_folder="input", shared_input_folder="_shared_inputs"):

    foundation_calculation_folder = foundation_location_name
    setup_dict["parent_input"]["foundation_calculation_folder"] = foundation_calculation_folder
    setup_dict["parent_input"]["input_folder"] = input_folder

    calculations_location = setup_dict["parent_input"]["calculations_location"]
    python_calculation_folder = setup_dict["parent_input"]["python_calculation_folder"]
    
    section_file_name = "_sections_input_" + foundation_location_name + ".xlsx"
    if os.path.exists(os.path.join(calculations_location, python_calculation_folder, foundation_calculation_folder, input_folder, section_file_name)):
        sections_file = pd.read_excel(os.path.join(calculations_location, python_calculation_folder, foundation_calculation_folder, input_folder, section_file_name))
        print(" -- Section file from individual foundation folder")
    else:
        section_file_name_shared = "_sections_input_shared.xlsx"
        sections_file = pd.read_excel(os.path.join(calculations_location, python_calculation_folder, shared_input_folder, section_file_name_shared))
        print(" -- Section file from shared folder")

    sections_dict = {}
    for _, row in sections_file.iterrows():
        foundation = row['foundation']
        section = row['section']
        
        if foundation not in sections_dict:
            sections_dict[foundation] = {}
        
        row_dict = row.drop(['foundation', 'section']).to_dict()
        sections_dict[foundation][section] = row_dict

    setup_dict['sections_input'] = {}

    for foundation_i in sections_dict.keys():

        for section_i in sections_dict[foundation_i].keys():

            if np.isnan(sections_dict[foundation_i][section_i]['z1_from_soil_surface']):
                sections_dict[foundation_i][section_i]['z1_from_soil_surface'] = 0
            
            if np.isnan(sections_dict[foundation_i][section_i]['z2_from_soil_surface']):
                sections_dict[foundation_i][section_i]['z2_from_soil_surface'] = np.inf

            if np.isnan(sections_dict[foundation_i][section_i]['l_outer']):
                sections_dict[foundation_i][section_i]['l_outer'] = sections_dict[foundation_i][section_i]['b_outer']
        
            if np.isnan(sections_dict[foundation_i][section_i]['include_submerged_mass']):
                sections_dict[foundation_i][section_i]['include_submerged_mass'] = False

        setup_dict['sections_input'][foundation_i] = sections_dict[foundation_i]
    
    return setup_dict


def load_calculation_input(setup_dict, calculation_name, foundation_location_name, shared_input_folder="_shared_inputs"):

    calculations_location = setup_dict["parent_input"]["calculations_location"]
    foundation_calculation_folder = setup_dict["parent_input"]["foundation_calculation_folder"]
    python_calculation_folder = setup_dict["parent_input"]["python_calculation_folder"]
    input_folder = setup_dict["parent_input"]["input_folder"]

    calculation_input_file = calculation_name  + "_input_" + foundation_location_name + ".xlsx"
    if os.path.exists(os.path.join(calculations_location, python_calculation_folder, foundation_calculation_folder, input_folder, calculation_input_file)):
        calculation_input_file = pd.read_excel(os.path.join(calculations_location, python_calculation_folder, foundation_calculation_folder, input_folder, calculation_input_file), sheet_name=None)
        print(" -- Calculation input file from individual foundation folder")
    else:
        section_file_name_shared = calculation_name + "_input_shared.xlsx"
        calculation_input_file = pd.read_excel(os.path.join(calculations_location, python_calculation_folder, shared_input_folder, section_file_name_shared), sheet_name=None)
        print(" -- Calculation input file from shared folder")

    setup_dict[calculation_name] = {}
    prefix = "Input"
    input_headings = [col for col in calculation_input_file['input'].columns if col.startswith(prefix)]
    setup_dict[calculation_name]["Inputs"] = input_headings

    calculation_input = calculation_input_file['input'].set_index("Calculation input")
    calculation_input = calculation_input[calculation_input.index.notnull()]

    for input_heading_i in input_headings:
        setup_dict[calculation_name][input_heading_i] = calculation_input[input_heading_i].to_dict()

    setup_dict['plotting'] = {}

    for sheet in calculation_input_file:
        if 'plot' in sheet.lower():
            plot_main_info = calculation_input_file[sheet][["plot_info", "plot_info_input"]].dropna(subset=['plot_info']).set_index("plot_info")["plot_info_input"].to_dict()
            plotting_input = calculation_input_file[sheet].dropna(subset=['label']).set_index("label").to_dict('index')
            plotting_input["plot_info"] = plot_main_info
            setup_dict['plotting'][sheet] = remove_nan_values(plotting_input)

    setup_dict['tables'] = {}

    for sheet in calculation_input_file:
        if 'table' in sheet.lower():
            table_main_info = calculation_input_file[sheet][["table_info", "table_info_input"]].dropna(subset=['table_info']).set_index("table_info")["table_info_input"].to_dict()
            tables_input = {}
            tables_input["table_info"] = table_main_info
            
            try:
                global_pdf_info = calculation_input_file[sheet][["global_symbol", "global_type", "global_description", "global_decimal_places", "global_include?"]].dropna(subset=['global_symbol'])
                section_pdf_info = calculation_input_file[sheet][["section_symbol", "section_type", "section_description", "section_decimal_places", "section_include?"]].dropna(subset=['section_symbol'])
                parameter_pdf_info = calculation_input_file[sheet][["parameter_method_code", "parameter_symbol", "parameter_type", "parameter_description", "parameter_decimal_places", "parameter_include?"]].dropna(subset=['parameter_symbol'])
                tables_input["global_pdf_info"] = global_pdf_info
                tables_input["section_pdf_info"] = section_pdf_info
                tables_input["parameter_pdf_info"] = parameter_pdf_info
            except Exception:
                tables_input["global_pdf_info"] = pd.DataFrame()
                tables_input["section_pdf_info"] = pd.DataFrame()
                tables_input["parameter_pdf_info"] = pd.DataFrame()
            
            setup_dict['tables'][sheet] = remove_nan_values(tables_input)

    return setup_dict


def float_or_str(input):
    
    if input is None or input == 'None':
        output = None
    else:
        try:
            output = float(input)
        except ValueError:
            output = str(input)
    
    return output


def insert_and_fill(df, depth_scour):

    df = df.set_index("depth")

    df = df.copy()
    df.loc[depth_scour] = np.nan
    df = df.sort_index()

    num_cols = df.select_dtypes(include="number").columns
    obj_cols = df.select_dtypes(include="object").columns

    for col in num_cols:
        df.loc[depth_scour, col] = df[col].interpolate(method="index").loc[depth_scour]

    df[obj_cols] = df[obj_cols].ffill()

    df = df.reset_index()  

    return df


def execute_task(input_heading,
                 module, 
                 calculation_name, 
                 foundation_location_name, 
                 gdb_df, 
                 parent_input, 
                 sections_input,
                 setup_dict_calc):
       
    output_dict = {}
    
    setup_input = setup_dict_calc[input_heading]

    gdb_df = clean_gdb_df(gdb_df)
    gdb_df_scour, scour_gdb, z_gs, z_ls = scour_introduce(gdb_df, setup_input, sections_input)
    setup_input["z_gs"] = z_gs
    setup_input["z_ls"] = z_ls

    print(f' --- {input_heading}')
    output_dict = {}

    output_dict['input'] = setup_input
    output_dict['output'] = module.task(calculation_name, 
                                        foundation_location_name, 
                                        gdb_df, 
                                        gdb_df_scour, 
                                        sections_input, 
                                        setup_input,
                                        parent_input,
                                        input_heading)

    return output_dict, gdb_df, gdb_df_scour, scour_gdb


def execute_caisson_task(input_headings,
                         module, 
                         calculation_name, 
                         foundation_location_name, 
                         gdb_df, 
                         parent_input, 
                         sections_input,
                         setup_dict_calc, 
                         p=None, browser=None, context=None, page=None):
    
    import _caisson_capacity._navigate_caisson as caisson

    output_dict = {}

    url_info_update = [p, browser, context, page]
    input_file_array = []
    output_file_array = []
    input_headings_calcuated = []
    calculation_method_array = []

    for input_heading in input_headings:

        if setup_dict_calc[input_heading]['execute']:

            input_headings_calcuated.append(input_heading)

            setup_input = setup_dict_calc[input_heading]

            gdb_df = clean_gdb_df(gdb_df)
            gdb_df_scour, scour_gdb, z_gs, z_ls = scour_introduce(gdb_df, setup_input, sections_input)

            setup_input['url_info'] = url_info_update

            print(f' --- {input_heading}')
            output_dict[input_heading] = {}

            output_dict[input_heading]['input'] = setup_input
            output_dict[input_heading]['output'], calculation_method = module.task(calculation_name, 
                                                                                   foundation_location_name, 
                                                                                   gdb_df, 
                                                                                   gdb_df_scour, 
                                                                                   sections_input,
                                                                                   setup_input,
                                                                                   parent_input,
                                                                                   input_heading)

            input_file_array.append(output_dict[input_heading]['output'][calculation_method]['input_file'])
            output_file_array.append(output_dict[input_heading]['output'][calculation_method]['output_file'])
            calculation_method_array.append(calculation_method)

    print(f' ---- Executing caisson')

    caisson.execute_main(foundation_location_name, input_file_array, output_file_array) # HERE

    for input_heading, calculation_method in zip(input_headings_calcuated, calculation_method_array):

        output_file_i = output_dict[input_heading]['output'][calculation_method]['output_file']

        results_dict = caisson.read_ouput_file(output_file_i)
            
        for key, value in results_dict.items():
            if key not in output_dict[input_heading]['output'][calculation_method]['plot_output']:
                output_dict[input_heading]['output'][calculation_method]['plot_output'][key] = value

        length_embedment = output_dict[input_heading]['output'][calculation_method]['plot_output']['length_embedment']
        output_dict[input_heading]['output'][calculation_method]['save_output'][length_embedment] = results_dict

    return output_dict, gdb_df, gdb_df_scour, scour_gdb


def load_param_map(setup_dict, shared_input_folder="_shared_inputs"):

    calculations_location = setup_dict["parent_input"]["calculations_location"]
    python_calculation_folder = setup_dict["parent_input"]["python_calculation_folder"]
    
    map_file_name_shared = "_plot_input_shared.xlsx"
    map_file = pd.read_excel(os.path.join(calculations_location, python_calculation_folder, shared_input_folder, map_file_name_shared), skiprows=2, sheet_name=None)
    
    setup_dict['cpt_map'] = map_file["cpt_map"].set_index('cpt_name').to_dict("index")
    setup_dict['param_map'] = map_file["param_map"].set_index('param_name').to_dict("index")

    return setup_dict