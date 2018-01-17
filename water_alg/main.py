import requests/requests
import boto3/boto3
import json
from boto3.dynamodb.conditions import Key, Attr
# PEP8 naming conventions for python variables and functions is snake_case
# PEP8 convention for python comments is to start two spaces after a statement
# install dependencies into folders with the same name

dynamodb = boto3.resource('dynamodb')  # specifies the AWS service to use
PF_TABLE = dynamodb.Table('<table>')  # specifies plant factor table
DATA_TABLE = dynamodb.Table('<table>')  # specifies plant sensor table

def water_alg(event, context):
    # water algorithm for determining watering amount
    # plot_area is omitted because it has not been implemented yet
    plant_type, date_time = get_event(event)
    pf = get_pf(plant_type)
    eto = get_eto()

    gal_water_reserve = eto * plant_factor * 0.623  # * plot_area
    cup_water_reserve = gal_water_reserve * 16  # converted to cups
    print ('water plot {} gallons or {} cups'.format(
        gal_water_reserve, cup_water_reserve))
    # then determine if watering is required and invoke watering function
    # if waterMoisture < 3 & waterReserveForPlot > 1:
    #     print ("the plot will be watered")
    #     willWater = True
    # else:
    #     print ("the plot will not be watered")
    #     willWater = False
    write_results(
        plant_type, date_time, pf, eto, gal_water_reserve)

def get_event(event):
    # query primary and sort keys from 'DATA_TABLE' for updating
    # requires testing with AWS !!!
    primary_key = str(
    [event]['Records']['dynamodb'][0]['Key'][0])
    sort_key = str(
    [event]['Records']['dynamodb'][0]['Key'][1]))
    print('primary = {}, sort = {}'.format(primary_key, sort_key)  # for testing
    return primary_key, sort_key

def get_pf(plant_type):
    # query plantfactor from database
    # plant_type is used to specify the attribute from 'PF_TABLE'
    print('retrieving pf...')

    # specifying what data to query from 'PF_TABLE'
    response = PF_TABLE.query(
        KeyConditionExpression = Key('<primary-key>').eq(plant_type))
    items = response['Items']  # query returns a JSON object, 'Items'

    # assign the plant factor value from 'PF_TABLE' to a variable
    plant_factor = float(items[0]['<return-attribute>'])
    print(plant_factor)  # for testing purposes
    return plant_factor

def get_eto():
    # CIMIS API request
    # KEY: www.cimis.water.ca.gov
    print('requesting eto...')
    API_KEY = 'f972cb2a-79fb-440f-9e78-7bf034475e22'
    WSN_NUM = '204'  # WSN station #204 (SCV)
    payload = {
        'appKey': API_KEY,
        'targets': WSN_NUM,
        'startDate': '2018-01-05',
        'endDate': '2018-01-05',
        'dataItems': 'day-asce-eto'
        }
    req = requests.get('http://et.water.ca.gov/api/data?', params=payload)
    full_response = req.json()

    # specifies the ETO from api request and assigns it to a variable
    eto = float(
        full_response['Data']['Providers'][0]['Records'][0]['DayAsceEto']['Value'])
    print(eto)  # for testing purposes
    return eto

def write_results(primary, sort, pf, eto, water):
    # put results to dynamoDB eve_sensor table
    # pf, eto, water_alg
    DATA_TABLE.update_item(
        Key={
            'plant_type': primary,
            'date_time': sort
        },
        UpdateExpression='set pf = :pf, eto = :eto, water_alg= :alg',
        ExpressionAttributeValues={
            ':pf': pf,
            ':eto': eto,
            ':alg': water
        }
    )
