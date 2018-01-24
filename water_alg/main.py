import requests  # must be included in AWS deployment package
import json
import tables  # 'tables.py' script for querying and inserting to dynamoDB
# PEP8 naming conventions for python variables and functions is snake_case
# PEP8 convention for python comments is to start two spaces after a statement

def water_alg(event, context):
    # water algorithm for determining watering amount
    # plot_area is omitted because it has not been implemented yet
    user_info = tables.get_user_info() # list with attributes from 'eve_user' table

    plant_type = user_info[1]
    date_time = str(
        event['Records'][0]['dynamodb']['Keys']['date_time']['S'])

    print('plant type = {}, date time = {}'.format(
        plant_type, date_time))  # for testing

    # list with the values and results of 'water_alg' calculations
    water_alg = [
        get_pf(plant_type),
        get_eto(date_time)
        ]

    plot_size = user_info[3]
    gal_water_reserve = eto * pf * 0.623 * plot_size
    cup_water_reserve = gal_water_reserve * 16  # converted to cups
    print ('water plot {} gallons or {} cups'.format(
        gal_water_reserve, cup_water_reserve))

    water_alg.append(gal_water_reserve)
    tables.write_results(user_info, water_alg)

def get_pf(plant_type):
    # query plantfactor from database
    # plant_type is used to specify the attribute from 'PF_TABLE'
    print('retrieving pf...')
    plant_factor = tables.table_query(
        tables.PF_TABLE, 'plant_type', plant_type, 'plant_factor')
    print(plant_factor)  # for testing purposes
    return plant_factor

def get_eto(date_time):
    # CIMIS API request
    # KEY: www.cimis.water.ca.gov
    print('requesting eto...')
    api_key = 'f972cb2a-79fb-440f-9e78-7bf034475e22'
    wsn_num = '204'  # WSN station #204 (SCV)
    start_end_date = date_time.split(' ')[0]
    payload = {
        'appKey': api_key,
        'targets': wsn_num,
        'startDate': start_end_date,
        'endDate': start_end_date,
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
            print('...get_eto failed')
    return eto
