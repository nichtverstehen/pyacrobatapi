import time, hashlib
import httplib, urllib
import xml.dom.minidom
import acrobat
import acrobat.exceptions
from acrobat.nodes import *
from acrobat.exceptions import GetAcrobatException

ACROBAT_HOST = "api.share.acrobat.com"
ACROBAT_APIURL = "/webservices/api/v1/"

class AcrobatClient(object):
	"""The acrobat client main class.
	You must set api_key and secret before using this class.
	Begin your work with a Login call.
	
	Instance members:
		username logged in username
		currentsecret secret acquired during login
		session Acrobat session id
		level user subscription level"""
	
	api_key = None
	secret = None
	
	"""Members:
	username
	currentsecret
	session
	level"""
	
	def __init__(self):
		self.username = None
		self.currentsecret = AcrobatClient.secret
		self.session = None
		self.level = None
	
	def _AuthString(self, method, host, url, api_key, secret, sessionid):
		"""Generate Authorization header
		
		Arguments:
		session - whether to use object's session member
		secret - whether to use
		
		Raises nothing"""
		
		calltime = str(int(time.time()*1000))
		data = method+" https://"+host+url+" "+calltime
		md5 = hashlib.md5(); md5.update((data+secret).encode('utf-8')); sig = md5.hexdigest()
		session = 'sessionid="%s",' % sessionid if sessionid is not None else ""
			
		auth = 'AdobeAuth %(session)sapikey="%(api_key)s",data="%(data)s",sig="%(sig)s"' \
			% {'session': session, 'api_key': api_key, 'data': data, 'sig': sig }
		
		return auth
		
	def AuthString(self, method, host, url):
		"""Generate Authorization header for a request.
		
		Raises nothing"""
		
		return self._AuthString(method, host, url, AcrobatClient.api_key, self.currentsecret, self.session)
		
	def ServiceRequest(self, method, url_part, payload, query=None, anon=False, headers=None):
		"""Makes authorised request to Acrobat service with current session+secret.
		Returns a HTTPResponse object
		Raises any kind of HTTPException or AcrobatException"""
		
		conn = httplib.HTTPSConnection(ACROBAT_HOST)
		
		path = urllib.quote((ACROBAT_APIURL+url_part).encode('utf-8'))
		qs = "?"+urllib.urlencode([(i,v.encode('utf-8')) for i,v in query.iteritems()]) if query is not None else ""
		
		if anon: auth = self._AuthString(method, ACROBAT_HOST, path+qs, AcrobatClient.api_key, AcrobatClient.secret, None)
		else: auth = self._AuthString(method, ACROBAT_HOST, path+qs, AcrobatClient.api_key, self.currentsecret, self.session)
		
		if type(payload) is unicode:
			payload = payload.encode('utf-8')
		
		if headers is None:
			headers = {}
		headers['Authorization'] = auth
		
		conn.request(method, path+qs, payload, headers)
		
		resp = conn.getresponse()
		if not resp.status == 200:
			raise GetAcrobatException(resp.read())
		
		return resp
		
	def NewSession(self, username, token):
		"""Starts a new session using specified token.
		You usually won't want to use this. Use Login() instead.
		Raises any kind of HTTPException or AcrobatException when used properly"""
		
		payload = '<request><authtoken>%s</authtoken></request>'%token
		resp = self.ServiceRequest("POST", "sessions/", payload, anon=True)
		doc = ParseXML(resp.read())
			
		self.session = GetNodeTextContent(doc.getElementsByTagName("sessionid"))
		self.currentsecret = GetNodeTextContent(doc.getElementsByTagName("secret"))
		self.level = GetNodeTextContent(doc.getElementsByTagName("level"))
		self.username = username

	def EndSession(self):
		"""Ends session and clears proper fields.
		Raises any kind of HTTPException or XMLError or BadSessionid"""
		
		self.ServiceRequest("DELETE", "sessions/%s/"%self.session, None)
		self.username = None
		self.session = None
		self.currentsecret = None
		self.level = None
	
	def GetSessionToken(self, username, password):
		"""Gets an auth token to create a session
		You usually won't want to use this. Use Login() instead.
		Raises any kind of HTTPException or AcrobatException."""
		
		payload = "<request><username>%s</username><password>%s</password></request>" % ( username, password )
		resp = self.ServiceRequest("POST", "auth/", payload, anon=True)
		doc = ParseXML(resp.read())
		
		tokenNodes = doc.getElementsByTagName("authtoken")
		authToken = GetNodeTextContent(tokenNodes)
			
		return authToken
	
	def Login(self, username, password):
		"""Logs in with Acrobat API and sets proper members
		Raises various HTTPException errors"""
		
		token = self.GetSessionToken(username, password)
		self.NewSession(username, token)
	
	def GetNodeXML(self, nodeId=None):
		"""Retrieves node content as an XML response. If nodeId is None (default) returns root folder info"""
		
		if nodeId: nodeIdPart = str(nodeId)+"/"
		else: nodeIdPart = ""
			
		resp = self.ServiceRequest("GET", "dc/"+nodeIdPart, None)
		return resp.read()
		
	def ParseNodeElement(self, node):
		"""Translate a <node> to a dict.
		Returns dict"""
		d = AttributesDict(node)
		
		for i in range(node.childNodes.length):
			item = node.childNodes.item(i)
			if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
				if item.tagName == 'recipients':
					d['recipients'] = set(ChildrenList(item, 'recipient'))
					
		return d
		
	def GetNodeDict(self, nodeId=None):
		"""Retrieves node content as a python dict. If nodeId is None (default) returns root folder info"""
		response = self.GetNodeXML(nodeId)
		
		doc = ParseXML(response)
		root = doc.documentElement
		d = {}
		for i in range(root.childNodes.length):
			item = root.childNodes.item(i)
			if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
				if item.tagName == 'node':
					d.update(self.ParseNodeElement(item))
				if item.tagName == 'children':
					d['children'] = []
					for i in range(item.childNodes.length):
						child = item.childNodes.item(i)
						if child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and child.tagName == 'node':
							d['children'].append(self.ParseNodeElement(child))
		return d
		
	def NodeFromDict(self, d):
		"""Constructs an acrobat.File or acrobat.Directory from a dict"""
		
		if d['directory'].lower()=='true':
			node = Directory(self, d)
		else:
			node = File(self, d)
			
		return node
		
	def GetNode(self, nodeId=None):
		"""Retrives node as an object (acrobat.File or acrobat.Directory)"""
		d = self.GetNodeDict(nodeId)
		return self.NodeFromDict(d)
		
	def MoveRename(self, nodeId, newName, toNodeId):
		"""Moves or renames a node. both newName and toNodeId can be None"""
	
		#params = []
		#if newName is not None:
		#	params.append("newname=%s"%newName)
		#if toNodeId is not None:
		#	params.append("destnodeid=%s"%toNodeId)
		path = "dc/%s/"%nodeId
		query = {}
		if newName is not None:
			query["newname"] = newName
		if toNodeId is not None:
			query['destnodeid'] = toNodeId
		
		# MOVE method is not working: http://forums.adobe.com/message/1993823
		self.ServiceRequest("MOVE", path, "<request/>", query=query)
		
	def Delete(self, nodeId):
		path = "dc/%s/"%nodeId
		self.ServiceRequest("DELETE", path, None)
		
	def Share(self, nodeId, level, shareWith, message = None):
		"""Sets sharing options for a node
		If the level parameter is 1, access is granted 
		to only those users with an Adobe ID that matches one of the given email addresses.
		If the level parameter is 2, anyone can access the file.
		
		Arguments:
			shareWith lists of Adobe IDs of the recipients
			level is 1 or 2
			A message is optional."""
			
		shareXmlList = ["<user>%s</user>"%user for user in shareWith]
		msgXml = "<message>%s</message>"%message if message else ""
		
		payload = "<request><share>%(share)s</share><level>%(level)s</level>%(msg)s</request>" \
			% {'share': "".join(shareXmlList), 'msg': msgXml, 'level': level }
		path = "dc/%s/share/"%nodeId
		self.ServiceRequest("PUT", path, payload)
		
	def Unshare(self, nodeId, unShareWith):
		"""Sets sharing options for a node. unShareWith is a list of Adobe IDs of the recipients"""
			
		unshareXmlList = ["<user>%s</user>"%user for user in unShareWith]
		payload = "<request><unshare>%(unshare)s</unshare></request>" % {'unshare': "".join(unshareXmlList) }
		path = "dc/%s/share/"%nodeId
		self.ServiceRequest("PUT", path, payload)
	
	def GetRendition(self, nodeId, key):
		"""Get a rendition of a file. Returns HTTPResponse object.
		Valid key values are: thumbnail, src, pdf"""
		url = "dc/%s/%s/" % (nodeId, key)
		return self.ServiceRequest("GET", url, None)
		
	def UpdateFile(self, name, content, nodeId=None, description=None, renditions=True, createpdf=False, return_dict=False):
		"""Creates or updates a file
		nodeid is a parent dir id/parent dir object (or None to upload to root) or a file id/file object to update file.
		Nowadays you cannot update metadata (descr, createpdf, return_dict) without uploading file contents.
		Descriptions are probably ignored"""
		
		url = "dc/"
		if isinstance(nodeId, Node):
			nodeId = nodeId.nodeid
		if nodeId is not None:
			url += nodeId+"/"
			
		descrXml = '<description>%s</description>'%description if description is not None else ''
		renditions = 'true' if renditions else 'false'
		createpdf = 'true' if createpdf else 'false'
		request = '<request><file><name>%s</name>'%name + descrXml +\
			'<renditions>%s</renditions><createpdf>%s</createpdf></file></request>'%(renditions, createpdf)
			
		if content is not None:
			boundary = '314159265358979323846UnIqUeBoUnDaRy'
			payload = '--'+boundary+'\r\n'+\
				'Content-disposition: form-data; name="request"\r\n'+\
				'Content-Type: text/xml\r\n\r\n'+\
				request.encode('utf-8')+\
				'\r\n--'+boundary+'\r\n'+\
				'Content-disposition: form-data; name="file"; filename="%s"\r\n'%name.encode('utf-8')+\
				'Content-Type: application/octet-stream\r\n'+\
				'Content-Transfer-Encoding: binary\r\n\r\n'+\
				content+\
				'\r\n--'+boundary+'--\r\n'
			headers = {'Content-type': 'multipart/form-data; boundary=%s'%boundary }
		else:
			# doesn't work without file content... anyway...
			payload = request
			headers = None
		
		resp = self.ServiceRequest("POST", url, payload, headers=headers)
		doc = ParseXML(resp.read())
		
		root = doc.documentElement
		for i in range(root.childNodes.length):
			item = root.childNodes.item(i)
			if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and item.tagName == 'node':
				d = self.ParseNodeElement(item)
				return self.NodeFromDict(d) if not return_dict else d
				
		raise acrobat.exceptions.Error("No <node>s in create folder response")
		
	def CreateDirectory(self, name, parentId=None, description=None, return_dict=False):
		"""Creates a folder. parentId is a nodeid or Node object
		Nowadays directories are not viewable from web and descriptions don't seem to work."""

		descrXml = "<description>%s</description>" % description if description is not None else ""
		payload = "<request><folder><name>%s</name>%s</folder></request>" % (name, descrXml)
		url = "dc/"
		if isinstance(parentId, Node):
			parentId = parentId.nodeid
		if parentId is not None:
			url += parentId+"/"
			
		resp = self.ServiceRequest("POST", url, payload)
		doc = ParseXML(resp.read())
		
		root = doc.documentElement
		for i in range(root.childNodes.length):
			item = root.childNodes.item(i)
			if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and item.tagName == 'node':
				d = self.ParseNodeElement(item)
				return self.NodeFromDict(d) if not return_dict else d
				
		raise acrobat.exceptions.Error("No <node>s in create folder response")


