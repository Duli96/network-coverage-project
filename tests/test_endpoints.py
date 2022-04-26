
from unittest.mock import patch
from wsgiref.headers import Headers
import pytest
import requests
import json
from unittest import mock



async def test_get_network(test_client):
    print("In test")
    response =await test_client.get("/api/network")
    
    assert response.status == 200
    print(await response.text())