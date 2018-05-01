# -*- coding: utf-8 -*-
import requests
import json
import re
from cStringIO import StringIO


""" Glance helpers
"""


def get_scoped_token(openrc):
    """Getting project-scoped token
    Project-scoped tokens are the bread and butter of OpenStack. They express your authorization to operate in a
    specific tenancy of the cloud and are useful to authenticate yourself when working with most other services.
    They contain a service catalog, a set of roles, and details of the project upon which you have authorization.

    A project-scoped token is similar to the below string:
    gBBBsfawerasaserse9"mLQilrmwtA-dfdfdfdfsasetrewfazsThelqeIE7nba3wgyxgrsawefsafawDuuxFMnY7E5hud_UT9bmI |
    KY39DRIVbv85sXmfddzbFma0UUQtA0Z7oDsRUKVz1zKp-zHVxfdsfasebsdgasegzas"

    Args:
          openrc (str): string variable containing `openrc` authorization and authentication file

    Return:
          project-scoped token (str): `X-Subject-Token` in the requested headers.
    """

    # Retrieve data from /root/openrc file:
    OS_PROJECT_DOMAIN_NAME = get_key_value(openrc, "OS_PROJECT_DOMAIN_NAME")
    OS_PROJECT_NAME = get_key_value(openrc, "OS_PROJECT_NAME")
    OS_USERNAME = get_key_value(openrc, "OS_USERNAME")
    OS_PASSWORD = get_key_value(openrc, "OS_PASSWORD")
    OS_AUTH_URL = get_key_value(openrc, "OS_AUTH_URL")

    url = OS_AUTH_URL + "/auth/tokens"
    headers = {'content-type': 'application/json'}

    payload = {
        "auth": {
            "scope": {
                "project": {
                    "domain": {
                        "name": OS_PROJECT_DOMAIN_NAME
                    },
                    "name": OS_PROJECT_NAME
                }
            },
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": OS_USERNAME,
                        "password": OS_PASSWORD,
                        "domain": {
                            "name": OS_PROJECT_DOMAIN_NAME
                        }
                    }
                }
            }
        }
    }

    payload_json = json.dumps(payload)

    res = requests.post(url, headers=headers, data=payload_json)

    return res.headers['X-Subject-Token']


def get_key_value(openrc_file, key):
    """ Getting key value based on the value regex

    Args:
        openrc_file (str): string variable containing `openrc` authorization and authentication file
        key (str): Key string. String variable `openrc_file` contents will be converted into python
            dict `os_vars`, the key here is one of the keys in the dict.

    Return:
        Key value (str): Value of key in the dict.

    """

    # Regex is something similar to 'export OS_PROJECT_DOMAIN_NAME=Default\n':
    regex = r'export\s+(OS_[A-Z_]+)=(.+)$'
    os_vars = {}

    fh = StringIO(openrc_file)
    for line in fh.readlines():
        matching = re.search(regex, line)
        if matching:
            # Remove the single quotes wrapping the password
            value = matching.groups()[1].replace("'", "")
            os_vars[matching.groups()[0]] = value

    try:
        key_value = os_vars[key]
    except KeyError as error:
        raise RuntimeError("Could not find variable {} in the file {}\nKeyError:\n{}".format(key, openrc_file, error))

    return key_value
