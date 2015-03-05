
from util.serial import query_serial

def vcp_io(q):
    l = query_serial('/dev/ttyACM0', 115200, 8, 'N', 1, q, '#> ')
    if len(l) == 0:
        return ''
    l = l.replace('#> ', '')
    l = l.strip()
    ll = l.split('\n')
    if len(ll) == 1:
        l = ll[0]
        l = l.split()[1]
        l = l.replace('0x', '')
        return l
    return '0'


def STM32USB_gpio(gpio='c13', val='1'):
    '''
    Записать/прочитать значение gdio
    @param ip_addr - ip-адрес устройства
    @param gpio - номер gpio
    @param val - 0 или 1 при записи, пустая строка при чтении
    @return val
    '''
    if False:
        cmd = ' '.join(['mdio', reg, data])
        cmd = cmd.strip()
        return telnet(ip_addr, cmd)
    else:
        q = 'gpio%s %s %s' % (gpio[0], gpio[1:], val)
        q = q.strip()
        q += '\n'
        return vcp_io(q)

def STM32USB_mdio(reg='1', data=''):
    '''
    Записать/прочитать регистр mdio
    @param ip_addr - ip-адрес устройства
    @param reg - номер регистра
    @param data - значение в виде 0xABCD
    @return значение регистра
    '''
    if False:
        cmd = ' '.join(['mdio', reg, data])
        cmd = cmd.strip()
        return telnet(ip_addr, cmd)
    else:
        q = 'mdio %s %s' % (reg, data)
        q = q.strip()
        q += '\n'
        return vcp_io(q)

