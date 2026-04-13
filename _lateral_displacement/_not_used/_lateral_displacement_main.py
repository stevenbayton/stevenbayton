# Load modules
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
target_folder = os.path.join(parent_dir, '_analysis_background_functions')
sys.path.append(target_folder)

import _background_execute as be
import _background_functions as bf
import _lateral_displacement_module

import _splice_read_res

# matplotlib.use('QtAgg')

# location_cpt_tool = r"\\nsv2-nasuni-01\Prosjekt\O10267\10267730-01\10267730-01-03 ARBEIDSOMRAADE\10267730-01 RIG\10267730-01-03 TEKNISKE PROGRAMFILER\POG_soil_assessment"
# interp_data = pd.read_excel(Path(location_cpt_tool)/"Interpretation"/"Soil_design_profiles.xlsx", sheet_name=None)
# location_cpt_tool = r"C:\Users\steb\OneDrive - Multiconsult\STEB\python_projects\pile_lateral_displacement"
# interp_data = pd.read_excel(Path(location_cpt_tool)/"Soil_design_profiles.xlsx", sheet_name=None)

# calc_name = 'ALUA-TEMP-3-CPT-40'
# l_design = 24.7
# calc_name = 'ALUB-TEMP-5-CPT-40'
# l_design = 23.2
# calc_name = 'TLGA-TEMP-4-CPT-40'
# l_design = 22.9
# calc_name = 'VEDA-TEMP-5-CPT-40'
# l_design = 21.1
# calc_name = 'eirin_le'
# l_design = 10

# result_folder = r"C:\Users\steb\OneDrive - Multiconsult\STEB\python_projects\pile_lateral_displacement"
# result_sub_folder = "result"
# verification_file_location = Path(r"C:\Users\steb\OneDrive - Multiconsult\STEB\python_projects\pile_lateral_displacement\POSTGRAF.DBF")
# verification_file_name = "36-1.57_pile at Eirin_LE soil_horizontal_API_pile group_LC06_Temp_Tie-in_ALL_ALS"
# verification_file_location = None
# verification_file_name = None

# global_load_f_x = 1741 # kN
# global_load_f_y = -2076 # kN
# global_load_f_z = -4008 # kN
# global_load_m_xx = 3122 # kNm
# global_load_m_yy = 2744 # kNm
# global_load_m_zz = -544 # kNm

print_prompts = False
depth_py_curve_plot = [1, 2, 3, 4, 5, 8.5]

setup_dict = {}

# setup_dict['pile_coords'] = {1: [-7.5, 7.335],
#                              2: [7.5, 7.335],
#                              3: [-7.5, -7.335],
#                              4: [7.5, -7.335]}

# setup_dict['b'] = 36 * 0.0254 # 0.9144
# setup_dict['tw'] = 1.5 * 0.0254
# setup_dict['b'] = 0.9144
# setup_dict['tw'] = 0.04
# setup_dict['z_stick_up'] = 0
# setup_dict['youngs_mod'] = 210 # MPa
# setup_dict['lateral_displacement'] = 'C'

# setup_dict['local_scour'] = 0
# setup_dict['global_scour'] = 0

# setup_dict['pf_load_var'] = 1
# setup_dict['pf_load_perm_fav'] = 1
# setup_dict['pf_load_perm_unfav'] = 1
# setup_dict['utilisation_factor'] = 1

# setup_dict['pf_mat'] = 1

# setup_dict['loads'] = {}
# setup_dict['load_increment_limit'] = 1.0
# setup_dict['load_increments'] = 0.2


# for pile_no_i, pilei in setup_dict['pile_coords'].items():
#      setup_dict['loads'][pile_no_i] = {}

#      setup_dict['loads'][pile_no_i]['load_horizontal_x'] = global_load_f_x / len(setup_dict['pile_coords'])
#      setup_dict['loads'][pile_no_i]['load_horizontal_y'] = global_load_f_y / len(setup_dict['pile_coords'])
#      setup_dict['loads'][pile_no_i]['load_vertical'] = global_load_f_z / len(setup_dict['pile_coords'])
#      if pilei[1] != 0:
#           setup_dict['loads'][pile_no_i]['load_horizontal_x'] -= global_load_m_zz/len(setup_dict['pile_coords'])/(2*pilei[1])
#           setup_dict['loads'][pile_no_i]['load_vertical'] += global_load_m_xx/len(setup_dict['pile_coords'])/(pilei[1])

