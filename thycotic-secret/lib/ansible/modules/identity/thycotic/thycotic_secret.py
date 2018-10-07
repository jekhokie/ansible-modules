#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: thycotic_secret

short_description: Management of Thycotic Secret Server secrets

version_added: "2.6"

description:
    - "Create and manage secrets in the Thycotic Secret Server software"

options:
    folder_id:
        description:
            - ID of the folder to store the secret in
        required: true
    secret_type_id:
        description:
            - ID of the type of secret being created
        required: true
    secret_name:
        description:
            - Name of the secret to be stored or referenced
        required: true
    secret_content:
        description:
            - Password or secret content to be stored
        required: true
    secret_field_ids:
        description:
            - Sequence of field IDs required to create the secret (requiring all IDs, in specific order)
        required: true
    secret_item_values:
        description:
            - Data for various fields corresponding to the secret_field_ids - can include blank strings
        required: true
    thycotic_wsdl_url:
        description:
            - Full path/URL to the Thycotic WSDL
        required: true
    thycotic_auth_username:
        description:
            - Username for the account to authenticate against Secret Server
        required: true
    thycotic_auth_password:
        description:
            - Password for the account to authenticate against Secret Server
        required: true
    thycotic_auth_domain:
        description:
            - Domain for the account to authenticate against Secret Server
        required: true

requirements:
    - suds

author:
    - Justin Karimi (@jekhokie) <jekhokie@gmail.com>
'''

EXAMPLES = '''
- name: Create a secret with a password
  delegate_to: localhost
  thycotic_secret:
    folder_id: "123"
    secret_type_id: "456"
    secret_name: "my test secret"
    secret_content: "supersecretpassword"
    secret_field_ids:
    - 108
    - 111
    - 110
    - 109
    - 251
    - 252
    secret_item_values:
    - "a"
    - "b"
    - "c"
    - ""
    - ""
    thycotic_wsdl_url: "https://thycotic.base.url/WebServices/SSWebService.asmx?wsdl"
    thycotic_auth_username: "MyUsername"
    thycotic_auth_password: "auth_password"
    thycotic_auth_domain: "local"
'''

RETURN = '''
secret:
    description: Metadata about the newly-created secret
    type: dict
    returned: always
    sample: none
