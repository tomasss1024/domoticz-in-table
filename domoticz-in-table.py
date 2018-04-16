#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from Domoticz import Domoticz
import json
import urlparse
import base64
import re
import os
import glob

PORT_NUMBER = 8000
domoticzurl='http://localhost:8080'
statusurl=domoticzurl+'/json.htm?type=devices&filter=all&used=true&order=Name'
variableurl=domoticzurl+'/json.htm?type=command&param=getuservariables'
domoticzusername = "domoticz_user"
domoticzpassword = "domoticz_password"
dcz=Domoticz(domoticzurl,domoticzusername,domoticzpassword)

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
        d={}	
        def do_AUTHHEAD(self):
          #print "send header"
          self.send_response(401)
          self.send_header('WWW-Authenticate', 'Basic realm=\"Basic authentication\"')
          self.send_header('Content-type', 'text/html')
          self.end_headers() 

        def do_HEAD(self):
          #print "send header"
          self.send_response(200)
          self.send_header('Content-type', 'text/html')
          self.end_headers() 
        
        def show_file(self, path):
           extension = os.path.splitext(path)[-1]
           mime_types = {
              '.html': 'text/html',
              '.jpg':'image/jpg',
              '.gif': 'image/gif',
              '.png': 'image/png',
              '.js': 'application/javascript',
              '.css': 'text/css',
           }
           #content_length = int(self.headers['Content-Length'])
           #file_content = self.rfile.read(content_length)
           f=open(path)
           self.send_response(200)
           self.send_header('Content-type',mime_types[extension])
           self.send_header('Cache-Control','public, max-age=604800')
           self.end_headers()
           #print file_content
           self.wfile.write(f.read())
           f.close()
           return

	#Handler for the GET requests
	def do_GET(self):
              # auth begin
              ''' Present frontpage with user authentication. '''
              if self.headers.getheader('Authorization') == None:
                  self.do_AUTHHEAD()
              #        self.wfile.write('no auth header received')
                  return
                  pass
              elif self.headers.getheader('Authorization') == 'Basic secretuser' or self.headers.getheader('Authorization') == 'Basic dXNlcjpwYXNzd29yZA==': # 'Basic ' + base64.b64encode('user:password')
                #    self.do_HEAD()
                #    self.wfile.write(self.headers.getheader('Authorization'))
                #    self.wfile.write('authenticated!')
                # auth end     #else continue GET processing... 
                wwwpath='www'
                parsed_path = urlparse.urlparse(self.path)
                message_parts = [
                        'CLIENT VALUES:',
                        'client_address=%s (%s)' % (self.client_address,
                                                    self.address_string()),
                        'command=%s' % self.command,
                        'path=%s' % self.path,
                        'real path=%s' % parsed_path.path,
                        'query=%s' % parsed_path.query,
                        'request_version=%s' % self.request_version,
                        '',
                        'SERVER VALUES:',
                        'server_version=%s' % self.server_version,
                        'sys_version=%s' % self.sys_version,
                        'protocol_version=%s' % self.protocol_version,
                        '',
                        'HEADERS RECEIVED:',
                        ]
                for name, value in sorted(self.headers.items()):
                    message_parts.append('%s=%s' % (name, value.rstrip()))
                message_parts.append('')
                message = '\r\n'.join(message_parts)
                
                # for the first domoticz use /0/ in url and for other /1/, /2/
                if re.findall('/[\d]+/',parsed_path.path,flags=re.IGNORECASE):
                   idxdomo,parsed_path_path=re.match('/([\d]+)(/.*)',parsed_path.path,flags=re.IGNORECASE).groups()
                   domotext='localhost'
                   if(idxdomo!='0'):
                   #if True:
                      try:
                         domofile=open("clients/"+idxdomo+'.txt',"r")
                         domotext=domofile.readlines()[0].strip()
                         domofile.close()
                      except:
                         self.send_response(500)
                         self.send_header('Content-type','text/html')
                         self.end_headers()
                         self.wfile.write('Read file error')
                         #self.show_error()
                         return
                   #print(domotext)
                   port=str(8080+int(idxdomo))
                   domoticzurl='http://localhost:'+port
                   #print(domoticzurl)
                   #return
                   dcz=Domoticz(domoticzurl,domoticzusername,domoticzpassword)
                else:
         	      self.send_response(500)
         	      self.send_header('Content-type','text/html')
         	      self.end_headers()
                      self.wfile.write('Device list:<br/>')
                      self.wfile.write('<a href="/0/">/0/</a><br/>')
                      for client in glob.glob("clients/*.txt"):
                          num=client[8:-4]
                          anch='<a href="/'+num+'/">/'+num+'/</a><br/>'
                          self.wfile.write(anch)
                      return
                          
                if parsed_path_path=='/json.html':
                   dvs={'rows':[]}
                   if 'type=command&param=udevice&idx=' not in parsed_path.query:
                   #if True:
                      if('plan=var' in parsed_path.query):
                         d=dcz.status(adarg='&favorite=1&plan=3')
                      else:
                         d=dcz.status() #(adarg='&favorite=1&plan=3')
                         d2={}
                         d2['Name']='ServerTime'
                         d2['Data']=d['ServerTime']
                         d2['idx']='1000'
                         d2['PlanID']='0'
                         dvs['rows'].append(d2)
                         d2={}
                         d2['Name']='Sunrise'
                         d2['Data']=d['Sunrise']
                         d2['idx']='1010'
                         d2['PlanID']='0'
                         dvs['rows'].append(d2)
                         d2={}
                         d2['Name']='Sunset'
                         d2['Data']=d['Sunset']
                         d2['idx']='1020'
                         d2['PlanID']='0'
                         dvs['rows'].append(d2)
                      del d['result']
                      ## parse idx
                      idx=False
                   if 'type=command&param=udevice&idx=' in parsed_path.query:
                      d=dcz.status(adarg='&favorite=1&plan=3')
                      #print(parsed_path.query)
                      idx,dum=re.match('.*idx=([\d]+)(.*)',parsed_path.query,flags=re.IGNORECASE).groups()
                      if idx in d['devbyidx']:
                         if re.findall('idx=[\d]+.*svalue=',parsed_path.query,flags=re.IGNORECASE):
                            idx,svalue=re.match('.*idx=([\d]+).*svalue=([^\s&]+)',parsed_path.query,flags=re.IGNORECASE).groups()
                            #print(idx+ ' '+svalue)
                            try:
                               rd=dcz.set_device_text(idx,svalue)
                            except:
                               pass
                         else: 
                          if re.findall('idx=[\d]+.*nvalue=',parsed_path.query,flags=re.IGNORECASE):
                            idx,nvalue=re.match('.*idx=([\d]+).*nvalue=([^\s&]+)',parsed_path.query,flags=re.IGNORECASE).groups()
                            #print(idx+ ' '+nvalue)
                            try:
                               if(nvalue=='0'):
                                  rd=dcz.set_device_off(idx)
                               else:
                                  rd=dcz.set_device_on(idx)
                            except:
                               pass
                         #print(parsed_path.query)
                         self.send_response(200)
                         self.end_headers()
                         self.wfile.write(json.dumps(rd, indent=4, separators=(',', ': ')))
      		      #self.wfile.write(json.dumps(dvs, indent=4, separators=(',', ': ')))
                      else:
                         rd={}
                         rd['status']='Fail'
                         rd['title']='idx is not variable!'
                         self.send_response(200)
                         self.end_headers()
                         self.wfile.write(json.dumps(rd, indent=4, separators=(',', ': ')))
      		      return

                   if re.findall('idx=[\d]+',parsed_path.query,flags=re.IGNORECASE):
                      idx=re.match('.*idx=([\d]+)',parsed_path.query,flags=re.IGNORECASE).groups()[0]
   
                   if False: #if idx:
                      try:
                         #d['devices']=d['devbyidx'][str(idx)]
                         #d['devices']=[elem for elem in d['devbyidx'] if elem['idx']==str(idx)]
                         dvs['devices']={idx:d['devbyidx'][idx]}
                      except:
                  	 self.send_response(500)
                  	 self.send_header('Content-type','text/html')
                  	 self.end_headers()
                         self.wfile.write('Devices error')
                         return
                   else:
                      #d['devices']=d['devbyidx']
                      d2={}
                      i=0
                      for d1 in d['devbyidx'].iteritems():
                         for d2 in d1:
                            #print(d2)
                            try:
                               d2.isdigit()
                            except:
                               d2['svalue']=d2['Data'].split(' ')[0].split('%')[0]
                               dvs['rows'].append(d2)
                      dvs['rows']=sorted(dvs['rows'],key=lambda k: k['idx'])
                      #sorted(dvs['rows'])
                      #dvs['rows']=d['devbyidx']
                      dvs['total']=len(dvs['rows'])
   
                   del d['devbyidx']
                   del d['devbyname']
                   #d=dcz.status()
                   self.send_response(200)
                   self.send_header('Content-type','text/html')
                   self.end_headers()
                   # Send the html message
                   #self.wfile.write("Hello World !")
                   ## debug
                   if 'debug=1' in parsed_path.query:
   		     self.wfile.write(message)
   		   self.wfile.write(json.dumps(dvs, indent=4, separators=(',', ': ')))
   		   return

                if parsed_path_path=='/':
                   parsed_path_path='/index.html'
                else:
                   parsed_path_path=parsed_path_path

                if parsed_path_path!='/':
                   try:
                      self.show_file(wwwpath+parsed_path_path)
                   except:
         	      self.send_response(500)
         	      self.send_header('Content-type','text/html')
         	      self.end_headers()
                      self.wfile.write('Read file error')
                      #self.show_error()
                   if 'debug=1' in parsed_path.query:
		      self.wfile.write(message)

                   return
                   

	def do_POST(self):
           self.do_GET()
        
        def show_error(self):
         	      self.send_response(500)
         	      self.send_header('Content-type','text/html')
         	      self.end_headers()
                      self.wfile.write('Read file error')
           

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close() 

