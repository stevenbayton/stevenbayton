# python modules
import numpy as np
# from playwright.sync_api import sync_playwright
import time
from pathlib import Path
import re
import zipfile
import cv2
import os
import subprocess
# import pyautogui

def write_caisson_file(foundation_location_name, 
                       input_heading, 
                       input_dict, 
                       b1, l1, t1, 
                       V_design, H_design, M_design, T_design,
                       mode_vhm, alpha_fo, alpha_fi, eta_fo, eta_reb, alpha_d_su, iplug_vmode, 
                       critical_ratio_su=2, t_lid=0.025, input_folder="_input_files", output_folder="_output_files", template_folder="_templates"):

    z = input_dict['z']
    eff_uw = input_dict['eff_uw']
    su_C = input_dict['su_C_found']
    su_D = input_dict['su_D_found']
    su_E = input_dict['su_E']
    su_ave = input_dict['su_input']

    if alpha_d_su == "Find slip surface":
        for z_int, su_bot1, su_top2 in zip(z[1:-1:2], su_ave[1:-1:2], su_ave[2:-1:2]):
            if z_int <= l1:
                continue
            else:
                ratio_top2_bot1 = max(1e-10, su_top2) / max(1e-10, su_bot1)
                if ratio_top2_bot1 > critical_ratio_su:
                    if z_int <= l1 + 0.5*b1:
                        alpha_d_su = (z_int - l1)/b1
                    else:
                        alpha_d_su = 0.5
                    break
                else:
                    alpha_d_su = 0.5

    if alpha_d_su == "Find slip surface":
        alpha_d_su = 0.5

    su_ave_l = 0

    for idx, (z_i, su_ave_i) in enumerate(zip(z[1:], su_ave[1:])):
        if z_i <= l1:
            su_ave_ii = (su_ave[idx]+su_ave_i)/2
            z_ii = (z_i - z[idx])
            su_ave_l += su_ave_ii*z_ii

    su_ave_l = su_ave_l/l1

    if l1 + alpha_d_su*b1 not in z:
        i = np.sum(z < l1 + alpha_d_su*b1)
        su_add = np.interp(l1 + alpha_d_su*b1, z, su_ave)
        z_upd = np.insert(z, i, l1 + alpha_d_su*b1)
        su_ave_upd = np.insert(su_ave, i, su_add)
    else:
        z_upd = z
        su_ave_upd = su_ave
    
    su_ave_end_bear = 0

    for idx, (z_i, su_ave_i) in enumerate(zip(z_upd[1:], su_ave_upd[1:])):
        if z_i > l1 and z_i <= l1 + alpha_d_su*b1:
            su_ave_ii = (su_ave_upd[idx]+su_ave_i)/2
            z_ii = (z_i - z_upd[idx])
            su_ave_end_bear += su_ave_ii*z_ii

    su_ave_end_bear = su_ave_end_bear/(alpha_d_su*b1)

    # Project info
    IFILE_DUMMY = ("_".join([foundation_location_name, input_heading, str(round(b1, 2)), str(round(l1, 2))]).lower() + '.i01').upper() # input caisson file
    OFILE = ("_".join([foundation_location_name, input_heading, str(round(b1, 2)), str(round(l1, 2))]).lower() + '.o01').upper()  # output caisson file
    PFILE = ("_".join([foundation_location_name, input_heading, str(round(b1, 2)), str(round(l1, 2))]).lower() + '.pdf').upper()  # output pdf file
    CPROG = "CAISSON_VHM" # program name ! Fixed
    RTITLE = (input_heading).upper() # run title
    PTITLE = "EMPTY" # project name
    PROJNO = "EMPTY"  # project number
    LOCATN = (foundation_location_name).upper() # location name

    # Soil information
    soil_matrix = []
    su_D_contribution = []

    for i in range(0, len(z) - 1, 2):
        zi = z[i]
        eff_uwi = eff_uw[i]
        su_aveti = max(0.01, su_ave[i])
        su_avebi = max(0.01, su_ave[i+1])
        if z[i+1] <= l1:
            su_D_contribution.append((su_D[i+1]+su_D[i])/2 * (z[i+1]-z[i]))
            su_D_base = su_D[i+1]
        if su_aveti > su_avebi:
            su_aveti = su_avebi = (su_aveti + su_avebi) / 2
        soil_matrix.append([str(round(zi, 2)), str(round(eff_uwi, 2)), str(round(su_aveti, 2)), str(round(su_avebi, 2)), '!'])

    su_D_ave_l1 = sum(su_D_contribution) / l1
    
    NUMSL = len(soil_matrix)
    SOIL_MAT = '\n'.join([' '.join(i) for i in soil_matrix])
    # SOIL_MAT_BASE = str(round(z[i+1], 2))
    SOIL_MAT_BASE = str(round(z[-1], 2))
    M_FAC = 1

    # Caisson model
    VHM_MODEL = "kay+palix_2011" # ! Fixed
    MODE_VHM = mode_vhm

    # Caisson geometry information
    caisson_matrix = [str(round(b1, 2)), str(round(l1, 2))]
    NCGEOM = int(1)
    CGEOM = "circular" # ! Fixed
    NFHXP = int(0) # number of full height cross plates
    WT_D_SIDE = round(t1 / b1, 3)
    WT_D_TOP = round(t_lid / b1, 3)
    IRO_LUG = 0.0 # caisson lug radial offset pointer
    R_LUG_USER = 0.0 # caisson lug radial offset
    CAISSON_MAT = ' '.join(caisson_matrix)

    # Steel-soil interface'
    M_t_outer = np.pi * b1 * l1 * su_D_ave_l1 * alpha_fo * b1 / 2
    M_t_inner = np.pi * (b1-2*t1) * l1 * su_D_ave_l1 * alpha_fi * (b1-2*t1) / 2

    I_t = np.pi * np.power(b1, 4) / 32
    W_t = I_t / (b1 / 2)
    M_t_plug = W_t * su_D_base

    M_t = min(M_t_outer + M_t_inner, M_t_outer + M_t_plug)
    eta_t = 1000 * T_design / M_t

    alpha_fo_updated = alpha_fo * np.power(1 - np.power(eta_t, 2), 0.5)
    alpha_fi_updated = alpha_fi * np.power(1 - np.power(eta_t, 2), 0.5)

    ALPHA_FO = round(alpha_fo_updated, 2)
    ALPHA_FI = round(alpha_fi_updated, 2)
    ETA_FO = int(eta_fo)
    ETA_REB = int(eta_reb)
    ALPHA_D_SU = alpha_d_su
    IPLUG_VMODE = int(iplug_vmode)
    VMAX_USER = 0.0 # ! Fixed

    # Reduction factors
    ETA_AMH = 1.0 # ! MH ellipse resistance reduction factor, aMH,new = ηaMH aMH
    ETA_BMH = 1.0 # ! MH ellipse resistance reduction factor, bMH,new = ηbMH bMH
    ETA_PHIMH = 1.0 # ! MH ellipse resistance rotation angle increase factor, ΦMH,new = ηφMH ΦMH

    # Load data
    NLC = 1
    NLFAC_LC = 1.0 # ! Fixed for now
    LFAC_LC = 1.0 # ! Fixed for now
    LOAD_MAT = ' '.join(map(str, [round(1000*V_design, 1), round(1000*H_design, 1), round(1000*M_design, 1), 1.0]))

    # Control data
    IOUTD = int(0) # Fixed
    IOUTE = 23 # Fixed
    EPS_INT = 1E-04 # ! Fixed
    JMAX_INT = 15 # ! Fixed
    JMIN_INT = 5 # ! Fixed

    replacements = {k: v for k, v in locals().items() if k.isupper()}

    def replace_placeholder(match):

        key = match.group(1)

        return str(replacements.get(key, f"<{key}>"))

    with open(Path(__file__).parent/template_folder/"_caisson_input_template_10_11_12_13.txt", "r", encoding="utf-8") as file:
        text = file.read()

    text = re.sub(r"<(\w+)>", replace_placeholder, text)

    input_file = Path(__file__).parent/input_folder/IFILE_DUMMY
    output_file = Path(__file__).parent/output_folder/OFILE

    with open(input_file, "w", encoding="utf-8") as file:
        file.write(text)

    input_dict["alpha_d_su"] = alpha_d_su
    input_dict["alpha_updated"] = alpha_fo_updated
    input_dict["su_ave_l"] = su_ave_l
    input_dict["su_ave_end_bear"] = su_ave_end_bear

    return input_file, output_file, input_dict


