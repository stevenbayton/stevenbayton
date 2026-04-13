# python modules
import subprocess
import os
from pathlib import Path
import pandas as pd
import numpy as np
import re

def save_grl_weap_srp(calculation_name, parent_input, results_dict_base, results_dict_shaft, z_in_soil_dis, soil_type_dis, quake_damp_dict, a_base_annulus, a_base_bo, a_shaft_inner, a_shaft_outer, plug_output_base, output_folder='output'):

    q_s_dis = []

    for idx, depth_i in enumerate(z_in_soil_dis):
        shaft_parameter_inc_i = results_dict_shaft["shaft_parameter_inc"][idx]
        q_s_ave = []
        for section_i in range(1, 10):
            if any(['z_s_section_'+str(section_i) in key for key in shaft_parameter_inc_i.keys()]):
                z_s_inc = shaft_parameter_inc_i['z_s_section_'+str(section_i) + '[calc_s]']
                if z_s_inc == depth_i:
                    q_s_ave.append(shaft_parameter_inc_i['q_s_section_' + str(section_i) + '[calc_s]'])

        q_s_dis.append(np.average(q_s_ave))
          
    q_b_dis = []

    for idx, depth_i in enumerate(z_in_soil_dis):
        base_parameter_inc_i = results_dict_base["base_parameter_inc"][idx]
        q_b_ave = []
        for section_i in range(1, 10):
            if any(['z_b_section_'+str(section_i) in key for key in base_parameter_inc_i.keys()]):
                z_b_inc = base_parameter_inc_i['z_b_section_'+str(section_i) + '[calc_b]']
                if z_b_inc == depth_i:
                    q_b_ave.append(base_parameter_inc_i['q_b_section_' + str(section_i) + '[calc_b]'])

        q_b_dis.append(np.average(q_b_ave))

    quake_sand_shaft = quake_damp_dict['quake_sand_shaft']
    quake_clay_shaft = quake_damp_dict['quake_clay_shaft']
    quake_sand_base = quake_damp_dict['quake_sand_base']
    quake_clay_base = quake_damp_dict['quake_clay_base']
    damping_sand_shaft = quake_damp_dict['damping_sand_shaft']
    damping_clay_shaft = quake_damp_dict['damping_clay_shaft']
    damping_sand_base = quake_damp_dict['damping_sand_base']
    damping_clay_base = quake_damp_dict['damping_clay_base']

    quake_shaft_dis = []
    quake_base_dis = []
    damping_shaft_dis = []
    damping_base_dis = []

    for soil_type_i in soil_type_dis:
        
        if soil_type_i.lower() in ['s', 's_c', 'si']:
            quake_shaft_dis.append(quake_sand_shaft)
            quake_base_dis.append(quake_sand_base)
            damping_shaft_dis.append(damping_sand_shaft)
            damping_base_dis.append(damping_sand_base)

        elif soil_type_i.lower() in ['c', 'c_s']:
            quake_shaft_dis.append(quake_clay_shaft)
            quake_base_dis.append(quake_clay_base)
            damping_shaft_dis.append(damping_clay_shaft)
            damping_base_dis.append(damping_clay_base)

    if plug_output_base.lower() == 'cored':
        base_area = a_base_annulus
        shaft_area = a_shaft_inner + a_shaft_outer
    else:
        base_area = a_base_bo
        shaft_area = a_shaft_outer

    setup_fac_dis = np.array([1 for xi in z_in_soil_dis])
    limit_dist_dis = np.zeros(len(z_in_soil_dis))
    setup_time_dis = np.zeros(len(z_in_soil_dis))
    shape_factor_dis = np.zeros(len(z_in_soil_dis))
    toe_area_dis = np.array([base_area for xi in z_in_soil_dis])

    save_folder = Path(parent_input["calculations_location"])/parent_input["python_calculation_folder"]/parent_input["foundation_calculation_folder"]/output_folder
    os.makedirs(save_folder/calculation_name/'grlweap', exist_ok=True)

    save_file_name = "SoilResistProfile" + str(z_in_soil_dis[-1]) + ".srp"

    with open(save_folder/calculation_name/'grlweap'/save_file_name, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<SoilResistProfile>\n')

        for i in range(len(z_in_soil_dis)):
            f.write('  <SoilResistEntry>\n')
            f.write(f'    <Depth>{z_in_soil_dis[i]}</Depth>\n')
            f.write(f'    <UnitShaftResist>{1000*q_s_dis[i]:.1f}</UnitShaftResist>\n')
            f.write(f'    <UnitToeResist>{1000*q_b_dis[i]:.1f}</UnitToeResist>\n')
            f.write(f'    <ShaftQuake>{0.001*quake_shaft_dis[i]:.4f}</ShaftQuake>\n')
            f.write(f'    <ToeQuake>{0.001*quake_base_dis[i]:.4f}</ToeQuake>\n')
            f.write(f'    <ShaftDamp>{damping_shaft_dis[i]:.2f}</ShaftDamp>\n')
            f.write(f'    <ToeDamp>{damping_base_dis[i]:.2f}</ToeDamp>\n')
            f.write(f'    <SetupFac>{setup_fac_dis[i]}</SetupFac>\n')
            f.write(f'    <LimitDist>{limit_dist_dis[i]}</LimitDist>\n')
            f.write(f'    <SetupTime>{setup_time_dis[i]}</SetupTime>\n')
            f.write(f'    <ShapeFactor>{shape_factor_dis[i]}</ShapeFactor>\n')
            f.write(f'    <ToeArea>{toe_area_dis[i]:.5f}</ToeArea>\n')
            f.write('  </SoilResistEntry>\n')

        f.write('</SoilResistProfile>\n')


def save_grl_weap_gwwb(driving_depth,
                       efficiency,
                       hammer_dict,
                       calculation_name, 
                       parent_input, 
                       results_dict_base, 
                       results_dict_shaft, 
                       z_in_soil_dis, 
                       soil_type_dis, 
                       quake_damp_dict, 
                       b_outer,
                       a_base_annulus, 
                       a_base_bo, 
                       a_shaft_inner, 
                       a_shaft_outer, 
                       total_pile_length,
                       plug_output_base, 
                       output_folder='output'):
    
    # File save
    input_heading = hammer_dict['input_heading']
    
    # Driving parameters
    wait_time = 1

    # Hammer parameters
    hammer_id = hammer_dict['hammer_id']
    hammer_name = hammer_dict['hammer_name']
    hammer_type = hammer_dict['hammer_type']
    stroke = 1.82

    # Pile parameters
    pile_inclination = 0
    pile_type = 3 # 2 = PipeCloseEnd, 3 = PipeOpenEnd
    pile_material = 'S'
    pile_cor = 0.85
    no_pile_segments = 1
    depth_start_pile_segment = 0
    depth_end_pile_segment = total_pile_length
    e_pile = 210000
    sw_pile = 77.5

    # Soil parameters
    shaft_gain_loss = 1
    toe_gain_loss = 1    
    q_s_dis = []

    for idx, depth_i in enumerate(z_in_soil_dis):
        shaft_parameter_inc_i = results_dict_shaft["shaft_parameter_inc"][idx]
        q_s_ave = []
        for section_i in range(1, 10):
            if any(['z_s_section_'+str(section_i) in key for key in shaft_parameter_inc_i.keys()]):
                z_s_inc = shaft_parameter_inc_i['z_s_section_'+str(section_i) + '[calc_s]']
                if z_s_inc == depth_i:
                    q_s_ave.append(shaft_parameter_inc_i['q_s_section_' + str(section_i) + '[calc_s]'])

        q_s_dis.append(np.average(q_s_ave))
          
    q_b_dis = []

    for idx, depth_i in enumerate(z_in_soil_dis):
        base_parameter_inc_i = results_dict_base["base_parameter_inc"][idx]
        q_b_ave = []
        for section_i in range(1, 10):
            if any(['z_b_section_'+str(section_i) in key for key in base_parameter_inc_i.keys()]):
                z_b_inc = base_parameter_inc_i['z_b_section_'+str(section_i) + '[calc_b]']
                if z_b_inc == depth_i:
                    q_b_ave.append(base_parameter_inc_i['q_b_section_' + str(section_i) + '[calc_b]'])

        q_b_dis.append(np.average(q_b_ave))

    quake_sand_shaft = quake_damp_dict['quake_sand_shaft']
    quake_clay_shaft = quake_damp_dict['quake_clay_shaft']
    quake_sand_base = quake_damp_dict['quake_sand_base']
    quake_clay_base = quake_damp_dict['quake_clay_base']
    damping_sand_shaft = quake_damp_dict['damping_sand_shaft']
    damping_clay_shaft = quake_damp_dict['damping_clay_shaft']
    damping_sand_base = quake_damp_dict['damping_sand_base']
    damping_clay_base = quake_damp_dict['damping_clay_base']

    quake_shaft_dis = []
    quake_base_dis = []
    damping_shaft_dis = []
    damping_base_dis = []

    for soil_type_i in soil_type_dis:
        
        if soil_type_i.lower() in ['s', 's_c', 'si']:
            quake_shaft_dis.append(quake_sand_shaft)
            quake_base_dis.append(quake_sand_base)
            damping_shaft_dis.append(damping_sand_shaft)
            damping_base_dis.append(damping_sand_base)

        elif soil_type_i.lower() in ['c', 'c_s']:
            quake_shaft_dis.append(quake_clay_shaft)
            quake_base_dis.append(quake_clay_base)
            damping_shaft_dis.append(damping_clay_shaft)
            damping_base_dis.append(damping_clay_base)

    if plug_output_base.lower() == 'cored':
        base_area = a_base_annulus
        shaft_area = a_shaft_inner + a_shaft_outer
    else:
        base_area = a_base_bo
        shaft_area = a_shaft_outer

    setup_fac_dis = np.array([1 for xi in z_in_soil_dis])
    toe_area_dis = np.array([10000*base_area for xi in z_in_soil_dis])
  

    save_folder = Path(parent_input["calculations_location"])/parent_input["python_calculation_folder"]/parent_input["foundation_calculation_folder"]/output_folder
    os.makedirs(save_folder/calculation_name/'grlweap', exist_ok=True)

    save_file_name = input_heading + "_" + str(z_in_soil_dis[-1]) + ".gwwb"

    with open(save_folder/calculation_name/'grlweap'/save_file_name, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<GRLWeap Version="2021.1.20.1">\n')

        f.write('  <GeneralInfo>\n')
        f.write('    <UnitIndex>0</UnitIndex>\n')
        f.write('  </GeneralInfo>\n')

        f.write('  <ProjectConfig>\n')

        # Project info
        f.write('    <ProjInfo>\n')
        f.write(f'      <ProjNo>project</ProjNo>\n')
        f.write(f'      <ProjDesc>desc</ProjDesc>\n')
        f.write('      <PileName />\n')
        f.write('    </ProjInfo>\n')

        f.write('    <InputOptions>\n')

        # General driving settings
        f.write('      <DriveabilityGLFactor>\n')
        f.write('        <GainLossFac>\n')
        f.write(f'          <ShaftGainLoss>{shaft_gain_loss}</ShaftGainLoss>\n')
        f.write(f'          <ToeGainLoss>{toe_gain_loss}</ToeGainLoss>\n')
        f.write('        </GainLossFac>\n')
        f.write('      </DriveabilityGLFactor>\n')

        # Driving chart, one depth per execution since friction fatigue included
        f.write('      <DrivingTable>\n')
        f.write('        <DrivingTableRow>\n')
        f.write(f'          <Depth>{driving_depth}</Depth>\n')
        f.write(f'          <TempLength>{total_pile_length}</TempLength>\n')
        f.write(f'          <WaitTime>{wait_time}</WaitTime>\n')
        f.write(f'          <HammerData>\n')
        f.write(f'            <CurrentEfficiency>{efficiency}</CurrentEfficiency>\n')
        f.write(f'            <CurrentStroke>{stroke}</CurrentStroke>\n')
        f.write(f'          </HammerData>\n')
        f.write(f'        </DrivingTableRow>\n')
        f.write('      </DrivingTable>\n')
        f.write('    </InputOptions>\n')

        # General driving settings
        f.write('    <AnalysisOptions>\n')
        f.write(f'      <AnalysisType>4</AnalysisType>\n') # 4 = driveability analysis
        f.write(f'      <SRDSource>0</SRDSource>\n') # 0 = standard setup method
        f.write(f'      <SoilDampOption>0</SoilDampOption>\n') # 0 = smith damping
        f.write('      <RSACycleNum>0</RSACycleNum>\n')
        f.write('      <AssGravity>9.81</AssGravity>\n')
        f.write('      <PileGravity>9.81</PileGravity>\n')
        f.write('      <DriveGravity>9.81</DriveGravity>\n')
        f.write('      <IterationNum>0</IterationNum>\n')
        f.write('      <NumericOutput>1</NumericOutput>\n')
        f.write('    </AnalysisOptions>\n')

        f.write('  </ProjectConfig>\n')

        # Soil parameters
        f.write('  <SoilInput>\n')
        f.write('    <Soil1>\n')
        f.write('      <SoilResistTableCollection>\n')
        f.write(f'        <SoilResistTable StartDepthIndex="{0}" EndDepthIndex="{len(z_in_soil_dis)-1}">\n')
        f.write('          <SoilResistTableData>\n')

        for i in range(len(z_in_soil_dis)):
            f.write('            <SoilTableRow>\n')
            f.write(f'              <Depth>{z_in_soil_dis[i]}</Depth>\n')
            f.write(f'              <UnitRs_LTSR>{1000*q_s_dis[i]:.1f}</UnitRs_LTSR>\n') # kPa
            f.write(f'              <UnitToeResist>{1000*q_b_dis[i]:.1f}</UnitToeResist>\n') # kPa
            f.write(f'              <ShaftQuake>{quake_shaft_dis[i]:.1f}</ShaftQuake>\n') # mm
            f.write(f'              <ToeQuake>{quake_base_dis[i]:.1f}</ToeQuake>\n') # mm
            f.write(f'              <ShaftDamp>{damping_shaft_dis[i]:.2f}</ShaftDamp>\n')
            f.write(f'              <ToeDamp>{damping_base_dis[i]:.2f}</ToeDamp>\n')
            f.write(f'              <ToeArea>{toe_area_dis[i]:.5f}</ToeArea>\n') # cm2
            f.write(f'              <SetupFac>{setup_fac_dis[i]}</SetupFac>\n')
            f.write('            </SoilTableRow>\n')

        f.write('          </SoilResistTableData>\n')
        f.write('        </SoilResistTable>\n')
        f.write('      </SoilResistTableCollection>\n')
        f.write('    </Soil1>\n')
        f.write('  </SoilInput>\n')

        # Pile segments parameters
        f.write('  <PileInput>\n')
        f.write('    <Pile1>\n')
        f.write('      <GeneralInfo>\n')
        f.write(f'        <TotalPileLength>{total_pile_length}</TotalPileLength>\n')
        f.write(f'        <FinalPeneDepth>{driving_depth}</FinalPeneDepth>\n')
        f.write(f'        <PileInclination>{pile_inclination}</PileInclination>\n')
        f.write(f'        <PileType>{pile_type}</PileType>\n')
        f.write(f'        <PileMaterial>{pile_material}</PileMaterial>\n') 
        f.write(f'        <PileSize>{b_outer}</PileSize>\n')
        f.write(f'        <ToeArea>{base_area}</ToeArea>\n')
        f.write('        <PileSegOption>0</PileSegOption>\n')
        f.write(f'        <PileTopCOR>{pile_cor}</PileTopCOR>\n')
        f.write(f'        <PileSegmentCount>{no_pile_segments}</PileSegmentCount>\n')
        f.write('      </GeneralInfo>\n')
        f.write('      <PileTableCollection>\n')
        f.write(f'        <PileTable StartDepthIndex="{0}" EndDepthIndex="{len(z_in_soil_dis)-1}">\n')
        f.write('          <PileTableData>\n')

        ##### If many pile segments create a loop here
        f.write('            <PileTableRow>\n')
        f.write(f'              <Depth>{depth_start_pile_segment}</Depth>\n')
        f.write(f'              <Area>{10000*a_base_annulus}</Area>\n') # cm2
        f.write(f'              <EModulus>{e_pile}</EModulus>\n') # Mpa
        f.write(f'              <SpecWt>{sw_pile}</SpecWt>\n') # kn/m2
        f.write(f'              <Perimeter>{shaft_area}</Perimeter>\n') # m
        f.write('              <CriticalIndex>0</CriticalIndex>\n')
        f.write('            </PileTableRow>\n')
        f.write('            <PileTableRow>\n')
        f.write(f'              <Depth>{depth_end_pile_segment}</Depth>\n')
        f.write(f'              <Area>{10000*a_base_annulus}</Area>\n') # cm2
        f.write(f'              <EModulus>{e_pile}</EModulus>\n') # Mpa
        f.write(f'              <SpecWt>{sw_pile}</SpecWt>\n') # kn/m2
        f.write(f'              <Perimeter>{shaft_area}</Perimeter>\n') # m
        f.write('              <CriticalIndex>0</CriticalIndex>\n')
        f.write('            </PileTableRow>\n')
        f.write('          </PileTableData>\n')
        f.write('        </PileTable>\n')
        f.write('      </PileTableCollection>\n')
        f.write('    </Pile1>\n')
        f.write('  </PileInput>\n')

        # Hammer parameters
        f.write('  <HammerInput>\n')
        f.write('    <SelectedHammers>\n')
        f.write(f'      <HammerData HammerID="{hammer_id}" HammerName="{hammer_name}" HammerType="{hammer_type}">\n')
        f.write(f'        <CurrEfficiency>{efficiency}</CurrEfficiency>\n')
        f.write(f'        <CurrentStroke>{stroke}</CurrentStroke>\n')
        f.write('        <StrokeIncr>0</StrokeIncr>\n')
        f.write('        <DriveSystem>\n')
        f.write('          <HammerCushion>\n')
        f.write('            <Area>0.0</Area>\n')
        f.write('            <Thickness>0.0</Thickness>\n')
        f.write('            <EModulus>0.0</EModulus>\n')
        f.write('            <COR>0.85</COR>\n')
        f.write('            <Stiffness>0.0</Stiffness>\n')
        f.write('          </HammerCushion>\n')
        f.write('          <Helmet>\n')
        f.write('            <HelmetSeg>\n')
        f.write('              <Weight>0.0</Weight>\n')
        f.write('            </HelmetSeg>\n')
        f.write('          </Helmet>\n')
        f.write('        </DriveSystem>\n')

        ### Only used for bearing graph and inspector chart analysis, not in driveabilty analysis
        f.write('        <SoilGeneralParam>\n')
        f.write('          <ShaftQuake>2.5</ShaftQuake>\n')
        f.write('          <ToeQuake>2.5</ToeQuake>\n')
        f.write('          <ShaftDamp>0.25</ShaftDamp>\n')
        f.write('          <ToeDamp>0.5</ToeDamp>\n')
        f.write('        </SoilGeneralParam>\n')
        f.write('      </HammerData>\n')
        f.write('    </SelectedHammers>\n')
        f.write('  </HammerInput>\n')
        f.write('</GRLWeap>\n')

    file_location_name = save_folder/calculation_name/'grlweap'/save_file_name

    return file_location_name


def run_grl_weap(file_location_name, efficiency):

    exe_path = r"C:\Program Files (x86)\PDI\GRLWEAP 14\DIGW14.exe"

    subprocess.run([exe_path, file_location_name])
    # subprocess.run([exe_path, file_location_name], check=True)

    output_file_location = os.path.dirname(file_location_name)
    output_file_name = os.path.basename(file_location_name).split('.gwwb')[0] + '.gwwo'

    output_file = output_file_location + "//" + output_file_name

    results_dict_grl = read_grl_ouput_file(output_file, efficiency)

    return results_dict_grl


def load_grl_output_file(path):

    with open(path, encoding="utf-8") as f:

        return [line.rstrip("\n") for line in f]
    

def clean_line(line):
    line = line.replace("\u00a0", " ")

    line = re.sub(r"(?<=\d) (?=\d)", "", line)

    return line.rstrip("\n")


def is_numeric_row(line):

    return bool(re.match(r"^\d", line))


def parse_soil_resistance(lines):

    soil_resistance_inc = []
    in_table = False

    for line in lines:
        line = clean_line(line)

        if line.startswith("Depth") and "Unit Rs" in line:
            in_table = True
            continue

        if in_table and line.startswith("m"):
            continue

        if not in_table:
            continue

        if not line or not is_numeric_row(line):
            break

        parts = re.split(r"\s+", line)

        soil_resistance_inc.append({"z_grl_section_1[output_grl]": float(parts[0]),
                                    "q_s_grl_section_1[output_grl]": 0.001*float(parts[1]),
                                    "q_b_grl_section_1[output_grl]": 0.001*float(parts[2])})
                
    return soil_resistance_inc


def parse_pile_stress(lines):

    pile_stress_inc = []
    in_table = False

    for line in lines:
        line = clean_line(line)

        if line.startswith("Lb Top") and "Mx.T-For." in line:
            in_table = True
            continue

        if in_table and line.startswith("m"):
            continue

        if not in_table:
            continue

        if not line or not is_numeric_row(line):
            break

        parts = re.split(r"\s+", line)

        pile_stress_inc.append({"z_grl_section_1[output_grl]": float(parts[0]),
                                "T_max_grl_section_1[output_grl]": 0.001*float(parts[1]),
                                "C_max_grl_section_1[output_grl]": 0.001*float(parts[2]),
                                "t_max_grl_section_1[output_grl]": float(parts[3]),
                                "c_max_grl_section_1[output_grl]": float(parts[4]),
                                "v_max_grl_section_1[output_grl]": float(parts[5]),
                                "d_max_grl_section_1[output_grl]": 0.001*float(parts[6]),
                                "E_grl_section_1[output_grl]": float(parts[7]),})
        
    return pile_stress_inc


def parse_summary(lines, efficiency):

    in_table = False

    for line in lines:
        line = clean_line(line)

        if line.startswith("Depth") and "Rut" in line:
            in_table = True
            continue

        if in_table and line.startswith("m         kN        kN"):
            continue

        if not in_table:
            continue

        if not line or not is_numeric_row(line):
            break

        parts = re.split(r"\s+", line)

        summary_blow = {"z_grl[output_grl]": float(parts[0]),
                        "Q_t_grl[output_grl]": 0.001*float(parts[1]),
                        "Q_s_grl[output_grl]": 0.001*float(parts[2]),
                        "Q_b_grl[output_grl]": 0.001*float(parts[3]),
                        "blc_grl[output_grl]": float(parts[4]),
                        "efficiency_grl[output_grl]": efficiency}
                
    return summary_blow
    

def read_grl_ouput_file(output_file, efficiency):

    output_lines = load_grl_output_file(output_file)

    soil_resistance_inc = parse_soil_resistance(output_lines)
    pile_stress_inc = parse_pile_stress(output_lines)
    summary_blow = parse_summary(output_lines, efficiency)

    results_dict_grl = {"grl_soil_resistance_inc": soil_resistance_inc,
                        "grl_pile_stress_inc": pile_stress_inc,
                        **summary_blow}
 
    return results_dict_grl


def stress_fatigue_analysis(output_result_save_breakdown, 
                            count_blow_results_dict,
                            a_base_global_dis,
                            s_n_curve,
                            scf=1.15):
    
    m, loga, k = s_n_curve_extract(s_n_curve)

    penetration_depth_array = count_blow_results_dict['penetration_depth_array']
    count_blow_interval_array = count_blow_results_dict['count_blow_interval_array']

    for depth_i in output_result_save_breakdown.keys():
        if 'grl_pile_stress_inc' in output_result_save_breakdown[depth_i]:
            stress_fatigue_dict = {}
            for grl_pile_stress_i in output_result_save_breakdown[depth_i]['grl_pile_stress_inc']:
                stress_fatigue_dict[grl_pile_stress_i['z_grl_section_1[output_grl]']] = {'t_max': [], 
                                                                                         'c_max': [], 
                                                                                         'count_blow_interval': [], 
                                                                                         'penetration_depth': []}

    for penetration_depth_i, count_blow_interval_i in zip(penetration_depth_array, count_blow_interval_array):
        grl_stress_i = output_result_save_breakdown[penetration_depth_i]['grl_pile_stress_inc']
        for stress_dict_i in grl_stress_i:
            depth_extract = stress_dict_i['z_grl_section_1[output_grl]']
            t_max_extract = stress_dict_i['t_max_grl_section_1[output_grl]']
            c_max_extract = stress_dict_i['c_max_grl_section_1[output_grl]']
            stress_fatigue_dict[depth_extract]['t_max'].append(t_max_extract)
            stress_fatigue_dict[depth_extract]['c_max'].append(c_max_extract)
            stress_fatigue_dict[depth_extract]['count_blow_interval'].append(count_blow_interval_i)
            stress_fatigue_dict[depth_extract]['penetration_depth'].append(penetration_depth_i)
    
    for stress_depth_i, data_i in stress_fatigue_dict.items():
        for a_base_global_i in a_base_global_dis:
            if stress_depth_i <= a_base_global_i[0]:
                thickness_i = a_base_global_i[5]
                break

        stress_range_i = np.array(data_i['c_max']) + np.array(data_i['t_max'])
        count_blow_interval_i = np.array(data_i['count_blow_interval'])
        a = stress_range_i*scf*np.power(thickness_i/0.025, k)
        b = np.power(10, (loga - m*np.log10(a)))
        c = count_blow_interval_i/b
        acc_damage = sum(c)

        stress_fatigue_dict[stress_depth_i]['acc_damage'] = acc_damage

    return stress_fatigue_dict

def count_blow(output_result_save):

    penetration_depth_array = []
    bct_depth_array = []
    count_blow_interval_array = []
    count_blow_total_array = []
    depth_0 = 0
    for depth_i in output_result_save.keys():
        if 'z_grl[output_grl]' in output_result_save[depth_i]:
            z_grl = output_result_save[depth_i]['z_grl[output_grl]']
            blc_grl = output_result_save[depth_i]['blc_grl[output_grl]']
            penetration_depth_array.append(z_grl)
            bct_depth_array.append(blc_grl)
            depth_interval = z_grl - depth_0
            count_blow_interval = blc_grl*depth_interval
            count_blow_interval_array.append(count_blow_interval)
            if len(count_blow_total_array) == 0:
                count_blow_total_array.append(count_blow_interval)
            else:
                count_blow_total_array.append(count_blow_total_array[-1]+count_blow_interval)
            depth_0 = z_grl

            output_result_save[depth_i]['count_blow_interval[output_grl]'] = count_blow_interval_array[-1]
            output_result_save[depth_i]['count_blow_total[output_grl]'] = count_blow_total_array[-1]

    count_blow_results_dict = {'penetration_depth_array': penetration_depth_array,
                               'count_blow_interval_array': count_blow_interval_array}

    return output_result_save, count_blow_results_dict


def s_n_curve_extract(s_n):

    s_n_curve_dict = {  'B1':   {'m': 4,
                                'loga': 15.117,
                                'k': 0},
                        'B2':    {'m': 4,
                                  'loga': 14.885,
                                  'k': 0},
                        'C':    {'m': 3,
                                'loga': 12.592,
                                'k': 0.05},
                        'C1':   {'m': 3,
                                'loga': 12.449,
                                'k': 0.1},
                        'C2':   {'m': 3,
                                'loga': 12.301,
                                'k': 0.15},
                        'D':    {'m': 3,
                                'loga': 12.164,
                                'k': 0.2},
                        'E':    {'m': 3,
                                'loga': 12.010,
                                'k': 0.2},
                        'F':    {'m': 3,
                                'loga': 11.855,
                                'k': 0.25},
                        'F1':   {'m': 3,
                                'loga': 11.699,
                                'k': 0.25},
                        'F3':   {'m': 3,
                                'loga': 11.546,
                                'k': 0.25},
                        'G':    {'m': 3,
                                'loga': 11.398,
                                'k': 0.25},
                        'W1':   {'m': 3,
                                'loga': 11.261,
                                'k': 0.25},
                        'W2':   {'m': 3,
                                'loga': 11.107,
                                'k': 0.25},
                        'W3':   {'m': 3,
                                'loga': 10.970,
                                'k': 0.25}}
    
    m = s_n_curve_dict[s_n]['m']
    loga = s_n_curve_dict[s_n]['loga']
    k = s_n_curve_dict[s_n]['k']

    return m, loga, k