#      if pilei[0] != 0:
#           setup_dict['loads'][pile_no_i]['load_horizontal_y'] += global_load_m_zz/len(setup_dict['pile_coords'])/(2*pilei[0])
#           setup_dict['loads'][pile_no_i]['load_vertical'] -= global_load_m_yy/len(setup_dict['pile_coords'])/(pilei[0])

#      setup_dict['loads'][pile_no_i]['load_horizontal_res'] = np.sqrt(np.power(setup_dict['loads'][pile_no_i]['load_horizontal_x'], 2) + np.power(setup_dict['loads'][pile_no_i]['load_horizontal_y'], 2))

# for pile_no_i in setup_dict['loads']:
#      print(f"H_x: {round(setup_dict['loads'][pile_no_i]['load_horizontal_x']/setup_dict['utilisation_factor'], 1)}, H_y: {round(setup_dict['loads'][pile_no_i]['load_horizontal_x']/setup_dict['utilisation_factor'], 1)}, H_res: {round(setup_dict['loads'][pile_no_i]['load_horizontal_res']/setup_dict['utilisation_factor'], 1)}, V: {round(setup_dict['loads'][pile_no_i]['load_vertical']/setup_dict['utilisation_factor'], 1)}")

# setup_dict['dz'] = 0.05

# setup_dict['l_min_foundation'] = l_design
# setup_dict['dl'] = 0.5

main_loop_dict = {}

main_loop_dict['global_loop'] =           [['Static']] # Static, Cyclic
main_loop_dict['calc_loop'] =             [['Stiff_head']] # Free_head, Fixed_head, Spring_head
main_loop_dict['method_loop'] =           [['API_87', 'API_87'],] # Sand, Clay

location_loop_dict = {}

location_loop_dict['location_loop'] =     [calc_name]
location_loop_dict['cpt_processed_loop'] = [None]
location_loop_dict['suptitle_loop'] =     ['ALUA']
location_loop_dict['l_foundation_loop'] = [l_design]

# --- python lateral displacement code
output_dict = be.execute_task(_lateral_displacement_module, setup_dict, main_loop_dict, location_loop_dict, interp_data)
L = location_loop_dict['l_foundation_loop'][0]

max_overall_load_python = float('-inf')
max_pile_python = None

for pile_no_i, pile_i in setup_dict['loads'].items():
    if not pile_i:
        continue

    outer_key_with_max_load_python = max(pile_i.values())

    if outer_key_with_max_load_python > max_overall_load_python:
        max_overall_load_python = outer_key_with_max_load_python
        max_pile_python = pile_no_i

output_dict_max = output_dict[location_loop_dict['location_loop'][0]][0][main_loop_dict['global_loop'][0][0]][main_loop_dict['calc_loop'][0][0]][max_pile_python][L]
final_load_python = list(output_dict_max)[-1]

 # --- SPLICE lateral displacement results
if verification_file_location is not None:
     data_py_splice = _splice_read_res.extract_res_1(verification_file_location, verification_file_name)
     pile_geometry_splice, loads_splice = _splice_read_res.extract_res_2(verification_file_location, verification_file_name)
     data_global_splice = _splice_read_res.extract_res_3(verification_file_location, verification_file_name)
else:
     data_py_splice = {}
     pile_geometry_splice = {}
     data_global_splice = {}

pile_load_breakdown_splice = {}
for pile_no_i, pile_i in pile_geometry_splice.items():
     pile_load_breakdown_splice[pile_no_i] = {}
     pile_load_breakdown_splice[pile_no_i]['f_x'] = loads_splice['f_x']/4 - loads_splice['m_zz']/4/(2*pile_i['dy'])
     pile_load_breakdown_splice[pile_no_i]['f_y'] = loads_splice['f_y']/4 + loads_splice['m_zz']/4/(2*pile_i['dx'])
     pile_load_breakdown_splice[pile_no_i]['f_res'] = np.sqrt(np.power(pile_load_breakdown_splice[pile_no_i]['f_x'], 2) + np.power(pile_load_breakdown_splice[pile_no_i]['f_y'], 2))

max_overall_load_splice = float('-inf')
max_pile_splice = None

