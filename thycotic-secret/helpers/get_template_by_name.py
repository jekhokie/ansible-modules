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

import argparse
import os
import json
import yaml
import suds

# parse the user arguments
parser = argparse.ArgumentParser(description='Get and format the required parameters for a Secret Template')
parser.add_argument('--name', help='Name of the Secret Template', required=True)
args = parser.parse_args()

# load configuration - required to obtain URL, username, password
# to log into the Thycotic instance
config_file = os.path.join(os.path.dirname(__file__), '../test_args/thycotic_secret.json')
with open(config_file) as f:
    CONFIG = json.load(f)['ANSIBLE_MODULE_ARGS']

# obtain the auth token
client = suds.client.Client(CONFIG["thycotic_wsdl_url"])
auth_token = client.service.Authenticate(CONFIG["thycotic_auth_username"],
                                         CONFIG["thycotic_auth_password"],
                                         "",
                                         CONFIG["thycotic_auth_domain"])

if auth_token.Token == "" is None:
    raise Exception("An authentication exception has occurred: {}".format(auth_token.Errors))

# GetSecretTemplates: get all templates, parse the desired based on provided name
templates = client.factory.create("GetSecretTemplates")
templates.token = auth_token.Token
secret_templates = client.service.GetSecretTemplates(templates)

if len(secret_templates.SecretTemplates[0]) == 0:
    raise(Exception("No Secret Templates found - errors: {}".format(secret_templates.Errors)))

# search for the template specified by the user
found_template = None
for template in secret_templates.SecretTemplates[0]:
    if template.Name == args.name:
        found_template = template
        break

if found_template == None:
    raise Exception("Could not find template with name {}".format(args.name))
print(found_template)

# parse the secret for the required fields needed
secret_type_id = found_template['Id']
field_ids = []
fields = []
for field in found_template.Fields.SecretField:
    field_ids.append(field.Id)
    fields.append("<REPLACEME_{}>".format(field.DisplayName))

template_yml = {
    "secretTypeId": found_template['Id'],
    "secretFieldIds": field_ids,
    "secretItemValues": fields
}

# output the results
print("-----------------------------------------------------")
print(yaml.dump(template_yml, default_flow_style=False))
print("-----------------------------------------------------")
print("Take the above and place them into your Ansible configuration - note you MUST include ALL")
print("fields (include blank strings if you don't wish to specify the values) in the particular order.")
