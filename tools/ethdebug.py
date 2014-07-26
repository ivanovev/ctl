
from collections import OrderedDict as OD
from util import Control, Monitor, Data, telnet_io_cb
from copy import deepcopy
import tkinter as tk
import socket
import time
import pdb

class EthDebug(Monitor):
    def __init__(self, dev):
        self.fileext = 'symtab'
        self.columns1 = ['name', 'addr', 'sz']
        self.columns2 = deepcopy(self.columns1)
        self.columns2.append('value')
        self.startio = False
        Monitor.__init__(self)
        self.root.title('UDP Eth debug')

    def add_main_menu(self):
        m1 = OD()
        m2 = OD()
        m2['Open ARM.symtab'] = self.fileopen_cb
        m2['separator'] = None
        m2['Exit'] = self.exit_cb
        m1['File'] = m2
        m3 = OD()
        m3['Connection'] = self.connection_cb
        m3[('Hide left tree',)] = self.hidetree1_cb
        m1['Settings'] = m3
        self.add_menus(m1)

    def init_layout(self):
        self.add_main_menu()

        self.ft = tk.Frame(self.frame)
        self.ft.grid(column=0, row=0, columnspan=2, sticky=tk.N)
        b = tk.Button(self.ft, text='>', command=self.add_cb)
        b.pack(side=tk.LEFT, padx=5, pady=5)
        b = tk.Button(self.ft, text='<', command=self.del_cb)
        b.pack(side=tk.LEFT, padx=5, pady=5)
        b = tk.Button(self.ft, text='Start', command=self.start_stop_cb)
        b.pack(side=tk.LEFT, padx=5, pady=5)


        self.fl = tk.Frame(self.frame)
        self.fl.grid(column=0, row=1, sticky=tk.NSEW)
        w = self.tree_add(self.fl, width1=0, columns=self.columns1)
        self.tree1 = self.tree
        self.add_widget_with_scrolls(self.fl, w)
        self.tree1.column(self.columns1[0], stretch=1)
        self.tree1.column(self.columns1[1], stretch=0)
        self.tree1.column(self.columns1[2], stretch=0)

        self.fr = tk.Frame(self.frame)
        self.fr.grid(column=1, row=1, sticky=tk.NSEW)
        w = self.tree_add(self.fr, width1=0, columns=self.columns2)
        self.tree2 = self.tree
        self.tree2.configure(displaycolumns=[self.columns2[i] for i in [0,3]])
        self.add_widget_with_scrolls(self.fr, w)
        self.tree2.column(self.columns2[0], stretch=1)
        self.tree2.column(self.columns2[3], stretch=1)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=1)

    def init_io(self):
        del self.io[:]
        self.io.add(self.udp_cb1, self.udp_cb2, self.udp_cb3, self.udpio_thread)

    def fileopen(self, *args):
        self.tree_clear(self.tree1)
        fname = args[0]
        f = open(fname)
        d = {}
        objects = OD()
        for l in f.readlines():
            ll = l.split()
            if len(ll) != 8:
                continue
            if ll[0][-1] != ':':
                continue
            if ll[1] in d:
                continue
            if ll[3].upper() != 'OBJECT':
                continue
            sz = ll[2]
            try:
                if not int(sz):
                    continue
            except:
                continue
            d[ll[1]] = ll[0]
            objects[ll[1]] = OD([('name',ll[7]),('addr',ll[1]),('sz',ll[2])])
        for k,v in objects.items():
            lvl0 = v['name']
            id0 = self.tree_add_lvl0(self.tree1, v)
            sz = int(v['sz'])
            if sz > 4:
                v['sz'] = '4'
                addr = int(v['addr'], 16)
                name = v['name']
                for i in range(0, sz, 4):
                    v['name'] = name + '+%.2x' % i
                    v['addr'] = '%.8x' % (addr + i)
                    self.tree_add_lvl1(self.tree1, lvl0, v, expand=False)

    def connection_cb(self, *args):
        data = Data(name='conn')
        data.add('remote_ip_addr', label='Remote IP address', wdgt='combo', value=['192.168.0.1'], text='192.168.0.1')
        data.add('remote_port', label='Remote port', wdgt='combo', value=['32784'], text='32784')
        data.add('local_ip_addr', label='Local IP address', wdgt='combo', value=['127.0.0.1'], text='127.0.0.1')
        data.add('local_port', label='Local port', wdgt='combo', value=['32784'], text='32784')
        data.add('packet_sz', label='UDP Packet size', wdgt='entry', text='256')
        data.add('period_ms', label='Data exchange period, ms', wdgt='entry', text='100')
        dlg = Control(data=data, parent=self.root, title='Connection settings', pady=5)
        dlg.add_buttons_ok_cancel()
        dlg.do_modal()
        if not hasattr(dlg, 'kw'):
            return
        if len(dlg.kw.keys()) == 0:
            return
        return dlg.kw

    def hidetree1_cb(self, *args):
        v = args[1]
        if int(v.get()):
            self.fl.grid_forget()
            self.frame.columnconfigure(0, weight=0)
        else:
            self.fl.grid(column=0, row=1, sticky=tk.NSEW)
            self.frame.columnconfigure(0, weight=1)

    def add_cb(self, *args):
        id1 = self.tree1.selection()
        if not id1:
            return
        children = self.tree1.get_children(id1)
        c1 = self.tree_columns(self.tree1)
        c2 = self.tree_columns(self.tree2)
        def copy1(data, lvl0):
            sz = int(data['sz'])
            if sz <= 4:
                fmt = '%%.%dx' % (sz*2)
                value = fmt % 0
                data['value'] = value
            if not lvl0:
                return self.tree_add_lvl0(self.tree2, data)
            else:
                return self.tree_add_lvl1(self.tree2, lvl0, data, expand=False)
        data = self.tree_data(self.tree1)
        name = data['name']
        if self.tree_find_id0(self.tree2, name):
            return
        copy1(data, None)
        if not children:
            return
        for i in children:
            data = self.tree_data(self.tree1, i)
            copy1(data, name)

    def del_cb(self, *args):
        id1 = self.tree2.selection()
        if id1:
            self.tree2.delete(id1)

    def addr_itemid_cb(self, id1):
        print(id1)
        data = self.tree_data(self.tree2, id1)
        if data['addr']:
            self.addresses[data['addr']] = data['name']

    def start_stop_cb(self, *args):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 1234
        msg = "1234"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', UDP_PORT))
        sock.sendto(msg.encode('ascii'), ('192.168.0.1', UDP_PORT))
        data, addr = sock.recvfrom(1024)
        print(data)
        '''
        self.startio = not self.startio
        if self.startio:
            self.addresses = OD()
            self.tree = self.tree2
            self.iteritems(self.addr_itemid_cb)
            print(self.addresses)
            self.root.after_idle(self.io.start)
        '''

    def udp_cb1(self, *args):
        print('udp_cb1')
        return self.startio

    def udp_cb2(self, *args):
        print('udp_cb2', *args)
        return False

    def udp_cb3(self, *args):
        print('udp_cb3', *args)
        self.root.after(1000, lambda: self.io.start(0))
        return False

    def udpio_thread(self):
        while True:
            time.sleep(1)
            break

