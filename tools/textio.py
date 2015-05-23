
from collections import OrderedDict as OD
from threading import Thread
import tkinter as tk
import tkinter.ttk as ttk
import pdb

from util import Data
from util.dataio import DataIO
from util.socketio import recv_data, send_data, chunks
from util.columns import *
from util.io import MyAIO
from .text2 import Text2

class TextIO(DataIO):
    def __init__(self, dev):
        self.aio = True
        self.io_start = lambda *args: asyncio.async(self.io.start())
        data = Data()
        DataIO.__init__(self, data=data, dev=dev, title='Pcl edit')
        self.fileext = 'pcl'
        self.filemode = 'r'
        self.center()

    def init_io(self):
        self.io = MyAIO(self)
        self.io.add(self.text_cb1, self.text_cb2)
        #del self.io[:]
        #self.io.add(lambda: self.efc_cb1('pcl'), self.tmp_cb2, self.tmp_cb3, self.cmdio_thread)
        #self.io.add(self.text_cb1, self.text_cb2, lambda: True, self.textio_thread)

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

    def fileopen(self, fname, *args):
        data = self.read_file(fname)
        self.txt.text.delete(0.0, tk.END)
        self.txt.text.insert(0.0, data)
        self.text_change_cb()

    def text_change_cb(self):
        self.update_fsz_md5()
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

    def textio_thread(self):
        dev = self.data.dev
        port = 8888
        ip_addr = self.data.get_value('ip_addr')
        if self.read:
            q = self.qi
            self.fsz = int(self.io.ioval['fsz'])
            self.io_func = recv_data
            if dev[c_type] == 'SAM7X':
                port = 8889
        else:
            q = self.qo
            self.fsz = int(self.data.get_value('fsz'))
            self.io_func = send_data
        if not self.fsz:
            return
        self.io_func(ip_addr, port, q, fsz=self.fsz)
        self.io_func.t.join()

    def text_cb1(self):
        if self.read:
            return True
        else:
            data = self.get_data()
            for c in self.chunks(data, 512):
                self.qo.put(c)
            return True

    def text_cb2(self):
        if self.read:
            line = self.qi.get_nowait()
            if int(self.pb['value']) == 0:
                self.text_clear(self.txt.text)
            self.text_append(self.txt.text, line, see=False)
        self.update_progress()
        return False

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in range(0, len(l), n):
            yield l[i:i+n]

