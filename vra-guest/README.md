# vra-guest

Module containing the ability to provision VMs via the VMware vRealize Automation software
using Blueprints.

***Note***: This module assumes that there is a Blueprint defined which allows a user to
provision a single VM instance with either a Linux or Windows-based OS. The intent is to
utilize vRA as a software API abstraction layer in front of VMware and build Blueprints that
model a single VM per instance and handle the network configuration requirements, possibly
creating multiple types of Blueprints to mirror the same functionality that public-cloud
providers such as AWS have for VM instance sizing (m4.large, t2.small).

## Prerequisites

This module requires a readily-available installation of the vRealize Automation software
that is reachable via the Ansible server and a user that is able to call the API and
invoke execution of Blueprints.

## Development/Testing

You can test the module functionality alongside an existing Ansible installation by specifying
the `ANSIBLE_LIBRARY` path to be the path of the library folder under this repository. For
instance - if you are in this directory specifically:

```bash
# set the library path to the module path under this folder:
ANSIBLE_LIBRARY=./lib/ansible/modules/

# run Ansible with the hosts file and corresponding playbook:
ansible-playbook -i ../../ansible/hosts --tags windows --check ../../ansible/test_vra.yml
```

The above will run the Ansible playbook and pick up the module from this repository, allowing
for fast development and feedback.

## Installation

In order to install this module into an Ansible installation permanently, place the file
`lib/ansible/modules/cloud/vmware/vra_guest.py` on your Ansible server in the directory
`<ANSIBLE_ROOT>/lib/ansible/modules/cloud/vmware/`.

An example of how to use the `vra_guest` module is included in the `sample_playbooks`
directory. All other documentation is included in the module itself.
