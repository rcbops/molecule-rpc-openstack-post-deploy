Role Name
=========

This role is to validate the post deployment process as described on the
following page:
https://one.rackspace.com/pages/viewpage.action?pageId=110992052

Requirements
------------

This role requires an existing rpc-openstack deployment and a JSON file
containing the ansible dynamic inventory for that infrastructure. This role is
assumed to be executed from the "Deployment Host" for said OpenStack
deployment.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: molecule-rpc-openstack-post-deploy, x: 42 }

License
-------

Apache 2.0
