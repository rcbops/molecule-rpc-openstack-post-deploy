import requests
import json
import re
from cStringIO import StringIO

# -*- coding: utf-8 -*-

""" Glance helpers

"""


def get_scoped_token(openrc):
    """Getting project-scoped token
    Project-scoped tokens are the bread and butter of OpenStack. They express your authorization to operate in a
    specific tenancy of the cloud and are useful to authenticate yourself when working with most other services.
    They contain a service catalog, a set of roles, and details of the project upon which you have authorization.

    A project-scoped token is similar to the below string:
    gAAAAABa50GczT9"mLQilrmwtA-ffY1WrRdJneZaVn9ZIzHwnCeMkrLThelqeIE7nba3wgyxkPETq4lpZCXtmeRMSDuuxFMnY7E5hud_UT9bmI |
    KY39DRIVbv85sXmfddzbFma0UUQtA0Z7oDsRUKVz1zKp-zHV3RDIRe7WzfhIyPWMjZr2c7dvUk"

    Args:
          openrc: string variable containing `openrc` authorization and authentication file

    Return:
          string: `X-Subject-Token` (Project-Scoped Token) in the requested headers.
    """

    # Retrieve data from /root/openrc file:
    OS_PROJECT_DOMAIN_NAME = _get_key_value(openrc, "OS_PROJECT_DOMAIN_NAME")
    OS_PROJECT_NAME = _get_key_value(openrc, "OS_PROJECT_NAME")
    OS_USERNAME = _get_key_value(openrc, "OS_USERNAME")
    OS_PASSWORD = _get_key_value(openrc, "OS_PASSWORD")
    OS_AUTH_URL = _get_key_value(openrc, "OS_AUTH_URL")

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


def _get_key_value(openrc_file, key):
    """ Getting key value based on the value regex

    Args:
        openrc_file: string variable containing `openrc` authorization and authentication file
        key: string for key. String variable `openrc_file` contents will be converted into python
            dict `os_vars`, the key here is one of the keys in the dict.

    Return:
        Value of key in the dict.

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

    return os_vars[key]