for pile_no_i, pile_i in pile_load_breakdown_splice.items():
    if not pile_i:
        continue

    outer_key_with_max_load_splice = max(pile_i.values())

    if outer_key_with_max_load_splice > max_overall_load_splice:
        max_overall_load_splice = outer_key_with_max_load_splice
        max_pile_splice = pile_no_i

if len(pile_load_breakdown_splice) > 0:
     final_load_splice = list(data_global_splice[max_pile_splice])[-1]
     dz_splice = data_global_splice[max_pile_splice][final_load_splice]['z'][1] - data_global_splice[max_pile_splice][final_load_splice]['z'][0]


# --- Plot comparison
# --- Plot 1: global 

# --- x & y axis

for pile_ax in ['res', 'x', 'y']:

     if pile_ax == 'x':
          m_ax_splice = 'myy'
          abs_ = 1
     elif pile_ax == 'y':
          m_ax_splice = 'mxx'
          abs_ = -1
     else:
          abs_ =1

     for pile_no_i, pilei in setup_dict['pile_coords'].items():

          output_dicti = output_dict[location_loop_dict['location_loop'][0]][0][main_loop_dict['global_loop'][0][0]][main_loop_dict['calc_loop'][0][0]][pile_no_i][L]
          
          fig, ax = plt.subplots(1, 6, sharey=True, figsize=(14, 10))

          if pile_ax in ['x', 'y']:
               z_python = output_dicti[final_load_python][pile_ax]['z_dis']
               p_ult_python = output_dicti[final_load_python][pile_ax]['p_ult_dis']
          else:
               z_python = output_dicti[final_load_python]['x']['z_dis']
               p_ult_python = output_dicti[final_load_python]['x']['p_ult_dis']

          ax[0].plot(p_ult_python, z_python, ls='--', color='grey')
          ax[0].plot(-p_ult_python, z_python, ls='--', color='grey')

          for load_ratio_ploti in np.arange(0, 1+setup_dict['load_increments']/10, setup_dict['load_increments']):
          
               load_plot_idx_key_python = min(output_dicti.keys(), key=lambda k: abs(k - load_ratio_ploti))

               if pile_ax in ['x', 'y']:
                    p_python = abs_*output_dicti[load_plot_idx_key_python][pile_ax]['p_dis']
                    y_python = abs_*output_dicti[load_plot_idx_key_python][pile_ax]['y_dis']
                    R_python = abs_*output_dicti[load_plot_idx_key_python][pile_ax]['R_dis']
                    M_python = output_dicti[load_plot_idx_key_python][pile_ax]['M_dis']
                    Q_python = output_dicti[load_plot_idx_key_python][pile_ax]['Q_dis']
               else:
                    theta_p_python, m_p_python = bf.p_y_bearing(output_dicti[load_plot_idx_key_python]['x']['p_dis'], -output_dicti[load_plot_idx_key_python]['y']['p_dis'])
                    p_python = m_p_python*np.sqrt(np.power(output_dicti[load_plot_idx_key_python]['x']['p_dis'], 2) + np.power(output_dicti[load_plot_idx_key_python]['y']['p_dis'], 2))
                    theta_y_python, m_y_python = bf.p_y_bearing(output_dicti[load_plot_idx_key_python]['x']['y_dis'], -output_dicti[load_plot_idx_key_python]['y']['y_dis'])
                    y_python = m_y_python*np.sqrt(np.power(output_dicti[load_plot_idx_key_python]['x']['y_dis'], 2) + np.power(output_dicti[load_plot_idx_key_python]['y']['y_dis'], 2))
                    theta_R_python, m_R_python = bf.p_y_bearing(output_dicti[load_plot_idx_key_python]['x']['R_dis'], -output_dicti[load_plot_idx_key_python]['y']['R_dis'])
                    R_python = m_R_python*np.sqrt(np.power(output_dicti[load_plot_idx_key_python]['x']['R_dis'], 2) + np.power(output_dicti[load_plot_idx_key_python]['y']['R_dis'], 2))
                    theta_M_python, m_M_python = bf.p_y_bearing(output_dicti[load_plot_idx_key_python]['x']['M_dis'], -output_dicti[load_plot_idx_key_python]['y']['M_dis'])
                    M_python = m_M_python*np.sqrt(np.power(output_dicti[load_plot_idx_key_python]['x']['M_dis'], 2) + np.power(output_dicti[load_plot_idx_key_python]['y']['M_dis'], 2))
                    theta_Q_python, m_Q_python = bf.p_y_bearing(output_dicti[load_plot_idx_key_python]['x']['Q_dis'], -output_dicti[load_plot_idx_key_python]['y']['Q_dis'])
                    Q_python = m_Q_python*np.sqrt(np.power(output_dicti[load_plot_idx_key_python]['x']['Q_dis'], 2) + np.power(output_dicti[load_plot_idx_key_python]['y']['Q_dis'], 2))

               ax[0].plot(p_python, z_python, color='k')
               ax[1].plot(p_python, z_python, color='k')
               ax[2].plot(y_python, z_python, color='k')
               if pile_no_i == 2 and pile_ax == 'res':
                    print(pile_no_i, pile_ax, y_python[0]*1000)
               ax[3].plot(R_python, z_python, color='k')
               ax[4].plot(M_python, z_python, color='k')
               ax[5].plot(Q_python, z_python, color='k')
               
               if len(data_global_splice) > 0:
                    load_plot_idx_key_splice = min(data_global_splice[pile_no_i].keys(), key=lambda k: abs(k - load_ratio_ploti))

                    if print_prompts:
                         print(f"Global ({pile_ax}), Pile: {pile_no_i}, Aim: {round(load_ratio_ploti, 1)}, Python: {round(load_plot_idx_key_python, 1)} ({abs_*round(load_ratio_ploti * (setup_dict['loads'][pile_no_i]['load_horizontal_' + pile_ax]), 1)}), splice: {round(load_plot_idx_key_splice, 1)} ({round(load_plot_idx_key_splice * pile_load_breakdown_splice[pile_no_i]['f_' + pile_ax], 1)})")

                    z_splice = data_global_splice[pile_no_i][load_plot_idx_key_splice]['z']

                    if pile_ax in ['x', 'y']:
                         p_splice = np.array([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['p' + pile_ax]])
                         y_splice = np.array(data_global_splice[pile_no_i][load_plot_idx_key_splice]['d' + pile_ax])
                    else:
                         theta_p_splice, m_p_splice = bf.p_y_bearing([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['px']], [i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['py']])
                         p_splice = m_p_splice*np.sqrt(np.power([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['px']], 2) + np.power([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['py']], 2))
                         theta_y_splice, m_y_splice = bf.p_y_bearing([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['dx']], [i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['dy']])
                         y_splice = m_y_splice*np.sqrt(np.power([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['dx']], 2) + np.power([i*setup_dict['b'] for i in data_global_splice[pile_no_i][load_plot_idx_key_splice]['dy']], 2))
                    
                    N = len(y_splice)
                    R_splice = np.zeros(N)
                    for i in range(1, N-1):
                         R_splice[i] = (1/(2*dz_splice))*(y_splice[i+1] - y_splice[i-1])
                    R_splice[-1] = (1/(2*dz_splice))*(3*y_splice[-1] - 4*y_splice[-2] + y_splice[-3])

                    if pile_ax in ['x', 'y']:
                         M_splice = np.array(data_global_splice[pile_no_i][load_plot_idx_key_splice][m_ax_splice])
                    else:
                         theta_M_splice, m_M_splice = bf.p_y_bearing(data_global_splice[pile_no_i][load_plot_idx_key_splice]['mxx'], data_global_splice[pile_no_i][load_plot_idx_key_splice]['myy'])
                         M_splice = m_M_splice*np.sqrt(np.power(data_global_splice[pile_no_i][load_plot_idx_key_splice]['mxx'], 2) + np.power(data_global_splice[pile_no_i][load_plot_idx_key_splice]['myy'], 2))

                    Q_splice = np.zeros(N)
                    Q_splice[0] = (1/(2*dz_splice))*(-3*M_splice[0] + 4*M_splice[1] - M_splice[2])
                    for i in range(1, N-1):
                         Q_splice[i] = (1/(2*dz_splice))*(M_splice[i+1] - M_splice[i-1])
                    Q_splice[-1] = (1/(2*dz_splice))*(3*M_splice[-1] - 4*M_splice[-2] + M_splice[-3])
                    
                    ax[0].plot(p_splice, z_splice, ls='--', color='r')
                    ax[1].plot(p_splice, z_splice, ls='--', color='r')
                    ax[2].plot(y_splice, z_splice, ls='--', color='r')
                    ax[3].plot(R_splice, z_splice, ls='--', color='r')
                    ax[4].plot(M_splice, z_splice, ls='--', color='r')
                    ax[5].plot(Q_splice, z_splice, ls='--', color='r')

          if print_prompts:
               print()

          ax[0].set_ylim(max(z_python), min(z_python))
          ax[0].plot([-1, -1], [-1, -1], color='k', label='python')
          ax[0].plot([-1, -1], [-1, -1], ls='--', color='r', label='splice')
          ax[0].legend(loc='lower left')

          ax[0].grid('on')
          ax[1].grid('on')
          ax[2].grid('on')
          ax[3].grid('on')
          ax[4].grid('on')
          ax[5].grid('on')

          if pile_ax == 'res':
               p_max = max(abs(min(p_python)), abs(max(p_python)))
               y_max = max(abs(min(y_python)), abs(max(y_python)))
               R_max = max(abs(min(R_python)), abs(max(R_python)))
               M_max = max(abs(min(M_python)), abs(max(M_python)))
               Q_max = max(abs(min(Q_python)), abs(max(Q_python)))
          
          extra_lim = 1.2
          ax[0].set_xlim(-extra_lim*p_max, extra_lim*p_max)
          ax[0].set_xlabel("Lateral soil resistance, p (kN/m)")
          ax[0].set_ylabel("Depth, z (m)")

          ax[1].set_xlim(-0.2*p_max, 0.2*p_max)
          ax[1].set_xlabel("Lateral soil resistance, p (kN/m)")

          ax[2].set_xlim(-extra_lim*y_max, extra_lim*y_max)
          ax[2].set_xlabel("Lateral displacement, y (m)")

          ax[3].set_xlim(-extra_lim*R_max, extra_lim*R_max)
          ax[3].set_xlabel("Rotation, r (rad)")

          ax[4].set_xlim(-extra_lim*M_max, extra_lim*M_max)
          ax[4].set_xlabel("Bending moment, M (kNm)")

          ax[5].set_xlim(-extra_lim*Q_max, extra_lim*Q_max)
          ax[5].set_xlabel("Shear force, Q (kN)")
          fig.suptitle(location_loop_dict['location_loop'][0])
          plt.savefig(Path(result_folder)/result_sub_folder/('Global_' + pile_ax + '_pile_no_'+str(pile_no_i) + '.png'))
          plt.close()

