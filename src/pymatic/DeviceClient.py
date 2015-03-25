'''
Created on 06.03.2015

@author: mail_000
'''

import logging
import sys

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from pymatic.HomeMaticClient import HomeMaticClient
from sleekxmpp.jid import JID
from sleekxmpp.plugins.xep_0050.stanza import Command

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
        
        # specify owner JID, * for everybody
        self.owner ='*' 
        
        

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.add_commands()
        self.add_nodes() 

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
        
    def add_nodes(self):
        'query datapoints and create nodes'
        
        devs = self.homematic.getDevices()
        
        for device in devs:
            
            self._add_node(device.ise,device.name)
            self['xep_0030'].set_node_handler('get_items'
                                       ,jid=self.boundjid.full
                                       ,node=device.ise
                                       ,handler=device.handleItems
                                       )
            device.add_commands(self)
            
            for (snode,sname) in device.subnodes.items():
                self._add_node(snode, sname, device.ise)
    
                 
        
    def _add_node(self,node='',name='',parent=None):
        disco = self['xep_0030']
        jid = self.boundjid
        item_jid = jid.full
        
        if not parent == None: 
            fullnode = "%s/%s" % (parent,node)
        else:
            fullnode = node
        
        disco.add_item(jid=item_jid,name=name,node=parent,subnode=fullnode,ijid=jid)
        disco.add_identity(category='automation',itype='device-node',name=name,node=fullnode,jid=jid)
            
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
        

    def _verify(self, caller):
        'verify that caller is egligable to run the program, currently matches against owner'
        if(self.owner == '*'):
            return True
        else:
            return JID(caller).bare == self.owner
            
    
    def _handle_hmprog_cmd(self,iq,session):
        logging.info('calling homematic program %(node)s for %(from)s',session)

        if not self._verify(session['from']):
            session['notes'] = [('error','Not Authorized')]
            return session

        try:
            self.homematic.runProgram(session['node'])
            session['notes'] =  [('info','OK')]
        except Exception as err:
            session['notes'] = [('error',err)]            
        return session
            
    def message(self, msg):
        #instead of just being rude, this will be a text-interface
        if msg['type'] in ('chat', 'normal'):
            msg.reply("%(body)s yourself!" % msg).send()

