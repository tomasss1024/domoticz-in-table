#!/usr/bin/env python

import json
import urllib2
import base64
from datetime import datetime
import re

class Domoticz():
 
    def __init__(self, url='http://localhost:8080',username='',password=''):
        self.baseurl = url
        self.username=username
        self.password=password
        self.base64string=base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
 
    def __execute__(self,url):
        req = urllib2.Request(url)
        if self.username!='':
           req.add_header("Authorization", "Basic %s" % self.base64string)
        return urllib2.urlopen(req, timeout=5)

    def set_device_on(self, xid):
        """
        Get the Domoticz device information.
        """
        print ('Sending on %s'%xid)
        url = "%s/json.htm?type=command&param=udevice&idx=%s&nvalue=1" % (self.baseurl, xid)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data

    def set_device_off(self, xid):
        """
        Get the Domoticz device information.
        """
        print ('Sending off %s'%xid)
        url = "%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0" % (self.baseurl, xid)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data

    def set_device_text(self,idx,name,level=0):
        print ('Sending text %s %s'%(idx,name))
        url = "%s/json.htm?type=command&param=udevice&idx=%s&nvalue=%i&svalue=%s" % (self.baseurl, idx,level,name)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data

    def set_selectorswitch(self,idx,level):
        print ('Sending level %s %d'%(idx,level))
        url = "%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Set%%20Level&level=%s" % (self.baseurl, idx,level)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data
    
    def set_switch(self,idx,switch):
	if switch==1:
            switch='On'
	if switch==0:
            switch='Off'
        print ('Sending switch %d %s'%(idx,switch))
        url = "%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=%s" % (self.baseurl, idx,switch)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data
        
    def set_scene(self,idx,switch):
	if switch==1:
            switch='On'
	if switch==0:
            switch='Off'
        print ('Sending switch %s %s'%(idx,switch))
        #url = "%s/json.htm?type=command&param=switchscene&idx=%s2&switchcmd=Off" % (self.baseurl, idx,switch)
        url = "%s/json.htm?type=command&param=switchscene&idx=%s&switchcmd=%s" % (self.baseurl, idx,switch)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data
        
    def update_var(self,idx,vname,vtype,vvalue):
        print ('Sending variable %s %s'%(idx,vvalue))
        url = "%s/json.htm?type=command&param=updateuservariable&idx=%s&vname=%s&vtype=%s&vvalue=%s" % (self.baseurl, idx,urllib2.quote(vname),vtype,urllib2.quote(vvalue))
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data
        
    def clear_device_log(self, xid):
        """
        Get the Domoticz device information.
        """
        print ('Clear log %s'%xid)
        #http://localhost:8080/json.htm?type=command&param=clearlightlog&idx=35 # 35=Main failure time
        url = "%s/json.htm?type=command&param=clearlightlog&idx=%s" % (self.baseurl, xid)
        print ('%s'%url)
        data = json.load(self.__execute__(url))
        return data

    def status(self,url=None,adarg=''):
        if url is None:
           url = "%s/json.htm?type=devices&filter=all&used=true&order=Name%s" % (self.baseurl,adarg)
        dbn={}
        dbi={}
        s=json.load(self.__execute__(url))
	#print (s)
	for v in s['result']:
           if v['Type']!='Scene' or v['Type']!='Group':
               name=v['Name']
               data=v['Data'].strip()
               idx=v['idx']
               planid=v['PlanID']
               try:
                   level=v['Level']
                   lastupdate=v['LastUpdate']
                   d={'Name':name,'Data':data,'Level':level,'LastUpdate':lastupdate,'idx':idx,'PlanID':planid}
               except KeyError:
                   d={'Name':name,'Data':data,'idx':idx,'PlanID':planid}
               dbn[name]=d
               dbi[idx]=d
        s['devbyname']=dbn
        s['devbyidx']=dbi
	return s
    
    def get_device(self,idx):
        dbn={}
        dbi={}
        url = "%s/json.htm?type=devices&rid=%s" % (self.baseurl, idx)
        print ('%s'%url)
        s = json.load(self.__execute__(url))
	#print(s)
	for v in s['result']:
           if True:
               name=v['Name']
               data=v['Data']
               vtype=v['Type']
               idx=v['idx']
               try:
                   lastupdate=v['LastUpdate']
                   d={'Name':name,'Type':vtype,'Data':data,'Value':data,'LastUpdate':lastupdate,'idx':idx}
               except KeyError:
                   d={'Name':name,'Type':vtype,'Data':data,'Value':data,'idx':idx}
               try:
                   d['Level']=v['Level']
               except KeyError:
                   pass
	return d
        
    def get_variables(self,url=None):
        if url is None:
           url = "%s/json.htm?type=command&param=getuservariables" % (self.baseurl)
        dbn={}
        dbi={}
        s=json.load(self.__execute__(url))
	#print(s)
	for v in s['result']:
           if v['Type']!='Scene' or v['Type']!='Group':
               name=v['Name']
               data=v['Value']
               vtype=v['Type']
               idx=v['idx']
               try:
                   lastupdate=v['LastUpdate']
                   d={'Name':name,'Type':vtype,'Data':data,'Value':data,'LastUpdate':lastupdate,'idx':idx}
               except KeyError:
                   d={'Name':name,'Type':vtype,'Data':data,'Value':data,'idx':idx}
               dbn[name]=d
               dbi[idx]=d
               s['devbyname']=dbn
               s['devbyidx']=dbi
	return s
        
    def get_variable(self,idx):
        dbn={}
        dbi={}
        url = "%s/json.htm?type=command&param=getuservariable&idx=%s" % (self.baseurl, idx)
        print ('%s'%url)
        s = json.load(self.__execute__(url))
	#print(s)
	for v in s['result']:
           if True:
               name=v['Name']
               data=v['Value']
               vtype=v['Type']
               idx=v['idx']
               try:
                   lastupdate=v['LastUpdate']
                   d={'Name':name,'Type':vtype,'Data':data,'Value':data,'LastUpdate':lastupdate,'idx':idx}
               except KeyError:
                   d={'Name':name,'Type':vtype,'Data':data,'Value':data,'idx':idx}
	return d
