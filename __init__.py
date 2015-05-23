
from . import gui, srv, tools
from util.columns import *
from util.misc import app_devtypes, app_devdata

devdata = lambda: app_devdata('CTL', get_columns([c_ip_addr]), app_devtypes(gui))

