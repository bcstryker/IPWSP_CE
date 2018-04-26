import sys
from openpyxl import load_workbook

filename = '/home/student/ipwsp/aws/AWS_SEED.xlsx'
column = 'A'
row = 3

class AWS_VPC():
    def __init__(self):
        try:
            wb = load_workbook(filename = filename, data_only = True)
        except IOError:
            sys.exit('Could not open file')
        else:
            self.wb = wb

    def get_row(self, col, row = 1, max_row = 4):
        ws = self.wb.active
        sheet = self.wb['Sheet1']
        cell_name = col + str(row)
        x = sheet[cell_name].value
        return x

col_A = AWS_VPC()
col_B = AWS_VPC()

contents_A = col_A.get_row('A')
contents_B = col_B.get_row('B')

print contents_A
print contents_B