# --- Plot 2: Load-disp (pile-head)

# --- x & y axis

for pile_ax in ['res', 'x', 'y']:

     if pile_ax == 'x':
          m_ax_splice = 'myy'
          abs_ = 1
     elif pile_ax == 'y':
          m_ax_splice = 'mxx'
          abs_ = -1
     else:
          abs_ = 1

     for pile_no_i, pilei in setup_dict['pile_coords'].items():

          output_dicti = output_dict[location_loop_dict['location_loop'][0]][0][main_loop_dict['global_loop'][0][0]][main_loop_dict['calc_loop'][0][0]][pile_no_i][L]

          fig, ax = plt.subplots(1, 1, sharey=True, figsize=(14, 10))

          if pile_ax in ['x', 'y']:
               y_0_python = [abs_*output_dicti[key][pile_ax]['y_dis'][0] for key in output_dicti.keys()]
          else:
               y_0_python = np.sqrt(np.power(np.array([abs_*output_dicti[key]['x']['y_dis'][0] for key in output_dicti.keys()]), 2) + np.power(np.array([abs_*output_dicti[key]['y']['y_dis'][0] for key in output_dicti.keys()]), 2))

          F_python = [abs_*key*(setup_dict['loads'][pile_no_i]['load_horizontal_' + pile_ax]) for key in output_dicti.keys()]

          ax.plot(y_0_python, F_python, color='k', label='python')

          if len(data_global_splice) > 0:
               if pile_ax in ['x', 'y']:
                    y_0_splice = [np.array(data_global_splice[pile_no_i][key]['d' + pile_ax][0]) for key in data_global_splice[pile_no_i].keys()]
               else:
                    y_0_splice = np.sqrt(np.power(np.array([data_global_splice[pile_no_i][key]['dx'][0] for key in data_global_splice[pile_no_i].keys()]), 2) + np.power(np.array([data_global_splice[pile_no_i][key]['dy'][0] for key in data_global_splice[pile_no_i].keys()]), 2))

               F_splice = [key*pile_load_breakdown_splice[pile_no_i]['f_' + pile_ax] for key in data_global_splice[pile_no_i].keys()]

               ax.plot(y_0_splice, F_splice, ls='--', color='r', label='splice')

          ax.legend(loc='lower left')

          ax.grid('on')
          ax.set_xlabel("Lateral displacement at pile head, y (m)")
          ax.set_ylabel("Lateral load at pile head, H (kN)")
          fig.suptitle(location_loop_dict['location_loop'][0])
          plt.savefig(Path(result_folder)/result_sub_folder/('F-y_' + pile_ax + '_pile_no_'+str(pile_no_i) + '.png'))
          plt.close()

