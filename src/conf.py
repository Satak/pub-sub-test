from os import getenv

PROJECT_ID = getenv('GCP_PROJECT')
SUBSCRIPTION_NAME = getenv('SUBSCRIPTION_NAME')
TOPIC_NAME = getenv('TOPIC_NAME')
CMDB_DATABASE = 'cmdb.sqlite'
SECRET = getenv('SECRET', 'my-super-secret-secretkey')
SERVER_ADDRESS = getenv('SERVER_ADDRESS', 'http://localhost:5000')

# NOTE: you can modify this list to create the customers dropdown menu
CUSTOMERS = [
    'Customer 1',
    'Customer 2',
    'Customer 3',
]
