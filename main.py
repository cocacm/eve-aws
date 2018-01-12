import requests

def get_pf():
    # use boto3
    # query plant_type from dynamoDB eve_pf table
    # query plant_factor from dynamoDB eve_pf table
    
def eto_request(event, context):
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
    eto = req.json()
    print(eto)
    return 'request successful'

def water_alg():
    # run water algorithm and return result
    # if watering is required, invoke watering function

def write_results():
    # put results to dynamoDB eve_sensor table
    # pf, eto, water_alg
