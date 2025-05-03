from typing import Any, Dict, List, Optional

from fastapi_pagination.ext.pymongo import paginate as pymongo_paginate
from pymongo import MongoClient

from configs import MONGO_URI


class MongoHelper:

    def __init__(
        self,
    ):
        self._client: Optional[MongoClient] = MongoClient(MONGO_URI)
        # fmt: off
        self._collection = self._client['corridas_db']['eventos']

    def find_all_objects(
        self,
        filters: dict,
    ):

        documents = self._collection.find(filters)

        return documents

    def find_all_objects_as_page(
        self,
        filters: dict,
        order: dict = {},
    ):

        documents_page = pymongo_paginate(
            collection=self._collection,
            query_filter=filters,
            sort=order,
        )

        return documents_page

    def find_all_objects_with_one_field(
        self,
        filters: dict,
        field: dict,
    ):

        documents = self._collection.find(filters, field)

        return documents

    def find_one_from_object(
        self,
        query: dict,
    ):

        document = self._collection.find_one(query)

        return document

    def insert_document(
        self,
        document: Dict[str, Any],
    ):
        document_id = self._collection.insert_one(document).inserted_id
        inserted_document = document.copy()
        inserted_document.update({"_id": document_id})
        return inserted_document

    def update_document(
        self,
        query: Dict[str, Any],
        update_operation: Dict[str, Any],
    ):
        return self._collection.update_one(
            query,
            update_operation,
        )

    def replace_document(
        self,
        query: Dict[str, Any],
        update_operation: Dict[str, Any],
    ):
        return self._collection.replace_one(
            query,
            update_operation,
        )

    def delete_one_document(
        self,
        query: Dict[str, Any],
    ):
        return self._collection.delete_one(query)