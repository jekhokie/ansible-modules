# thycotic-secret

Module containing the ability to create and manage Thycotic Secret Server secrets.

## Prerequisites

This module requires a readily-available installation of the Thycotic Secret Server
software that is reachable via the Ansible server and a user that is able to call the
respective SOAP API of the endpoint.

## Development/Testing

First and foremost, install Ansible and set up your environment for module development
so you can develop and run the module testing from this project directory:

```bash
# set the library path to the module path under this folder:
export ANSIBLE_LIBRARY=./lib/ansible/modules/

# set up the python virtualenv and development environment
. <PATH_TO_ANSIBLE>/venv/bin/activate
. <PATH_TO_ANSIBLE>/hacking/env-setup

# install the required dependencies
pip install -r requirements.txt
```

Assuming that your `hosts` file and `test_thycotic.yml` playbook are in the Ansible directory
(you can copy them from the `sample_playbooks` directory, re-name them to `*.yml` files,
and modify the parameters to make them your own), you can test the module functionality
alongside an existing Ansible installation:

```bash
# copy sample playbooks and edit them
cp sample_playbooks/test_thycotic.yml.sample <PATH_TO_ANSIBLE>/test_thycotic.yml
vim <PATH_TO_ANSIBLE>/test_thycotic.yml

# run Ansible with the hosts file and corresponding playbook:
ansible-playbook -i "localhost," --tags generic --check <PATH_TO_ANSIBLE>/test_thycotic.yml
```

The above will run the Ansible playbook and pick up the module from this repository, allowing
for fast development and feedback.

If you wish to utilize raw test inputs you can utilize samples from the `test_args/` directory
like so:

```bash
# run the python test case using the test JSON data:
python ./lib/ansible/modules/identity/thycotic/thycotic_secret.py test_args/thycotic_secrets.json
```

## Installation

In order to install this module into an Ansible installation permanently, place the file
`lib/ansible/modules/identity/thycotic/thycotic_secret.py` on your Ansible server in the directory
`<ANSIBLE_ROOT>/lib/ansible/modules/identity/thycotic/`.

An example of how to use the `thycotic_secret` module is included in the `sample_playbooks`
directory. All other documentation is included in the module itself.

## Other Notes

Some other useful information:

* Link to the WSDL for the Secret Server you are using: [link](https://<THYCOTIC_HOSTNAME>/WebServices/SSWebService.asmx?wsdl)
* Can use utilities such as Postman for executing SOAP requests.
