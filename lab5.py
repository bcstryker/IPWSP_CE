import sys
import openpyxl

filename = 'home/student/ipwsp/aws/AWS_SEED.xlsx'
column = 'A'
row = 3

def get_row(col, row = 1, max_row = 4):
    wb = load_workbook(filename = filename, data_only = True)
    ws = wb.active
    sheet = wb['Sheet1']
    cell_name = column + str(row)
    x = sheet[cell_name].value
    print x

get_row('A')
get_row('B')
