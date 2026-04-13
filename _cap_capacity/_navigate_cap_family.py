# python modules
import math
import numpy as np
import subprocess
import shutil
import re

def run_CAP(main_folder, foundation_location_name,input_heading, b_save, b1, l1, calc_type='CAP', subfolder='executables'):
    try:
        subprocess.run(['CAP.exe'], cwd=str(main_folder/subfolder/calc_type), shell=True, stderr=subprocess.DEVNULL)
        SF_min, z_slip_min, angle_min, SF_array, z_slip_array, angle_array, output_file = output_file_CAP(main_folder, foundation_location_name, input_heading, b_save, b1, l1)
    except:
        print('CAP calculation did not run')
        SF_min = np.nan
        z_slip_min = np.nan
        angle_min = np.nan
        SF_array = []
        z_slip_array = []
        angle_array = []
        output_file = {}

    results_dict = {"SF[output]": SF_array,
                    "z[output]": z_slip_array,
                    "angle[output]": angle_array}
        
    return results_dict, output_file

def run_CAPT(main_folder, foundation_location_name, input_heading, b_save, b1, l1, calc_type='CAPT', subfolder='executables'):
    try:
        subprocess.run(['CAPT.exe'], cwd=str(main_folder/subfolder/calc_type), shell=True, stderr=subprocess.DEVNULL)
        SF_min, z_slip_min, angle_min, SF_array, z_slip_array, angle_array, output_file = output_file_CAPT(main_folder, foundation_location_name, input_heading, b_save, b1, l1)    
    except:
        print('CAPT calculation did not run')
        SF_min = np.nan
        z_slip_min = np.nan
        angle_min = np.nan
        SF_array = []
        z_slip_array = []
        angle_array = []
        output_file = {}

    results_dict = {"SF[output]": SF_array,
                    "z[output]": z_slip_array,
                    "angle[output]": angle_array}
        
    return results_dict, output_file

def run_CARL(main_folder, foundation_location_name, input_heading, b_save, b1, l1, calc_type='CARL', subfolder='executables'):
    try:
        subprocess.run(['CARL.exe'], cwd=str(main_folder/subfolder/calc_type), shell=True, stderr=subprocess.DEVNULL)
        SF_min, z_slip_min, x_slip_min, SF_array, z_slip_array, x_slip_array, output_file = output_file_CARL(main_folder, foundation_location_name, input_heading, b_save, b1, l1)
    except:
        print('CARL calculation did not run')
        SF_min = np.nan
        z_slip_min = np.nan
        x_slip_min = np.nan
        SF_array = []
        z_slip_array = []
        x_slip_array = []
        output_file = {}

    results_dict = {"SF[output]": SF_array,
                    "z[output]": z_slip_array,
                    "x[output]": x_slip_array}
        
    return results_dict, output_file


