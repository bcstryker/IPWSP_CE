import boto3

pub1_sub_id = ''
pub2_sub_id = ''
pri1_sub_id = ''
pri2_sub_id = ''
pub_rt_id = ''
pri_rt_id = ''
igw_id = ''
sg_id = ''
instance_id = ''
cidr = '10.50.0.0/22'
my_ip = '34.210.73.72'
ami_id = 'ami-bc39e1c3'
instance_type = 't2.nano'
subnet_list = [
                {
                    'Name':'pub_subnet_1',
                    'Cidr':'10.50.0.0/24',
                    'AZ':'us-east-1b'
                },{
                    'Name':'pub_subnet_2',
                    'Cidr':'10.50.1.0/24',
                    'AZ':'us-east-1c'
                },{
                    'Name':'pri_subnet_1',
                    'Cidr':'10.50.2.0/24',
                    'AZ':'us-east-1b'
                },{
                    'Name':'pri_subnet_2',
                    'Cidr':'10.50.3.0/24',
                    'AZ':'us-east-1c'
                }
              ]

rt_list = [
            {
                'Name':'pub_rt',
                'sub_1':pub1_sub_id,
                'sub2':pub2_sub_id
            },{
                'Name':'pri_rt',
                'sub_1':pri1_sub_id,
                'sub2':pri2_sub_id
            }
          ]

class VpcBuild():
    def __init__(self):
        region = 'us-west-2'
        session = boto3.session.Session(region_name = region)
        self.vpc = session.client('ec2') #typo?
        new_vpc = self.vpc.create_vpc(CidrBlock = cidr)
        self.vpc_id = new_vpc['Vpc']['VpcId']

    def SubnetBuild(self):
        global pub1_sub_id
        global pub2_sub_id
        global pri1_sub_id
        global pri2_sub_id
        for subnet in subnet_list:
            subnet_build = self.vpc.create_subnet(VpcId = self.vpc_id,
                                                  AvailabilityZone = subnet['AZ'],
                                                  CidrBlock = subnet['Cidr'])
            if subnet['Name'] == 'pub_subnet_1':
                pub1_sub_id = subnet_build['Subnet']['SubnetId']
            if subnet['Name'] == 'pub_subnet_2':
                pub2_sub_id = subnet_build['Subnet']['SubnetId']
            if subnet['Name'] == 'pri_subnet_1':
                pri1_sub_id = subnet_build['Subnet']['SubnetId']
            if subnet['Name'] == 'pri_subnet_2':
                pri2_sub_id = subnet_build['Subnet']['SubnetId']

    def IgwBuild(self):
        global igw_id
        new_igw = self.vpc.create_internet_gateway()
        igw_id = new_igw['InternetGateway']['InternetGatewayId']
        att_igw = self.vpc.attach_internet_gateway(InternetGatewayId = igw_id,
                                                   VpcId = self.vpc_id)

    def RtBuild(self):
        global pub_rt_id
        global pri_rt_id
        for rt in rt_list:
            new_rt = self.vpc.create_route_table(VpcId = self.vpc_id)
            if rt['Name'] == 'pub_rt':
                pub_rt_id = new_rt['RouteTable']['RouteTableId']
                self.vpc.associate_route_table(RouteTableId = pub_rt_id,
                                               SubnetId = pub1_sub_id)
                self.vpc.associate_route_table(RouteTableId = pub_rt_id,
                                               SubnetId = pub2_sub_id)
                self.vpc.create_route(RouteTableId = pub_rt_id,
                                      DestinationCidrBlock = '0.0.0.0/0',
                                      GatewayId = igw_id)
            elif rt['Name'] == 'pri_rt':
                pri_rt_id = new_rt['RouteTable']['RouteTableId']
                self.vpc.associate_route_table(RouteTableId = pri_rt_id,
                                               SubnetId = pri1_sub_id)
                self.vpc.associate_route_table(RouteTableId = pri_rt_id,
                                               SubnetId = pri2_sub_id)
                self.vpc.create_route(RouteTableId = pri_rt_id,
                                      DestinationCidrBlock = '0.0.0.0/0',
                                      GatewayId = igw_id)

    def SecurityGroupBuild(self):
        global sg_id
        new_sg = self.vpc.create_security_group(Description = 'python_sg',
                                                GroupName = 'python_sg',
                                                VpcId = self.vpc_id)
        sg_id = new_sg['GroupId']
        update_sg = self.vpc.authorize_security_group_ingress(CidrIp = '%s/32'% my_ip,
                                                              GroupId = sg_id,
                                                              IpProtocol = 'tcp',
                                                              FromPort = 1,
                                                              ToPort = 60000)
    def InstanceBuild(self):
        global instance_id
        new_instance = self.vpc.run_instances(ImageId = ami_id,
                                              InstanceType = instance_type,
                                              InstanceInitiatedShutdownBehavior = 'terminate',
                                              MinCount = 1,
                                              MaxCount = 1,
                                              NetworkInterfaces = [{
                                                'DeviceIndex':0,
                                                'SubnetId':pub1_sub_id,
                                                'Groups':[sg_id],
                                                'AssociatePublicIpAddress':True,
                                                'DeleteOnTermination':True
                                              }])
        print new_instance
        #instance_id = new_instance[]

    def CreateTags(self):
        subnet_tag_list = [
                        {
                            'Name':'pub_subnet_1',
                            'SubnetId':pub1_sub_id
                        },{
                            'Name':'pub_subnet_2',
                            'SubnetId':pub2_sub_id
                        },{
                            'Name':'pri_subnet_1',
                            'SubnetId':pri1_sub_id
                        },{
                            'Name':'pri_subnet_2',
                            'SubnetId':pri2_sub_id
                        }
                      ]
        route_table_tag_list = [
                                 {
                                    'Name':'pub_rt',
                                    'RouteTableId':pub_rt_id
                                 },{
                                    'Name':'pri_rt',
                                    'RouteTableId':pri_rt_id
                                 }
                               ]
        print instance_id
        self.vpc.create_tags(Resources = [self.vpc_id, instance_id],
                             Tags = [{'Key':'Name','Value':'python_vpc'}])
        for subnet in subnet_tag_list:
            self.vpc.create_tags(Resources = [subnet['SubnetId']],
                                 Tags = [{'Key':'Name','Value':subnet['Name']}])
        for rt in route_table_tag_list:
            self.vpc.create_tags(Resources = [rt['RouteTableId']],
                                 Tags = [{'Key':'Name','Value':rt['Name']}])

def main():
    vpc = VpcBuild()
    vpc.SubnetBuild()
    vpc.IgwBuild()
    vpc.RtBuild()
    vpc.SecurityGroupBuild()
    vpc.InstanceBuild()
    vpc.CreateTags()
    print 'VPC and EC2 instance build completed!'

if __name__ == '__main__':
    main()
