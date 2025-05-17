import json
from bson import json_util

MONGO_URI = 'mongodb://localhost:27018/'


def convert_to_json(response):
    response = json.loads(json_util.dumps(response))
    return response