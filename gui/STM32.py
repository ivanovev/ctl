
from collections import OrderedDict as OD
from util import process_cb
from ..tools import EthDebug

def startup_cb(apps, mode, dev):
    if mode == 'ethdbg':
        return EthDebug(dev)

def get_menu(dev):
    menu = OD()
    menu['Eth debug'] = lambda dev: process_cb('ethdbg', dev)
    return menu

