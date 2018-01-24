import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')  # specifies the AWS service to use

PF_TABLE = dynamodb.Table('eve_pf')      # specifies plant factor table
DATA_TABLE = dynamodb.Table('eve_data')  # specifies plant sensor table
USER_TABLE = dynamodb.Table('eve_user')  # specifies the user table

CURRENT_USER = 'zero'  # the value of your 'user_id' from 'USER_TABLE'

# ---------- DYNAMODB TABLE FUNCTIONS ----------
def get_user_info():
    # get information about the user, plant and plot size for water_alg
    user_info = []  # inserted to 'DATA_TABLE' after calculations

    # the attributes to query from 'USER_TABLE'
    user_attr = [
        'user_id',
        'plant_type',
        'plant_spec',
        'plot_size']

    # populate 'PLANT_INFO' with 'CURRENT_USER' item from 'USER_TABLE'
    for each in user_attr:
        user_info.append(
            table_query(USER_TABLE, 'user_id', CURRENT_USER, each))

    return user_info

def table_query(table, key, value, attr):
    # queries an attribute from dynamoDB table
    # table: the table being queried
    # key: the primary key (partition key)
    # value: value of the primary key
    # attr: the attribute being queried
    response = table.query(
        KeyConditionExpression = Key(key).eq(value))
    items = response['Items']  # query returns a JSON object, 'Items'

    # assign the plant factor value from 'PF_TABLE' to a variable
    queried = items[0][attr]   # the attribute requested
    return queried

def write_results(date_time, user, alg):
    # put results to dynamoDB eve_sensor table
    # pf, eto, water_alg
    DATA_TABLE.update_item(
        Key={
            'date_time': date_time
        },
        UpdateExpression='set user = :user alg = :alg',
        ExpressionAttributeValues={
            ':user': user,
            ':alg': alg
        }
    )
