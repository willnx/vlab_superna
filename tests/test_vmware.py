# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_superna_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_show_superna(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``superna`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'Superna'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta': {'component': 'Superna',
                                               'created': 1234,
                                               'version': '1.0',
                                               'configured': False,
                                               'generation': 1}}

        output = vmware.show_superna(username='alice')
        expected = {'Superna': {'meta': {'component': 'Superna',
                                                             'created': 1234,
                                                             'version': '1.0',
                                                             'configured': False,
                                                             'generation': 1}}}
        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_superna(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_superna`` returns None when everything works as expected"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'SupernaBox'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta': {'component': 'Superna',
                                               'created': 1234,
                                               'version': '1.0',
                                               'configured': False,
                                               'generation': 1}}

        output = vmware.delete_superna(username='bob', machine_name='SupernaBox', logger=fake_logger)
        expected = None

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_superna_value_error(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_superna`` raises ValueError when unable to find requested vm for deletion"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'win10'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta': {'component': 'Superna',
                                               'created': 1234,
                                               'version': '1.0',
                                               'configured': False,
                                               'generation': 1}}

        with self.assertRaises(ValueError):
            vmware.delete_superna(username='bob', machine_name='myOtherSupernaBox', logger=fake_logger)

    @patch.object(vmware.virtual_machine, 'block_on_boot')
    @patch.object(vmware.virtual_machine, 'configure_network')
    @patch.object(vmware.virtual_machine, 'set_meta')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_superna(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova,
                            fake_get_info, fake_Ova, fake_set_meta, fake_configure_network,
                            fake_block_on_boot):
        """``create_superna`` returns a dictionary upon success"""
        fake_logger = MagicMock()
        fake_deploy_from_ova.return_value.name = 'mySuperna'
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}
        ip_config = {
            'static-ip' : "1.2.3.4",
            'default-gateway' : '1.2.3.1',
            'netmask': '255.255.255.0',
            'dns' : ['1.2.3.2'],
            'domain' : 'vlab.local'
        }

        output = vmware.create_superna(username='alice',
                                       machine_name='SupernaBox',
                                       image='1.0.0',
                                       network='someLAN',
                                       ip_config=ip_config,
                                       logger=fake_logger)
        expected = {'mySuperna': {'worked': True}}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_superna_invalid_network(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova):
        """``create_superna`` raises ValueError if supplied with a non-existing network"""
        fake_logger = MagicMock()
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}
        ip_config = {
            'static-ip' : "1.2.3.4",
            'default-gateway' : '1.2.3.1',
            'netmask': '255.255.255.0',
            'dns' : ['1.2.3.2'],
            'domain' : 'vlab.local'
        }

        with self.assertRaises(ValueError):
            vmware.create_superna(username='alice',
                                  machine_name='SupernaBox',
                                  image='1.0.0',
                                  network='someOtherLAN',
                                  ip_config=ip_config,
                                  logger=fake_logger)

    @patch.object(vmware.os, 'listdir')
    def test_list_images(self, fake_listdir):
        """``list_images`` - Returns a list of available Superna versions that can be deployed"""
        fake_listdir.return_value = ['Superna_Eyeglass-2.6.1.ova']

        output = vmware.list_images()
        expected = ['2.6.1']

        # set() avoids ordering issue in test
        self.assertEqual(set(output), set(expected))

    def test_convert_name(self):
        """``convert_name`` - defaults to converting to the OVA file name"""
        output = vmware.convert_name(name='2.6.1')
        expected = 'Superna_Eyeglass-2.6.1.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version(self):
        """``convert_name`` - can take a OVA file name, and extract the version from it"""
        output = vmware.convert_name('Superna_Eyeglass-2.6.1.ova', to_version=True)
        expected = '2.6.1'

        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()