def read_ouput_file(output_file):

    search_markers = {"ilc        D      L      L/D       Vmax        Hmax         H0          Bw      su_av_L":        {"name": "summary_caisson",
                                                                                                                         "count": 0},
                      "ilc      D       L      FOS   row |    V           H            M    |     ilc":                 {"name": "fos_results",
                                                                                                                        "count": 0},
                      "Hx          My          Vz          H*         M*          V*          it   iv       row":       {"name": "hvm_results",
                                                                                                                        "count": 0},
                      }

    current_marker = None
    results_line = []
    output_dict_i = {}

    with open(output_file, 'r') as file:

        for line in file:

            line_stripped = line.strip()
            
            if line_stripped == "":
                continue

            if current_marker is None:
                if line_stripped in search_markers:
                    current_marker = line_stripped
                    results_line = []
                    search_markers[current_marker]['count'] += 1
            else:
                if "-----------" in line_stripped or "icgeom"  in line_stripped or "[" in line_stripped:
                    continue
                            
                if line_stripped == current_marker:
                    if search_markers[current_marker]["name"] not in output_dict_i:
                        output_dict_i[search_markers[current_marker]["name"]] = []
                        
                    output_dict_i[search_markers[current_marker]["name"]].append(results_line)
                    current_marker = None
                    results_line = []
                elif search_markers[current_marker]['count'] <= 1:
                    results_line.append([float(x) for x in line_stripped.split()])
 
    return output_dict_i


