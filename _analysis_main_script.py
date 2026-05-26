# Load modules
import os
import importlib.util
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
target_folder = os.path.join(base_dir, '_analysis_background_functions')
sys.path.append(target_folder)

import _background_execute as b_exe
import _background_plot as b_plot
import _background_save as b_save

calculations_location = r"\\nsv2-nasuni-01\Prosjekt\O10267\10267730-01\10267730-01-03 ARBEIDSOMRAADE\10267730-01 RIG\10267730-01-03 TEKNISKE PROGRAMFILER" # PPF
# calculations_location = r"\\nsv2-nasuni-01\Prosjekt\O10269\10269544-01\10269544-01-03 WORKSPACE\10269544-01 RIG\10269544-01-03 TECHNICAL WORK FILES" # CN
# calculations_location = r"\\nsv2-nasuni-01\Prosjekt\O10271\10271514-01\10271514-01-03 ARBEIDSOMRAADE\10271514-01 RIG\10271514-01-03 TEKNISKE PROGRAMFILER\Caisson" # PLEM
setup_dict = b_exe.load_parent_input(calculations_location)
setup_dict = b_exe.load_param_map(setup_dict)
gdb_dict = b_exe.load_gdb_input(setup_dict)
cpt_dict, setup_dict = b_exe.load_cpt_input(setup_dict)

# foundation_location_name_loop = ["CN_CPT_60"]
# foundation_location_name_loop = ["CIM6"]
foundation_location_name_loop = ["VEDA"]
# foundation_location_name_loop = ["ALUA", "ALUB", "TLGA", "VEDA"]
# foundation_location_name_loop = ["ALUA_cond_clay", "ALUA_cond_sand", "ALUB_cond_clay", "ALUB_cond_sand", "TLGA_cond_clay", "TLGA_cond_sand", "VEDA_cond_clay", "VEDA_cond_sand"]
# foundation_location_name_loop = ["Eirin_le"]
# foundation_location_name_loop = ["CN_CPT_140", "CN_CPT_139", "CN_BH_139_pseudo"]
# foundation_location_name_loop = ["CN_BH_139_pseudo"]
# 
# calculation_name_loop = ["_installation"]
# calculation_name_loop = ["_removal"]
# calculation_name_loop = ["_axial_capacity"]
# calculation_name_loop = ["_cap_capacity"]
# calculation_name_loop = ["_caisson_capacity"]
# calculation_name_loop = ["_lateral_capacity"]
calculation_name_loop = ["_lateral_displacement"]
# calculation_name_loop = ["_axial_displacement"]
# calculation_name_loop = ["_axial_capacity", "_axial_displacement"]
# calculation_name_loop = ["_lateral_capacity", "_lateral_displacement"]

print()

for calculation_name in calculation_name_loop:

       print(f' - Calculating{calculation_name.replace("_", " ")}...')

       module_name = calculation_name

       if calculation_name == '_removal':
              module_name = '_installation'

       module_path = os.path.join(base_dir, module_name, module_name + "_module.py")
       spec = importlib.util.spec_from_file_location(module_name, module_path)
       module = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(module)

       for foundation_location_name in foundation_location_name_loop:

              print(f' -- Location: {foundation_location_name}')
                          
              setup_dict = b_exe.load_sections_input(setup_dict, foundation_location_name)
              setup_dict = b_exe.load_calculation_input(setup_dict, calculation_name, foundation_location_name)

              if foundation_location_name in gdb_dict:
                     gdb_df = gdb_dict[foundation_location_name]
              else:
                     gdb_df = None
                     print(f"Design profile for {foundation_location_name} not found in GDB file")
                     continue
              
              parent_input = setup_dict['parent_input']    
              sections_input = setup_dict['sections_input']
              setup_dict_calc = setup_dict[calculation_name]
              input_headings = setup_dict_calc["Inputs"]

              if calculation_name not in ['_caisson_capacity']:

                     for input_heading_i in input_headings:

                            if setup_dict_calc[input_heading_i]['execute']:

                                   output_dict, gdb_df ,gdb_df_scour, scour_gdb = b_exe.execute_task(input_heading_i, module, calculation_name, foundation_location_name, gdb_df, parent_input, sections_input, setup_dict_calc)

                                   print(f' ---- Saving')
                                   b_save.execute_save(input_heading_i, parent_input, setup_dict, output_dict, calculation_name, foundation_location_name)
                                   print(f' ---- Plotting')
                                   b_plot.execute_plot(input_heading_i, gdb_df, gdb_df_scour, scour_gdb, cpt_dict, setup_dict, output_dict, calculation_name, foundation_location_name)

                                   print()

              else:

                     output_dict, gdb_df, gdb_df_scour, scour_gdb = b_exe.execute_caisson_task(input_headings, module, calculation_name, foundation_location_name, gdb_df, parent_input, sections_input, setup_dict_calc)
                     
                     print(f' ---- Saving')

                     for input_heading_i in input_headings:

                            if setup_dict_calc[input_heading_i]['execute']:
                                   b_save.execute_save(input_heading_i, parent_input, setup_dict, output_dict[input_heading_i], calculation_name, foundation_location_name)
                                   
                     print(f' ---- Plotting')

                     for input_heading_i in input_headings:

                            if setup_dict_calc[input_heading_i]['execute']:
                                   b_plot.execute_plot(input_heading_i, gdb_df, gdb_df_scour, scour_gdb, cpt_dict, setup_dict, output_dict[input_heading_i], calculation_name, foundation_location_name)


                     print()
