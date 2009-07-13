def GetAcrobatException(status):
	exceptions = { 
		'BadApikey': BadApikey,
		'BadAuthHeader': BadAuthHeader,
		'BadAuthQuery': BadAuthQuery,
		'BadCalltime': BadCalltime,
		'BadFormat': BadFormat,
		'BadMethod': BadMethod,
		'BadSessionid': BadSessionid,
		'BadSig': BadSig,
		'Error': Error,
		'LimitReached': LimitReached,
		'MissingElements': MissingElements,
		'Unauthorized': Unauthorized,
		'BadAuthtoken': BadAuthtoken,
		'NotVerified': NotVerified,
		'NoTOU': NoTOU,
		'BadLogin':	BadLogin,
		'LockedOut': LockedOut,
		'BadNodeID': BadNodeID,
		'BadUpload': BadUpload,
		'DuplicateName': DuplicateName,
		'IllegalFiletype': IllegalFiletype,
		'QuotaReached': QuotaReached,
		'AccessDenied': AccessDenied,
		'BadRendition': BadRendition,
		'Processing': Processing
	}
	return exceptions.get(status, Error)

		
class AcrobatException(Exception):
	pass
class BadApikey(AcrobatException):
	"""The given API key is invalid."""
	pass
class BadAuthHeader(AcrobatException):
	"""The authorization header has the wrong format or syntax."""
	pass
class BadAuthQuery(AcrobatException):
	"""The query does not contain the required parameters. 
	This error is only returned when the authorization parameters are 
	passed in an HTTP request rather than in an HTTP header as described 
	in Using authorization parameters in an HTTP request."""
	pass
class BadCalltime(AcrobatException):
	"""The given calltime has problems:
	Either it does not come after the calltime of the most recent successful request, or
	The request was issued too soon after the prior request.
	The suggested time between requests per session is half a second."""
	pass
class BadFormat(AcrobatException):
	"""The request body is malformed."""
	pass
class BadMethod(AcrobatException):
	"""Not a valid HTTP method on this endpoint."""
	pass
class BadSessionid(AcrobatException):
	"""The given sessionid does not exist or is expired."""
	pass
class BadSig(AcrobatException):
	"""The authorization signature is incorrect."""
	pass
class Error(AcrobatException):
	"""An unknown error has occurred."""
	pass
class LimitReached(AcrobatException):
	"""The number of allowable requests was exceeded in the last hour."""
	pass
class MissingElements(AcrobatException):
	"""The request body is missing required elements."""
	pass
class Unauthorized(AcrobatException):
	"""The user does not have authorization to perform the requested action."""
	pass
class BadAuthtoken(AcrobatException):
	"""Invalid authorization token."""
	pass
class NotVerified(AcrobatException):
	"""User has not verified email address yet."""
	pass
class NoTOU(AcrobatException):
	"""User has not accepted terms of use agreement."""
	pass
class BadLogin(AcrobatException):
	"""Invalid username or password."""
	pass
class LockedOut(AcrobatException):
	"""Too many failed login attempts; try again later."""
	pass
class XMLError(AcrobatException):
	"""Not an Adobe exception. Raised when xml parsing failed"""
	pass
class BadAuthQuery(AcrobatException):
	"""The query does not contain the required parameters. 
	This error is only returned when the authorization parameters are 
	passed in an HTTP request rather than in an HTTP header as described 
	in Using authorization parameters in an HTTP request."""
	pass
class BadCalltime(AcrobatException):
	"""The given calltime has problems:
	Either it does not come after the calltime of the most recent successful request, or
	The request was issued too soon after the prior request.
	The suggested time between requests per session is half a second."""
	pass
class BadFormat(AcrobatException):
	"""The request body is malformed."""
	pass
class BadMethod(AcrobatException):
	"""Not a valid HTTP method on this endpoint."""
	pass
class BadSessionid(AcrobatException):
	"""The given sessionid does not exist or is expired."""
	pass
class BadSig(AcrobatException):
	"""The authorization signature is incorrect."""
	pass
class Error(AcrobatException):
	"""An unknown error has occurred."""
	pass
class LimitReached(AcrobatException):
	"""The number of allowable requests was exceeded in the last hour."""
	pass
class MissingElements(AcrobatException):
	"""The request body is missing required elements."""
	pass
class Unauthorized(AcrobatException):
	"""The user does not have authorization to perform the requested action."""
	pass

# uploads
class BadNodeID(AcrobatException):
	"""Attempt to upload a file into a nonexistent folder."""
	pass
class BadUpload(AcrobatException):
	"""Upload failed for some other reason."""
	pass
class DuplicateName(AcrobatException):
	"""A file with the same name already exists."""
	pass
class IllegalFiletype(AcrobatException):
	"""Attempt to upload a file which is in an unsupported file format."""
	pass
class QuotaReached(AcrobatException):
	"""Adding the file would exceed the user's storage quota."""
	pass
	
# renditions
class AccessDenied(AcrobatException):
	"""User does not have the proper privileges to download this file."""
	pass
class BadRendition(AcrobatException):
	"""Not a valid rendition request."""
	pass
class Processing(AcrobatException):
	"""File is still being processed. Please wait a few minutes."""
	pass
	