# --- Plot 3: Moment-rotation (pile-head)

# --- x & y axis

for pile_ax in ['res', 'x', 'y']:

     if pile_ax == 'x':
          m_ax_splice = 'myy'
          abs_ = 1
     elif pile_ax == 'y':
          m_ax_splice = 'mxx'
          abs_ = -1

     for pile_no_i, pilei in setup_dict['pile_coords'].items():

          output_dicti = output_dict[location_loop_dict['location_loop'][0]][0][main_loop_dict['global_loop'][0][0]][main_loop_dict['calc_loop'][0][0]][pile_no_i][L]

          fig, ax = plt.subplots(1, 1, sharey=True, figsize=(14, 10))

          if pile_ax in ['x', 'y']:
               R_0_python = [abs_*output_dicti[key][pile_ax]['R_dis'][0] for key in output_dicti.keys()]
               M_0_python = [output_dicti[key][pile_ax]['M_dis'][0] for key in output_dicti.keys()]
          else:
               R_0_python = np.sqrt(np.power(np.array([abs_*output_dicti[key]['x']['R_dis'][0] for key in output_dicti.keys()]), 2) + np.power(np.array([abs_*output_dicti[key]['y']['R_dis'][0] for key in output_dicti.keys()]), 2))
               M_0_python = np.sqrt(np.power(np.array([abs_*output_dicti[key]['x']['M_dis'][0] for key in output_dicti.keys()]), 2) + np.power(np.array([abs_*output_dicti[key]['y']['M_dis'][0] for key in output_dicti.keys()]), 2))
               
          ax.plot(R_0_python, M_0_python, color='k', label='python')

          if len(data_global_splice) > 0:
               if pile_ax in ['x', 'y']:
                    def_0 = np.array([data_global_splice[pile_no_i][key]['d' + pile_ax][0] for key in data_global_splice[pile_no_i].keys()])
                    def_1 = np.array([data_global_splice[pile_no_i][key]['d' + pile_ax][1] for key in data_global_splice[pile_no_i].keys()])
                    def_2 = np.array([data_global_splice[pile_no_i][key]['d' + pile_ax][2] for key in data_global_splice[pile_no_i].keys()])
                    R_0_splice = (1/(2*dz_splice))*(-3*def_0 + 4*def_1 - def_2)
                    M_0_splice = [data_global_splice[pile_no_i][key][m_ax_splice][0] for key in data_global_splice[pile_no_i].keys()]
               else:
                    def_0 = np.sqrt(np.power(np.array([data_global_splice[pile_no_i][key]['dx'][0] for key in data_global_splice[pile_no_i].keys()]), 2) + np.power(np.array([data_global_splice[pile_no_i][key]['dy'][0] for key in data_global_splice[pile_no_i].keys()]), 2))
                    def_1 = np.sqrt(np.power(np.array([data_global_splice[pile_no_i][key]['dx'][1] for key in data_global_splice[pile_no_i].keys()]), 2) + np.power(np.array([data_global_splice[pile_no_i][key]['dy'][1] for key in data_global_splice[pile_no_i].keys()]), 2))
                    def_2 = np.sqrt(np.power(np.array([data_global_splice[pile_no_i][key]['dx'][2] for key in data_global_splice[pile_no_i].keys()]), 2) + np.power(np.array([data_global_splice[pile_no_i][key]['dy'][2] for key in data_global_splice[pile_no_i].keys()]), 2))
                    R_0_splice = (1/(2*dz_splice))*(-3*def_0 + 4*def_1 - def_2)
                    M_0_splice = np.sqrt(np.power(np.array([data_global_splice[pile_no_i][key]['mxx'][0] for key in data_global_splice[pile_no_i].keys()]), 2) + np.power(np.array([data_global_splice[pile_no_i][key]['myy'][0] for key in data_global_splice[pile_no_i].keys()]), 2))

               ax.plot(R_0_splice, M_0_splice, ls='--', color='r', label='splice')

          ax.legend(loc='lower left')

          ax.grid('on')
          ax.set_xlabel("Rotation at pile head, R (rad)")
          ax.set_ylabel("Bending moment at pile head, H (kNm)")
          fig.suptitle(location_loop_dict['location_loop'][0])
          plt.savefig(Path(result_folder)/result_sub_folder/('M-R_' + pile_ax + '_pile_no_'+str(pile_no_i) + '.png'))
          plt.close()

