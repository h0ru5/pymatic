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
        rlist = self._getXmlObject(action)       
        return [child.attrib for child in rlist]
    
    def getPrograms(self):
        return self.getResultList('programlist')       
        
    def runProgram(self,id):
        qs = {'program_id' : id}
        return self._getXmlObject('runprogram',qs)
    
    def getDevicesRaw(self):
        return self.getResultList('devicelist')       
        
    def getDevices(self):
        rdevs=self.getResultList('devicelist')
        return map(hmdevs.getDetails, rdevs)
        
if __name__ == '__main__':      
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    hm = HomeMaticClient('192.168.178.20')
    print hm.getDevices()    
