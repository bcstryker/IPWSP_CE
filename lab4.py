import sys
from openpyxl import load_workbook

filename = '/home/student/ipwsp/aws/AWS_SEED.xlsx'
column = 'A'
row = 3

wb = load_workbook(filename = filename)
ws = wb.active
sheet = wb['Sheet1']
cell_name = column + str(row)
x = sheet[cell_name].value

print x
