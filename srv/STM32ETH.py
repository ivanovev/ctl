
from telnetlib import Telnet
from re import compile
from util.misc import ping
from util.socketio import send_data, recv_data, get_fsz
import socket

def STM32ETH_telnet(ip_addr, cmd, *args):
    '''
    Обратиться по протоколу telnet к устройству %ip_addr% и выполнить команду %cmd%
    @param ip_addr - ip-адрес устройства
    @param cmd - команда
    @return результат выполнения команды cmd
    '''
    if len(args):
        cmd = ' '.join([cmd] + list(args))
        cmd = cmd.strip()
    if not ping(ip_addr):
        print('Failed to ping %s' % ip_addr)
        return
    try:
        tn = Telnet(ip_addr)
        s = tn.read_until(b'#> ', 5)
        cmd += '\n\r'
        tn.write(cmd.encode('ascii'))
        s = tn.read_until(b'#> ', 5)
        tn.close()

        def splitstr(s, b):
            r = compile(b)
            ss = r.split(s)
            ss = list(filter(lambda x: len(x), ss))
            return ss
        s = s.decode('ascii')
        ss = splitstr(s, '[\[\] \t\n\r:]+')
        ss0 = ss[0]
        if ss0 in ['0', '1']:
            ss = splitstr(s, '[\t\n\r]+')
            ss1 = ss[0]
            ss1 = ss1.replace('[%s]' % ss0, '')
            ss1 = ss1.strip()
            return ss1
        ss = s.split('\n')
        print('Failed to parse', ss)
        return
    except:
        print('telnet error')
        #print(sys.exc_info())
        return

def STM32ETH_recv_file(ip_addr, fname, fsz, src):
    if src == 'flash':
        assert STM32ETH_telnet(ip_addr, 'flash tx1 %s' % fsz)
        recv_data(ip_addr, 8888, fname, fsz)
        recv_data.t.join()

def STM32ETH_send_file(ip_addr, fname, src):
    if src == 'flash':
        fsz = get_fsz(fname)
        assert STM32ETH_telnet(ip_addr, 'flash rx2 %s' % fsz)
        send_data(ip_addr, 8888, fname)
        send_data.t.join()

def STM32ETH_dbg(ip_addr='192.168.0.1', port='1234', addr0='0', *addrn):
    port = int(port)
    addrn = list(addrn)
    addrn.insert(0, addr0)
    msg = bytes()
    for a in addrn:
        a = int(a, 16)
        for i in range(0, 4):
            msg += bytes([(a >> 8*(3-i)) & 0xFF])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, (ip_addr, port))
    data, addr = sock.recvfrom(len(msg))
    dd = []
    for i in range(0, len(data), 4):
        dd.append('0x%s' % ''.join('%.2X' % data[i+j] for j in range(0, 4)))
    return ' '.join(dd)

def STM32ETH_tftp_put(ip_addr='192.168.0.1', fname='script.pcl'):
    print('tftp_put')
    return ''
