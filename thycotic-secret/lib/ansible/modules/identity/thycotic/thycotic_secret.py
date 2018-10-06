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


    # TODO: Make sure the secret does not yet exist - if so, just update the password/fields to the
    #       values requested if there is a change (and update the module response for changes).


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
