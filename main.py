#!/usr/bin/env python

import os
import sys
import requests

from config import SOURCE_URL, SOURCE_TOKEN, SOURCE_PAAS_TOKEN, DESTINATION_URL, DESTINATION_TOKEN, DESTINATION_PAAS_TOKEN



def create_inventory(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN): 
    """ Make an API call to obtain details about hosts """
    url = SOURCE_URL + '/api/v1/entity/infrastructure/hosts'
    params = { "includeDetails": "false" }
    headers = { "Authorization" : "Api-Token " + SOURCE_TOKEN }

    print("Making API call to source tenant to obtain list of hosts to:", url)

    response = requests.request("GET", url, params=params, headers=headers)
    print("API response is:", response.status_code)

    """ Hosts is a list of dictionaries containing all details on all the hosts """
    hosts = response.json()

    """ From hosts we grab a list of linux and windows hosts here """
    linux_hosts = list(filter(lambda linuxhosts: linuxhosts['osType'] == 'LINUX', hosts))
    windows_hosts = list(filter(lambda linuxhosts: linuxhosts['osType'] == 'WINDOWS', hosts))

    """ Write a list of IPAddreses of Linux/Windows hosts to a inventory files; In case host has multiple IPs we take the first one. """
    file = open("linux_inventory.txt", 'w')
    for d in linux_hosts:
        file.write(d['ipAddresses'][0])
        file.write("\n")
    file.close()

    file = open("windows_inventory.txt", 'w')
    for d in windows_hosts:
        file.write(d['ipAddresses'][0])
        file.write("\n")
    file.close()



def run_ansible(DESTINATION_URL, DESTINATION_PAAS_TOKEN):
    """ Use Ansible to execute a playbooks on the hosts in inventory files """
    cmd = '/usr/bin/ansible-playbook -i /root/DynatraceAPI/linux_inventory.txt /root/DynatraceAPI/migrate-tenant.yml --extra-vars "DESTINATION_URL={} DESTINATION_PAAS_TOKEN={}"'.format(DESTINATION_URL,DESTINATION_PAAS_TOKEN)
    os.system(cmd)


def migrate_aps(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN):
    """ Make an API call to obtain details about Applications """
    url = SOURCE_URL + '/api/config/v1/applications/web'
    headers = { "Authorization" : "Api-Token " + SOURCE_TOKEN }
   
    print("Making API call to source tenant obtain list of applications on:", url)

    response = requests.request("GET", url, headers=headers)
    print("API response is:", response.status_code)


    """ Aps is a dictionary of a list of dictionaries containing all details on all the Aps we want to migrate """
    aps = response.json()
    #print(aps)

    """ applist is a list of aps formatted from api call """
    applist = [d.get('id') for sublists in aps.values() for d in sublists]
    #print(applist)
    for ap in applist:
        url = SOURCE_URL + '/api/config/v1/applications/web/{}'.format(ap)
        headers = { "Authorization" : "Api-Token " + SOURCE_TOKEN }
        print("Making API call to source tenant to get application config:", url)
        response = requests.request("GET", url, headers=headers)
        print("API response is:", response.status_code)
        details = response.json()
        # here we have to drop identifier from details and only then we can post it:
        details.pop('identifier')
        #print(details)

        url2 = DESTINATION_URL + '/api/config/v1/applications/web'
        print("Making API call to destination tenant to create applications:", url)
        headers2 = { "Authorization" : "Api-Token " + DESTINATION_TOKEN }
        response2 = requests.request("POST", url2, headers=headers2, json=details)
        print("API response is:", response2.status_code)


def migrate_services(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN):
    """ Make an API call to obtain details about services """
    url = SOURCE_URL + '/api/config/v1/service/requestAttributes'
    headers = { "Authorization" : "Api-Token " + SOURCE_TOKEN }

    print("Making API call to source tenant obtain list of services on:", url)
    response = requests.request("GET", url, headers=headers)
    print("API response is:", response.status_code)

    """ Services is a dictionary of a list of dictionaries containing all details on all the Aps we want to migrate """
    services = response.json()
    #print(services)

    """ svlist is a list of services formatted from api call """
    svlist = [d.get('id') for sublists in services.values() for d in sublists]
    for sv in svlist:
        url = SOURCE_URL + '/api/config/v1/service/requestAttributes/{}'.format(sv)
        headers = { "Authorization" : "Api-Token " + SOURCE_TOKEN }
        print("Making API call to source tenant to get service config:", url)
        response = requests.request("GET", url, headers=headers)
        print("API response is:", response.status_code)
        details = response.json()
        #  here we have to drop identifier from details and only then we can post it:
        details.pop('id')
        #  print(details)

        url2 = DESTINATION_URL + '/api/config/v1/service/requestAttributes'
        headers2 = { "Authorization" : "Api-Token " + DESTINATION_TOKEN }
        print("Making API call to destination tenant to create services:", url2)
        response2 = requests.request("POST", url, headers=headers2, json=details)
        print("API response is:", response.status_code)
        msg = response2.json()
        print(msg)

def migrate_rules(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN):
    """ Make an API call to obtain details about services """
    url = "https://faw85907.live.dynatrace.com/api/config/v1/applicationDetectionRules"
    headers = { "Authorization" : "Api-Token 2LY0YApfTceQfKVDVYtLs" }

    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    """ Rules is a dictionary of a list of dictionaries containing all details on all the rules we want to migrate """
    rules = response.json()
    #print(rules)

    """ rulelist is a list of services formatted from api call """
    rulelist = [d.get('id') for sublists in rules.values() for d in sublists]
    for rule in rulelist:
        url = SOURCE_URL + '/api/config/v1/applicationDetectionRules/{}'.format(rule)
        headers = { "Authorization" : "Api-Token " + SOURCE_TOKEN }
        print("Making API call to source tenant obtain list of rules on:", url)
        response = requests.request("GET", url, headers=headers)
        print("API response is:", response.status_code)
        details = response.json()
        # here we have to drop identifier from details and only then we can post it:
        details.pop('id')
        #print(details)

        url2 = DESTINATION_URL + '/api/config/v1/applicationDetectionRules'
        headers2 = { "Authorization" : "Api-Token " + DESTINATION_TOKEN }
        response2 = requests.request("POST", url2, headers=headers2, json=details)
        print("API response is:", response2.status_code)
        msg = response2.json()
        print(msg)


#####################################################################################
#   EXECUTE SECTION                                                                 #
#####################################################################################


if __name__ == "__main__":
   
    create_inventory(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN)
    
    run_ansible(DESTINATION_URL, DESTINATION_PAAS_TOKEN)

    migrate_aps(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN)

    migrate_services(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN)

#    migrate_rules(SOURCE_URL, SOURCE_TOKEN, DESTINATION_URL, DESTINATION_TOKEN)
           
