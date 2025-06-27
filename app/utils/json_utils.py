# app/utils/json_utils.py
import json
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Union


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def convert_to_json(obj: Any) -> Any:
    """
    Converte objetos MongoDB para JSON serializável.

    Args:
        obj: Objeto a ser convertido

    Returns:
        Objeto convertido para JSON serializável
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json(item) for item in obj]
    else:
        return obj