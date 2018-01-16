import requests
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
# PEP8 naming conventions for python variables and functions is snake_case
# PEP8 convention for python comments is to start two spaces after a statement

# run water algorithm and return result
# if watering is required, invoke watering function

def water_alg():
    # water algorithm
    # plot_area is omitted because it has not been implemented yet
    plant_factor = get_pf()
    eto = eto_request()

    gal_water_reserve = eto * plant_factor * 0.623  # * plot_area
    cup_water_reserve = gal_water_reserve * 16  # converted to cups
    print ('water plot {} gallons or {} cups'.format(
        gal_water_reserve, cup_water_reserve))

    # if waterMoisture < 3 & waterReserveForPlot > 1:
    #     print ("the plot will be watered")
    #     willWater = True
    # else:
    #     print ("the plot will not be watered")
    #     willWater = False

def get_pf():
    # query plantfactor from database
    print('retrieving pf...')
    dynamodb = boto3.resource('dynamodb')  # specifies the AWS service to use
    pf_table = dynamodb.Table('eve_pf')  # specifies dynamodb table

    # specifying what data to query
    response = pf_table.query(
        KeyConditionExpression = Key('<primary>').eq('<element>'))
    items = response['Items']  # query returns a json object, 'Items'

    # assign the plant factor from table to a variable
    plant_factor = float(items[0]['<value>'])
    print(plant_factor)  # for testing purposes
    return plant_factor

def eto_request():
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

# def write_results():
#     # put results to dynamoDB eve_sensor table
#     # pf, eto, water_alg

water_alg()
