import boto3
import botocore
import logging
import sys

from botocore.exceptions import ClientError

csvfile = 'lc_list.csv'

aws_region = 'ap-northeast-2'
session = boto3.Session(profile_name='dev')
client = session.client('ec2')

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
### column ###
1 : AutoScalingGroupName
2 : LaunchConfigurationName
3 : LaunchConfigurationName
4 : ImageId
5 : KeyName
6 : SG
7 : InstanceType
8 : IamInstanceProfile
"""

def read_csv_tags(filename):
    lc_data = {}
    try:
        logger.info('Getting CSV : {}'.format(filename))
        with open(filename) as file:
            for line in file:
                line_spl = line.rstrip().split(',')
                asg_name = line_spl[1]
                if asg_name not in lc_data: 
                    lc_data[asg_name] = {
                        'LaunchConfigurationName': line_spl[2], 
                        'ImageId': line_spl[3],
                        'KeyName': line_spl[4],
                        'SG': line_spl[5],
                        'InstanceType': line_spl[6],
                        'IamInstanceProfile': line_spl[7]
                    }
        return lc_data

    except ClientError as e:
        message = 'getting csv error {}'.format(e)
        logger.error(message)

def create_launch_template(launch_configuration_list):
    for lt_name, lc_data in launch_configuration_list.items():
        #"""
        response = client.create_launch_template(
                #DryRun = True,
            LaunchTemplateName = str(lt_name),
            LaunchTemplateData = {
                'IamInstanceProfile': {
                    'Arn': str(lc_data['IamInstanceProfile'])
                },
                'ImageId': str(lc_data['ImageId']),
                'InstanceType': str(lc_data['InstanceType']),
                'KeyName': str(lc_data['KeyName']),
                'SecurityGroupIds': [
                    'sg-02e64faa041c6021a',
                    'sg-054f1745484108122'
                ]
            },
        )
        #"""
        print(lt_name, lc_data)

def delete_launch_template(launch_configuration_list):
    for lt_name, lc_data in launch_configuration_list.items():
        response = client.delete_launch_template(
        LaunchTemplateName=lt_name
        )
        print(lt_name)

def main():
    try:
        launch_configuration_list = read_csv_tags(csvfile)
        create_launch_template(launch_configuration_list) 
        #delete_launch_template(launch_configuration_list) 
    except ClientError as e:
        message = 'main error {}'.format(e)
        logger.error(message)

if __name__ == "__main__":
    main()
