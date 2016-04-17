#!/usr/bin/python 

"""
Query UCS for systems data and then import into a mysql database. 
Usage:
    get_ucs_macs.py --host=<host> --user=<user> --pass=<pass> --print=<yes|no> --mysql_host=<mysql_host> --mysql_login=<mysql_login> --mysql_pass=<mysql_pass>
Options:
    --host=<host>               IP Address of the UCS VIP
    --user=<user>               Username for UCS
    --pass=<pass>               Password for UCS
    --print=<print>             Print information from UCS
    --mysql_host=<mysql_host>   Mysql server to parse   
    --mysql_login=<mysql_login> Mysql login 
    --mysql_pass=<mysql_pass>   Mysql pass 
    --version                   Script version
"""

from UcsSdk import *
from UcsSdk.MoMeta.OrgOrg import OrgOrg
from UcsSdk.MoMeta.LsServer import LsServer
from UcsSdk.MoMeta.VnicEther import VnicEther
from docopt import docopt
from collections import defaultdict
import datetime
import MySQLdb as mysql


args = docopt(__doc__, version='{} 1.0'.format(__file__))
hostname = args['--host']
username = args['--user']
password = args['--pass']
print1 = args['--print']
mysql_host = args['--mysql_host']  
mysql_login = args['--mysql_login']  
mysql_pass = args['--mysql_pass']  

""" 
Use this and comment out the latter if on mac. 
""" 
# Mysql server connection, currently using tcookdev's mysql db for testing . 
# tcookdev_db = mysql.connector.connect(user='infra', password='inframgmt',
#                              host='10.10.42.16',
#                              database='infra')


tcookdev_db = mysql.connect(mysql_host, mysql_login, mysql_pass, 'infra')
date1 = datetime.datetime.now()

"""
The mysql schema for systems database. 
"""
add_host = ("INSERT INTO systems "
               "(id, mac1, mac2, mac3, ucs_blade_name, hostname, pxe_ip, perm_ip, ks_template, type, status, location, blade, last_updated, os_version) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

update_host = ("UPDATE systems SET systems.ucs_blade_name=%s, systems.last_updated=%s where systems.mac1=%s") 


def update_mysql(values, print1="NULL"):
    """ 
    Update hosts names when changed on UCS, this is done by comparing the first mac address to the hostname currently residing on the 
    Data base. 
    """ 
    hostname1 = values[0]
    mac_address = values[1][0]
    cursor = tcookdev_db.cursor()
    data_host = ( hostname1, date1, mac_address )
    cursor.execute(update_host, data_host)
    tcookdev_db.commit()
    cursor.close()
     

def add_to_mysql(values, print1="NULL"):
    """ 
    Takes values list containing list [hostname [mac,mac,mac]]
    Updates mysql with systems database from values list array . 
    """ 
    data_host = ""
    hostname1 = values[0]
    mac_address = values[1]
    if print1 == "yes":
        print  hostname1 +  "**" + values[1][0]
    """ Assign mac/s based on the number of the nics provided. 
     Values are submitted in the following format [ hostname [mac1 , mac2, mac3]] .
     Values[0] = hostname  values[0][0-3] = mac addresses . 

     We run this over 3 itterations because some servers have 1 nic some have 2 and others have 3 , 
     want to always make sure we have all the macs available from each server.  
    """
    if len(values[1]) == 1:
        macaddr1 = mac_address[0]
        macaddr2 = ""
   	data_host = ( "", macaddr1, "",  "", hostname1, "", "", "", "centos5", "UCS2", "", "", "", date1, "5" )
    elif len(values[1]) == 2:
        macaddr1 = mac_address[0]
        macaddr2 = mac_address[1]
   	data_host = ( "", macaddr2, macaddr1, "", hostname1, "", "", "", "centos5", "UCS2", "", "", "", date1, "5" )
    else: 
        macaddr1 = mac_address[0]
        macaddr2 = mac_address[1]
        macaddr3 = mac_address[2]
   	data_host = ( "", macaddr2, macaddr1, macaddr3, hostname1, "", "", "", "centos5", "UCS2", "", "", "", date1, "5" )
     
    cursor = tcookdev_db.cursor()
    cursor.execute(add_host, data_host)
    tcookdev_db.commit()
    cursor.close()


def query_mysql(values):
    """ 
    Query mysql for mac address provided by UCS query.
    Returns mac address if matched and skipped.
    """
    ucs_host = values[0] 
    ucs_mac1 = values[1][0]
    #if print1 == "yes":
        #print  ucs_host +  "**" + ucs_mac1 
    cursor = tcookdev_db.cursor()
    #query = """SELECT * FROM systems where mac1 = '%s';""" 
    query = """SELECT * FROM systems where ucs_blade_name = '%s';""" 
    query = query % ( ucs_host ) 
    cursor.execute(query) 
    row = cursor.fetchone()
    while row is not None:
       return row[1]
       row = cursor.fetchone()
    tcookdev_db.commit()
    cursor.close()

def query_mysql_hostname_update(values):
    """ 
    Check to see if the hostname that was previously associated with the first mac address 
    has changed, if so then update to the new hostname. 
    """ 
    ucs_host = values[0] 
    ucs_mac1 = values[1][0]
    cursor = tcookdev_db.cursor()
    query = """SELECT * FROM systems where mac1 = '%s' and not ucs_blade_name = '%s';""" 
    query = query % ( ucs_mac1, ucs_host ) 
    cursor.execute(query) 
    row = cursor.fetchone()
    while row is not None:
       return row[1]
       row = cursor.fetchone()
    tcookdev_db.commit()
    cursor.close()

def get_macs(handle=None):
    """
    Grab all the SP instances and return their macs
    """
    macs = defaultdict(dict)
    orgObj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : "org-root"})[0]
    servers = handle.GetManagedObject(orgObj, LsServer.ClassId())
    for server in servers:
        if server.Type == 'instance':
            childs = handle.ConfigResolveChildren(VnicEther.ClassId(), server.Dn, None, YesOrNo.TRUE)
            macs[server.Name]
            for child in childs.OutConfigs.GetChild():
                macs[server.Name][child.Name] = child.Addr
    return macs

if __name__ == '__main__':

    try:
        # Connect and login to the UCS 
        handle = UcsHandle()
        handle.Login(hostname, username, password)
        """ 
 	Submit query for ethernet information of assigned blades in UCS
 	Returns a dictionary of metadata key value pairs from UCS. 
        """ 
        macs = get_macs(handle=handle)
        values01 = []
        for host, interfaces in macs.iteritems():
	    values01 = [ host, interfaces.values() ]
	    if query_mysql(values01) != None:
                #print "the following mac address is a duplicate" + " " +  query_mysql(values01) + ": not udpating" 
                continue
            else: 
	        add_to_mysql(values01, print1)

	    if query_mysql_hostname_update(values01) != None:
                #update_mysql(values01, print1)
                print "skipped adding the second time"

                
	handle.Logout()
    except Exception, err:
        print 'Exception: {}'.format(str(err))
        import traceback, sys
        print '-' * 60
        traceback.print_exc(file=sys.stdout)
        print '-' * 60

