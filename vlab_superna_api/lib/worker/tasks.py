# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from vlab_api_common import get_task_logger

from vlab_superna_api.lib import const
from vlab_superna_api.lib.worker import vmware

app = Celery('superna', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)


@app.task(name='superna.show', bind=True)
def show(self, username, txn_id):
    """Obtain basic information about Superna

    :Returns: Dictionary

    :param username: The name of the user who wants info about their default gateway
    :type username: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_SUPERNA_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        info = vmware.show_superna(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp


@app.task(name='superna.create', bind=True)
def create(self, username, machine_name, image, network, ip_config, txn_id):
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

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_SUPERNA_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_superna(username, machine_name, image, network, ip_config, logger)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='superna.delete', bind=True)
def delete(self, username, machine_name, txn_id):
    """Destroy an instance of Superna

    :Returns: Dictionary

    :param username: The name of the user who wants to delete an instance of Superna
    :type username: String

    :param machine_name: The name of the instance of Superna
    :type machine_name: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_SUPERNA_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        vmware.delete_superna(username, machine_name, logger)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
    return resp


@app.task(name='superna.image', bind=True)
def image(self, txn_id):
    """Obtain a list of available images/versions of Superna that can be created

    :Returns: Dictionary

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_SUPERNA_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    resp['content'] = {'image': vmware.list_images()}
    logger.info('Task complete')
    return resp
