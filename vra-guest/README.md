# vra-guest

Module containing the ability to provision VMs via the VMware vRealize Automation software
using Blueprints.

***Note***: This module assumes that there is a Blueprint defined which allows a user to
provision a single VM instance with either a Linux or Windows-based OS. The intent is to
utilize vRA as a software API abstraction layer in front of VMware and build Blueprints that
model a single VM per instance and handle the network configuration requirements, possibly
creating multiple types of Blueprints to mirror the same functionality that public-cloud
providers such as AWS have for VM instance sizing (m4.large, t2.small).

***Note***: At this time, this module only creates VMs if they do not exist and is
idempotent based on the existence of a VM based on the hostname. This module cannot yet be
utilized to modify parameters of existing VMs.

## Prerequisites

This module requires a readily-available installation of the vRealize Automation software
that is reachable via the Ansible server and a user that is able to call the API and
invoke execution of Blueprints.

## Development/Testing

First and foremost, install Ansible and set up your environment for module development
so you can develop and run the module testing from this project directory:

```bash
# set the library path to the module path under this folder:
ANSIBLE_LIBRARY=./lib/ansible/modules/

# set up the python virtualenv and development environment
. <PATH_TO_ANSIBLE>/venv/bin/activate
. <PATH_TO_ANSIBLE>/hacking/env-setup

# install the required dependencies
pip install -r requirements.txt
```

Assuming that your `hosts` file and `test_vra.yml` playbook are in the Ansible directory
(you can copy them from the `sample_playbooks` directory, re-name them to `*.yml` files,
and modify the parameters to make them your own), you can test the module functionality
alongside an existing Ansible installation:

```bash
# copy sample playbooks and edit them
cp sample_playbooks/test_vra.yml.sample <PATH_TO_ANSIBLE>/test_vra.yml
vim <PATH_TO_ANSIBLE>test_vra.yml

# run Ansible with the hosts file and corresponding playbook:
ansible-playbook -i <PATH_TO_ANSIBLE>/hosts --tags windows --check <PATH_TO_ANSIBLE>/test_vra.yml
```

The above will run the Ansible playbook and pick up the module from this repository, allowing
for fast development and feedback.

If you wish to utilize raw test inputs you can utilize samples from the `test_args/` directory
like so:

```bash
# run the python test case using the test JSON data:
python ./lib/ansible/modules/cloud/vmware/vra_guest.py test_args/vra_guest.json
```

## Installation

In order to install this module into an Ansible installation permanently, place the file
`lib/ansible/modules/cloud/vmware/vra_guest.py` on your Ansible server in the directory
`<ANSIBLE_ROOT>/lib/ansible/modules/cloud/vmware/`.

An example of how to use the `vra_guest` module is included in the `sample_playbooks`
directory. All other documentation is included in the module itself.
