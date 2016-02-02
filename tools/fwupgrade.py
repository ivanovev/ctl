
import asyncio
from collections import OrderedDict as OD
from util import Control, Data, c_type, c_ip_addr
from util.tftp import Tftp
import pdb

class FWupgrade(Control):
    def __init__(self, dev, title='FW upgrade'):
        data = Data()
        data.dev = dev
        data.buttons = OD()
        self.txcrc32 = True
        self.add_tx_cmds(data, txcrc32=self.txcrc32)
        Control.__init__(self, data, dev, title=title)
        data.cmds['send'].w.configure(text='Start upgrade')
        self.fileext = 'bin'
        self.filemode = 'rb'
        self.io_start = lambda *args: asyncio.async(self.io.start())

    def init_io(self):
        self.io = Tftp(self.data.dev[c_ip_addr], 69, self, 'fw.bin', read=False, wnd=self)

    def fileopen(self, fname):
        print(fname)
        if hasattr(self.io, 'st'):
            if getattr(self.io.st, 'closed', False):
                self.io.st.close()
        self.data.set_value('fname', fname)
        self.update_fsz_crc32(fname)
        self.io.st = open(fname, 'rb')
        self.io.remotefname = '.'.join([self.data.get_value('crc32'), self.fileext]).replace('0x', '')
        return True

    def write_cb(self, *args):
        self.io.read = False
        fname = self.data.get_value('fname')
        if fname:
            self.fileopen(fname)
            self.io_start()

