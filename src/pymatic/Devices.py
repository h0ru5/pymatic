'''
Created on 07.03.2015

@author: mail_000
'''

import logging

def getDetails(ddict):
    dtype = ddict['device_type']
    if dtype == Thermostat.dtype: 
        return Thermostat(ddict)
    elif dtype == Blinds.dtype: 
        return Blinds(ddict)
    elif dtype == Switch.dtype: 
        return Switch(ddict)
    else:
        return Device(ddict)

class Device(object):
    '''
    classdocs
    '''

    type='unkown'
    ise=-1
    name=''
    ddict = {}

    def __init__(self, ddict):
        '''
        Constructor
        '''
        self.type = ddict['device_type']
        self.ise = ddict['ise_id']
        self.name = ddict['name']
        self.ddict = ddict
        self.subnodes = {}
        
class Thermostat(Device):
    dtype='HM-CC-RT-DN'
    def __init__(self,ddict):
        Device.__init__(self,ddict)
        logging.debug("found Thermostat %r at %s",self.name,self.ise)
        self.subnodes['val'] = 'Ist-Temperatur x C'
        self.subnodes['ctrl'] = 'Soll-Temperatur: x C'
        self.subnodes['mode'] = 'Modus: x'
        
class Blinds(Device):
    dtype='HM-LC-Bl1-FM'
    def __init__(self,ddict):
        Device.__init__(self,ddict)
        logging.debug("found Blinds %r at %s",self.name,self.ise)
        self.subnodes['lvl'] = 'Level x%'

class Switch(Device):  
    dtype='HM-PB-6-WM55'
    def __init__(self,ddict):
        Device.__init__(self,ddict)
        logging.debug("found Switch %r at %s",self.name,self.ise)