# def wait_for_stable_screen(page,
#                            repeats=2, interval=300, timeout=100000):

#     start = time.time()
#     stable_count = 0

#     last = page.screenshot()

#     while (time.time() - start) * 1000 < timeout:
#         page.wait_for_timeout(interval)
#         current = page.screenshot()

#         if current == last:
#             stable_count += 1
#             if stable_count >= repeats:
#                 return
#         else:
#             stable_count = 0

#         last = current

#     raise TimeoutError("Screen did not become stable")


# def click_image(page, 
#                 images,
#                 image_name, 
#                 count=0,
#                 wait_for_stable=True,
#                 critical=True,
#                 ratio_x=0.5, ratio_y=0.5, threshold=0.95):

#     screenshot_path = Path(images[image_name].parent / ("current_screen.png"))
#     page.screenshot(path=screenshot_path)

#     screen = cv2.imread(str(screenshot_path))
#     template = cv2.imread(images[image_name])

#     result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
#     _, max_val, _, max_loc = cv2.minMaxLoc(result)

#     if max_val < threshold:
#         if wait_for_stable and count < 20 and critical:
#             wait_for_stable_screen(page)
#             click_image(page, images, image_name)

#         elif count >= 20 or not critical:
#             print(f" ------ (Failed to find {image_name} button, trying again)")
#             return False, [None, None], count
        
#     h, w, _ = template.shape
#     click_x = max_loc[0] + int(ratio_x * w)
#     click_y = max_loc[1] + int(ratio_y * h)

#     flutter = page.locator("flutter-view")
#     flutter.wait_for()

