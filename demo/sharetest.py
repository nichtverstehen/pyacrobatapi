import acrobat
import getpass
import os.path

acrobat.AcrobatClient.api_key = "1b2a5945948665a97d717ad6788d2XXX"
acrobat.AcrobatClient.secret =  "d2c3ef3b182b8ca83XXXXXXXXXXXXXXX"

def main():
	print "Acrobat.com Share console\n"
	
	username = raw_input('Username: ')
	password = getpass.getpass()
	print

	client = acrobat.AcrobatClient()
	client.Login(username, password)

	stack = []

	current = client.GetNode()
	stack.append(current)

	cmd = ''
	while cmd != 'exit':
		line = raw_input(stack_path(stack)+'> ')
		
		args = line.split()
		if args == []: continue
		cmd = args[0]
		
		try:
			if cmd == 'help' or cmd == '?':
				print 'Valid commands: cd, cdup, ls, rm, pwd, cat, pass, share, unshare, level, upload, url, stat, ren, mkdir, help, exit'
			
			elif cmd == 'ls':
				current.Update()
				for v in current.children:
					f = v.sharelevel if v.hascontent else 'd'
					if v.directory:
						print '%s   %s   %s'%(v.nodeid, f, v.name)
					else:
						print '%s   %s   %s'%(v.nodeid, f, v.name)
					
			elif cmd == 'cd':
				if len(args) < 2: print "cd <dir>"; continue
				
				if args[1] == '..':
					stack.pop()
					current = stack[-1]
					current.Update()
					continue
					
				v = get_by_name(current.children, args[1])
				if v is not None and v.directory:
					current=v
					stack.append(v)
				else:
					print "Not found"
				
			elif cmd == 'cat':
				if len(args) < 2: print "cat <file>"; continue
				
				v = get_by_name(current.children, args[1])
				if v is not None and v.hascontent:
					print v.GetSourceFile()
				else:
					print "Not found"
				
			elif cmd == 'stat':
				if len(args) < 2: print "rm <node>"; continue
				
				v = get_by_name(current.children, args[1])
				if v is not None:
					for k, p in v.data.iteritems():
						print '%20s %s'%(k, p)
				else:
					print "Not found"
					
			elif cmd == 'url':
				if len(args) < 2: print "url <file>"; continue
				
				v = get_by_name(current.children, args[1])
				if v is not None and v.hascontent:
					print v.GetPublicURL()
				else:
					print "Not found"
					
			elif cmd == 'level':
				if len(args) < 3: print "level <file> <level>"; continue
				v = get_by_name(current.children, args[1])
				if v is not None and v.hascontent:
					v.Share(args[2])
				else:
					print "Not found"
			
			elif cmd == 'share':
				if len(args) < 2: print "share <file> [<email>]"; continue
				v = get_by_name(current.children, args[1])
				if v is not None and v.hascontent:
					if len(args) < 3:
						print '\n'.join(v.recipients)
					else:
						v.Share(v.sharelevel if v.sharelevel > 0 else 1, args[2])
						v.Update()
				else:
					print "Not found"
			
			elif cmd == 'unshare':
				if len(args) < 3: print "unshare <file> <email>"; continue
				v = get_by_name(current.children, args[1])
				if v is not None and v.hascontent:
					v.Unshare(args[2])
					v.Update()
				else:
					print "Not found"
				
			elif cmd == 'rm':
				if len(args) < 2: print "rm <node>"; continue
				
				v = get_by_name(current.children, args[1])
				if v is not None:
					v.Delete()
					current.Update()
				else:
					print "Not found"
					
			elif cmd == 'upload':
				if len(args) < 2: print "upload <localfile>"; continue
				
				try:
					with open(args[1], 'r') as f:
						name = os.path.basename(args[1])
						current.UploadFile(name, f.read())
					current.Update()
				except IOError:
					print 'IOError'
				
			elif cmd == 'ren':
				if len(args) < 3: print "rm <node> <name>"; continue
				
				v = get_by_name(current.children, args[1])
				if v is not None and args[1] != "":
					v.Rename(args[2])
					current.Update()
				else:
					print "Not found"
				
			elif cmd == 'pwd':
				print stack_path(stack)
				
			elif cmd == 'mkdir':
				if len(args) < 2: print "mkdir <name>"; continue
				
				current.CreateSubdir(args[1])
				current.Update()
				
			elif cmd == 'cdup':
				stack.pop()
				current = stack[-1]
				current.Update()
			
			elif cmd == 'exit':
				client.EndSession()
				
			else:
				print "Unknown command"
				
		except acrobat.AcrobatException, e:
			print e
	
def get_by_name(l, name):
	for v in l:
		if v.name == name:
			return v
			
def stack_path(stack):
	return "/".join([v.name for v in stack])

if __name__=='__main__':
	main()