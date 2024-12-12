import boto3
from typing import Dict, Any
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.table_name = 'asm-tickets'
        self.table = self._get_or_create_table()
    
    def _get_or_create_table(self):
        try:
            # Try to get the table
            table = self.dynamodb.Table(self.table_name)
            table.load()  # This will raise an exception if table doesn't exist
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create the table if it doesn't exist
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'ticket_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'ticket_id',
                            'AttributeType': 'S'
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                # Wait for the table to be created
                table.wait_until_exists()
                return table
            else:
                raise e

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.table.put_item(Item=ticket_data)
            return ticket_data
        except ClientError as e:
            print(f"Error creating ticket: {e}")
            raise
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        try:
            response = self.table.get_item(Key={'ticket_id': ticket_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting ticket: {e}")
            raise
    
    def list_tickets(self) -> list:
        try:
            response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error listing tickets: {e}")
            raise