# XML helper functions
def ParseXML(xmlstr):
	"""Parses xml and generates XMLError when failed.
	Returns xml.dom.minidom.Document
	Raises XMLError when failed"""
	try:
		doc = xml.dom.minidom.parseString(xmlstr)
	except:
		raise acrobat.exceptions.XMLError("Could not parse response", xmlstr)
	return doc
	
def AttributesDict(node):
	"""Creates a python dict from node attributes:
	{ 'attr1name': 'attr1value', 'attr2name': 'attr2value', ..., 'attrNname': 'attrNvalue' }
	Returns dict
	Raises nothing"""
	
	d = {}
	for i in range(node.attributes.length):
		attr = node.attributes.item(i)
		d[attr.name] = attr.value
		
	return d
			
def ChildrenList(node, tagName):
	"""Creates a python list from text contents of node's subelements (child elements).
	It uses only subelements with specidied tagName or all subelements
	Returns list
	Raises nothing"""
	
	l = []
	for i in range(node.childNodes.length):
		item = node.childNodes.item(i)
		if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
			if tagName is None or tagName == item.tagName:
				l.append(GetNodeTextContent(item))
				
	return l
		
	
def GetNodeTextContent(node):
	"""Recursively concatenate Text node contents.
	
	Arguments:
		node - a Node or a NodeList
		
	Returns str
	
	Raises nothing"""
	if type(node) is xml.dom.minidom.NodeList:
		t = ""
		for i in range(node.length):
			t += GetNodeTextContent(node.item(i))
		return t
	elif node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
		return GetNodeTextContent(node.childNodes)
	else:
		return node.nodeValue