def input_file_CAP(foundation_location_name, input_heading, input_dict, b_save, b1, b2, pf_mat, V_design, H_design, M_design, main_folder, z_emb_start=0, z_emb_end=0, zstep=0, WH=0, WT=0, phi_int=25, subfolder='executables', calc_type='CAP'):
    
    z = input_dict['z']
    su_C = input_dict['su_C_u']
    su_D = input_dict['su_D_u']
    su_E = input_dict['su_E_o']
    
    GAMS = 0.019
    GAMW = 0.01
    PS = 0

    file_name = "_".join([foundation_location_name, input_heading, str(round(b_save, 2)), str(round(z_emb_start, 2))]).lower()
    input_file_save = main_folder/subfolder/calc_type/(file_name + '_CAP.in')
    input_file = main_folder/subfolder/calc_type/'CAPin'
    file = open(input_file,'w')
    file.write('# Free format input #\n')
    file.write('#####################\n')
    file.write('Project Information\n')
    file.write('MN/M\n')
    file.write('#####\n')
    file.write('# 3 lines x 8 parameters\n')
    file.write('%0.1f %0.1f %0.1f %0.1f %0.1f %0.3f %0.2f %0.0f\n' %(b1, b2, z_emb_start, z_emb_end, zstep, GAMS, GAMW, PS))
        
    VS = VF = V_design
    VSTEP = 0
    H = H_design
    M = M_design
    
    REDBS_CAP = 0.5
    REDSS_CAP = 0.4
    CRACK = 1
    PASTYP = 0

    DELPH = WH  
    DELPT = WT
    
    LF = 1
    file.write('%0.3f %0.3f %0.3f %0.3f %0.3f %0.3f %0.3f %0.1f\n' %(VS, VF, VSTEP, H, M, DELPH, DELPT, LF))
    zstep = 0.2
    ZMAX = np.min((zstep*199, 3*b1 + z_emb_start))

    file.write('%0.1f %0.2f %0.1f %0.1f %0.0f %0.0f 0 0\n'%(ZMAX, zstep, REDBS_CAP, REDSS_CAP, CRACK, PASTYP))
    file.write('# 10 parameters\n')
    file.write('%0.0f 1 1 1 1 0 0 0 0 0\n' %(len(z)))
    file.write('# multiple lines x 5 parameters\n')
               
    e = abs(M/VS)
    p = (VS)/(b1*b2)
    if M != 0:
        pm = (M)/(b2*b1**2)*6
        x0 = p - pm
        x1 = p + pm
        ye = -b1/(x1 - x0)*x0                                                        # distance from heal to where combined stress equals zero
        xe = x1/(b1 - ye)*(2*e - ye)                                                 # magnitude of combined stress at 2e limit of CAP
        pav = (1/2*xe/(2*e)*((2*e - ye)) - (2/3)*WH)                            # average stress over the length of 2e for CAP minus 2/3rd of WH for the reduced effective stress
        suI = np.tan(np.radians(phi_int - 5))/pf_mat*pav        
    else:
        suI = su_D[0]
    
    for idx, (zi, suci, sudi, suei) in enumerate(zip(z, su_C, su_D, su_E)):
        if idx == 0:
            file.write('%0.3f %0.3f %0.3f %0.3f %0.3f\n' %(0, max(0.001, suci/1000), max(0.001, sudi/1000), max(0.001, suei/1000), max(0.001, suI/1000)))
        else:
            file.write('%0.3f %0.3f %0.3f %0.3f 0\n' %(zi, max(0.001, suci/1000), max(0.001, sudi/1000), max(0.001, suei/1000)))
   
    file.write('# 2 parameters\n')
    file.write('0 0')
    file.close()
    shutil.copy(input_file, input_file_save)
        
    return input_file_save

def input_file_CARL(foundation_location_name, input_heading, input_dict, b_save, b1, b2, V_design, H_design, M_design, main_folder, z_emb_start=0, z_emb_end=0, zstep=0, WH=0, WT=0, subfolder='executables', calc_type='CARL'):
    
    z = input_dict['z']
    su_C = input_dict['su_C_u']
    su_D = input_dict['su_D_u']
    su_E = input_dict['su_E_o']

    GAMS = 0.019
    GAMW = 0.01
    
    file_name = "_".join([foundation_location_name, input_heading, str(round(b_save, 2)), str(round(z_emb_start, 2))]).lower()
    input_file_save = main_folder/subfolder/calc_type/(file_name + '_CARL.in')
    input_file = main_folder/subfolder/calc_type/'CARL.in'
    file = open(input_file,'w')
    file.write('Project Information\n')
    file.write('MN, m\n')

    file.write('%10.1f%10.1f%10.1f%10.1f%10.1f%10.3f%10.2f\n' %(b1, b2, z_emb_start, z_emb_end, zstep, GAMS, GAMW))
            
    VS = VF = V_design
    VSTEP = 0
    H = H_design
    M = M_design
    
    REDBS_CARL = 0.5
    REDSS_CARL = 0.4
    CRACK = 1
    PASTYP = 0 

    DELPH = WH
    DELPT = WT
            
    LF = 1
    file.write('%10.3f%10.3f%10.1f%10.3f%10.3f%10.3f%10.3f%10.1f\n' %(VS, VF, VSTEP, H, M, DELPH, DELPT, LF))
    zstep = 0.2
    ZMAX = 0.5*math.floor(b1/2/0.5) + z_emb_start

    file.write('%10.1f%10.2f%10.1f%10.1f%10.0f%10.0f%10.0f%10.0f\n'%(ZMAX, zstep, REDBS_CARL, REDSS_CARL, CRACK, PASTYP, 0, 0))
    file.write('%5.0f%3.0f%3.0f%3.0f%3.0f%3.0f\n' %(len(z), 1, 1, 1, 1, 0))
    
    for idx, (zi, suci, sudi, suei) in enumerate(zip(z, su_C, su_D, su_E)):
        if idx == 0:
            file.write('%10.3f%10.3f%10.3f%10.3f\n' %(0, max(0.001, suci/1000), max(0.001, sudi/1000), max(0.001, suei/1000)))
        else:
            file.write('%10.3f%10.3f%10.3f%10.3f\n' %(zi, max(0.001, suci/1000), max(0.001, sudi/1000), max(0.001, suei/1000)))

    file.close()
    shutil.copy(input_file, input_file_save)
        
    return input_file_save

