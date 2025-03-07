#!/usr/bin/python3
#
# final tasks
# thomas@linuxmuster.net
# 20220105
#

import configparser
import constants
import os
import re
import sys

from functions import getSetupValue, mySetupLogfile, printScript, readTextfile
from functions import subProc, waitForFw, writeTextfile

logfile = mySetupLogfile(__file__)

# remove temporary files
if os.path.isfile('/tmp/setup.ini'):
    os.unlink('/tmp/setup.ini')

# disable unwanted services
unwanted = ['iscsid', 'dropbear', 'lxcfs']
for item in unwanted:
    msg = 'Disabling service ' + item + ' '
    printScript(msg, '', False, False, True)
    try:
        subProc('systemctl stop ' + item + '.service', logfile)
        subProc('systemctl disable ' + item + '.service', logfile)
        printScript(' Success!', '', True, True, False, len(msg))
    except:
        printScript(' not installed!', '', True, True, False, len(msg))

# restart apparmor service
msg = 'Restarting apparmor service '
printScript(msg, '', False, False, True)
try:
    subProc('systemctl restart apparmor.service', logfile)
    printScript(' Success!', '', True, True, False, len(msg))
except Exception as error:
    printScript(error, '', True, True, False, len(msg))
    sys.exit(1)

# write schoolname to sophomorix school.conf
msg = 'Writing school name to school.conf '
printScript(msg, '', False, False, True)
try:
    schoolname = getSetupValue('schoolname')
    rc, content = readTextfile(constants.SCHOOLCONF)
    # need to use regex because sophomorix config files do not do not comply with the ini file standard
    content = re.sub(r'SCHOOL_LONGNAME=.*\n',
                     'SCHOOL_LONGNAME=' + schoolname + '\n', content)
    rc = writeTextfile(constants.SCHOOLCONF, content, 'w')
    printScript(' Success!', '', True, True, False, len(msg))
except Exception as error:
    printScript(error, '', True, True, False, len(msg))
    sys.exit(1)

# import devices
msg = 'Starting device import '
printScript(msg, '', False, False, True)
try:
    subProc('linuxmuster-import-devices', logfile)
    printScript(' Success!', '', True, True, False, len(msg))
except Exception as error:
    printScript(error, '', True, True, False, len(msg))
    sys.exit(1)

# wait for fw
skipfw = getSetupValue('skipfw')
if skipfw == 'False':
    try:
        waitForFw(wait=30)
    except Exception as error:
        print(error)
        sys.exit(1)

# import subnets
msg = 'Starting subnets import '
printScript(msg, '', False, False, True)
try:
    subProc('linuxmuster-import-subnets', logfile)
    printScript(' Success!', '', True, True, False, len(msg))
except Exception as error:
    printScript(error, '', True, True, False, len(msg))
    sys.exit(1)

# create web proxy sso keytab
msg = 'Creating web proxy sso keytab '
printScript(msg, '', False, False, True)
try:
    subProc(constants.FWSHAREDIR + '/create-keytab.py -v', logfile)
    printScript(' Success!', '', True, True, False, len(msg))
except Exception as error:
    printScript(error, '', True, True, False, len(msg))
    sys.exit(1)

# admin password not more needed in setup.ini
msg = 'Removing admin password from setup.ini '
printScript(msg, '', False, False, True)
setupini = constants.SETUPINI
try:
    setup = configparser.RawConfigParser(
        delimiters=('='), inline_comment_prefixes=('#', ';'))
    setup.read(setupini)
    setup.set('setup', 'adminpw', '')
    with open(setupini, 'w') as INIFILE:
        setup.write(INIFILE)
    printScript(' Success!', '', True, True, False, len(msg))
except:
    printScript(' Failed!', '', True, True, False, len(msg))
    sys.exit(1)
