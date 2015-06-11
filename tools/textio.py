
import io, asyncio
import tkinter as tk
import tkinter.ttk as ttk

from util import Data
from util.tftp import Tftp
from util.control import Control
from util.columns import c_ip_addr
from util.myio import MyAIO
from .text2 import Text2

class TextIO(Control, io.BytesIO):
    def __init__(self, dev):
        data = Data()
        Control.__init__(self, data=data, dev=dev, title='Pcl edit')
        io.BytesIO.__init__(self)
        self.aio = True
        self.io_start = lambda *args: asyncio.async(self.io.start())
        self.fileext = 'pcl'
        self.filemode = 'r'

    def init_io(self):
        self.io = Tftp(self.data.dev[c_ip_addr], 69, self, 'script.pcl', read=True, wnd=self)

    def append_wdgt(self, column, name, label, text, width=None, state=None, msg='', row=0, columnspan=1):
        self.data.add_page(name, send=False)
        self.data.add(name, label=label, wdgt='entry', text=text, width=width, state=state, msg=msg)
        f11 = self.init_frame(self.f1, self.data.cmds)
        f11.grid(column=column, row=row, sticky=tk.W, columnspan=columnspan)

    def init_layout(self):
        self.add_menu_file()
        self.f1 = tk.Frame(self.frame)
        self.f1.grid(column=0, row=0, sticky=tk.W)
        self.append_wdgt(0, 'ip_addr', 'IP Address', self.data.dev['ip_addr'] if hasattr(self.data, 'dev') else '192.168.0.1', 10)
        self.append_wdgt(1, 'crc32', 'CRC32', '0', 10, 'readonly')
        self.append_wdgt(2, 'fsz', ' Size', '0', 8, 'readonly', 'dec')
        self.append_wdgt(3, 'fszhex', '', '0', 8, 'readonly', 'hex')
        self.append_wdgt(4, 'fszsel', '', '0', 8, 'readonly', 'selection')
        self.append_wdgt(5, 'fszselhex', '', '0', 8, 'readonly', 'selection hex')
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
        self.seek(0)
        self.truncate(0)
        self.write(self.get_data())
        self.io_start()

    def write(self, bb):
        if self.io.read:
            self.text_append(self.txt.text, bb.decode('ascii'), see=False)
        else:
            bb = bb.encode('ascii')
            io.BytesIO.write(self, bb)

    def close(self):
        pass

    def fileopen(self, fname, *args):
        f = open(fname, 'rb')
        data = f.read()
        f.close()
        self.txt.text.delete(0.0, tk.END)
        self.txt.text.insert(0.0, data)
        self.text_change_cb()

    def text_change_cb(self):
        self.update_fsz_crc32()
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