def input_file_CAPT(foundation_location_name, input_heading, input_dict, b_save, b1, b2, V_design, main_folder, z_emb_start=0, z_emb_end=0, zstep=0, subfolder='executables', calc_type='CAPT'):
    
    z = input_dict['z']
    su_C = input_dict['su_C_u']
    su_D = input_dict['su_D_u']
    su_E = input_dict['su_E_o']

    GAMS = 0.019
    GAMW = 0.01
    
    file_name = "_".join([foundation_location_name, input_heading, str(round(b_save, 2)), str(round(z_emb_start, 2))]).lower()
    input_file_save = main_folder/subfolder/calc_type/(file_name + '_CAPT.in')
    input_file = main_folder/subfolder/calc_type/'CAPT.in'
    file = open(input_file,'w')
    file.write('Project Information\n')
    file.write('MN, m\n')
    
    file.write('%10.2f%10.2f%10.1f%10.1f%10.1f%10.3f%10.2f\n' %(0.5*b1, b2, z_emb_start, z_emb_end, zstep, GAMS, GAMW))
        
    VS = VF = V_design
    VSTEP = 0
    H = 0
    M = 0
    
    REDBS_CAPT = 0.0
    REDSS_CAPT = 0.5
    PASTYP = 1  
    CRACK = 0

    DELPH = 0
    DELPT = 0

    LF = 1
    file.write('%10.3f%10.3f%10.1f%10.3f%10.3f%10.3f%10.3f%10.1f\n' %(0.5*VS, 0.5*VF, VSTEP, H, M, DELPH, DELPT, LF))
    zstep = 0.2
    ZMAX = 2*b1
    
    file.write('%10.1f%10.2f%10.1f%10.1f%10.0f%10.0f\n'%(ZMAX, zstep, REDBS_CAPT, REDSS_CAPT, CRACK, PASTYP))
    file.write('%5.0f%3.0f%3.0f%3.0f\n' %(len(z), 1, 1, 1))

    for idx, (zi, suci, sudi, suei) in enumerate(zip(z, su_C, su_D, su_E)):
        if idx == 0:
            file.write('%10.3f%10.3f%10.3f%10.3f\n' %(0, max(0.001, suci/1000), max(0.001, sudi/1000), max(0.001, suei/1000)))
        else:
            file.write('%10.3f%10.3f%10.3f%10.3f\n' %(zi, max(0.001, suci/1000), max(0.001, sudi/1000), max(0.001, suei/1000)))

    file.close()
    shutil.copy(input_file, input_file_save)
        
    return input_file_save

def output_file_CAP(main_folder, foundation_location_name, input_heading, b_save, b1, l1, calc_type='CAP', subfolder='executables'):

    file_name = "_".join([foundation_location_name, input_heading, str(round(b_save, 2)), str(round(l1, 2))]).lower()
    output_file_save = main_folder/subfolder/calc_type/(file_name + '_CAP.out')
    output_file = main_folder/subfolder/calc_type/'CAPOut'
    file = open(output_file, 'r')

    read_SF = 0

    SF_min = []
    z_slip_min = []
    angle_min = []
        
    for line in file:
        if 'Z' in line and 'ALPHA' in line  and 'SF' in line and not 'LF' in line:
            read_SF = 1
            SF_i = []
            z_slip_i = []
            angle_i = []

        if read_SF == 1:
            if 'MINIMUM SAFETY FACTOR' in line:
                read_SF = 0                

                SF_i = np.array(SF_i)
                SF_i[SF_i <= 0] = np.inf
                SF_minii = np.min(SF_i[1:])
                SF_array = SF_i
                SF_diff = np.absolute(SF_i - SF_minii)
                SF_index = SF_diff.argmin()
                SF_min.append(SF_minii)

                z_slip_i = np.array(z_slip_i)
                z_slip_array = z_slip_i
                z_slip_minii = z_slip_i[SF_index]
                z_slip_min.append(z_slip_minii)

                angle_i = np.array(angle_i)
                angle_array = angle_i
                angle_minii = angle_i[SF_index]
                angle_min.append(angle_minii)

            try:
                z_slip_i.append(float(line.split()[0]))
                angle_i.append(float(line.split()[1]))
                SF_i.append(float(line.split()[2]))
            except:
                pass
    
    idx = SF_min.index(np.min(SF_min))
    SF = SF_min[idx]
    z_slip = z_slip_min[idx]
    angle = angle_min[idx]
    
    file.close()
    shutil.copy(output_file, output_file_save)
    
    return SF, z_slip, angle, SF_array, z_slip_array, angle_array, output_file_save


