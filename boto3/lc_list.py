import boto3
import logging
import sys
import argparse
import pandas as pd
from botocore.exceptions import ClientError
from openpyxl import Workbook
from datetime import datetime
import pandas as pd

# Arguments
parser = argparse.ArgumentParser(description='Launch Configurations')
parser.add_argument("-p",  "--profile", help='dev or prod')
args = parser.parse_args()

if args.profile is None:
    parser.error("-p or --profile requires")

# profile
aws_profile = args.profile
aws_region = 'ap-northeast-2'
session = boto3.Session(profile_name=aws_profile)

print ("env:", session.profile_name)

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# describe_launch_configurations
def describe_launch_configurations(region, lc_name):
    client = session.client('autoscaling')
    paginator = client.get_paginator('describe_launch_configurations')
    response_iterator = paginator.paginate(
       LaunchConfigurationNames=[lc_name]
    )
    try:
        for page in response_iterator:
            for j in page['LaunchConfigurations']:
                sg = ' / '.join(j['SecurityGroups'])
                data_tuple = (
                    j['LaunchConfigurationName'],
                    j['ImageId'],
                    j['KeyName'],
                    sg,
                    j['InstanceType'],
                    j['IamInstanceProfile']
                )
        return data_tuple

    except ClientError as e:
        message = 'Error getting list of launch configurations: {}'.format(e)
        logger.error(message)

    return {}

# describe_auto_scaling_groups
def describe_auto_scaling_groups(region):
    logger.info('Getting Launch Configurations In-Use for ASG: {}'.format(region))
    client = session.client('autoscaling')
    paginator = client.get_paginator('describe_auto_scaling_groups')
    response_iterator = paginator.paginate()
    data_list = []
    try: 
        for page in response_iterator:
            for j in page['AutoScalingGroups']:
                if 'LaunchConfigurationName' in j:
                    asg_name = j['AutoScalingGroupName']
                    lc_name = j['LaunchConfigurationName']
                    lc_tuple = describe_launch_configurations(aws_region, lc_name) 
                    data_tuple = (
                        asg_name,
                        lc_name
                    )
                    murge_tuple = data_tuple + lc_tuple 
                    data_list.append(murge_tuple)
        return data_list
        
    except ClientError as e:
        message = 'Error getting list of autoscaling group: {}'.format(e)
        logger.error(message)

    return {}

def write_excel(file):
    # excel 저장
    wb = Workbook()
    ws = wb.active

    header = ('AutoScalingGroupName', 'LaunchConfigurationName', 'LaunchConfigurationName', 'ImageId', 'KeyName', 'SG', 'InstanceType', 'IamInstanceProfile')
    ws.append(header)
    for data in file:
        ws.append(data)

    # file 저장
    excel_name = 'lc_list_' + datetime.now().strftime('%Y%m%d%H%M') + '.xlsx'
    wb.save(excel_name)
    # input
    import_excel = pd.read_excel(excel_name)
    import_excel.to_csv('./lc_list.csv')

def main():

    inventory = []

    try:
        inventory = describe_auto_scaling_groups(aws_region)
    except ClientError as e:
        message = 'Error getting inventory, check your credential configuration or try with the -r argument: {}'.format(e)
        logger.error(message)

    write_excel(inventory)
    return inventory

if __name__ == "__main__":
    main()