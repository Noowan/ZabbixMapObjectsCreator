import re
from pyzabbix import ZabbixAPI
import sys

DEBUG = True


def get_hostgroups():
    ZBX_SERVER = 'http://10.8.203.203'
    zapi = ZabbixAPI(ZBX_SERVER)
    zapi.login(api_token="2ed059cdc3b53cc0a46dc2f3f88b762495a9884ea94b0c1b3f5fdb1d06e4b2a2")
    hostgroups = zapi.hostgroup.get(output=['groupid', 'name'], real_hosts=1)
    return hostgroups


def get_hosts(_groupids):
    ZBX_SERVER = 'http://10.8.203.203'
    zapi = ZabbixAPI(ZBX_SERVER)
    zapi.login(api_token="2ed059cdc3b53cc0a46dc2f3f88b762495a9884ea94b0c1b3f5fdb1d06e4b2a2")
    hosts = zapi.host.get(output=['hostid', 'host', 'name'], groupids=_groupids, real_hosts=1, selectInterfaces=['ip'])
    return hosts


def get_items():
    final_groupids = []
    hostgroups = get_hostgroups()
    for hostgroup in hostgroups:
        print(hostgroup['name'])
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
        sys.exit()

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
    ZBX_SERVER = 'http://10.8.203.203'
    zapi = ZabbixAPI(ZBX_SERVER)
    zapi.login(api_token="2ed059cdc3b53cc0a46dc2f3f88b762495a9884ea94b0c1b3f5fdb1d06e4b2a2")
    maps = zapi.map.get(output=['sysmapid', 'name'], selectSelements=['selementid', 'elements', 'elementtype', 'label'], sortfield='name')
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
        selementsdict['selementid'] = str(i+1)
        selementsdict['elementtype'] = '0'
        selementsdict['iconid_off'] = '151'
        selementsdict['label'] = '{HOST.HOST}'
        selementsdict['elements'] = []
        selementsdict['elements'].append({'hostid': hostid})
        request['selements'].append(selementsdict)
        i+=1

    ZBX_SERVER = 'http://10.8.203.203'
    zapi = ZabbixAPI(ZBX_SERVER)
    zapi.login(api_token="2ed059cdc3b53cc0a46dc2f3f88b762495a9884ea94b0c1b3f5fdb1d06e4b2a2")
    zapi.do_request(method='map.update', params=request)

    print()


if __name__ == "__main__":
    items = get_items()
    selected_map = get_map()

    print(selected_map['name'])
    result = input("Is map correct? Y or N\n")
    if result == 'N':
        sys.exit()

    result = update_map(items, selected_map)

    print('STOPPED')
