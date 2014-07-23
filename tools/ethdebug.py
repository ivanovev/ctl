
from collections import OrderedDict as OD
from util import Data, telnet_io_cb
from util.control import Control
import tkinter as tk

class EthDebug(Control):
    def __init__(self, dev):
        Control.__init__(self)

    def add_main_menu(self):
        m1 = OD()
        m2 = OD()
        m2['Open ARM.symtab'] = self.fileopenarmsymtab_cb
        m2['separator'] = None
        m2['Exit'] = self.exit_cb
        m1['File'] = m2
        m3 = OD()
        m3['Connection'] = self.connection_cb
        m1['Settings'] = m3
        self.add_menus(m1)

    def init_layout(self):
        self.add_main_menu()

        self.fl = tk.Frame(self.frame)
        self.fl.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        w = self.tree_add(self.fl, None)
        self.add_widget_with_scrolls(self.fl, w)

        self.fm = tk.Frame(self.frame)
        self.fm.pack(expand=0, side=tk.LEFT)
        b = tk.Button(self.fm, text='>', command=self.add_cb)
        b.pack(side=tk.TOP, padx=5, pady=5)
        b = tk.Button(self.fm, text='<', command=self.del_cb)
        b.pack(side=tk.BOTTOM, padx=5, pady=5)

        self.fr = tk.Frame(self.frame)
        self.fr.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        w = self.tree_add(self.fr, None)
        self.add_widget_with_scrolls(self.fr, w)

    def fileopenarmsymtab_cb(self, *args):
        print('fileopenarmsymtab_cb')

    def connection_cb(self, *args):
        print('connection_cb')

    def add_cb(self, *args):
        print('add_cb')

    def del_cb(self, *args):
        print('del_cb')

