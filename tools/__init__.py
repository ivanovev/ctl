
from collections import OrderedDict as OD
from util import process_cb
from .textio import TextIO
from .fwupgrade import FWupgrade

def menus():
    menus = OD()
    menus['Tcl edit'] = lambda *args: process_cb('tclupd')
    return menus