def output_file_CAPT(main_folder, foundation_location_name, input_heading, b_save, b1, l1, calc_type='CAPT', subfolder='executables'):

    file_name = "_".join([foundation_location_name, input_heading, str(round(b_save, 2)), str(round(l1, 2))]).lower()
    output_file_save = main_folder/subfolder/calc_type/(file_name + '_CAPT.out')
    output_file = main_folder/subfolder/calc_type/'CAPT.out'
    file = open(output_file, 'r')

    read_SF = 0

    SF_min = []
    z_slip_min = []
    angle_min = []
    
    for line in file:
        if 'Z' in line and 'ALPHA' in line  and 'SF' in line and not 'LF' in line:
            read_SF = 1
            SF_i = []
            z_slip_i = []
            angle_i = []

        if read_SF == 1:
            if 'MINIMUM SAFETY FACTOR' in line:
                read_SF = 0

                SF_i = np.array(SF_i)
                SF_i[SF_i <= 0] = np.inf
                SF_array = SF_i
                z_slip_i = np.array(z_slip_i)
                angle_i = np.array(angle_i)
                if len(SF_i) == 0:
                    SF_minii = 0
                    z_slip_minii = 0
                    angle_minii = 0
                else:
                    SF_minii = np.min(SF_i)
                    z_slip_array = z_slip_i
                    angle_array = angle_i
                    SF_diff = np.absolute(SF_i - SF_minii)
                    SF_index = SF_diff.argmin()
                    z_slip_minii = z_slip_i[SF_index]
                    angle_minii = angle_i[SF_index]
                SF_min.append(SF_minii)
                z_slip_min.append(z_slip_minii)
                angle_min.append(angle_minii)
            try:
                z_slip_i.append(float(line.split()[0]))
                angle_i.append(float(line.split()[1]))
                SF_i.append(float(line.split()[2]))

            except:
                pass
    
    idx = SF_min.index(np.min(SF_min))
    SF = SF_min[idx]
    if SF == 0:
        SF = np.inf
        
    z_slip = z_slip_min[idx]
    if z_slip == 0:
        z_slip = np.inf

    angle = angle_min[idx]
    if angle == 0:
        angle = np.inf

    file.close()
    shutil.copy(output_file, output_file_save)
    
    return SF, z_slip, angle, SF_array, z_slip_array, angle_array, output_file_save


def output_file_CARL(main_folder, foundation_location_name, input_heading, b_save, b1, l1, calc_type='CARL', subfolder='executables'):

    file_name = "_".join([foundation_location_name, input_heading, str(round(b_save, 2)), str(round(l1, 2))]).lower()
    output_file_save = main_folder/subfolder/calc_type/(file_name + '_CARL.out')
    output_file = main_folder/subfolder/calc_type/'CARL.out'
    file = open(output_file, 'r')

    read_SF = 0

    SF_min = []
    SF_array = []

    pattern = r'-?\d+\.\d{2}'
    
    for line in file:

        line = line.strip()

        if 'DEPTH    HOR. DISTANCE FROM CIRCLE CENTRE TO RIGHT EDGE' in line:

            count = 0
            read_SF = 1

            SF_i = []
            x_slip_array = []
            z_slip_array = []

        if read_SF == 1:
            
            if 'MINIMUM SAFETY FACTOR' in line:
                read_SF = 0        
     
                for sfi in SF_i:
                    sfi[sfi <= 0] = np.inf
                    SF_minii = np.min(sfi)
                    SF_array.append(sfi)
                    SF_diff = np.absolute(sfi - SF_minii)
                    SF_index = SF_diff.argmin()
                    SF_min.append(SF_minii)

                    x_slip_array.append(x_array[SF_index])

            if line:

                line = line.replace("******", " 0.00")
                line = line.replace("Inf", " 99.99")
                
                if count == 1:
                    x_array = np.float64(np.array(line.split()))
                elif count != 0:
                    try:
                        numbers = re.findall(pattern, line)
                        values = [float(num) for num in numbers]
                        z_slip_array.append(float(line.split()[0]))
                        SF_i.append(np.float64(np.array(values)))
                    except Exception:
                        pass

                count += 1

    idx = SF_min.index(np.min(SF_min))
    SF = SF_min[idx]
    z_slip = z_slip_array[idx]
    x_slip = x_slip_array[idx]
            
    file.close()
    shutil.copy(output_file, output_file_save)
    
    return SF, z_slip, x_slip, SF_array, z_slip_array, x_array, output_file_save