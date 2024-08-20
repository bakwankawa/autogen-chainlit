import os
import json
import redis
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from apify_client import ApifyClient
import yaml

current_dir = os.path.dirname(os.path.abspath(__file__))

# Function to load YAML data from a file
def load_yaml(file_path):
    if not hasattr(load_yaml, 'data'):
        with open(file_path, 'r') as file:
            load_yaml.data = yaml.safe_load(file)
    return load_yaml.data

# Load environment variables
load_dotenv()

# GPT-4 Configuration
gpt4_config = {
    "cache_seed": None,
    "temperature": 0,
    "config_list": json.loads(os.getenv("GPT4_CONFIG_LIST")),
    "timeout": 120,
}

# Redis Configuration
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "port": int(os.getenv("REDIS_PORT")),
    "password": os.getenv("REDIS_PASSWORD"),
    "ssl": True,
    "ssl_cert_reqs": None
}

# Cosmos DB Configuration
COSMOS_DB_CONFIG = {
    "url": os.getenv("COSMOS_DB_URL"),
    "auth": os.getenv("COSMOS_DB_AUTH"),
}

SELECTED_VALUE = os.getenv("SELECTED_VALUE")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

# Initialize Redis client
redis_client = redis.Redis(**REDIS_CONFIG)  # Use redis.Redis instead of redis.StrictRedis

# Initialize Cosmos DB client
cosmos_client = CosmosClient(COSMOS_DB_CONFIG['url'], COSMOS_DB_CONFIG['auth'])  # Adjusted client initialization

# Initialize Apify client
apify_client = ApifyClient(token=APIFY_API_KEY)

# Load the messages from the YAML file
yaml_path = os.path.join(current_dir, 'prompt.yaml')
data = load_yaml(yaml_path)  # Load the YAML content

# Extract the messages
admin_system_message = data['prompt']['admin_system_message']
manager_system_message = data['prompt']['manager_system_message']
spokesman_system_message = data['prompt']['spokesman_system_message']
analyst_system_message = data['prompt']['analyst_system_message']
researcher_internal_system_message = data['prompt']['researcher_internal_system_message']
researcher_external_system_message = data['prompt']['researcher_external_system_message']