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
    folder:
        description:
            - Directory under which the secret is/should live
        required: true
    secret_name:
        description:
            - Name of the secret to be stored or referenced
        required: true
    secret_content:
        description:
            - Password or secret content to be stored
        required: true
    thycotic_base_url:
        description:
            - Base URL of the Thycotic instance
        required: true
    thycotic_wsdl_path:
        description:
            - WSDL path to be appended to the 'thycotic_base_url'
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
    - PyYaml
    - pysimplesoap

author:
    - Justin Karimi (@jekhokie) <jekhokie@gmail.com>
'''

EXAMPLES = '''
- name: Create a secret with a password
  delegate_to: localhost
  thycotic_secret:
    folder: "test_folder/sub_folder_1"
    secret_name: "my test secret"
    secret_content: "supersecretpassword"
    thycotic_base_url: "https://thycotic.base.url"
    thycotic_wsdl_path: "WebServices/SSWebService.asmx?wsdl"
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

import yaml
from zeep import Client
from ansible.module_utils.basic import AnsibleModule

class ThycoticHelper(object):
    '''Helper class for managing interaction with Thycotic and corresponding resources.'''

    def __init__(self, module):
        """
        Default constructor
        Args:
            module: object containing parameters passed by playbook

        Returns: (ThycoticHelper) Instance of the ThycoticHelper class
        """
        self.module = module
        self.folder = module.params['folder']
        self.secret_name = module.params['secret_name']
        self.secret_content = module.params['secret_content']
        self.thycotic_wsdl_url = "%s/%s" % (module.params['thycotic_base_url'], module.params['thycotic_wsdl_path'])
        self.auth_username = module.params['thycotic_auth_username']
        self.auth_password = module.params['thycotic_auth_password']
        self.auth_domain = module.params['thycotic_auth_domain']
        self.auth_token = ""

        # initialize token for auth
        self.get_auth()

    def get_auth(self):
        """
        Get an auth token and store for all subsequent requests

        Returns: None (updates the instance with the token)
        """
        try:
            # attempt to get a client connection, timing out if unreachable for 15 seconds
            client = Client(self.thycotic_wsdl_url)

            # perform a request for an auth token, and raise an exception if none can be obtained
            response = client.service.Authenticate(username=self.auth_username, password=self.auth_password, domain=self.auth_domain)
            auth_token = response['Token']

            if auth_token is None:
                raise Exception("An authentication exception has occurred: %s" % response['Errors'])

            # store auth token for subsequent requests
            self.auth_token = auth_token
        except Exception as e:
            self.module.fail_json(msg="Failed to get auth token: %s" % (e))

def run_module():
    # available options for the module
    module_args = dict(
        folder=dict(type='str', required=True),
        secret_name=dict(type='str', required=True),
        secret_content=dict(type='str', required=True),
        thycotic_base_url=dict(type='str', required=True),
        thycotic_wsdl_path=dict(type='str', required=True),
        thycotic_auth_username=dict(type='str', required=True),
        thycotic_auth_password=dict(type='str', required=True, no_log=True),
        thycotic_auth_domain=dict(type='str', required=True)
    )

    # seed result dict that is returned
    result = dict(
        changed=False,
        failed=False,
        destroy_id=''
    )

    # default Ansible constructor
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # initialize the interface and get an auth token
    thycotic_helper = ThycoticHelper(module)

    # check mode - see whether the secret need to be created

    # only create the secret if it doesn't already exist

    # assign results for output

    # successful run
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
