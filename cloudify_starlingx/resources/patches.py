import re

from ..utils import (
    get_child_deployments,
    with_rest_client,
    add_new_label)
from ..decorators import with_starlingx_resource
from ...starlingx_server.sdk.client import StarlingxPatchClient
from ...starlingx_server.sdk.dcmanager import StarlingxDcManagerClient

from cloudify_starlingx_sdk.resources.configuration import SystemResource
from cloudify.exceptions import OperationRetry


@with_starlingx_resource(SystemResource)
def upload_patch(resource, ctx, autoapply: bool, refresh_status: bool, patch_dir: str, **kwargs):
    """
        Steps:
        1. Upload patch from patch dir
        2. Apply patch (optional)
        3. Check status (optional)
        :param autoapply: make patch apply
        :param patch_dir: patch directory
        :param refresh_status: refresh status of subcloud
    """
    client_config = resource.client_config
    auth_url = client_config.get('auth_url')
    username = client_config.get('username')
    password = client_config.get('api_key')
    project_name = client_config.get('project_name')
    user_domain_id = client_config.get('user_domain_id')
    project_domain_id = client_config.get('project_domain_id')    

    # ctx.logger.info("""auth_url={},username={},password={},project_name={}, user_domain_id={},
    # #                                                      project_domain_id={}""".format(res))
    patch_client = StarlingxPatchClient.get_patch_client(auth_url=auth_url, username=username, password=password,
                                                         project_name=project_name, user_domain_id=user_domain_id,
                                                         project_domain_id=project_domain_id)
    outputs = patch_client.upload_patch(patch_dir=patch_dir)

    if autoapply:
        for output in outputs:
            patch_id = re.findall(' \"(.*) is now available', output)
            apply_patch( ctx=ctx, patch_id=patch_id)

    if refresh_status:
        refresh_status(ctx=ctx)


@with_starlingx_resource(SystemResource)
def apply_patch(resource, ctx, patch_id: str):
    client_config = resource.client_config
    auth_url = client_config.get('auth_url')
    username = client_config.get('username')
    password = client_config.get('api_key')
    project_name = client_config.get('project_name')
    user_domain_id = client_config.get('user_domain_id')
    project_domain_id = client_config.get('project_domain_id')    
    subcloud_name =  _get_subcloud_name(ctx=ctx)
    # ctx.logger.info("""auth_url={},username={},password={},project_name={}, user_domain_id={},
    # #                                                      project_domain_id={}""".format(res))
    patch_client = StarlingxPatchClient.get_patch_client(auth_url=auth_url, username=username, password=password,
                                                         project_name=project_name, user_domain_id=user_domain_id,
                                                         project_domain_id=project_domain_id)
    dc_patch_client = StarlingxDcManagerClient.get_patch_client(auth_url=auth_url, username=username, password=password,
                                                             project_name=project_name, user_domain_id=user_domain_id,
                                                             project_domain_id=project_domain_id)
    out = patch_client.apply_patch(patch_id=patch_id)
    assert out['info'] == '{} has been applied\n'.format(patch_id)
    #TODO strategy create and apply
    dc_patch_client.create_subcloud_update_strategy(type_of_strategy="patch", cloud_name=subcloud_name,
                                                          max_parallel_subclouds=1, stop_on_failure=True,
                                                          subcloud_apply_type="serial")
    dc_patch_client.execute_action_on_strategy(type_of_strategy="patch", action="apply")


@with_rest_client
@with_starlingx_resource(SystemResource)
def refresh_status(resource, ctx, rest_client):
    deployment_id = ctx.deployment.id
    child_deployment_ids =  get_child_deployments(deployment_id)
    for child_deployment_id in child_deployment_ids:
        rest_client.executions.start(
            deployment_id=child_deployment_id,
            workflow_id='check_status',
            queue=False
        )


def _get_status(resource, ctx):
    client_config = resource.client_config
    auth_url = client_config.get('auth_url')
    username = client_config.get('username')
    password = client_config.get('api_key')
    project_name = client_config.get('project_name')
    user_domain_id = client_config.get('user_domain_id')
    project_domain_id = client_config.get('project_domain_id')    
    subcloud_name =  _get_subcloud_name(ctx=ctx)
    dc_patch_client = StarlingxDcManagerClient.get_patch_client(auth_url=auth_url, username=username, password=password,
                                                             project_name=project_name, user_domain_id=user_domain_id,
                                                             project_domain_id=project_domain_id)
    return dc_patch_client.get_all_strategy_steps_for_cloud(subcloud_name)["state"]


@with_starlingx_resource(SystemResource)
def check_status(resource, ctx):
    statuses_list = ['complete', 'failed']
    deployment_id = ctx.deployment.id
    status = _get_status(resource, ctx)
    if status not in statuses_list:
        raise OperationRetry
    else:
        add_new_label('csys-subcloud-status',
                      status,
                      deployment_id)


def _get_subcloud_name(ctx):
    subcloud_dict = ctx.instance.runtime_properties.get('subcloud', {})
    return str(list(subcloud_dict.items())[0][1]['name'])
