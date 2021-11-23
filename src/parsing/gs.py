from datetime import datetime

import gspread as gs
from gspread.utils import rowcol_to_a1
#from .db_helper import db_help
import src.parsing.db_helper as db_help
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

regions = {
    1: "Россия",
    2: "Татарстан",
    3: "Казань",
    4: "Иннополис"}
vacancy_scheme = ["name", "company_name", "salary_from", "salary_to", "required_experience", "employment_mode",
                  "schedule",
                  "key_skills", "city", "responsibility", "requirement", "link", "link_to_company"]
vacancy_scheme_shift = {2: 0,  # name
                        6: 1,  # company_name
                        4: 2,  # salary_from
                        5: 3,  # salary to
                        11: 4,  # experience
                        12: 5,  # mode
                        13: 6,  # schedule
                        14: 7,  # skills
                        15: 8,  # city
                        8: 9,  # resp
                        9: 10,  # req
                        3: 11,  # link
                        7: 12  # link_to_company
                        }

cv_scheme = ["name", "age", "salary", "e_year", "e_month", "sex", "city", "education", "last_work", "specializations",
             "mode", "schedule", "previous_positions", "key_skills", "languages", "link"]
cv_scheme_shift = {1: 0,  # name
                   3: 1,  # age
                   4: 2,  # salary
                   6: 3,  # e_year
                   7: 4,  # e_month
                   9: 5,  # sex
                   10: 6,  # city
                   17: 7,  # education
                   8: 8,  # last_work
                   12: 9,  # specializations
                   13: 10,  # mode
                   14: 11,  # schedule
                   15: 12,  # prev_pos
                   16: 13,  # key_skills
                   18: 14,  # languages
                   2: 15 # link
                   }

credentials = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
spreadsheet_id = "1YhQcE7XHZg2qlyhF9ulMvGUC1VBT2iyemKIQiU1XRoY"
gc = gs.authorize(credentials)
spread_sheet = gc.open_by_key(spreadsheet_id)


def create_worksheet(worksheet_name, data_length, schema_length):
    if not is_worksheet_exists(worksheet_name):
        spread_sheet.add_worksheet(worksheet_name, data_length + 1, schema_length)
        print("Created new worksheet with name: {}".format(worksheet_name))
    else:
        print("Worksheet with name: {} already exists".format(worksheet_name))


def is_worksheet_exists(worksheet_name):
    worksheets = spread_sheet.worksheets()
    worksheets_names = [x.title for x in worksheets]
    if worksheet_name not in worksheets_names:
        return False
    else:
        return True


def delete_worksheet(worksheet_name):
    if is_worksheet_exists(worksheet_name):
        spread_sheet.del_worksheet(spread_sheet.worksheet(worksheet_name))
        print("Worksheet with name: {} has been deleted".format(worksheet_name))
    else:
        print("Worksheet with name: {} does not exist".format(worksheet_name))


def upload_data(worksheet_name, scheme, scheme_shift, data, table_name):
    global spread_sheet
    delete_worksheet(worksheet_name)
    create_worksheet(worksheet_name, len(data), len(scheme))

    if len(data) == 0:
        return

    worksheet = spread_sheet.worksheet(worksheet_name)

    # update scheme
    scheme_range = worksheet.range(1, 1, 1, len(scheme))
    ind = 0
    for cell in scheme_range:
        cell.value = scheme[ind]
        ind += 1

    # update data
    data_range = worksheet.range(2, 1, len(data) + 1, len(scheme_shift))
    for index in range(len(data)):
        for uc in range(len(data[index])):
            if scheme_shift.get(uc, -1) != -1:
                data_range[index * len(scheme_shift) + scheme_shift[uc]].value = data[index][uc]

    # run updates
    worksheet.update_cells(scheme_range)
    worksheet.update_cells(data_range)
    table_formatting(worksheet, len(data), len(scheme), table_name, scheme)
    print("Data has been uploaded")


