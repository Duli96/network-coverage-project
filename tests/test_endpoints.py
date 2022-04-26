
import resource
from unittest.mock import patch
from wsgiref.headers import Headers
import pytest
import requests
import json
from unittest import mock
from pathlib import Path



resources = Path(__file__).parent


async def test_get_network(test_client,db):
    print("In test")
    response =await test_client.get("/api/network")
    
    assert response.status == 200
    print(await response.text())

# @mock.patch('app.queries.generate_id')
async def test_add_new_network(test_client,db):

    data = {'Graph File': (resources/'data-1.graphml').open("rb")}
    response = await test_client.post("/api/network",data = data)
    r = await response.text()
    print(r)
    assert response.status == 201