#!/usr/bin/env python
#
# Purpose: Helper script to identify the required data fields for a particular
# secret template that is used to create secrets in a Thycotic Secret Server
# instance.
#
# Requirements:
#  - This script depends on the file ../test_args/thycotic_secret.json
#    to exist and have valid URL endpoints and credentials for Thycotic
#  - Remember to install dependencies prior to running this file
#      pip install -r requirements
#
# Parameters:
#  - 'name': Name of the secret template being searched for
#
# Returns:
#  - 'args': YAML object that can be copy/pasted into the 'args' section of
#            the Ansible thycotic_secret module
#
# Example:
#    python helpers/get_template_by_name.py --name 'Password'
#
#    args:
#      username: 'Test User'
#      password: 'supersecretpassword'

import argparse
import os
import json
import yaml
from zeep import Client

# parse the user arguments
parser = argparse.ArgumentParser(description='Get and format the required parameters for a Secret Template')
parser.add_argument('--name', help='Name of the Secret Template', required=True)
args = parser.parse_args()

# load configuration - required to obtain URL, username, password
# to log into the Thycotic instance
config_file = os.path.join(os.path.dirname(__file__), '../test_args/thycotic_secret.json')
with open(config_file) as f:
    CONFIG = json.load(f)['ANSIBLE_MODULE_ARGS']

# this is not DRY - same code exists in the module, but no great way to
# consolidate given this is simply a helper script
client = Client("%s/%s" % (CONFIG['thycotic_base_url'], CONFIG['thycotic_wsdl_path']))

# perform a request for an auth token, and raise an exception if none can be obtained
response = client.service.Authenticate(username=CONFIG['thycotic_auth_username'],
                                       password=CONFIG['thycotic_auth_password'],
                                       domain=CONFIG['thycotic_auth_domain'])
auth_token = response['Token']

if auth_token is None:
    raise Exception("An authentication exception has occurred: %s" % response['Errors'])

# GetSecretTemplates: Get all templates, parse the desired based on provided name
response = client.service.GetSecretTemplates(token=auth_token)

found_template = None
for template in response['SecretTemplates']['SecretTemplate']:
    if template['Name'] == args.name:
        found_template = template
        break

if found_template == None:
    raise Exception("Could not find template with name %s" % args.name)

# parse the secret for the required fields needed
template_name = "<REPLACEME_%s>" % found_template['Name']
secret_type_id = found_template['Id']
field_ids = []
fields = []
for field in found_template['Fields']['SecretField']:
    field_ids.append(field['Id'])
    fields.append("<REPLACEME_%s>" % field['DisplayName'])

template_yml = {
    "secretTypeId": found_template['Id'],
    "secretName": "<REPLACEME_secretName>",
    "secretFieldIds": field_ids,
    "secretItemValues": fields,
    "folderName": "solutions/custom_folder"
}

# output the results
print("-----------------------------------------------------")
print(yaml.dump(template_yml, default_flow_style=False))
print("-----------------------------------------------------")
print("WARNING: YOU MUST WRAP STRING VALUES IN THE ABOVE WITH QUOTES AND INDENT APPROPRIATELY")
