from gspread import *
from gspread_formatting import *
from Telegram.writespreadsheet import authorize_google_sheet, sheetname, worksheet
from gspread_formatting import batch_updater, CellFormat, Color


shades_dict = {
    1000000: Color(0.9, 1, 0.9),  # Lighter green
    950000:  Color(0.88, 0.98, 0.88),
    900000:  Color(0.86, 0.96, 0.86),
    850000:  Color(0.84, 0.94, 0.84),
    800000:  Color(0.82, 0.92, 0.82),
    750000:  Color(0.8, 0.9, 0.8),
    700000:  Color(0.78, 0.88, 0.78),
    650000:  Color(0.76, 0.86, 0.76),
    600000:  Color(0.74, 0.84, 0.74),
    550000:  Color(0.72, 0.82, 0.72),
    500000:  Color(0.7, 0.8, 0.7),
    450000:  Color(0.68, 0.78, 0.68),
    400000:  Color(0.66, 0.76, 0.66),
    350000:  Color(0.64, 0.74, 0.64),
    300000:  Color(0.62, 0.72, 0.62),
    250000:  Color(0.6, 0.7, 0.6),
    200000:  Color(0.58, 0.68, 0.58),
    150000:  Color(0.56, 0.66, 0.56),
    100000:  Color(0.54, 0.64, 0.54)
}

alt_shades_dict = {
    1000000: Color(1, 0.95, 0.85),  # Lighter orange
    950000:  Color(0.98, 0.93, 0.83),
    900000:  Color(0.96, 0.91, 0.81),
    850000:  Color(0.94, 0.89, 0.79),
    800000:  Color(0.92, 0.87, 0.77),
    750000:  Color(0.9, 0.85, 0.75),
    700000:  Color(0.88, 0.83, 0.73),
    650000:  Color(0.86, 0.81, 0.71),
    600000:  Color(0.84, 0.79, 0.69),
    550000:  Color(0.82, 0.77, 0.67),
    500000:  Color(0.8, 0.75, 0.65),
    450000:  Color(0.78, 0.73, 0.63),
    400000:  Color(0.76, 0.71, 0.61),
    350000:  Color(0.74, 0.69, 0.59),
    300000:  Color(0.72, 0.67, 0.57),
    250000:  Color(0.7, 0.65, 0.55),
    200000:  Color(0.68, 0.63, 0.53),
    150000:  Color(0.66, 0.61, 0.51),
    100000:  Color(0.64, 0.59, 0.49)
}


def applyChanges(sheet):
    data = sheet.get_all_values()
    
    if len(data) <= 1:
        return

    current_category = data[1][0]
    use_alt_colors = False
    color_dict = shades_dict if not use_alt_colors else alt_shades_dict
    
    # Formats Batch
    batch_formats = []
    
    for row_idx in range(1, len(data)):
        category, _, subs = data[row_idx]
        
        if category != current_category:
            current_category = category
            use_alt_colors = not use_alt_colors
            color_dict = shades_dict if not use_alt_colors else alt_shades_dict #

        try: #Confirm int
            subs = int(subs.replace(',', ''))
        except ValueError:
            continue

        background_color = None

        #Get color for row
        for threshold, color in sorted(color_dict.items(), reverse=True):
            if subs >= threshold:
                background_color = color
                break

        if background_color:
            # Add to batch
            batch_formats.append({
                'range': f'A{row_idx + 1}:C{row_idx + 1}',
                'format': CellFormat(backgroundColor=background_color)
            })

        # print(f"row {row_idx + 1}")

    # Apply
    with batch_updater(sheet.spreadsheet) as batcher:
        for format_info in batch_formats:
            batcher.format_cell_range(sheet, format_info['range'], format_info['format'])

# Main
def formatTheWorksheet():
    """
    Format worksheet with predefined metrics
    """
    # Authorize
    client = authorize_google_sheet()
    
    # Apply to sheet
    sheet= sheetname
    worksname= worksheet
    spreadsheet = client.open(sheet)
    changableworksheet = spreadsheet.worksheet(worksname)
    applyChanges(changableworksheet)

# if __name__ == "__main__":
#     print("Formatting")
#     formatTheWorksheet()
