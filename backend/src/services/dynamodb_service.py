import boto3
import botocore.session
from boto3.dynamodb.conditions import Key

# dynamodb = session.resource('dynamodb' )
dynamodb = boto3.resource("dynamodb")
# tableName = 'visual-schedules-data-table'

class DynamoService:
    def __init__(self, tableName: str):
        self._table = dynamodb.Table(tableName)
        # print("Querying {}".format(self._table.table_name) )

    def get_data(self, pk: str, sk: str):
        print("Query for pk:{} sk:{}".format(pk, sk))            
        data = self._table.get_item( Key = { 'pk': pk, 'sk': sk })
        print ("DATA RETURNED: %s" % data)
        return data.get('Item', None)

    def put_data(self, pk: str, sk: str, **attributes):
        item = {
            'pk': pk,
            'sk': sk
        }
        # print("ATTTRIBUTES")
        for param, value in attributes.items():
            item.update({param: value}) 
        print("Add to dynamo:  item:{}".format(item))
        result = self._table.put_item(Item=item)
        return { 'http_status': result.get("ResponseMetadata").get("HTTPStatusCode"),
            'item': item}
        

    def delete_data(self, pk: str, sk: str):
        self._table.delete_item( Key = { 'pk': pk, 'sk': sk })

    def queryOnPrimaryKey(self, key):
        return self._table.query(
            KeyConditionExpression=Key("pk").eq(key)
        )["Items"]    

    def queryOnSortKey(self, key):
        return self._table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("sk").eq(key)
        )["Items"]   

    def update_data (self, pk: str, sk: str, update_field: str, update_value):
        key = {
            'pk': pk,
            'sk': sk
        }
        update_expression = f'set {update_field} = :value'
        return self._table.update_item(
            Key = key,
            UpdateExpression = update_expression,
            ExpressionAttributeValues={
                ':value': update_value
            },
            ReturnValues='UPDATED_NEW'
        )
