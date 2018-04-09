# vra-guest

Module containing the ability to provision VMs via the VMware vRealize Automation software
using Blueprints.

## Prerequisites

This module requires a readily-available installation of the vRealize Automation software
that is reachable via the Ansible server and a user that is able to call the API and
invoke execution of Blueprints.

## Installation

In order to install this module, place the file `modules/cloud/vmware/vra_guest.py` on
your Ansible server in the directory `<ANSIBLE_ROOT>/lib/ansible/modules/cloud/vmware/`.

An example of how to use the `vra_guest` module is included in the `sample_playbooks`
directory. All other documentation is included in the module itself.
