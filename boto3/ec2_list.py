import boto3
from openpyxl import Workbook
from datetime import datetime

data_list = []

# profile name 지정
session = boto3.Session(profile_name='prod')
client = session.client('ec2')
paginator = client.get_paginator('describe_instances')
response_iterator = paginator.paginate()

# page별 반복
for page in response_iterator:
    # page 내의 Reservations 내의 Instances 반복하며 인스턴스 정보 출력
    for j in page['Reservations']:
        for i in j['Instances']:
            NameTag = ''
            # 인스턴스 정보 안에 Tags 정보가 있는 경우만
            if 'Tags' in i:
                # Tags 정보 중 Name Key를 찾아 Value값 반환해서 저장
                for tag in i['Tags']:
                    if tag['Key'] == 'Name':
                        NameTag = tag['Value']
            
            data_tuple = (
                # Name Tag 값
                NameTag,
                # private ip
                i['PrivateDnsName'],
                # instance id
                i['InstanceId'],
                # image id
                i['ImageId'],
                # instance platform (ex, linux/unix)
                i['PlatformDetails'],
                # instance type (ex, t3.medium)
                i['InstanceType'],
                # 생성 시간 > time형식 변경 필요
                i['LaunchTime'].strftime('%Y-%m-%d'),
                # 현재 State (ex, running)
                i['State']['Name']
            )
            data_list.append(data_tuple)


# excel file로 저장
wb = Workbook()
ws = wb.active

header = ('NameTag', 'PrivateDnsName', 'InstanceId', 'ImageId', 'Platform', 'InstanceType', 'LaunchTime', 'State')
ws.append(header)
for data in data_list:
    ws.append(data)

# 현재 시간을 사용해 file 저장
excel_name = 'ec2_list_' + datetime.now().strftime('%Y%m%d%H%M') + '.xlsx'
wb.save(excel_name)