#     page.evaluate("""([x, y]) => {
#                   const old = document.getElementById('playwright-click-marker');
#                   if (old) old.remove();
#                   const dot = document.createElement('div');
#                   dot.id = 'playwright-click-marker';
#                   dot.style.position = 'absolute';
#                   dot.style.left = x + 'px';
#                   dot.style.top = y + 'px';
#                   dot.style.width = '10px';
#                   dot.style.height = '10px';
#                   dot.style.background = 'red';
#                   dot.style.borderRadius = '50%';
#                   dot.style.zIndex = 9999;
#                   dot.style.pointerEvents = 'none';
#                   document.body.appendChild(dot);
#                   }""",
#                   [click_x, click_y],)

#     return True, [click_x, click_y], count


# def execute_main(page, 
#                  images,
#                  input_file_array, 
#                  output_file,
#                  timeout=1000):
    
#     headless = False
#     url_login = "https://app.casksoftware.com/login"
#     username = "ingerid.jahren@multiconsult.no"
#     password = "Cgje7fLwUE7nsQJv"
    
#     # username = "erik.torum@multiconsult.no"
#     # password = "eR}RV=G7W&90"

#     while True:

#         try:

#             p = sync_playwright().start()

#             browser = p.chromium.launch(channel="msedge", headless=headless)
#             context = browser.new_context(accept_downloads=True)
#             page = context.new_page()

#             page.goto(url_login, wait_until="load", timeout=20000)

#             print(' ----- Launching cask')

#             page.wait_for_selector("flutter-view")
#             page.wait_for_timeout(5*timeout)

#             found, coords, count = click_image(page, images, 'username')
#             page.mouse.click(coords[0], coords[1])
#             page.wait_for_timeout(timeout)
#             page.keyboard.type(username)

#             found, coords, count = click_image(page, images, 'password')
#             page.mouse.click(coords[0], coords[1])
#             page.wait_for_timeout(timeout)
#             page.keyboard.type(password)

#             page.wait_for_timeout(timeout)

#             found, coords, count = click_image(page, images, 'sign_in')
#             page.mouse.click(coords[0], coords[1])
            
#             wait_for_stable_screen(page)

#             print(' ----- Navigating to caisson analysis')

#             page.mouse.wheel(0, -10000)
#             found, coords, count = click_image(page, images, 'caisson')
#             page.mouse.click(coords[0], coords[1])
            
#             page.wait_for_timeout(3*timeout)
#             wait_for_stable_screen(page)

#             print(' ----- Creating new project')
            
#             found, coords, count = click_image(page, images, 'new_project')
#             page.mouse.click(coords[0], coords[1])
            
#             page.wait_for_timeout(2*timeout)
#             wait_for_stable_screen(page)
#             page.wait_for_timeout(2*timeout)

#             found, coords, count = click_image(page, images, 'project_name', critical=False)
#             page.mouse.click(coords[0], coords[1])
#             page.keyboard.press("Control+A")
#             page.keyboard.press("Backspace")
#             page.keyboard.type("python_interface") 
            
#             page.wait_for_timeout(5*timeout)

#             found, coords, count = click_image(page, images, 'upload')
            
#             print(' ----- Uploading input files')

#             with page.expect_file_chooser() as fc_info:
#                 page.mouse.click(coords[0], coords[1])

#             page.wait_for_timeout(3*timeout)    
#             fc_info.value.set_files(input_file_array)
#             page.wait_for_timeout(3*timeout)

#             page.mouse.wheel(0, 5000)
#             page.wait_for_timeout(3*timeout)

#             print(' ----- Calculating')

#             found, coords, count = click_image(page, images, 'calculate')
#             page.mouse.click(coords[0], coords[1])          
#             page.mouse.wheel(0, 20000)

#             wait_for_stable_screen(page)    
#             page.wait_for_timeout(3*timeout)  