# --- Plot 4: p-y curves

# --- x & y axis

for pile_ax in ['res', 'x', 'y']:

     if pile_ax == 'x':
          m_ax_splice = 'myy'
          abs_ = 1
     elif pile_ax == 'y':
          m_ax_splice = 'mxx'
          abs_ = -1
     else:
          abs_ = 1

     for pile_no_i, pilei in setup_dict['pile_coords'].items():

          fig, ax = plt.subplots(1, 2, figsize=(14, 10))

          for depth_ploti in depth_py_curve_plot:
              
              depth_plot_python_idx = np.where((np.round(output_dicti[final_load_python]['x']['z_dis'], 2) < depth_ploti + setup_dict['dz']/2) & (np.round(output_dicti[final_load_python]['x']['z_dis'], 2) > depth_ploti - setup_dict['dz']/2))[0][0]
              
              if pile_ax in ['x', 'y']: 
                    y_z_python = [abs_*output_dicti[key][pile_ax]['y_dis'][depth_plot_python_idx] for key in output_dicti.keys()]
                    p_z_python = [abs_*output_dicti[key][pile_ax]['p_dis'][depth_plot_python_idx] for key in output_dicti.keys()]
              else:
                    y_z_python = np.sqrt(np.power(np.array([abs_*output_dicti[key]['x']['y_dis'][depth_plot_python_idx] for key in output_dicti.keys()]), 2) + np.power(np.array([abs_*output_dicti[key]['y']['y_dis'][depth_plot_python_idx] for key in output_dicti.keys()]), 2))
                    p_z_python = np.sqrt(np.power(np.array([abs_*output_dicti[key]['x']['p_dis'][depth_plot_python_idx] for key in output_dicti.keys()]), 2) + np.power(np.array([abs_*output_dicti[key]['y']['p_dis'][depth_plot_python_idx] for key in output_dicti.keys()]), 2))
               
              ax[0].plot(y_z_python, p_z_python, color='k')
              ax[1].plot(y_z_python, p_z_python, color='k')

              if len(data_global_splice) > 0: 
                    depth_plot_adji = depth_ploti - setup_dict['global_scour']
                    depth_plot_splice_index = min(data_py_splice.keys(), key=lambda k: abs(k - depth_plot_adji))
                    y_z_splice = data_py_splice[depth_plot_splice_index]['y']
                    p_z_splice = [i*setup_dict['b'] for i in data_py_splice[depth_plot_splice_index]['p']]
                                        
                    ax[0].plot(y_z_splice, p_z_splice, ls='--', color='r')
                    ax[1].plot(y_z_splice, p_z_splice, ls='--', color='r')

          ax[0].plot([-1, -1], [-1, -1], color='k', label='python')
          ax[0].plot([-1, -1], [-1, -1], ls='--', color='r', label='splice')
          ax[0].legend(loc='lower left')

          ax[0].set_xlim(0, 0.1)
          ax[0].set_ylim(0, 600)
          ax[1].set_xlim(0, 0.0025)
          ax[1].set_ylim(0, 200)

          ax[0].grid('on')
          ax[1].grid('on')
          ax[0].set_xlabel("Lateral displacement, y (m)")
          ax[1].set_xlabel("Lateral displacement, y (m)")
          ax[0].set_ylabel("Lateral soil resistance, p (kN/m)")
          fig.suptitle(location_loop_dict['location_loop'][0])
          plt.savefig(Path(result_folder)/result_sub_folder/('p-y_' + pile_ax + '_pile_no_'+str(pile_no_i) + '.png'))
          plt.close()