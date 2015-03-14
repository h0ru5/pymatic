'''
Created on 07.03.2015

@author: h0ru5 (Johannes Hund)
'''

from ConfigParser import SafeConfigParser
import logging
import os

from pymatic.DeviceClient import DeviceClient
from sleekxmpp.jid import JID


if __name__ == '__main__':
    defauls = {
                'owner' : '*'
               }
    
    config = SafeConfigParser()
    fn = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pymatic.ini')
    config.read(fn)
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    
    jid = config.get('xmpp','jid')
    passwd = config.get('xmpp','pass')
    homematic = config.get('homematic','host')
    
    fulljid = JID(jid)
        
    xmpp = DeviceClient(fulljid, passwd,homematic)
    xmpp.owner = config.get('homematic','owner') 
    xmpp.connect()
    xmpp.process(block=True)