
from collections import OrderedDict as OD
from util import process_cb
from ..tools import TextIO, FWupgrade

def startup_cb(apps, mode, dev):
    if mode == 'tclupd':
        return TextIO(dev)
    if mode == 'fwupg':
        return FWupgrade(dev)

def get_menu(dev):
    menu = OD()
    menu['Tcl update'] = lambda dev: process_cb('tclupd', dev)
    menu['FW upgrade'] = lambda dev: process_cb('fwupg', dev)
    return menu

