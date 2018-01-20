import requests
import boto3
import json
from decimal import Decimal, getcontext
from boto3.dynamodb.conditions import Key, Attr
# PEP8 naming conventions for python variables and functions is snake_case
# PEP8 convention for python comments is to start two spaces after a statement
# install dependencies into folders with the same name

dynamodb = boto3.resource('dynamodb')  # specifies the AWS service to use

PF_TABLE = dynamodb.Table('eve_pf')  # specifies plant factor table
DATA_TABLE = dynamodb.Table('eve_sensor')  # specifies plant sensor table

PLANT_TYPE = None
DATE_TIME = None

# query primary and sort keys from 'DATA_TABLE' for updating
# requires testing with AWS !!!

def water_alg(event, context):
    # water algorithm for determining watering amount
    # plot_area is omitted because it has not been implemented yet
    PLANT_TYPE = str(
        event['Records'][0]['dynamodb']['Keys']['plant_type']['S'])
    DATE_TIME = str(
        event['Records'][0]['dynamodb']['Keys']['date_time']['S'])

    print('plant type = {}, date time = {}'.format(
        PLANT_TYPE, DATE_TIME))  # for testing

    pf = get_pf()
    eto = get_eto()

    gal_water_reserve = eto * pf * 0.623  # * plot_area
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
    getcontext().prec = 38
    write_results(str(pf), str(eto), str(gal_water_reserve)

def get_pf():
    # query plantfactor from database
    # plant_type is used to specify the attribute from 'PF_TABLE'
    print('retrieving pf...')

    # specifying what data to query from 'PF_TABLE'
    response = PF_TABLE.query(
        KeyConditionExpression = Key('plant_type').eq(PLANT_TYPE))
    items = response['Items']  # query returns a JSON object, 'Items'

    # assign the plant factor value from 'PF_TABLE' to a variable
    plant_factor = float(items[0]['plant_factor'])   # the attribute requested
    print(plant_factor)  # for testing purposes
    return plant_factor

def get_eto():
    # CIMIS API request
    # KEY: www.cimis.water.ca.gov
    print('requesting eto...')
    api_key = 'f972cb2a-79fb-440f-9e78-7bf034475e22'
    wsn_num = '204'  # WSN station #204 (SCV)
    date = DATE_TIME.split(' ')[0]
    payload = {
        'appKey': api_key,
        'targets': wsn_num,
        'startDate': date,
        'endDate': date,
        'dataItems': 'day-asce-eto'
        }
    eto = None
    while eto is None:
        try:
            req = requests.get('http://et.water.ca.gov/api/data?', params=payload)
            full_response = req.json()

            # specifies the ETO from api request and assigns it to a variable
            eto = float(
                full_response['Data']['Providers'][0]['Records'][0]['DayAsceEto']['Value'])
            print(eto)  # for testing purposes
        except TypeError:
            print('get_eto failed')
    return eto

def write_results(pf, eto, water):
    # put results to dynamoDB eve_sensor table
    # pf, eto, water_alg
    DATA_TABLE.update_item(
        Key={
            'plant_type': PLANT_TYPE,
            'date_time': DATE_TIME
        },
        UpdateExpression='set pf = :pf, eto = :eto, water_alg= :alg',
        ExpressionAttributeValues={
            ':pf': pf,
            ':eto': eto,
            ':alg': water
        }
    )
