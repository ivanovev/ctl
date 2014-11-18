
from collections import OrderedDict as OD
from util import process_cb
from ..tools import TextIO, FWupgrade

def startup_cb(apps, mode, dev):
    if mode == 'ethdbg':
        return EthDebug(dev)
    if mode == 'pclupd':
        return TextIO(dev)
    if mode == 'fwupg':
        return FWupgrade(dev)

def get_menu(dev):
    menu = OD()
    menu['Eth debug'] = lambda dev: process_cb('ethdbg', dev)
    menu['Pcl update'] = lambda dev: process_cb('pclupd', dev)
    menu['FW upgrade'] = lambda dev: process_cb('fwupg', dev)
    return menu

