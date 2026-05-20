# python modules
import copy
from datetime import date
import matplotlib.colors as mcolors
from pathlib import Path
import re
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from svglib.svglib import svg2rlg
import pandas as pd
from reportlab.pdfbase.pdfmetrics import stringWidth

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.font_manager")


def clean_fig_no(fig_no):

    if fig_no == "nan":
        return "NONE"
    
    if fig_no == "True":
        return str(1)

    return fig_no


def template_A4_portrait(c, info, pdf_type, today=date.today()):
    
    c.setLineWidth(1.0)
    c.line(8.2*mm, 40*mm, 198.7*mm, 40*mm)  # bold horizontal line
    c.line(8.2*mm, 40*mm, 8.2*mm, 8.8*mm)  # bold vertical line
    c.rect(8.2*mm, 8.8*mm, 190.5*mm, 281.3*mm, fill=0)  # Border
    c.setLineWidth(0.5)
    c.line(8.2*mm, 33*mm, 198.7*mm, 33*mm)
    c.line(143.6*mm, 40*mm, 143.6*mm, 8.8*mm)
    c.line(171.1*mm, 19*mm, 171.1*mm, 40*mm)
    c.line(143.6*mm, 26*mm, 198.7*mm, 26*mm)
    c.line(143.6*mm, 19*mm, 198.7*mm, 19*mm)
    if len(info['main_title']) <= 60:
        style = ParagraphStyle(name='Normal', fontName='Helvetica-Bold', fontSize=11)
    elif len(info['main_title']) <= 75:
        style = ParagraphStyle(name='Normal', fontName='Helvetica-Bold', fontSize=9)
    else:
        style = ParagraphStyle(name='Normal', fontName='Helvetica-Bold', fontSize=8)
    text = latex_to_reportlab(info['main_title'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 10.2*mm, 35*mm)
    
    style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=11)
    text = latex_to_reportlab(info['sub_title1'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 10.2*mm, 27*mm)

    style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=10)
    text = latex_to_reportlab(info['sub_title2'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 10.2*mm, 20*mm)

    text = latex_to_reportlab(info['sub_title3'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 10.2*mm, 13*mm)
    
    c.setFont('Helvetica', 8)
    c.setFillColorRGB(mcolors.to_rgb('k')[0], mcolors.to_rgb('k')[1], mcolors.to_rgb('k')[2])
    c.drawString(145.1*mm, 37*mm, 'Document No.:')
    c.drawString(145.6*mm, 34*mm, info['doc_no'])

    if pdf_type == 'figure':
        c.drawString(145.1*mm, 30*mm, 'Figure No.:')
        c.drawString(145.6*mm, 27*mm, info['fig_no'])
    elif pdf_type == 'table':
        c.drawString(145.1*mm, 30*mm, 'Table No.:')
        c.drawString(145.6*mm, 27*mm, info['table_no'])

    c.drawString(145.1*mm, 23*mm, 'Date:')
    c.drawString(145.6*mm, 20*mm, today.strftime("%Y-%m-%d"))

    c.drawString(172.6*mm, 37*mm, 'Calculation by:')
    c.drawString(173.1*mm, 34*mm, info['calc_by'])

    c.drawString(172.6*mm, 30*mm, 'Checked by:')
    c.drawString(173.1*mm, 27*mm, info['check_by'])

    c.drawString(172.6*mm, 23*mm, 'Approved by:')
    c.drawString(173.1*mm, 20*mm, info['approv_by'])

    image = Path.cwd()/"_analysis_background_functions"/'multi_logo.svg'
    drawing = svg2rlg(str(image)) 
    drawing = scale_drawing(drawing, 45*mm)
    renderPDF.draw(drawing, c, 148*mm, 6.5*mm)
    
    return c


def template_A4_landscape(c, info, pdf_type, today=date.today()):   

    c.setLineWidth(1.0)
    c.line(90*mm, 40*mm, 290.1*mm, 40*mm) # bold horizontal line
    c.line(90*mm, 40*mm, 90*mm, 8.2*mm) # bold vertical line
    c.rect(8.8*mm, 8.2*mm, 281.3*mm, 190.5*mm, fill = 0) # Border
    c.setLineWidth(0.5)
    c.line(90*mm, 33*mm, 290.1*mm, 33*mm) # below Document No.
    c.line(235*mm, 40*mm, 235*mm, 8.2*mm) # left of all Document No.
    c.line(262.5*mm, 19*mm, 262.5*mm, 40*mm) # left of calculation by
    c.line(235*mm, 26*mm, 290.1*mm, 26*mm) # below Figure No.
    c.line(235*mm, 19*mm, 290.1*mm, 19*mm)  # below Data/Drawnby
    if len(info['main_title']) <= 60:
        style = ParagraphStyle(name='Normal', fontName='Helvetica-Bold', fontSize=11)
    elif len(info['main_title']) <= 75:
        style = ParagraphStyle(name='Normal', fontName='Helvetica-Bold', fontSize=9)
    else:
        style = ParagraphStyle(name='Normal', fontName='Helvetica-Bold', fontSize=8)

    text = latex_to_reportlab(info['main_title'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 92*mm, 35*mm)
    
    style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=11)
    text = latex_to_reportlab(info['sub_title1'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 92*mm, 27*mm)

    style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=10)
    text = latex_to_reportlab(info['sub_title2'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 92*mm, 20*mm)

    text = latex_to_reportlab(info['sub_title3'])
    p = Paragraph(text, style)
    p.wrapOn(c, 1000*mm, 1000*mm)
    p.drawOn(c, 92*mm, 13*mm)
    
    c.setFont('Helvetica', 8)
    c.setFillColorRGB(mcolors.to_rgb('k')[0], mcolors.to_rgb('k')[1], mcolors.to_rgb('k')[2])
    c.drawString(236.5*mm, 37*mm, 'Document No.:'); 
    c.drawString(237*mm, 34*mm, info['doc_no'])

    if pdf_type == 'figure':
        c.drawString(236.5*mm, 30*mm, 'Figure No.:')
        c.drawString(237*mm, 27*mm, info['fig_no'])
    elif pdf_type == 'table':
        c.drawString(236.5*mm, 30*mm, 'Table No.:')
        c.drawString(237*mm, 27*mm, info['table_no'])

    c.drawString(236.5*mm, 23*mm, 'Date:')
    c.drawString(237*mm, 20*mm, today.strftime("%Y-%m-%d"))

    c.drawString(264*mm, 37*mm, 'Calculation by:')
    c.drawString(264.5*mm, 34*mm, info['calc_by'])

    c.drawString(264*mm, 30*mm, 'Checked by:')
    c.drawString(264.5*mm, 27*mm, info['check_by'])

    c.drawString(264*mm, 23*mm, 'Approved by:')
    c.drawString(264.5*mm, 20*mm, info['approv_by'])

    image = Path.cwd()/"_analysis_background_functions"/'multi_logo.svg'
    drawing = svg2rlg(str(image)) 
    drawing = scale_drawing(drawing, 45*mm)
    renderPDF.draw(drawing, c, 239*mm, 6*mm)
    
    return c


def save_figure_pdf(info, scale_ls=265, scale_pt=180, start_x_ls=17, start_y_ls=45, start_x_pt=12, start_y_pt=48):

    pdf_name = str(info['pdf_directory'])
    svg_path = str(info['svg_path'])
    orientation = info['orientation']

    c = canvas.Canvas(pdf_name)

    drawing = svg2rlg(svg_path)
        
    if orientation.lower() == 'landscape':   
        c.setPageSize(landscape(A4))     
        drawing = scale_drawing(drawing, scale_ls*mm)
        renderPDF.draw(drawing, c, start_x_ls*mm, start_y_ls*mm)
        c = template_A4_landscape(c, info, 'figure')
    elif orientation.lower() == 'portrait':
        c.setPageSize(A4)
        drawing = scale_drawing(drawing, scale_pt*mm)
        renderPDF.draw(drawing, c, start_x_pt*mm, start_y_pt*mm)
        c = template_A4_portrait(c, info, 'figure')

    c.showPage()      
    c.save()   


def parse_column(col):
    
    parameter_symbol = col[0].split("_section")[0]
    parameter_type = col[1]
    rest = col[-1]

    if '?' not in rest:
        output_dict = {}
        ignore = True
    else:
        parts = rest.split("?")
        parameter_label = parts[0].strip()
        parameter_scope = parts[1].strip()

        output_dict = {"symbol": parameter_symbol,
                    "type": parameter_type,
                    "label": parameter_label,
                    "scope": parameter_scope}
        ignore = False

    return output_dict, ignore
        

def format_value(val, fmt):

    if str(fmt).lower() == "str":
        if str(val).lower() == 'nan':
            upd_val = 'N/A'
        else:
            upd_val = str(val).replace("_", " ").title()
    else:
        try:
            fmt = int(fmt)
        except Exception:
            fmt = fmt

        if type(fmt) is int:
            if str(val).lower() == 'nan':
                upd_val = 'N/A'
            elif val == 0:
                upd_val = f"{float(abs(val)):.{int(fmt)}f}"
            else:
                upd_val = f"{float(val):.{int(fmt)}f}"
        else:
            upd_val = val
        
    return upd_val
    

def get_col_widths(df, header_rows, font_size, font_name):

    n_cols = len(df.columns)
    col_widths = []

    for col_idx in range(n_cols):
        max_width = 0

        text = wrap_text(str(header_rows[0][col_idx]), max_words=2)
        width1 = stringWidth(text[1].replace('<sub>', '').replace('</sub>', '').replace('<super>', '').replace('</super>', ''), font_name, font_size)
        width2 = stringWidth(text[2].replace('<sub>', '').replace('</sub>', '').replace('<super>', '').replace('</super>', ''), font_name, font_size)
        max_width = max(max_width, width1, width2)

        text = wrap_text(str(header_rows[1][col_idx]), max_words=10)
        width1 = stringWidth(text[1].replace('<sub>', '').replace('</sub>', '').replace('<super>', '').replace('</super>', ''), font_name, font_size)
        width2 = stringWidth(text[2].replace('<sub>', '').replace('</sub>', '').replace('<super>', '').replace('</super>', ''), font_name, font_size)
        max_width = max(max_width, width1, width2)
        
        text = wrap_text(str(header_rows[2][col_idx]), max_words=10)
        width1 = stringWidth(text[1].replace('<sub>', '').replace('</sub>', '').replace('<super>', '').replace('</super>', ''), font_name, font_size)
        width2 = stringWidth(text[2].replace('<sub>', '').replace('</sub>', '').replace('<super>', '').replace('</super>', ''), font_name, font_size)
        max_width = max(max_width, width1, width2)

        col_widths.append(max_width + 8)

    return col_widths


def wrap_text(text, max_words=2):

    words = text.split()
    if len(words) <= max_words:
        return text, text, text
    
    return " ".join(words[:max_words]) + "<br/>" + " ".join(words[max_words:]), " ".join(words[:max_words]), " ".join(words[max_words:])


def split_col(col):
        
    table_heading1 = col.split('#')[0]
    table_heading2 = col.split('#')[-1]
    match = re.match(r"(.*?)\[(.*?)\]", table_heading1)
    
    if match:
        return match.group(1), match.group(2), table_heading2
    
    return table_heading1, "", table_heading2


def custom_sort_key(col, param_priority, method_priority):

    param, method, rest = col

    try:
        method = float(method)
    except Exception:
        method = method

    param_pri = param_priority.get(param, 999)
    method_pri = method_priority.get(method, 999)
    method_alpha = method
    param_alpha = param

    sort_key = (param_pri, method_pri, method_alpha, param_alpha)

    return sort_key


def save_table_pdf(info, df, calc_symbol_info, parameter_symbol_info, method_order, parameter_first, top_margin=50, bottom_margin=125, left_right_margin=45, font_size_table=4):

    header_font_name = 'Helvetica-Bold'
    header_style = ParagraphStyle(name='Header1',
                                  fontName=header_font_name,
                                  fontSize=font_size_table,
                                  leading=font_size_table+3,
                                  spaceBefore=0,
                                  spaceAfter=0,)
    
    df2 = copy.deepcopy(df)
    
    pairs = [split_col(c) for c in df2.columns]
    df2.columns = pd.MultiIndex.from_tuples(pairs)
  
    param_priority  = {p: i for i, p in enumerate(parameter_first)}
    method_priority = {m: i for i, m in enumerate(method_order)}
    sorted_cols = sorted(df2.columns, key=lambda c: custom_sort_key(c, param_priority, method_priority))
    df2 = df2[sorted_cols]
    
    new_cols = []
    formats = {}
    keep_cols = []

    for col in df2.columns:
        meta, ignore = parse_column(col)

        if not ignore:
      
            if ((calc_symbol_info["calc_symbol"] == meta["symbol"]) & (calc_symbol_info["calc_type"].fillna("").str.split(";").apply(lambda x: meta["type"] in [v.strip() for v in x]))).any():
                
                index = (calc_symbol_info["calc_symbol"] == meta["symbol"]) & (calc_symbol_info["calc_type"].fillna("").str.split(";").apply(lambda x: meta["type"] in [v.strip() for v in x]))
                description = calc_symbol_info["calc_description"][index].iloc[0]
                decimal = calc_symbol_info["calc_decimal_places"][index].iloc[0]
                keep = calc_symbol_info["calc_include?"].fillna(False)[index].iloc[0]

                save = (description,  meta["label"], meta["scope"])

                if not keep:
                    continue

            elif ((parameter_symbol_info["parameter_symbol"] == meta["symbol"]) & (parameter_symbol_info["parameter_type"].fillna("").str.split(";").apply(lambda x: meta["type"] in [v.strip() for v in x]))).any():
                
                index = (parameter_symbol_info["parameter_symbol"] == meta["symbol"]) & (parameter_symbol_info["parameter_type"].fillna("").str.split(";").apply(lambda x: meta["type"] in [v.strip() for v in x]))
                description = parameter_symbol_info["parameter_description"][index].iloc[0]
                decimal = parameter_symbol_info["parameter_decimal_places"][index].iloc[0]
                keep = parameter_symbol_info["parameter_include?"].fillna(False)[index].iloc[0]

                save = (description,  meta["label"], meta["scope"])

                if not keep:
                    continue

            else:

                print(f"{col} not in Excel input file, omitted")
                continue

        keep_cols.append(col)
        new_cols.append(save)
        formats[save] = decimal

    df2 = df2[keep_cols]
    df2.columns = pd.MultiIndex.from_tuples(new_cols)
    df2 = df2.loc[:, ~df2.columns.duplicated()]

    formatted_data = []

    for idx, row in enumerate(df2.values.tolist()):

        if row[0] > info['table_limit']:
            continue

        new_row = []
        for col, val in zip(df2.columns, row):

            fmt = formats.get(col)
            new_row.append(format_value(val, fmt))
        formatted_data.append(new_row)

    header_rows = list(zip(*df2.columns))
    header_rows = [list(row) for row in header_rows]

    col_widths = get_col_widths(df2, header_rows, font_size_table, header_font_name)

    styles = [header_style]*len(header_rows)

    styled_headers = []

    for i, row in enumerate(header_rows):
        styled_row = []
        if i == 0:
            max_words = 2
        else:
            max_words = 10
        for cell in row:
            txt = str(cell)
            txt = wrap_text(txt, max_words=max_words)[0]
            styled_row.append(Paragraph(txt, styles[i]))
        styled_headers.append(styled_row)

    data = styled_headers + formatted_data
    
    table = Table(data, colWidths=col_widths, repeatRows=len(header_rows))

    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.75, 0.75, 0.75))]))
    table.setStyle(TableStyle([('BACKGROUND', (0, 1), (-1, 1), colors.Color(0.85, 0.85, 0.85))]))    
    table.setStyle(TableStyle([('BACKGROUND', (0, 2), (-1, 2), colors.Color(0.85, 0.85, 0.85))]))

    table.setStyle(TableStyle([('FONTNAME', (0, 3), (-1, -1), 'Helvetica'),
                               ('FONTSIZE', (0, 0), (-1, -1), font_size_table),
                               ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                               ('TOPPADDING', (0, 0), (-1, -1), 0),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                               ('LEFTPADDING', (0, 0), (-1, -1), 4),
                               ('RIGHTPADDING', (0, 0), (-1, -1), 4),]))
          
    pdf_name = str(info['pdf_directory'])
    orientation = info['orientation']

    if orientation.lower() == 'landscape':  
        page_width, page_height = landscape(A4)
    elif orientation.lower() == 'portrait':
        page_width, page_height = A4

    y_start = page_height - top_margin
    usable_width = page_width - 2*left_right_margin
    usable_height = page_height - top_margin - bottom_margin
    
    parts = []
    remaining = table

    while remaining:
        split_parts = remaining.split(usable_width, usable_height)

        if len(split_parts) == 1:
            parts.append(split_parts[0])
            break
        else:
            parts.append(split_parts[0])
            remaining = split_parts[1]

    page_num = 1

    c = canvas.Canvas(pdf_name)
        
    if orientation.lower() == 'landscape':   
        c.setPageSize(landscape(A4))   
        for i, part in enumerate(parts):
            if i > 0:
                c.showPage()
                page_num += 1

            c = template_A4_landscape(c, info, 'table')

            w, h = part.wrap(usable_width, usable_height)

            part.drawOn(c, left_right_margin, y_start - h)

    elif orientation.lower() == 'portrait':
        c.setPageSize(A4)
        c = template_A4_portrait(c, info, 'table')
     
    c.save()   


def scale_drawing(drawing, new_drawing_width):

    scaling_factor = new_drawing_width/drawing.minWidth()
    drawing.width = drawing.minWidth()*scaling_factor
    drawing.height = drawing.height*scaling_factor
    drawing.scale(scaling_factor, scaling_factor)

    return drawing


def latex_to_reportlab(text):
    text = re.sub(r'_\{(.*?)\}', r'<sub>\1</sub>', text)
    text = re.sub(r'\^\{(.*?)\}', r'<sup>\1</sup>', text)
    
    return text