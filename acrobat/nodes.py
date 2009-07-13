from datetime import datetime
import acrobat
import urllib

class Node(object):
	def __init__(self, client, data):
		"""You shouldn't construct this object yourself."""
		self.client = client
		self.data = data
		
	def UpdateData(self, data):
		"""Update internal dict with node info"""
		self.data.update(data)
		
	def Update(self, client=None):
		"""Update node info from server. Returns nothing."""
		if client is None:
			client = self.client
		self.data.update(client.GetNodeDict(self.nodeid))
		
	def Move(self, nodeId):
		"""Move to directory specified with nodeId. Returns nothing."""
		self.client.MoveRename(self.nodeid, self.name, nodeId)
	
	def Rename(self, newname):
		"""Renames node. Returns nothing"""
		self.client.MoveRename(self.nodeid, newname, None)
		self.data['name'] = newname
		
	def Delete(self):
		"""Deletes node. The object remains valid (though an Update() will fail. Returns nothing"""
		self.client.Delete(self.nodeid)
	
	@property
	def name(self):
		"""The node name."""
		return self.data['name']
		
	@property
	def nodeid(self):
		"""The string that uniquely identifies the node."""
		return self.data['nodeid']
		
	@property
	def directory(self):
		"""True if the node is a folder or a directory."""
		return self.data['directory'].lower() == 'true'
		
	@property
	def hascontent(self):
		"""True if the node is a file."""
		return self.data['hascontent'].lower() == 'true'
		
	@property 
	def link(self):
		"""True if someone else has shared this file with you."""
		return self.data['link'].lower() == 'true'
		
	@property
	def createddate(self):
		"""The node creation date."""
		return datetime.fromtimestamp(int(self.data['createddate'])/1000)
		
	@property
	def modifieddate(self):
		"""The nodes last modified date."""
		return datetime.fromtimestamp(int(self.data['modifieddate'])/1000)
	
	@property
	def owner(self):
		"""The Adobe ID of a given nodes owner."""
		return self.data['owner']
		
	@property
	def ownername(self):
		"""The full owner name of a given node."""
		return self.data['ownername']
		
	@property
	def description(self):
		"""The node description."""
		return self.data['description']
	
		
class File(Node):
	def Share(self, level, shareWith=[], message = None):
		"""Set sharing options. See AcrobatClient.Share help for more info.
		shareWith is an Adobe ID or a list or set of Adobe IDs"""
		
		if type(shareWith) is set:
			shareWith = list(unShareWith)
		if type(shareWith) is not list:
			shareWith = [shareWith]
			
		self.client.Share(self.nodeid, level, shareWith, message)
		self.data['sharelevel'] = level
		self.data['recipients'].update(shareWith)
		
	def Unshare(self, unShareWith):
		"""Remove a recipient. unShareWith is an Adobe ID or a list or set of Adobe IDs"""
		
		if type(unShareWith) is set:
			unShareWith = list(unShareWith)
		if type(unShareWith) is not list:
			unShareWith = [unShareWith]
			
		self.client.Unshare(self.nodeid, unShareWith)
		self.data['recipients'].difference_update(unShareWith)
		
	def UpdateFile(self, content, description=None, renditions=True, createpdf=False):
		"""Uploads file and returns resulting File object"""
		d = self.client.UpdateFile(self.name, content, self, description, renditions, createpdf, return_dict=True)
		self.UpdateData(d)
		
	def GetThumbnail(self):
		"""Returns HTTPResponse with thumbnail data"""
		return self.client.GetRendition(self.nodeid, "thumbnail").read()
		
	def GetSourceFile(self):
		"""Returns HTTPResponse with source file data"""
		return self.client.GetRendition(self.nodeid, "src").read()
	
	def GetPDF(self):
		"""Returns HTTPResponse with pdf data (if converted)"""
		return self.client.GetRendition(self.nodeid, "pdf").read()
		
	def GetPublicURL(self):
		"""Unsupported method. Builds a url to download file publicly"""
		return "https://share.acrocomcontent.com/adc/src/%s?nodeId=%s" % (urllib.quote(self.name), self.nodeid)
		
	@property
	def adobedoc(self):
		"""True if the file is a special file from Adobe."""
		return self.data['adobedoc'].lower() == 'true'
	
	@property
	def author(self):
		"""The author of a document, if the author's name was able to be extracted from file metadata."""
		return self.data['author']
	 
	@property
	def filesize(self):
		"""The file size in bytes."""
		return int(self.data['filesize'])
		
	@property
	def flashpreviewembed(self):
		"""The HTML object code that can be used to embed a flash preview in a web page."""
		return self.data['flashpreviewembed']
		
	@property
	def flashpreviewpagecount(self):
		"""The number of document pages if a flash preview was successfully generated."""
		return int(self.data['flashpreviewpagecount'])
		
	@property
	def flashpreviewstate(self):
		"""The preview state: 1: The flash preview is ready. 0: The flash preview is still being generated. -1: Flash preview generation failed."""
		return int(self.data['flashpreviewstate'])

	@property
	def mimetype(self):
		"""The file type, such as PDF, doc, and so on."""
		return self.data['mimetype']
	
	@property
	def recipients(self):
		"""The Adobe IDs of each person with which the document has been shared. Each Adobe ID will be a child recipient element."""
		return self.data['recipients']
	
	@property
	def recipienturl(self):
		"""The URL a recipient uses to view a document (such as a link in an email)."""
		return self.data['recipienturl']

	@property
	def sharelevel(self):
		"""The share level: 
		0: The file is unshared. 
		1: The file is only accessible to those with whom the file has been shared. 
		2: The file is publicly accessible."""
		return int(self.data['sharelevel'])
		
	@property
	def thumbnailstate(self):
		"""The thumbnail state: 
		1: The thumbnail is ready. 
		0: The thumbnail is still being generated. 
		-1: Thumbnail generation failed."""
		return int(self.data['thumbnailstate'])
		
	@property
	def pdfstate(self):
		"""The PDF state: 
		-1: PDF generation failed. 
		0: PDF queued for generation. 
		1: PDF available but not downloadable. 
		2: PDF downloadable. 
		3: PDF generation in progress."""
		return int(self.data['pdfstate'])
	
class Directory(Node):
	def CreateSubdir(self, name, description=None):
		"""Creates a subdirectory"""
		return self.client.CreateDirectory(name, self, description)
		
	def UploadFile(self, name, content, description=None, renditions=True, createpdf=False):
		"""Uploads file and returns resulting File object"""
		return self.client.UpdateFile(name, content, self, description, renditions, createpdf)
	
	@property
	def children(self):
		"""Node's children"""
		# untested
		if not self.data.has_key('children'):
			self.Update()
		
		children = [self.client.NodeFromDict(d) for d in self.data['children']]
		return children
		