def table_formatting(worksheet, data_length, scheme_length, table_name, scheme):
    body = []
    print("Started sheet formatting")
    # update font
    font_format = {
        "repeatCell": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 0,
                "endRowIndex": worksheet.row_count
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "LEFT",
                    "textFormat": {
                        "fontSize": 12,
                        "fontFamily": "Oswald"
                    }
                }
            },
            "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
        }
    }

    # update scheme borders
    body.append({
        "updateBorders": {
            "range": {
                "startColumnIndex": 0,
                "endColumnIndex": scheme_length,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "sheetId": worksheet.id
            },
            "bottom": {
                "style": "SOLID",
                "width": 1
            }
        }
    })
    for i in range(scheme_length):
        body.append(__update_borders(worksheet, i + 1, i + 1, 1, data_length + 1))

    if table_name == "vacancy":
        body.append(__resize_columns(worksheet, scheme.index("name") + 1, scheme.index("name") + 1, 250))
        body.append(
            __resize_columns(worksheet, scheme.index("company_name") + 1, scheme.index("company_name") + 1, 250))
        body.append(__resize_columns(worksheet, scheme.index("salary_from") + 1, scheme.index("salary_from") + 1, 70))
        body.append(__resize_columns(worksheet, scheme.index("salary_to") + 1, scheme.index("salary_to") + 1, 70))
        body.append(__resize_columns(worksheet, scheme.index("schedule") + 1, scheme.index("schedule") + 1, 120))
        body.append(__resize_columns(worksheet, scheme.index("key_skills") + 1, scheme.index("key_skills") + 1, 200))
        body.append(
            __resize_columns(worksheet, scheme.index("responsibility") + 1, scheme.index("responsibility") + 1, 500))
        body.append(__resize_columns(worksheet, scheme.index("requirement") + 1, scheme.index("requirement") + 1, 500))
        body.append(
            __resize_columns(worksheet, scheme.index("employment_mode") + 1, scheme.index("employment_mode") + 1, 120))
        body.append(__resize_columns(worksheet, scheme.index("required_experience") + 1,
                                     scheme.index("required_experience") + 1, 80))


    elif table_name == "cv":
        body.append(__resize_columns(worksheet, scheme.index("name") + 1, scheme.index("name") + 1, 250))
        body.append(__resize_columns(worksheet, scheme.index("age") + 1, scheme.index("age") + 1, 30))
        body.append(__resize_columns(worksheet, scheme.index("salary") + 1, scheme.index("salary") + 1, 70))
        body.append(__resize_columns(worksheet, scheme.index("e_year") + 1, scheme.index("e_year") + 1, 30))
        body.append(__resize_columns(worksheet, scheme.index("e_month") + 1, scheme.index("e_month") + 1, 30))
        body.append(__resize_columns(worksheet, scheme.index("sex") + 1, scheme.index("sex") + 1, 70))
        body.append(__resize_columns(worksheet, scheme.index("city") + 1, scheme.index("city") + 1, 70))
        body.append(__resize_columns(worksheet, scheme.index("education") + 1, scheme.index("education") + 1, 150))
        body.append(__resize_columns(worksheet, scheme.index("last_work") + 1, scheme.index("last_work") + 1, 200))
        body.append(
            __resize_columns(worksheet, scheme.index("specializations") + 1, scheme.index("specializations") + 1, 200))
        body.append(__resize_columns(worksheet, scheme.index("mode") + 1, scheme.index("mode") + 1, 200))
        body.append(__resize_columns(worksheet, scheme.index("schedule") + 1, scheme.index("schedule") + 1, 200))
        body.append(
            __resize_columns(worksheet, scheme.index("previous_positions") + 1, scheme.index("previous_positions") + 1,
                             200))
        body.append(__resize_columns(worksheet, scheme.index("key_skills") + 1, scheme.index("key_skills") + 1, 200))
        body.append(__resize_columns(worksheet, scheme.index("languages") + 1, scheme.index("languages") + 1, 200))

    body.append(font_format)
    request = {
        "requests": body
    }
    try:
        worksheet.spreadsheet.batch_update(request)
    except Exception as e:
        print(e)
    print("Finished sheet formatting")


def __resize_columns(worksheet, start, end, size):
    body = {
        "updateDimensionProperties": {
            "range": {
                "sheetId": worksheet.id,
                "dimension": "COLUMNS",
                "startIndex": start - 1,
                "endIndex": end
            },
            "properties": {
                "pixelSize": size
            },
            "fields": "pixelSize"
        }
    }
    return body


def __update_borders(worksheet, start_col, end_col, start_row, end_row):
    body = {
        "updateBorders": {
            "range": {
                "startColumnIndex": start_col - 1,
                "endColumnIndex": end_col,
                "startRowIndex": start_row - 1,
                "endRowIndex": end_row,
                "sheetId": worksheet.id
            },
            "right": {
                "style": "SOLID",
                "width": 1
            },
            "left": {
                "style": "SOLID",
                "width": 1
            }
        }
    }
    return body


def upload_to_gs(table_name: str, query: str, region: int):
    table = 'analysis_%s' % table_name
    db = db_help.db_helper()
    data = db.select_by_query_and_region(table, query, region)

    if table_name == "vacancy":
        upload_data("vacancy_" + query + "_" + regions[region] + "_" + str(datetime.today().date()), vacancy_scheme,
                    vacancy_scheme_shift, data, table_name)
    else:
        upload_data("cv_" + query + "_" + regions[region] + "_" + str(datetime.today().date()), cv_scheme,
                    cv_scheme_shift,
                    data, table_name)


