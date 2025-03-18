import random
import re
import sys
import requests
import os
from dotenv import load_dotenv

HEADERS={"Content-Type": 'application/json-rpc'}

load_dotenv('params.env')
API_TOKEN = os.getenv('API_TOKEN')
URL = os.getenv('URL')


def get_hostgroups():
    payload = {
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": ["groupid", "name"],
        },
        "auth": API_TOKEN,
        "id": 1
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    response = response.json()
    return response['result']

def get_hosts(_groupids):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name"],
            "groupids": _groupids,
            "selectInterfaces": ["ip"]
        },
        "auth": API_TOKEN,
        "id": 1
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    response = response.json()
    return response['result']

def get_items():
    final_groupids = []
    hostgroups = get_hostgroups()
    #for hostgroup in hostgroups:
        #print(hostgroup['name'])
    selected_groups = input("Print comma separated list of groups to iteract\n")
    selected_groups = selected_groups.split(",")

    for selected_group in selected_groups:
        selected_group = selected_group.rstrip()
        selected_group = selected_group.lstrip()
        for hostgroup in hostgroups:
            if re.search(selected_group, hostgroup['name']) != None:
                final_groupids.append(hostgroup)

    print("Selected groups:\n")
    for final_groupid in final_groupids:
        print(final_groupid['name'])
    result = input("Is group list correct? Y or N\n")
    if result == 'N':
        return False

    hosts = []
    groupids = ""
    for final_groupid in final_groupids:
        items = get_hosts(final_groupid['groupid'])
        for item in items:
            hosts.append(item)

    print("Devices list:")
    for host in hosts:
        host['ip'] = host["interfaces"][0]["ip"]
        del host['interfaces']
        print(f"{host['hostid']}, {host['name']}, {host['ip']}")

    return hosts

def get_map():
    payload = {
        "jsonrpc": "2.0",
        "method": "map.get",
        "params": {
            "output": ["sysmapid", "name", "height", "width"],
            "selectSelements": ['selementid', 'elements', 'elementtype', 'label'],
            "sortfield": 'name'
        },
        "auth": API_TOKEN,
        "id": 1
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    response = response.json()
    maps = response['result']
    select = input("Print map name which you want to edit\n")
    for map in maps:
        if re.search(select, map['name']) != None:
            return map
def update_map(items, selected_map):
    hostids = []
    sysmapid = selected_map['sysmapid']
    for item in items:
        hostids.append(item['hostid'])

    request = {}
    request['sysmapid'] = sysmapid
    request['selements'] = []
    i = 0
    for hostid in hostids:
        elements = []
        hostiddict = {'hostid': hostid}
        elements.append(hostiddict)
        selementsdict = {}
        selementsdict['selementid'] = str(i + 1)
        selementsdict['elementtype'] = '0'
        selementsdict['iconid_off'] = '151'
        selementsdict['label'] = '{HOST.HOST}\n{HOST.IP}'
        selementsdict['x'] = str(random.randint(50, int(selected_map['width']) - 100))
        selementsdict['y'] = str(random.randint(50, int(selected_map['height']) - 100))
        selementsdict['elements'] = []
        selementsdict['elements'].append({'hostid': hostid})
        request['selements'].append(selementsdict)
        i += 1


    payload = {
        "jsonrpc": "2.0",
        "method": "map.update",
        "params": request,
        "auth": API_TOKEN,
        "id": 1
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    response = response.json()

def check_API_availability():
    if API_TOKEN == None or URL == None:
        raise ValueError("API_TOKEN or URL is not specified in .env file")
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
        "output": ["hostid", "host", "name"],
        "selectInterfaces": ["ip"]
        },
        "auth": API_TOKEN,
        "id": 1
    }
    response = requests.post(URL, json=payload, headers=HEADERS).json()
    if 'error' in response:
        raise BaseException(f"{response['error']['message']} - {response['error']['data']}")



if __name__ == "__main__":
    check_API_availability()
    while True:
        items = get_items()
        if items != False:
            break
    selected_map = get_map()

    print(selected_map['name'])
    result = input("Is map correct? Y or N\n")
    if result == 'N':
        sys.exit()

    result = update_map(items, selected_map)

    print('Finished')
