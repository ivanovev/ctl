
from collections import OrderedDict as OD
from util import Data, telnet_io_cb
from util.dataio import DataIO

class FWupgrade(DataIO):
    def __init__(self, dev, title='FW upgrade'):
        data = Data()
        data.dev = dev
        data.buttons = OD()
        self.add_tx_cmds(data, txmd5=True)
        DataIO.__init__(self, data, dev, title=title)
        data.cmds['send'].w.configure(text='Start upgrade')

    def init_io(self):
        del self.io[:]
        self.io.add(lambda: self.efc_cb1('fw'), self.tmp_cb2, self.tmp_cb3, self.cmdio_thread)
        self.io.add(self.data_cb1, self.data_cb2, lambda: True, self.dataio_thread)

