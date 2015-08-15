# Adobe Acrobat Share API python client library

Python library to acess Acrobat.com Share API. See Links to find Adobe documentation and to sign up for a developer key.

## Usage

Just look though an example code:

	import acrobat

	acrobat.AcrobatClient.api_key = "1b2a5945948665a97d717ad6788d2XXX"
	acrobat.AcrobatClient.secret =  "d2c3ef3b182b8ca83XXXXXXXXXXXXXXX"

	client = acrobat.AcrobatClient()
	client.Login(username, password) # initiate a session

	root = client.GetNode() # retrieve root node info
	print root.nodeid
	print len(root.children)
	print root.children[0].name # name of a node
	print type(root.children[0]) # Directory or File (subclasses of Node)

	file_nodeid = root.children[0].nodeid
	file = client.GetNode(file_nodeid) # file refers to the same node as root.children[0]

	newfile = root.UploadFile("example.txt", "Contents of uploaded file") # create a new file
	newfile.Share(1, "user@example.org") # share the file
	newfile.Share(2) # make the file public
	print newfile.GetSourceFile() # prints uploaded content
	print newfile.GetPublicLink() # prints a link to download a file without authentication (if it is made public)


Node, that this example code doen't properly catch exceptions, raised by acrobat library or `httplib`. See `acrobat.exceptions` and docstrings for more information about exceptions, raised by the library.

Besides a pseudo-shell to access contents of Acrobat Share is included in the package. See `demo/sharetest.py`.
