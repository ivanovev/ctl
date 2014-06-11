
from util.serial import query_serial

def STM32_mdio(ip_addr='192.168.0.1', reg='1', data=''):
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
        return STM32_telnet(ip_addr, cmd)
    else:
        if data:
            q = 'mdio %s %s\n' % (reg, data)
        else:
            q = 'mdio %s\n' % reg
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

