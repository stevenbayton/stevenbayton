import numpy as np

def extract_res_1(verification_file_location, verification_file_name, file_type=".res1"):
    
    data_splice = {}

    with open(verification_file_location/(verification_file_name+file_type), 'r') as file:

        read = 0

        for line in file:

            line = line.strip()

            if "COMPLETE P-Y / T-Z / Q-Z RESULTS" in line:
                line_split = line.split()
                line_split = [i for i in line_split if ':' not in i]
                idx_depth = line_split.index('DEPTH')
                depth = float(line_split[idx_depth+1])
                data_splice[depth] = {}
                data_splice[depth]['p'] = []
                data_splice[depth]['y'] = []

            if "#" in line or "Program GENSOD" in line:
                read = 0

            if read:
                line_split = line.split()
                if len(line_split) > 1:
                    data_splice[depth]['p'].append(float(line_split[1]))
                    data_splice[depth]['y'].append(float(line_split[2]))

            if "POINT   PY-STRESS  PY-DISPLC    TZ-STRESS  TZ-DISPLC    QZ-STRESS  QZ-DISPLC" in line:
                read = 1

    return data_splice


def extract_res_2(verification_file_location, verification_file_name, file_type=".res2"):
    
    with open(verification_file_location/(verification_file_name+file_type), 'r') as file:

        read1 = 0
        read2 = 0
        pile_geometry = {}
        loads = {}

        for line in file:

            line = line.strip()

            if "Dummy pile" in line:
                read1 = 0

            if read1:
                line_split = line.split()
                pile_number = float(line_split[1])
                pile_geometry[pile_number] = {}
                pile_geometry[pile_number]['dx'] = float(line_split[4])
                pile_geometry[pile_number]['dy'] = float(line_split[5])
                pile_geometry[pile_number]['dz'] = float(line_split[6])

            if read2:
                line_split = line.split()
                loads['f_x'] = float(line_split[2])
                loads['f_y'] = float(line_split[3])
                loads['f_z'] = float(line_split[4])
                loads['m_xx'] = float(line_split[5])
                loads['m_yy'] = float(line_split[6])
                loads['m_zz'] = float(line_split[7])
                read2 = 0

            if "Pile NGEN NSYM   X1-Y1-Z1-(Pile head coords)    X2-Y2-Z2-(Pile tip coords)" in line:
                read1 = 1

            if "Pile  X-force      Y-force      Z-force     XX-moment    YY-moment   ZZ-moment" in line:
                read2 = 1

    return pile_geometry, loads
                

def extract_res_3(verification_file_location, verification_file_name, file_type=".res3"):
    
    pile_number = []

    with open(verification_file_location/(verification_file_name+file_type), 'r') as file:

        read = 0

        for line in file:

            line = line.strip()

            if "CONDITIONS ALONG PILE" in line:
                line_split = line.split()
                pile_number_i = float(line_split[3])
                if pile_number_i not in pile_number:
                    pile_number.append(pile_number_i)

    data_splice = {}

    for pile_number_i in pile_number:
        data_splice[pile_number_i] = {}

    with open(verification_file_location/(verification_file_name+file_type), 'r') as file:

        read1 = 0
        read2 = 0

        for line in file:

            line = line.strip()

            if "CONDITIONS ALONG PILE" in line:
                line_split = line.split()
                pile_number_i = float(line_split[3])

            if "TOTAL LOAD/DISP" in line:
                line_split = line.split()
                load_inc = float(line_split[6])

                for pile_number_i in pile_number:
                    data_splice[pile_number_i][load_inc] = {}
                    data_splice[pile_number_i][load_inc]['z'] = []
                    data_splice[pile_number_i][load_inc]['dx'] = []
                    data_splice[pile_number_i][load_inc]['dy'] = []
                    data_splice[pile_number_i][load_inc]['dz'] = []
                    data_splice[pile_number_i][load_inc]['mxx'] = []
                    data_splice[pile_number_i][load_inc]['myy'] = []
                    data_splice[pile_number_i][load_inc]['fz'] = []
                    data_splice[pile_number_i][load_inc]['px'] = []
                    data_splice[pile_number_i][load_inc]['py'] = []

            if "#" in line:
                read1 = 0
                read2 = 0

            if read1:
                line_split = line.split()
                if len(line_split) > 1:
                    data_splice[pile_number_i][load_inc]['z'].append(float(line_split[-10]))
                    data_splice[pile_number_i][load_inc]['dx'].append(float(line_split[-9]))
                    data_splice[pile_number_i][load_inc]['dy'].append(float(line_split[-8]))
                    data_splice[pile_number_i][load_inc]['dz'].append(float(line_split[-7]))
                    data_splice[pile_number_i][load_inc]['mxx'].append(float(line_split[-3]))
                    data_splice[pile_number_i][load_inc]['myy'].append(float(line_split[-2]))
                    data_splice[pile_number_i][load_inc]['fz'].append(float(line_split[-1]))

            if read2:
                line_split = line.split()
                if len(line_split) > 1:
                    data_splice[pile_number_i][load_inc]['px'].append(float(line_split[-7]))
                    data_splice[pile_number_i][load_inc]['py'].append(float(line_split[-6]))

            if "X          Y          Z         X         Y         Z       XX-LOCAL   YY-LOCAL    FORCE" in line:
                read1 = 1

            if "X-LOCAL    Y-LOCAL    STRESS     X-LOCAL   Y-LOCAL    AXIAL    TORSION    LATERAL  AXIAL    RATIO" in line:
                read2 = 1

    return data_splice