#             print(' ----- Downloading')
#             page.mouse.wheel(0, -20000)
#             found=False
#             count = 0
#             while not found:
#                 found, coords, count = click_image(page, images, 'save', count=count, wait_for_stable=False)
#                 if found:
#                     break
#                 page.mouse.wheel(0, 20)
#                 count += 1
#                 page.wait_for_timeout(timeout)
            
#             with page.expect_download() as download_info:
#                 page.wait_for_timeout(3*timeout)
#                 page.mouse.click(coords[0], coords[1])

#             page.wait_for_timeout(3*timeout)

#             download = download_info.value

#             output_path = output_file[0].parent

#             zip_path = output_path/download.suggested_filename
#             download.save_as(zip_path)
            
#             extract_folder = output_path

#             with zipfile.ZipFile(zip_path, "r") as z:
#                 for name in z.namelist():
#                     if name.endswith(".O01"):
#                         z.extract(name, extract_folder)

#             os.remove(zip_path)

#             page.mouse.wheel(0, -20000)
#             wait_for_stable_screen(page)

#             found, coords, count = click_image(page, images, 'cancel')
#             page.mouse.click(coords[0], coords[1])
            
#             wait_for_stable_screen(page)

#             found, coords, count = click_image(page, images, 'cancel_confirm')
#             page.mouse.click(coords[0], coords[1])
                
#             wait_for_stable_screen(page)
#             page.reload(wait_until="networkidle")
#             wait_for_stable_screen(page)
            
#             found, coords, count = click_image(page, images, 'delete', ratio_x=0.96, threshold=0.5)
#             try:
#                 page.mouse.click(coords[0], coords[1])
#             except Exception:
#                 print("Could not delete")

#             wait_for_stable_screen(page)
#             page.wait_for_timeout(timeout)

#             found, coords, count = click_image(page, images, 'account')
#             page.mouse.click(coords[0], coords[1])
#             page.wait_for_timeout(3*timeout)
#             wait_for_stable_screen(page)

#             page.wait_for_timeout(10*timeout)
            
#             # found, coords, count = click_image(page, images, 'password')

#             print(' ----- Closing cask')

#             page.close()
#             browser.close()
#             p.stop()

#             break

#         except Exception:

#             page.close()
#             browser.close()
#             p.stop()

#     return


def execute_main(foundation_location_name,
                 input_file_array, 
                 output_file_array):
    
    url_login = "https://app.casksoftware.com/login"  # try dev. if fails
    username = "ingerid.jahren@multiconsult.no"
    password = "Cgje7fLwUE7nsQJv"
    
    # username = "erik.torum@multiconsult.no"
    # password = "eR}RV=G7W&90"

    edge_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    downloads_location = os.path.join(Path.home(), "Downloads")
    print(f" ---- Location of downloads folder: {downloads_location}")

    print(f" ----- Username: {username}")
    print(f" ----- Password: {password}")        
    print(f" ----- Input files path: {input_file_array[0].parent}") 

    subprocess.Popen([edge_location, url_login])   

    zip_file_name = input(f"------ Name of CAISSON project [{foundation_location_name}]: ") or foundation_location_name
    zip_path = os.path.join(downloads_location, (zip_file_name + '.zip'))
    
    zip_files = True
    output_file_missing_array = [os.path.basename(file_i) for file_i in output_file_array]

    while zip_files:

        with zipfile.ZipFile(zip_path, "r") as z:
            for name in z.namelist():
                if name.endswith(".O01"):
                    z.extract(name, output_file_array[0].parent)
                    if name in output_file_missing_array:
                        output_file_missing_array.remove(name)

        if len(output_file_missing_array) > 0:
            output_file_missing_array = [os.path.basename(file_i) for file_i in output_file_array]
            zip_files = True
            input(f" ----- Some output files missing, CAISSON error, re-run and press ENTER to retry")   
        else:
            zip_files = False
            print(f" ----- All output files present")   

    os.remove(zip_path)    

    return
