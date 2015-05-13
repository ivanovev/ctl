
from collections import OrderedDict as OD
from copy import deepcopy
from util import Control, Monitor, Data, ToolTip, telnet_io_cb, sel_dec, async
import tkinter as tk
import binascii, select, socket, struct, time
import pdb

import asyncio

class EthDebug(Monitor):
    def __init__(self, dev):
        self.fileext = 'symtab'
        self.columns1 = ['name', 'addr', 'sz']
        self.columns2 = ['name', 'addr', 'sz', 'offset'] + ['+%d' % (4*i) for i in range(0, 8)]
        #print(self.columns2)
        self.startio = False
        self.aio = True
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
        self.ft.grid(column=0, row=0, sticky=tk.N)
        b = tk.Button(self.ft, text='>>', command=lambda: self.add_cb(self.tree1))
        b.pack(side=tk.LEFT, padx=5, pady=5)
        b = tk.Button(self.ft, text='<<', command=lambda: self.del_cb(self.tree2))
        b.pack(side=tk.LEFT, padx=5, pady=5)
        b = tk.Button(self.ft, text='...', command=self.add_memory_cb)
        ToolTip(b, msg='Add memory region', follow=True, delay=0)
        b.pack(side=tk.LEFT, padx=5, pady=5)
        self.start = tk.IntVar()
        b = tk.Checkbutton(self.ft, text='Start', variable=self.start, command=lambda: asyncio.async(self.start_stop_cb()))
        b.pack(side=tk.LEFT, padx=5, pady=5)

        self.paned = tk.PanedWindow(self.frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.grid(column=0, row=1, sticky=tk.NSEW)

        self.fl = tk.Frame(self.paned)
        self.paned.add(self.fl, sticky=tk.NSEW, padx=5)
        w = self.tree_add(self.fl, width1=0, columns=self.columns1)
        self.tree1 = self.tree
        self.add_widget_with_scrolls(self.fl, w)
        self.tree1.column(self.columns1[0], stretch=1)
        self.tree1.column(self.columns1[1], stretch=0)
        self.tree1.column(self.columns1[2], stretch=0)
        self.tree1.tag_configure('color', background='lightgray')

        self.fr = tk.Frame(self.paned)
        self.paned.add(self.fr, sticky=tk.NSEW, padx=5)
        w = self.tree_add(self.fr, width1=0, columns=self.columns2)
        self.tree2 = self.tree
        #self.tree2['show'] = 'headings'
        displaycolumns = deepcopy(self.columns2)
        #displaycolumns.pop(displaycolumns.index('addr'))
        #displaycolumns.pop(displaycolumns.index('sz'))
        self.tree2.configure(displaycolumns=displaycolumns)
        self.add_widget_with_scrolls(self.fr, w)
        self.tree2.column(self.columns2[0], stretch=1)
        self.tree2.column(self.columns2[3], stretch=1)
        self.tree2.tag_configure('color', background='lightgray')

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=1)

    def init_io(self):
        del self.io[:]
        self.io.add(self.dbg_cb1, self.dbg_cb2, self.dbg_cb3, self.dbgio_thread)

    def fileopen(self, *args):
        self.tree_clear(self.tree1)
        fname = args[0]
        f = open(fname)
        objects = OD()
        for l in f.readlines():
            ll = l.split()
            if len(ll) != 8:
                continue
            num = ll[0]
            if num[-1] != ':':
                continue
            addr = ll[1]
            sz = ll[2]
            try:
                sz1 = int(sz)
            except:
                continue
            objtype = ll[3].upper()
            name = ll[7]
            if addr in objects:
                continue
            if objtype == 'OBJECT':
                try:
                    if not sz1:
                        continue
                except:
                    continue
            elif objtype == 'NOTYPE':
                if name[0] == '$':
                    continue
                if not sz1:
                    sz = '4'
                    sz1 = 4
            else:
                continue
            objects[addr] = name
            if sz1 <= 4:
                self.tree1.insert('', 'end', values=(name, addr, sz))
                continue
            id0 = self.tree1.insert('', 'end', tags=('color'), values=(name, addr, sz))
            addr = int(addr, 16)
            for i in range(0, sz1, 4):
                sz2 = '4' if i + 4 < sz1 else '%d' % (sz1 - i)
                self.tree1.insert(id0, 'end', values=(name+'+%.2x'%i, '%.8x'%(addr+i), sz2))

    def get_conn_data(self):
        conn = Data(name='conn')
        conn.add('remote_ipaddr', label='Remote IP address', wdgt='combo', value=['192.168.0.1'], text='192.168.0.1')
        conn.add('remote_port', label='Remote port', wdgt='combo', value=['12345'], text='12345')
        conn.add('local_ipaddr', label='Local IP address', wdgt='combo', value=['127.0.0.1', '192.168.0.100'], text='192.168.0.100')
        conn.add('local_port', label='Local port', wdgt='combo', value=['54321'], text='54321')
        conn.add('packet_sz', label='UDP Packet size', wdgt='entry', text='256')
        conn.add('period_ms', label='Data exchange period, ms', wdgt='entry', text='100')
        if hasattr(self, 'conn'):
            for k,v in self.conn.items():
                conn.set_value(k,v)
        return conn

    def connection_cb(self, *args):
        data = self.get_conn_data()
        dlg = Control(data=data, parent=self.root, title='Connection settings', pady=5)
        dlg.add_buttons_ok_cancel()
        dlg.do_modal()
        if not hasattr(dlg, 'kw'):
            return
        if len(dlg.kw.keys()) == 0:
            return
        self.conn = dlg.kw

    def hidetree1_cb(self, *args):
        v = args[1]
        if int(v.get()):
            self.paned.remove(self.fl)
        else:
            self.paned.add(self.fl, before=self.fr)

    def add_memory(self, name, addr, sz):
        addr = int(addr, 16)
        sz = int(sz)
        if sz > 512:
            sz = 512
        tags1 = ('color') if sz > 32 else ()
        offset = 0
        while offset < sz:
            sz1 = sz - offset
            if sz1 > 32: sz1 = 32
            if sz1 % 4:
                sz1 = ((sz1>>2) + 1) << 2
            values = [name, '%.8X' % (addr + offset), '%d' % sz1]
            values.append('%d' % offset)
            for j in range(0, sz1, 4):
                values.append('%.8X' % 0)
            if offset == 0:
                id2 = self.tree2.insert('', 'end', tags=tags1, values=tuple(values))
            else:
                self.tree2.insert(id2, 'end', values=tuple(values))
            offset += sz1
        self.update_offsets()

    def update_offsets(self):
        offset = 0
        for id1 in self.iter_tree(self.tree2):
            self.tree2.set(id1, 'offset', '%d' % offset)
            sz1 = int(self.tree2.set(id1, 'sz'))
            offset += sz1

    @sel_dec
    def add_cb(self, w, id1=None):
        if id1:
            data = self.tree1.set(id1)
            name = data['name']
            addr = data['addr']
            sz = data['sz']
            self.add_memory(name, addr, sz)

    def add_memory_cb(self):
        mem = Data(name='mem')
        mem.add('name', label='Name', wdgt='entry', text='new')
        mem.add('addr', label='Start address', wdgt='entry', text='00000000')
        mem.add('sz', label='Size in bytes', wdgt='entry', text='4')
        dlg = Control(data=mem, parent=self.root, title='Add memory', pady=5)
        dlg.add_buttons_ok_cancel()
        dlg.do_modal()
        if not hasattr(dlg, 'kw'):
            return
        if len(dlg.kw.keys()) == 0:
            return
        self.add_memory(dlg.kw['name'], dlg.kw['addr'], dlg.kw['sz'])

    @sel_dec
    def del_cb(self, w, id1=None):
        if id1:
            self.tree2.delete(id1)
            self.update_offsets()

    def addr_itemid_cb(self, id1):
        #print(id1)
        data = self.tree_data(self.tree2, id1)
        if data['addr']:
            self.addresses[data['addr']] = data['name']

    def prepare_io_msg(self):
        msg = bytes()
        for id1 in self.iter_tree(self.tree2):
            addr = self.tree2.set(id1, 'addr')
            msg += bytes(reversed(binascii.unhexlify(addr)))
            sz = int(self.tree2.set(id1, 'sz'))
            if sz > 4:
                addr = int(addr, 16)
                for i in range(4, sz, 4):
                    msg += struct.pack('i', addr + i)
        return msg

    def do_io(self, sock, msg, remote_ipaddr, remote_port, timeout):
        #print(sock, msg, remote_ipaddr, remote_port)
        sz = sock.sendto(msg, (remote_ipaddr, remote_port))
        r,w,x = select.select([sock], [], [], timeout)
        #print(r,w,x)
        if r:
            data, addr = sock.recvfrom(1024)
            #print(data, len(data))
            return data

    @asyncio.coroutine
    def start_stop_cb(self, *args):
        if not self.start.get():
            return
        #print('start')
        data = self.get_conn_data()
        remote_ipaddr = data.get_value('remote_ipaddr')
        remote_port = int(data.get_value('remote_port'))
        local_ipaddr = data.get_value('local_ipaddr')
        local_port = int(data.get_value('local_port'))
        period_ms = float(data.get_value('period_ms'))
        if period_ms < 1:
            period_ms = 1
        period_ms /= 1000

        msg = self.prepare_io_msg()
        #print(msg)
        if not msg:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((local_ipaddr, local_port))
        sock.setblocking(0)
        #print(local_ipaddr, local_port)

        while self.start.get():
            data = yield from async(self.do_io, sock, msg, remote_ipaddr, remote_port, 3*period_ms/1000)
            if data:
                self.update_wnd(data)
            yield from async(lambda: time.sleep(period_ms))
        #sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        #print('stop')

    def update_wnd(self, data):
        for id1 in self.iter_tree(self.tree2):
            offset = int(self.tree2.set(id1, 'offset'))
            sz = int(self.tree2.set(id1, 'sz'))
            for i in range(0, sz, 4):
                value = binascii.hexlify(data[(offset+i):(offset+i+4)])
                self.tree2.set(id1, '+%d' % i, value.upper())

    def get_addresses_cb(self, itemid):
        data = self.tree_data(self.tree2, itemid)
        if 'addr' not in data:
            return
        self.addresses.append(data['addr'])

    def dbg_cb1(self, *args):
        self.addresses = []
        self.iteritems(self.tree2, self.get_addresses_cb, None)
        return False

    def dbg_cb2(self, *args):
        #print('dbg_cb2', *args)
        return False

    def dbg_cb3(self, *args):
        #print('dbg_cb3', *args)
        self.root.after(1000, lambda: self.io.start(0))
        return False

    def dbgio_thread(self):
        while True:
            time.sleep(1)
            break

