# OSP Hacks
In the interest of executing the converge steps on OSP, some hackery took
place. This document lists the manual changes to the system that were made in
order to accomodate this molecule.

## Manual testing process
This section walks through the process of running the tests on an OSP MNAIO
deploy on Phobos. Details about the context for these steps and where they
differ from an RPC-Openstack deployment are discussed in the [Context Documentation](## Context Documentaion)
section.

### Deploy
Follow [Corey Wright's gist](https://gist.github.com/coreywright/17fd443a9ce4fca20da7a68da0fdbe22)
for bringing up the OSP-13 environment. Detailed steps shown here executed on
20180928.

Create MNAIO host on phobos
```
openstack server create             \
    --flavor ironic-storage-gating  \
    --key-name jrd-mbpro            \
    --image baremetal-ubuntu-bionic \
    --nic net-id=ironic             \
    --wait                          \
    jrd-osp13
```

1. SSH as ubuntu user to the IP address of the created host.
1. Start a screen session to protect the interaction against the connection terminating.
1. Escalate to root user.
1. Run osp-mnaio installation. The `REDHAT_PASSWORD` value can be obtained by
   contacting the ASC team.
```
screen
sudo su -
git clone https://github.com/rcbops/osp-mnaio /opt/osp-mnaio
cd /opt/osp-mnaio/
export REDHAT_ISO_URL=http://172.20.41.45/rhel-server-7.5-x86_64-dvd.iso
export REDHAT_USERNAME=rs-rpc-test
export REDHAT_PASSWORD=...
export REDHAT_POOL_ID=8a85f98c631d065501632d160bce6cb6
export REDHAT_CONSUMER_NAME=johnduarte
./build.sh
```

### Setup testing repos

On MNAIO host as ubuntu user:
```
git clone https://github.com/rcbops/rpc-openstack-system-tests sys-tests
chmod -R a+w sys-tests
sudo ln -s /home/ubuntu/sys-tests /root/sys-tests
```


On the MNAIO host as root user: Run execute_tests to create venv
This will fail after the venv is setup because the `dynamic_inventory.json` file
will not be available for the script to obtain. Execution of the `molecularize`,
`molecule converge`, and `molecule verify` commands will come after this
failure and are detailed below.
```
cd ~/sys-tests
./execute_tests.sh
. venv-molecule/bin/activate
```

On the MNAIO host as root user: Modify the sys-tests/execute_tests.sh
1. Comment out the line that copies the dynamic_inventory.py file
1. Remove the for do/done wrapper to run tests on all of the molecules
1. Set TEST=molecules/molecule-rpc-openstack-post-deploy

On the MNAIO host as root user, create the dynamic_inventory.py file
```
git clone https://github.com/jtyr/ansible-ini_inventory ~/tools/ini_inventory

cp /opt/osp-mnaio/playbooks/inventory/hosts /tmp/hosts

cat >> /tmp/hosts <<EOD

[network_hosts]
director

[utility]
director

[utility_all]
director
EOD

python ~/tools/ini_inventory/ini_inventory.py \
    --filename /tmp/hosts \
    --list > ~/sys-tests/dynamic_inventory.json
```

On director as root user, create clouds.yaml file and edit the file.
Ensure that the values in the `clouds.yaml` file match those in the
`/home/stack/overcloudrc` file. This should involve just changing the
auth_url and the password.
```
mkdir -p /root/.config/openstack
cat > /root/.config/openstack/clouds.yaml <<EOD
clouds:
  default:
    auth:
      auth_url: http://192.168.24.13:5000/v3
      project_name: admin
      tenant_name: admin
      username: admin
      password: HTrVTxUT7sh4MjpfdbY88vttz
      user_domain_name: Default
      project_domain_name: Default
    region_name: regionOne
    interface: internal
    identity_api_version: "3"
EOD
```

From development system
```
export POST_DEPLOY=<path/to/molecule-rpc-openstack-post-deploy/checkout>
export OSP_HOST=<ip-address-of-MNAIO-host>
rsync -vaz --delete  -e 'ssh' $POST_DEPLOY ubuntu@$OSP_HOST:sys-tests/molecules/
```

On the MNAIO host as root user, run the converge step
```
cd ~/sys-tests
moleculerize \
    --output molecules/molecule-rpc-openstack-post-deploy/molecule/default/molecule.yml \
    dynamic_inventory.json
cd molecules/molecule-rpc-openstack-post-deploy
molecule converge
```

To repeat:
1. From development system:
```
rsync -vaz --delete  -e 'ssh' $POST_DEPLOY ubuntu@$OSP_HOST:sys-tests/molecules/
```
1. From MNAIO host:
```
cd - ; moleculerize --output molecules/molecule-rpc-openstack-post-deploy/molecule/default/molecule.yml dynamic_inventory.json  ; cd - ; molecule converge
```

To run tests:
1. From MNAIO host:
```
export RPC_PRODUCT_RELEASE=master
cd - ; moleculerize --output molecules/molecule-rpc-openstack-post-deploy/molecule/default/molecule.yml dynamic_inventory.json  ; cd - ; molecule --debug verify
```

## Context Documentaion

### clouds.yaml
RPC-O assumes the presence of the clouds.yaml file on the target host that is
running the `os_*` modules. This file was manually put on the director under
the root account. The values for the auth section were derived from the
`overcloudrc` file on the director at `/home/stack/overcloudrc`. Also be aware
that the `region_name` is case sensitive and is *NOT* the same as the
_RegionOne_ value used on RPC-O installations.

```
[root@director ~]# cat /root/.config/openstack/clouds.yaml
clouds:
  default:
    auth:
      auth_url: http://192.168.24.13:5000/v3
      project_name: admin
      tenant_name: admin
      username: admin
      password: HTrVTxUT7sh4MjpfdbY88vttz
      user_domain_name: Default
      project_domain_name: Default
    region_name: regionOne
    interface: internal
    identity_api_version: "3"
```

### Inventory
The inventory file is location on the deploy host at
`/opt/osp-mnaio/playbooks/inventory/hosts`. This file is in the INI format.

#### JSON
Somehow I converted it to the JSON format needed by moleculerize.
Maybe?
```
git clone https://github.com/jtyr/ansible-ini_inventory ~/tools/ini_inventory

python ~/tools/ini_inventory/ini_inventory.py \
    --filename /opt/osp-mnaio/playbooks/inventory/hosts
    --list > ~/sys-tests/dynamic_inventory.json
```

#### Additional host definitions
The following sections were added to the `dynamic_inventory.json` file in
order to ensure that the director is set to the node groups expected by the
rpc-o centric playbooks.

##### Network
The network hosts need to be defined in the json inventory prior to running
molecularize. This is currently a manual step. So, the execute_tests.sh script
needs to be updated *NOT* to copy the dynamic inventory locally. The JSON
inventory needs to be created with the tool above and the following segment
needs to be injected into it.
```
"network_hosts": {
  "hosts": [
    "director"
  ]
},
```

##### Utility
The utility hosts are used by the ansible within ansible execution of the
openstack-ansible-ops playbooks. These hosts need to be defined in the
inventory file on the target host. This problem has been solved by copying the
inventory file to a temp location using the `copy` module and injecting the
host definitions with the `blockinfile` module.

This is the json represenation for reference.
```
  "utility": {
      "children": [],
      "hosts": [
          "director"
      ]
  },
  "utility_all": {
      "children": [
          "utility"
      ],
      "hosts": []
  },
```

Here are the ansible tasks used to solve the problem:

Copy the file:
```
- name: Copy inventory to working file
  copy:
    src: "{{ find_inventory_file.stdout }}"
    dest: "{{ working_inventory }}"
    remote_src: True

- name: Set proper inventory file
  set_fact:
    inventory_file: "{{ working_inventory }}"
```

Inject the declarations:
```
- name: Add Utility to remote inventory
  blockinfile:
    path: "{{ inventory_file }}"
    block: |
      [utility]
      director
      [utility_all]
      director
  when:
    - rpc_openstack is undefined
```

##### Infra
The tests are currently set to run on os-infra_hosts. So, this is also added
ot the inventory with the director as the only member of the group.

#### Hack openstack-ansible-ops
The openstack-ansible-ops openstack-service-setup ensures that the python
shade module is installed via apt. This fails on a redhat based host, so the
following sed commands were added to install it via pip instead.
```
sed -i 's/apt:/pip:/' openstack-service-setup.yml
sed -i 's/python-shade/shade/' openstack-service-setup.yml
```
