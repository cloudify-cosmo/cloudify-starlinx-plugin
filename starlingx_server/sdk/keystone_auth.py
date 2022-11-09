import json

import requests
from keystoneauth1.identity import v3
from keystoneauth1 import session

DC_MANAGER_API_URL = 'dcmanager_url'
PATCHING_API_URL = 'patch_url'
SYSINV_API_URL = 'sysinv_url'

CHECKERS = ['/', '/v1.0', '/v1']


def get_token_from_keystone(auth_url: str, username: str, password: str, project_name: str = 'admin',
                            user_domain_name: str = None, project_domain_name: str = None,
                            user_domain_id: str = None, project_domain_id: str = None, verify: bool = True) -> str:
    """
    This function return keystone token.
    :param auth_url: Keystone url
    :param username: Keystone username
    :param password: Keystone password
    :param project_name: Keystone project
    :param user_domain_name: User domain name
    :param project_domain_name: Project domain name
    :param user_domain_id: User domain id
    :param project_domain_id: Project domain id
    :param verify: check SSL certs

    :rtype: str
    """
    auth = v3.Password(auth_url=auth_url,
                       username=username,
                       password=password,
                       project_name=project_name,
                       user_domain_name=user_domain_name,
                       project_domain_name=project_domain_name,
                       user_domain_id=user_domain_id,
                       project_domain_id=project_domain_id)

    sess = session.Session(auth=auth, verify=verify)
    token = sess.get_token()

    return token


def get_endpoints(auth_url: str, headers: dict, verify: bool = True) -> dict:
    """
    Returns API URLS for DcManager and Patch API.

    :param auth_url: Keystone auth url
    :param headers: Header containing token
    :param verify: check SSL certs

    :rtype: dict
    """
    url = '{}/auth/catalog'.format(auth_url)
    endpoints = requests.get(url=url, headers=headers, verify=verify)
    all_endpoints = {}

    for entity in endpoints.json()['catalog']:
        if entity['type'] == 'dcmanager':
            for endpoint in entity['endpoints']:
                if endpoint['interface'] == 'public':
                    endpoint = endpoint['url']
                    for checker in CHECKERS:
                        if endpoint.endswith(checker):
                            endpoint = endpoint[:-len(checker)]
                    all_endpoints[DC_MANAGER_API_URL] = endpoint
                    break

        if entity['type'] == 'patching':
            for endpoint in entity['endpoints']:
                if endpoint['interface'] == 'public':
                    endpoint = endpoint['url']
                    for checker in CHECKERS:
                        if endpoint.endswith(checker):
                            endpoint = endpoint[:-len(checker)]
                    all_endpoints[PATCHING_API_URL] = endpoint
                    break

        if entity['type'] == 'platform':
            for endpoint in entity['endpoints']:
                if endpoint['interface'] == 'public':
                    endpoint = endpoint['url']
                    for checker in CHECKERS:
                        if endpoint.endswith(checker):
                            endpoint = endpoint[:-len(checker)]
                    all_endpoints[SYSINV_API_URL] = endpoint
                    break

    return all_endpoints
