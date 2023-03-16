import requests


from urllib import request
from bs4 import BeautifulSoup
import json

def test_1(authorized_client_admin):
    res = authorized_client_admin("/login")

    """url = 'http://127.0.0.1:8000/login'
    html = request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.findAll('div'))
    #site_json = json.loads(soup.text)
    # printing for entrezgene, do the same for name and symbol
    #print([d.get('entrezgene') for d in site_json['hits'] if d.get('entrezgene')])"""

