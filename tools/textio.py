
import asyncio
import tkinter as tk
import tkinter.ttk as ttk

from util import Data
from util.tftp import Tftp
from util.control import Control
from util.columns import c_ip_addr
from util.myio import MyAIO
from .text2 import Text2

class TextIO(Control):
    def __init__(self, dev):
        data = Data()
        Control.__init__(self, data=data, dev=dev, title='Pcl edit')
        self.aio = True
        self.io_start = lambda *args: asyncio.async(self.io.start())
        self.fileext = 'pcl'
        self.filemode = 'r'

    def init_io(self):
        self.io = Tftp(self.data.dev[c_ip_addr], 69, 'script.pcl')
        self.io.data_cb = self.data_cb

    def append_wdgt(self, column, name, label, text, width=None, state=None, msg='', row=0, columnspan=1):
        self.data.add_page(name, send=False)
        self.data.add(name, label=label, wdgt='entry', text=text, width=width, state=state, msg=msg)
        f11 = self.init_frame(self.f1, self.data.cmds)
        f11.grid(column=column, row=row, sticky=tk.W, columnspan=columnspan)

    def init_layout(self):
        self.add_menu_file()
        self.f1 = tk.Frame(self.frame)
        self.f1.grid(column=0, row=0, sticky=tk.W)
        self.append_wdgt(0, 'ip_addr', 'IP Address', self.data.dev['ip_addr'] if hasattr(self.data, 'dev') else '192.168.0.1', 15)
        self.append_wdgt(1, 'fsz', ' Size', '0', 8, 'readonly', 'dec')
        self.append_wdgt(2, 'fszhex', '', '0', 8, 'readonly', 'hex')
        self.append_wdgt(3, 'fszsel', '', '0', 8, 'readonly', 'selection')
        self.append_wdgt(4, 'fszselhex', '', '0', 8, 'readonly', 'selection hex')
        self.append_wdgt(0, 'crc32', 'CRC32', '0', 15, 'readonly', row=1)
        self.append_wdgt(1, 'md5', 'MD5', '0', 40, 'readonly', row=1, columnspan=3)
        self.txt = Text2(self.frame)
        self.txt.grid(column=0, row=2, sticky=tk.NSEW)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        if hasattr(self.data, 'dev'):
            self.add_fb()
            self.pb = ttk.Progressbar(self.fb, orient=tk.HORIZONTAL, maximum=100)
            self.pb.pack(fill=tk.X, expand=1, padx=5, pady=5, side=tk.LEFT)
            self.add_button(self.fb, 'Read', self.read_cb)
            self.add_button(self.fb, 'Write', self.write_cb)
            self.txt.text_change_cb = self.text_change_cb

    def read_cb(self, *args):
        self.io.read = True
        self.ip_addr = self.data.get_value(c_ip_addr)
        self.text_clear(self.txt.text)
        self.io_start()

    def write_cb(self, *args):
        self.io.read = False
        self.io_start()

    def data_cb(self, bb=b''):
        if bb:
            self.text_append(self.txt.text, bb.decode('ascii'), see=False)
        else:
            return self.get_data().encode('ascii')


    def fileopen(self, fname, *args):
        f = open(fname, 'rb')
        data = f.read()
        f.close()
        self.txt.text.delete(0.0, tk.END)
        self.txt.text.insert(0.0, data)
        self.text_change_cb()

    def text_change_cb(self):
        #self.update_fsz_md5()
        try:
            data = self.txt.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.data.set_value('fszsel', '%d' % len(data))
            self.data.set_value('fszselhex', '0x%X' % len(data))
        except:
            pass

    def filesave(self, fname):
        data = self.get_data()
        f = open(fname, 'w')
        f.write(data)
        f.close()

    def get_data(self):
        data = self.txt.text.get(0.0, tk.END)
        if len(data):
            data = data[:-1]
        return data

