'''
Created on 07.03.2015

@author: mail_000
'''

import logging

def createDeviceProxy(hmc,ddict):
    dtype = ddict['device_type']
    if dtype == Thermostat.dtype: 
        return Thermostat(hmc,ddict)
    elif dtype == Blinds.dtype: 
        return Blinds(hmc,ddict)
    elif dtype == Switch.dtype: 
        return Switch(hmc,ddict)
    else:
        return Device(hmc,ddict)

class Device(object):
    '''
    classdocs
    '''

    type='unkown'
    
    def __init__(self, hmc, ddict):
        '''
        Constructor
        '''
        self.data = {}
        self.ise=-1
        self.name=''
        self.type = ddict['device_type']
        self.ise = ddict['ise_id']
        self.name = ddict['name']
        self.ddict = ddict
        self.subnodes = {}
        self.update(hmc)
        
    def _toValue(self,dptype):
        return self.data[dptype]['value']
            
    def update(self,hmc):
        self.data = hmc.getDataPoints(self.ise)
        self.rssi = self._toValue('RSSI_DEVICE')
        self.rssi_peer = self._toValue('RSSI_DEVICE')
        self.await_conf = self._toValue('CONFIG_PENDING')
        self._updateState()
    
    def _updateState(self):
        'overridden by subclasses - does spython have abstract class?'
        pass        
        
class Thermostat(Device):
    dtype='HM-CC-RT-DN'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Thermostat %r at %s",self.name,self.ise)
        
    def _updateState(self):
        self.valve = self._toValue('VALVE_STATE')
        self.boost = self._toValue('BOOST_STATE')
        self.val = self._toValue('ACTUAL_TEMPERATURE')
        self.ctl = self._toValue('SET_TEMPERATURE')
        self.subnodes['val'] = 'Ist-Temperatur %s C' % self.val
        self.subnodes['ctrl'] = 'Soll-Temperatur: %s C' % self.ctl
        self.subnodes['valve'] = 'Ventil: %s %%' % self.valve
        self.subnodes['mode'] = 'Modus: xyz'
    
        
class Blinds(Device):
    dtype='HM-LC-Bl1-FM'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Blinds %r at %s",self.name,self.ise)
        
    
    def _updateState(self):
        self.level = self._toValue('LEVEL')
        self.subnodes['lvl'] = 'Level %s' % self.level

class Switch(Device):  
    dtype='HM-PB-6-WM55'
    def __init__(self,hmc,ddict):
        Device.__init__(self,hmc,ddict)
        logging.debug("found Switch %r at %s",self.name,self.ise)