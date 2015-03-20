'''
Created on 06.03.2015

@author: mail_000
'''

import logging
import urllib2
import urllib
import xml.etree.cElementTree as ET

import pymatic.Devices as hmdevs

class HomeMaticClient(object):
    '''
    classdocs
    '''

    def __init__(self, host):
        self.host = host
        self.PLACEHOLDER="http://%s/config/xmlapi/%s.cgi"
        self.devs = self.getDevices()

    def _getUrl(self,action):
        return self.PLACEHOLDER % (self.host, action)
        
    def _getXmlObject(self,action,query=None):
        pl = self._getUrl(action)
        if not query is None:
            pl += "?" + urllib.urlencode(query, True)
        logging.debug("getting %s",pl)
        res = urllib2.urlopen(pl)
        xml = res.read()
        return ET.fromstring(xml)
    
    def getResultList(self,action,query=None):
        rlist = self._getXmlObject(action,query)       
        return [child.attrib for child in rlist]
    
    def getPrograms(self):
        return self.getResultList('programlist')       
        
    def runProgram(self,progid):
        qs = {'program_id' : progid}
        return self._getXmlObject('runprogram',qs)
    
    def getDevicesRaw(self):
        return self.getResultList('devicelist')       
        
    def getDevices(self):
        return [hmdevs.createDeviceProxy(self, rdev) for rdev in self.getResultList('devicelist')]
    
    def getDataPoints(self,deviceid=None):
        if deviceid == None:
            datapoints = self._getXmlObject('statelist').getiterator('datapoint')
        else:
            datapoints = self._getXmlObject('state', {'device_id' : deviceid}).getiterator('datapoint')
        return {dp.attrib['type']:dp.attrib for dp in datapoints} 
    
    def setDataPoint(self,ise,data):
        """set the data point specified by the ise to the given value"""
        logging.debug('setting %s to %s',ise,data)
        qs = {'ise_id' : ise, 'new_value' : data}
        return self.getResultList('statechange',qs)
        
        
if __name__ == '__main__':
    #quick tests
    import sys
    if sys.version_info < (3, 0):
        from sleekxmpp.util.misc_ops import setdefaultencoding
        setdefaultencoding('utf8')
    else:
        raw_input = input
      
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    
        
