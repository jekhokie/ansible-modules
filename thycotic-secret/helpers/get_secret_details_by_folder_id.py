#!/usr/bin/env python
#
# Purpose: Helper script to demonstrate searching for a secret within a folder
# having a specific ID.
#
# Requirements:
#  - This script depends on the file ../test_args/thycotic_secret.json
#    to exist and have valid URL endpoints and credentials for Thycotic
#  - Remember to install dependencies prior to running this file
#      pip install -r requirements
#
# Parameters:
#  - 'name': Name of the secret being searched for
#  - 'folder-id': Name of the secret being searched for
#
# Returns:
#  - 'args': Secret response data if the secret was found having the name and folderId
#            the Ansible thycotic_secret module
#
# Example:
#    python helpers/get_secret_details_by_folder_id.py --name 'Password' --folder-id 123

import argparse
import os
import json
import yaml
import suds

# parse the user arguments
parser = argparse.ArgumentParser(description='Get and format the required parameters for a Secret Template')
parser.add_argument('--name', help='Name of the Secret', required=True)
parser.add_argument('--folder-id', help='ID of the folder to search within', required=True)
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

# GetSecretsByFolder: get the secret within a folder having a particular name
secrets = client.factory.create("SearchSecretsByFolder")
secrets.token = auth_token.Token
secrets.searchTerm = args.name
secrets.folderId = args.folder_id
secrets.includeSubFolders = False
secrets.includeDeleted = False
secrets.includeRestricted = False
secret_results = client.service.SearchSecretsByFolder(secrets)

if len(secret_results.SecretSummaries) == 0:
    raise(Exception("No Secret with name '{}' found in folder with ID {} - errors: {}".format(args.name, args.folder_id, secret_results.Errors)))
else:
    print("--------------------------")
    print("Secret Result:")
    print("--------------------------")
    print(secret_results)

# GetSecret: get the secret details having a particular ID
# TODO: This will grab the first result, but if there are duplicates, this
#       logic is likely to have issues since you won't know which instance you're grabbing
secret = secret_results.SecretSummaries[0][0]
secret_template = client.factory.create("GetSecret")
secret_template.token = auth_token.Token
secret_template.secretId = secret.SecretId
secret_template.loadSettingsAndPermissions = False
secret_data = client.service.GetSecret(secret_template)

if len(secret_data.Errors) > 0:
    raise(Exception("Could not get details of Secret with ID {} - errors: {}".format(secret.SecretId, secret_data.Errors[0])))

# print a list of all key/value pairs for the secret
print("--------------------------")
print("Secret Data:")
print("--------------------------")
for d in secret_data.Secret.Items.SecretItem:
    print("{} - {}".format(d.FieldName, d.Value))
