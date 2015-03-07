'''
Created on 06.03.2015

@author: mail_000
'''

import logging
import sys

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from pymatic.HomeMaticClient import HomeMaticClient

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

class DeviceClient(ClientXMPP):

    def __init__(self, jid, password,hmhost='homematic-ccu'):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # If you wanted more functionality, here's how to register plugins:
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0050') # Ad-hoc commands
        self.register_plugin('xep_0004') # Dataforms
        
        self.homematic = HomeMaticClient(hmhost)
        
        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()
        
        self.add_commands()
        self.add_nodes() 
        
    def add_nodes(self):
        #TODO query datapoints and create nodes
        
        name='My node'
        node='mynode'
        subnode = 'mysubnode'
        subname='My sub node'
        
        self._add_node(node,name)
        self._add_node(subnode, subname, node)
        
    def _add_node(self,node='',name='',parent=None):
        disco = self['xep_0030']
        jid = self.boundjid
        item_jid = jid.full
        
        disco.add_item(jid=item_jid,name=name,node=parent,subnode=node,ijid=jid)
        disco.add_identity(category='automation',itype='device-node',name=name,node=node,jid=jid)
        
    
    def add_commands(self):
        self['xep_0050'].add_command(node='programslist',
                                     name='List programs',
                                     handler=self._handle_programslist_cmd)
        
        for program in self.homematic.getPrograms():
            self['xep_0050'].add_command(node='%(id)s' % program,
                                     name='HM: %(name)s' % program,
                                     handler=self._handle_hmprog_cmd)
        
    def _handle_programslist_cmd(self, iq,session):
        logging.info('called to list programs')
        plist = ["%(id)s: %(name)s" % program for program in self.homematic.getPrograms()]
        session['notes'] = [('info','\n'.join(plist))]
        return session
        
    def _handle_hmprog_cmd(self,iq,session):
        logging.info('calling homematic program %(node)s',session)
        try:
            self.homematic.runProgram(session['node'])
            print session
            session['notes'] =  [('info','OK')]
        except Exception as err:
            session['notes'] = [('error',err)]            
        return session
            
    def message(self, msg):
        #instead of just being rude, this will be a text-interface
        if msg['type'] in ('chat', 'normal'):
            msg.reply("%(body)s yourself!" % msg).send()

