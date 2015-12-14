
from telnetlib import Telnet
import re

from util import ping
from util.socketio import send_data, recv_data, get_fsz

def SAM7X_telnet(ip_addr, cmd, *args):
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
        print('Failed to ping  %s' % ip_addr)
        return
    try:
        tn = Telnet(ip_addr)
        tn.read_until(b'#> ', 2)
        cmd += '\n'
        tn.write(cmd.encode('ascii'))
        s = tn.read_until(b'#> ', 2)
        tn.close()
        '''
        try:
            tn.write(b'exit\n')
            tn.read_until(b'#> ', 2)
            tn.close()
        except:
            pass
        '''

        def splitstr(s, b):
            r = re.compile(b)
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

def SAM7X_name(ip_addr):
    '''
    Получить имя устройства по адресу %ip_addr% (префикс #xxx>)
    @param ip_addr - ip-адрес устройства
    @return имя устройства
    '''
    return SAM7X_telnet(ip_addr, 'name')

def SAM7X_alt_uart(ip_addr='192.168.0.1', cmd='', *args):
    '''
    alt_uart io
    '''
    if cmd == '':
        return ''
    cmd = 'alt_uart ' + cmd
    return SAM7X_telnet(ip_addr, cmd, *args)

def SAM7X_spi(ip_addr='192.168.0.1', spi='17', data='0000', ncpha='', cpol='', save=''):
    '''
    Обратиться по spi
    @param ip_addr - ip-адрес устройства
    @param spi - номер spi
    @param data - значение в виде 0xABCD
    @param ncpha - фаза spiclk (0 - по нечётным перепадам spiclk, 1 - по чётным)
    @param cpol - полярность spiclk (0: _|^|_|^|_|^|_..., 1: ^|_|^|_|^|_|^...)
    @param save - сохранение в efc, -1, 0, 1, 63 или '' (-1 или '' - не сохранять)
    @return ответ spi
    '''
    cmd = ' '.join(['spi', spi, data, ncpha, cpol, save])
    cmd = cmd.strip()
    return SAM7X_telnet(ip_addr, cmd)

def SAM7X_gpio(ip_addr='192.168.0.1', ngpio='52', data='1', save=''):
    '''
    Обратиться по gpio
    @param ip_addr - ip-адрес устройства
    @param ngpio - номер gpio
    @param data - data out - 0 или 1; data in - ''; gpio out data status - odsr
    @param save - 1 или '' (сохранение при записи)
    @return значение gpio
    '''
    cmd = ' '.join(['gpio', ngpio, data, save])
    cmd = cmd.strip()
    return SAM7X_telnet(ip_addr, cmd)

def SAM7X_efc(ip_addr='192.168.0.1', sg='spi', nsg='0', nreg='0', sz=''):
    '''
    Прочитать сохранённое значение spi или gpio
    @param ip_addr - ip-адрес устройства
    @param sg - spi или gpio
    @param nsg - номер spi или gpio
    @param nreg - если arg1 == spi, то номер регистра 0, 1, 2...
    @param sz - если arg1 == spi, то размер регистра 1, 2, 3 или 4 байта
    @return зачение сохранённого регистра spi или gpio
    '''
    cmd = ' '.join(['efc', sg, nsg, nreg, sz])
    cmd = cmd.strip()
    return SAM7X_telnet(ip_addr, cmd)

try:
    from util.serial import query_serial
except:
    pass

def SAM7X_mdio(ip_addr='192.168.0.1', nreg='1', data=''):
    '''
    Записать/прочитать регистр mdio
    @param ip_addr - ip-адрес устройства
    @param nreg - номер регистра
    @param data - значение в виде 0xABCD
    @return значение регистра
    '''
    if True:
        cmd = ' '.join(['mdio', nreg, data])
        cmd = cmd.strip()
        return SAM7X_telnet(ip_addr, cmd)
    else:
        if v == '': v = None
        #print(r,v)
        l = query_serial('/dev/ttyUSB0', 115200, 8, 'N', 1, '$', '>')
        if len(l) == 0:
            return
        r = nreg.replace('R', '')
        q = 'r ' + r
        if v != None:
            q += ' ' + v
        q += '\n'
        l = query_serial('/dev/ttyUSB0', 115200, 8, 'N', 1, q, '>')
        l = l.replace('>', '')
        l = l.strip()
        ll = l.split('\n')
        print(ll, len(ll))
        if len(ll) == 1:
            l = ll[0]
            l = l.split()[1]
            l = l.replace('0x', '')
            return l
        return '0'

def SAM7X_uart(ip_addr='192.168.0.1', uart='1', cmd='mr 0', *args):
    '''
    Обратиться по spi
    @param ip_addr - ip-адрес устройства
    @param uart - номер spi (0, 1, 2 - DBGU)
    @param cmd - команда
    @return ответ uart
    '''
    cmd = ' '.join(['uart'] + [uart] + [cmd] + list(args))
    cmd = cmd.strip()
    return SAM7X_telnet(ip_addr, cmd)

def SAM7X_send_file(ip_addr, fname, spi='1', dma='0'):
    '''
    Write file to alt sdram via spi and dma
    '''
    fsz = get_fsz(fname)
    if fsz % 0x200:
        print('bad fsz:', sz)
        return
    assert SAM7X_telnet(ip_addr, 'spi %s dlybs 0x80' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s dlybct 0x4' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s scbr 0x10' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s bits 8' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s ncpha 0' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s cpol 1' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s rx 0x%X' % (spi, fsz))
    assert SAM7X_telnet(ip_addr, 'dma start %s 0x%X' % (dma, fsz))
    send_data(ip_addr, fname)
    send_data.t.join()
    return '0x%X' % fsz

def SAM7X_recv_file(ip_addr, fname, fsz, spi='2', dma='1'):
    '''
    Read file from alt sdram via spi and dma
    '''
    fsz = get_fsz(fname, fsz)
    if fsz % 0x200:
        print('bad fsz:', sz)
        return
    assert SAM7X_telnet(ip_addr, 'spi %s dlybs 0x80' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s dlybct 0x4' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s scbr 0x10' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s bits 8' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s ncpha 0' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s cpol 1' % spi)
    assert SAM7X_telnet(ip_addr, 'spi %s tx 0x%X' % (spi, fsz))
    assert SAM7X_telnet(ip_addr, 'dma start %s 0x%X' % (dma, fsz))
    recv_data(ip_addr, fname, fsz)
    recv_data.t.join()
    return '0x%X' % fsz

