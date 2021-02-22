# -*- coding: UTF-8 -*-
"""Business logic for backend worker tasks"""
import time
import random
import os.path
from vlab_inf_common.vmware import vCenter, Ova, vim, virtual_machine, consume_task

from vlab_superna_api.lib import const


def show_superna(username):
    """Obtain basic information about Superna

    :Returns: Dictionary

    :param username: The user requesting info about their Superna
    :type username: String
    """
    info = {}
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        superna_vms = {}
        for vm in folder.childEntity:
            info = virtual_machine.get_info(vcenter, vm, username)
            if info['meta']['component'] == 'Superna':
                superna_vms[vm.name] = info
    return superna_vms


def delete_superna(username, machine_name, logger):
    """Unregister and destroy a user's Superna

    :Returns: None

    :param username: The user who wants to delete their jumpbox
    :type username: String

    :param machine_name: The name of the VM to delete
    :type machine_name: String

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == machine_name:
                info = virtual_machine.get_info(vcenter, entity, username)
                if info['meta']['component'] == 'Superna':
                    logger.debug('powering off VM')
                    virtual_machine.power(entity, state='off')
                    delete_task = entity.Destroy_Task()
                    logger.debug('blocking while VM is being destroyed')
                    consume_task(delete_task)
                    break
        else:
            raise ValueError('No {} named {} found'.format('superna', machine_name))


def create_superna(username, machine_name, image, network, ip_config, logger):
    """Deploy a new instance of Superna

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new Superna
    :type username: String

    :param machine_name: The name of the new instance of Superna
    :type machine_name: String

    :param image: The image/version of Superna to create
    :type image: String

    :param network: The name of the network to connect the new Superna instance up to
    :type network: String

    :param ip_config: The IPv4 network configuration for the Avamar instance.
    :type ip_config: Dictionary

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER,
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        image_name = convert_name(image)
        logger.info(image_name)
        ova = Ova(os.path.join(const.VLAB_SUPERNA_IMAGES_DIR, image_name))
        try:
            network_map = vim.OvfManager.NetworkMapping()
            network_map.name = ova.networks[0]
            try:
                network_map.network = vcenter.networks[network]
            except KeyError:
                raise ValueError('No such network named {}'.format(network))
            the_vm = virtual_machine.deploy_from_ova(vcenter=vcenter,
                                                     ova=ova,
                                                     network_map=[network_map],
                                                     username=username,
                                                     machine_name=machine_name,
                                                     logger=logger,
                                                     power_on=False)
        finally:
            ova.close()

        virtual_machine.configure_network(the_vm, ip_config)
        virtual_machine.power(the_vm, state='on')
        meta_data = {'component' : "Superna",
                     'created' : time.time(),
                     'version' : image,
                     'configured' : False,
                     'generation' : 1}
        virtual_machine.set_meta(the_vm, meta_data)
        info = virtual_machine.get_info(vcenter, the_vm, username, ensure_ip=True)
        return  {the_vm.name: info}


def list_images():
    """Obtain a list of available versions of Superna that can be created

    :Returns: List
    """
    images = os.listdir(const.VLAB_SUPERNA_IMAGES_DIR)
    images = [convert_name(x, to_version=True) for x in images]
    return images


def convert_name(name, to_version=False):
    """This function centralizes converting between the name of the OVA, and the
    version of software it contains.

    :param name: The thing to covert
    :type name: String

    :param to_version: Set to True to covert the name of an OVA to the version
    :type to_version: Boolean
    """
    if to_version:
        return name.split('-')[-1].replace('.ova', '')
    else:
        return 'Superna_Eyeglass-{}.ova'.format(name)
