import os
import time
import paramiko
from subprocess import check_output
from config import *

def remote_revert_clean():
	print "--- Remote svn revert/clean"
	remote_in, remote_out, remote_err = remote.exec_command('cd ' + remote_path + '; svn revert -R .')
	print remote_out.read()
	print remote_err.read()
	remote_in, remote_out, remote_err = remote.exec_command('cd ' + remote_path + '; svn st | grep \'^?\' | awk \'{print $2}\' | xargs -I{} rm -rf \'{}\'')
	print remote_out.read()
	print remote_err.read()


remote = paramiko.SSHClient()
remote.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote.connect('sonic.local.buonny', username=username, password=password)

os.chdir(absolut_local_path)

print "--- local svn up:"
print check_output('svn up', shell=True)

remote_revert_clean()

print "--- remote svn up:"
remote_in, remote_out, remote_err = remote.exec_command('cd ' + remote_path + '; svn up')
print remote_out.read()
print remote_err.read()

print '--- started.'
last_diff = ''
count = 1

while True:

	check_output('svn diff > patch.diff', shell=True)
	curr_diff = check_output('cat patch.diff', shell=True)
	
	if (last_diff != curr_diff):
		print "--- new diff generated"
		last_diff = curr_diff

		remote_revert_clean()

		print "--- sending patch..."
		sftp = remote.open_sftp()
		sftp.put('patch.diff', absolut_remote_path + 'patch.diff')
		sftp.close()

		print "--- remote patch"
		#remote_in, remote_out, remote_err = remote.exec_command('cd ' + remote_path + '; svn patch patch.diff')
		remote_in, remote_out, remote_err = remote.exec_command('cd ' + remote_path + '; patch -p0 < patch.diff')
		print remote_out.read()
		print remote_err.read()
		
		check_output('terminal-notifier -message "synced ' + str(count) + '"', shell=True)
		count += 1
		print '--- waiting new diff...'
		
	time.sleep(1)
	
