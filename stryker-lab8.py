from boto3 import Session
import simplejson as json
from pprint import pprint as pp

service = 'ec2'
region = 'us-east-1'
vpc_cidr = '10.40.0.0/22'
pub1_subnet = '10.40.0.0/24'
my_ip = '34.210.73.72'
ami_id = 'ami-bc39e1c3'
instance_type = 't2.nano'

aws = Session()
session = aws.client(service, region_name = region)
new_vpc = session.create_vpc(CidrBlock = vpc_cidr)
vpc_id = new_vpc['Vpc']['VpcId']
'''
vpc = json.dumps(new_vpc, indent = 2)
vpc_json = json.loads(vpc)
for vpc_config in vpc_json.values():
    for key, value in vpc_config.iteritems():
		if key == 'VpcId':
			vpc_id = value
'''
pub1_subnet_build = session.create_subnet(VpcId = vpc_id, CidrBlock = pub1_subnet)
pub1_sub_id = pub1_subnet_build['Subnet']['SubnetId']
'''
sub1_dumps = json.dumps(pub1_subnet_build, indent = 2)
sub1_json = json.loads(sub1_dumps)
for sub_data in sub1_json.values():
    for key, value in sub_data.iteritems():
        if key == 'SubnetId':
            pub1_sub_id = value
'''
new_igw = session.create_internet_gateway()
igw_id = new_igw['InternetGateway']['InternetGatewayId']
'''
igw = json.dumps(new_igw, indent = 2)
igw_json = json.loads(igw)
for igw_config in igw_json.values():
    for key, value in igw_config.iteritems():
        if key == 'InternetGatewayId':
            igw_id = value
'''
att_igw = session.attach_internet_gateway(InternetGatewayId = igw_id, VpcId = vpc_id)
pub_rt = session.create_route_table(VpcId = vpc_id)
pp(pub_rt)
pub_rt_id = pub_rt['RouteTable']['RouteTableId']
'''
pub_rt_dumps = json.dumps(pub_rt, indent = 2)
pub_rt_json = json.loads(pub_rt_dumps)
for rt_data in pub_rt_json.values():
    for key, value in rt_data.iteritems():
        if key == 'RouteTableId':
            pub_rt_id = value
'''
rt_assoc_pub1 = session.associate_route_table(RouteTableId = pub_rt_id,
                                              SubnetId = pub1_sub_id)
igw_route_add = session.create_route(RouteTableId = pub_rt_id,
                                     DestinationCidrBlock = '0.0.0.0/0',
                                     GatewayId = igw_id)
new_sg = session.create_security_group(Description = 'python_sg',
                                       GroupName = 'python_sg',
                                       VpcId = vpc_id)
sg_id = new_sg['GroupId']
update_sg = session.authorize_security_group_ingress(CidrIp = '%s/32' % my_ip,
                                                     GroupId = sg_id,
                                                     IpProtocol = 'tcp',
                                                     FromPort = 1,
                                                     ToPort = 60000)

new_instance = session.run_instances(ImageId = ami_id,
                                     InstanceType = instance_type,
                                     InstanceInitiatedShutdownBehavior = 'terminate',
                                     MinCount = 1,
                                     MaxCount = 1,
                                     NetworkInterfaces = [{ 'DeviceIndex' : 0,
                                                            'SubnetId' : pub1_sub_id,
                                                            'Groups' : [sg_id],
                                                            'AssociatePublicIpAddress' : True,
                                                            'DeleteOnTermination' : True}])