'''

import suds
from ansible.module_utils.basic import AnsibleModule

def run_module():
    # available options for the module
    module_args = dict(
        folder_id=dict(type="int", required=True),
        secret_type_id=dict(type="int", required=True),
        secret_name=dict(type="str", required=True),
        secret_content=dict(type="str", required=True),
        secret_field_ids=dict(type="list", required=True),
        secret_item_values=dict(type="list", required=True),
        thycotic_wsdl_url=dict(type="str", required=True),
        thycotic_auth_username=dict(type="str", required=True),
        thycotic_auth_password=dict(type="str", required=True, no_log=True),
        thycotic_auth_domain=dict(type="str", required=True)
    )

    # seed result dict that is returned
    result = dict(
        changed=False,
        failed=False
    )

    # default Ansible constructor
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # create the SOAP client for interaction
    client = suds.client.Client(module.params["thycotic_wsdl_url"])

    # get an auth token
    token = client.service.Authenticate(module.params["thycotic_auth_username"],
                                        module.params["thycotic_auth_password"],
                                        "",
                                        module.params["thycotic_auth_domain"])

    # first, inspect whether the secret exists - and if so, check whether the fields just need to be updated
    secrets = client.factory.create("SearchSecretsByFolder")
    secrets.token = token.Token
    secrets.searchTerm = module.params["secret_name"]
    secrets.folderId = module.params["folder_id"]
    secrets.includeSubFolders = False
    secrets.includeDeleted = False
    secrets.includeRestricted = False
    secret_results = client.service.SearchSecretsByFolder(secrets)

    if len(secret_results.SecretSummaries) > 0:
        # found the secret already exists - figure out if it needs to be updated or not
        # TODO: This will grab the first result, but if there are duplicates, this
        #       logic is likely to have issues since you won't know which instance you're grabbing
        secret = secret_results.SecretSummaries[0][0]
        secret_template = client.factory.create("GetSecret")
        secret_template.token = token.Token
        secret_template.secretId = secret.SecretId
        secret_template.loadSettingsAndPermissions = False
        secret_data = client.service.GetSecret(secret_template)

        if len(secret_data.Errors) > 0:
            module.fail_json(msg="Failed to get details of existing Secret with ID {} - errors: {}".format(secret.SecretId, secret_data.Errors[0]))

        # parse each data field for each mapping and ensure values are aligned - if not, update
        need_to_update = False
        for i, prop in enumerate(secret_data.Secret.Items.SecretItem):
            # first, ensure the property ID matches what we expect (ensure template has not been changed)
            if prop.FieldId != module.params["secret_field_ids"][i]:
                module.fail_json(msg="Failed to assess Secret - field ID {} in position {} does not line up with expected value {}".format(prop.FieldId, i, module.params["secret_field_ids"][i]))

            # convert value to blank string in case None type to enable comparison with provided string values
            prop.Value = "" if (prop.Value == None) else prop.Value

            # next, ensure the value is correct - if not, kick out and perform a full update of all fields to be on the safe side
            if prop.Value != module.params["secret_item_values"][i]:
                need_to_update = True
                break

        # if we need to update the secret, perform a full update of all fields to be on the safe side
        if need_to_update == True:
            result['changed'] = True
            update_secret = client.factory.create("UpdateSecret")
            update_secret.token = token.Token
            update_secret.secret = secret_data.Secret
            for i, item in enumerate(module.params["secret_item_values"]):
                update_secret.secret.Items.SecretItem[i].Value = item
            update_result = client.service.UpdateSecret(update_secret)

            if (len(update_result.Errors) > 0):
                module.fail_json(msg="Failed to update Secret with ID {} - errors: {}".format(secret.SecretId, update_result.Errors))
    else:
        # did not find an existing secret - create new from scratch
        # this implementation is terribly inflexible and confusing needing to specify IDs for various
        # components - you will need to navigate through the GUI to get the ID numbers for these sections:
        #  - Secret Type ID: "Create New Secret", then view the "SecretTypeID" parameter in the URL - additionally
        #                    you can use the script 'get_template_by_name.py' in the 'helpers/' directory which
        #                    is a bit more friendly and lets you specify the name of the Secret Type you're looking for
        #  - Folder ID: Right-click on the folder, select "Inspect", then capture the "id" attribute of the
        #               label DOM element (minus the 'f_' part)
        #  - Secret Field IDs: Need to get this from a scripted query of the Secret Template using the
        #                      Secret Template ID - IDs need to be in the correct order
        #  - Secret Item Values: Corresponding values, in order, to the Field IDs in previous bullet
        #
        # There is a Python script in the utils/ directory that allows you to specify a Secret Template ID
        # and will pull the information related to what the field IDs are for the specific template
        result['changed'] = True

        new_secret = client.factory.create("AddSecret")
        new_secret.token = token.Token
        new_secret.secretTypeId = module.params["secret_type_id"]
        new_secret.secretName = module.params["secret_name"]
        new_secret.folderId = module.params["folder_id"]
        new_secret.secretFieldIds = client.factory.create("ArrayOfInt")
        new_secret.secretFieldIds.int = module.params["secret_field_ids"]
        new_secret.secretItemValues = client.factory.create("ArrayOfString")
        new_secret.secretItemValues.string = module.params["secret_item_values"]

        # attempt to create the secret, but thrown an error if something goes wrong
        try:
            secret = client.service.AddSecret(new_secret)
            if secret.Errors != "":
                module.fail_json(msg="Failed to create secret '{}' in Thycotic: {}".format(module.params["secret_name"], secret.Errors[0]))
            else:
                result['secret_name'] = secret.Secret.Name
                result['secret_id'] = secret.Secret.Id
                result['folder_id'] = secret.Secret.FolderId
        except Exception as e:
            module.fail_json(msg="Failed to create secret '{}' in Thycotic: {}".format(module.params["secret_name"], e))

    # successful run
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
