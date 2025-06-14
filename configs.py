import json
import os

from bson import json_util
from dotenv import load_dotenv

load_dotenv()

MONGODB_REMOTE_URI = os.getenv("MONGODB_REMOTE_URI")


def convert_to_json(response):
    response = json.loads(json_util.dumps(response))
    return response
