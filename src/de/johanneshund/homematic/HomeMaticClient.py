'''
Created on 06.03.2015

@author: mail_000
'''

import logging
import urllib2
import urllib
import xml.etree.cElementTree as ET


class HomeMaticClient(object):
    '''
    classdocs
    '''

    def __init__(self, host):
         self.host = host
         self.PLACEHOLDER="http://%s/config/xmlapi/%s.cgi"

    def getUrl(self,action):
        return self.PLACEHOLDER % (self.host, action)
        
    def getXmlObject(self,action,query=None):
        pl = self.getUrl(action)
        if not query is None:
            pl += "?" + urllib.urlencode(query, True)
        logging.debug("getting %s",pl)
        res = urllib2.urlopen(pl)
        xml = res.read()
        return ET.fromstring(xml)
    
    def getPrograms(self):
        plist = self.getXmlObject('programlist')       
        return [child.attrib for child in plist]
    
    def runProgram(self,id):
        qs = {'program_id' : id}
        return self.getXmlObject('runprogram',qs)
        
      
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    
    hm  = HomeMaticClient('192.168.178.20')
    ls = hm.getPrograms()

    for program in ls:
        logging.debug("%(id)s: %(name)s",program)
    
    hm.runProgram(1681)
    
    
