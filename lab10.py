import boto3
import xlsxwriter
import sqlite3 as sql

class VpcGet():
    def __init__(self):
        region = 'us-east-1'
        session = boto3.session.Session(region_name = region)
        vpc = session.client('ec2')
        self.vpcs = self.describe_vpcs()

    def VpcWorksheet(self):
        workbook = xlsxwriter.Workbook('/home/student/Desktop/vpcs.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 2, 24)
        worksheet.write(col, row, 'VPC Name')
        worksheet.write(col + 1, row, 'VPC ID')
        worksheet.write(col + 2, row, 'CIDR Block')
        col = 1
        row = 1
        for vpc in self.vpcs['Vpcs']:
            vpc_id = vpc['VpcId']
            cidr_block = vpc['CidrBlock']
            try:
                for tags in vpc['Tags']:
                    if tags['Key'] == 'Name':
                        vpc_name = tags['Value']
            except (KeyError, TypeError):
                vpc_name = 'N/A'
            worksheet.write(col, row, vpc_name)
            worksheet.write(col + 1, row, vpc_id)
            worksheet.write(col + 2, row, cidr_block)
            row += 1
        workbook.close()

    def VpcDatabase(self):
        conn = sql.connect('/home/student/ipwsp/databases/ipwsp.db')
        curs = conn.cursor()
        table = 'aws_vpcs'
        print '- Accessing and creating/flushing database table {tableName}'.format(table)
        try:
            curs.execute("CREATE TABLE {tableName} (vpc_name text, vpc_id text, cidr_block text)".format(table))
        except sql.OperationalError:
            conn.rollback()
            curs.execute("DROP TABLE {tableName}".format(table))
            curs.execute("CREATE TABLE {tableName} (vpc_name text, vpc_id text, cidr_block text)".format(table))
        print '- Iterating JSON data and inserting into database table'
        for vpc in self.vpcs['Vpcs']:
            vpc_id = vpc['VpcId']
            cidr_block = vpc['CidrBlock']
            try:
                for tags in vpc['Tags']:
                    if tags['Key'] == 'Name':
                        vpc_name = tags['Value']
            except (KeyError, TypeError):
                vpc_name = 'N/A'
            curs.execute("INSERT INTO {tableName} VALUES ({vpcName}, {vpcId}, {cidrBlock})".format(table,
                                                                                                   vpc_name,
                                                                                                   vpc_id,
                                                                                                   cidr_block))
        conn.commit()
        conn.close()

def main():
    vpc = VpcGet()
    vpc.VpcWorksheet()
    vpc.VpcDatabase()
    print '- Worksheet and database table have been created and populated'

if __name__ == '__main__:
    main()
