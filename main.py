import requests
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

# run water algorithm and return result
# if watering is required, invoke watering function

def eto_request(event, context):                    #the nameing convention is a bit wonky, but it will work for this case.
    #Query plantfactor from database
    dynamodb = boto3.resource('dynamodb')                                       #specifies which resource to use think of 'dynamodb' as a Math class
    table = dynamodb.Table('PlantFactorData')                                   #Change 'plantfactordata' to the table name that holds your plantfactor data (the primary key is PlantType and sort key is PlantFactor)
    response = table.query(KeyConditionExpression = Key('PlantType').eq('Tree'))    #This is how I specify what data to query
    items = response['Items']                                                      # the query returned a json object starting with Items
    plantFactor = float(items[0]['PlantFactor'])                                    #This assigns plantfactor to a variable
    print (plantFactor)                                                             #testing purposes
# def get_pf():
    # use boto3
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
    fullResponse = req.json()
    eto = float(fullResponse['Data']['Providers'][0]['Records'][0]['DayAsceEto']['Value'])      #this specifies the ETO and assigns it to eto variable
    print(eto)                                                                     #testing purposes
    waterReserveForPlot = eto * plantFactor * 0.623 #* plotArea                 #Commented plotArea because we haven't implemented this yet
    print (waterReserveForPlot)
    # if waterMoisture < 3 & waterReserveForPlot > 1:
    #     print ("the plot will be watered")
    #     willWater = True
    # else:
    #     print ("the plot will not be watered")
    #     willWater = False
# def write_results():
#     # put results to dynamoDB eve_sensor table
#     # pf, eto, water_alg
