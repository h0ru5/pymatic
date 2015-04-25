'''
Created on 07.03.2015

@author: mail_000
'''

import logging
from sleekxmpp.plugins.xep_0030.stanza.items import DiscoItems
from sleekxmpp.plugins.xep_0050.stanza import Command

def createDeviceProxy(hmc,ddict):
    dtype = ddict['device_type']
    devclasses = [Thermostat,Blinds,Switch,DoorLock]
    
    for dc in devclasses:
        if dc.dtype==dtype: 
            return dc(hmc,ddict)
    
    #no match
    return Device(hmc,ddict) 

class Device(object):
    '''
    classdocs
    '''

    type='unkown'
    hmc = None
    
    def __init__(self, hmc, ddict):
        '''
        Constructor
        '''
        self.hmc = hmc
        self.ddict = ddict
        self.type = ddict['device_type']
        self.ise = ddict['ise_id']
        self.name = ddict['name']
        
        self.subnodes = {}
        self.data = {}
        self.writable_dps = []
        self.exposed_dps = []
        
        self.exposed_dps.append('RSSI_PEER')
        self.exposed_dps.append('RSSI_DEVICE')
        
    def _toValue(self,dptype):
        return self.data[dptype]['value']
            
    def update(self):
        self.data = self.hmc.getDataPoints(self.ise)
        self.rssi_peer = self._toValue('RSSI_PEER')
        self.await_conf = self._toValue('CONFIG_PENDING')
        self.rssi = self._toValue('RSSI_DEVICE')

        for dptype in self.exposed_dps:
            dp = self.data[dptype]
            self.subnodes[dp['ise_id']] = '%(type)s: %(value)s %(valueunit)s' % dp
        
        self._updateState()
    
    def handleItems(self, jid, node, ifrom, args):
        'return info for device subnode (=datapoint)'
        logging.debug('custom node info request for %s -> %s', node, self.name)
        self.update()
        items = DiscoItems()
        for (snode,sname) in self.subnodes.iteritems():
            items.add_item(jid.full, node + "/" + snode, sname)
        return items
        
    def add_commands(self, xmpp):
        'adds commands for this device'
        self.xmpp = xmpp
        for dptype in self.writable_dps:
            subnode = self.data[dptype]['ise_id']
            xmpp['xep_0050'].add_command(node=self.ise + '/' + subnode,
                                         handler=self._handle_cmd_ctrl_start)
            xmpp['xep_0030'].add_feature(Command.namespace,self.ise + '/' + subnode,xmpp.boundjid)
    
    def _handle_cmd_info(self, iq,session):
        'handle info command'
        logging.info('called to give info')
        self.data = self.hmc.getDataPoints(self.ise)
        rlist=[]
        
        for dpdict in self.data.values():
            rlist.append('%(type)s = %(value)s' % dpdict)
              
        session['notes'] = [('info','\n'.join(rlist))]
        return session
        
    def _updateState(self):
        'overridden by subclasses - does python have abstract class?'
        pass        
    
    def _handle_cmd_ctrl_start(self, iq,session):
        'handle command to set temperature'
        session['node'] = iq['command']['node']        
        logging.info('called command to set ')
                      
        form = self.xmpp['xep_0004'].makeForm('form', 'Set Value')
        form['instructions'] = 'Enter the Value to set'
        form.addField(var='new_value',
                      ftype='text-single',
                      label='New Value')

        session['payload'] = form
        session['next'] = self._handle_cmd_ctrl_finish
        session['has_next'] = False
        
        return session
    
    def _handle_cmd_ctrl_finish(self, payload,session):
        form = payload
        newval = form['values']['new_value']
        ise = session['node'].split('/')[1]
        
        logging.info('%s is setting value of %s to %s ',session['from'],ise,newval)
        
        self.hmc.setDataPoint(ise,newval)
        
        session['notes'] = [('info','set value to %s' % newval)]
        
        session['payload'] = None
        session['next'] = None

        return session
    
    def setValue(self,dptype,value):
        ise=self.data[dptype]['ise_id']
        self.hmc.setDataPoint(ise,value)
    
class Thermostat(Device):
    dtype='HM-CC-RT-DN'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Thermostat %r at %s",self.name,self.ise)
        self.exposed_dps += ['VALVE_STATE','ACTUAL_TEMPERATURE','SET_TEMPERATURE']
        self.writable_dps += ['SET_TEMPERATURE']
        
    def _updateState(self):
        self.valve = self._toValue('VALVE_STATE')
        self.boost = self._toValue('BOOST_STATE')
        self.val = self._toValue('ACTUAL_TEMPERATURE')
        self.ctl = self._toValue('SET_TEMPERATURE')
        
class Blinds(Device):
    dtype='HM-LC-Bl1-FM'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Blinds %r at %s",self.name,self.ise)
        self.exposed_dps += ['LEVEL']
        self.writable_dps += ['LEVEL']
        
    def _updateState(self):
        self.level = self._toValue('LEVEL')

class Switch(Device):  
    dtype='HM-PB-6-WM55'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Switch %r at %s",self.name,self.ise)

class DoorLock(Device):
    dtype='HM-Sec-Key'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Doorlock %r at %s",self.name,self.ise)
        self.exposed_dps += ['STATE','STATE_UNCERTAIN', 'OPEN']
        self.writable_dps += ['STATE','OPEN']
        
        
