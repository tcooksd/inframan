#!/usr/bin/python 

import os
import sys

import MySQLdb
from MySQLdb.cursors import DictCursor


class DbConnect:
    def __init__(self, **kwargs):
        """
        The db parameter instantiates this class, please see 
        notes for each function. 
        """
        self.db = kwargs['db']
        #Misc global to pass to class if need be . 
        self.misc_global = kwargs.get('val2')
        self.host1 = kwargs.get('host1')
        self.connection = MySQLdb.connect( user="root",
                passwd="usendit1", db=self.db,
                host="localhost", cursorclass=DictCursor,
                use_unicode=True)
        self.tables = ['system' , 'netinterface', 'vlans',
                'templates', 'subtemplate' , 'cookbooks']

    def query_db(self, query11):
        """
        Returns a list of values returned from db query 
        takes arg:
        1. statement of db query. 
        """
        cursor1 = self.connection.cursor()
        cursor1.execute(query11) 
        values1 = cursor1.fetchall()
        cursor1.close()
        return values1 

    def add_host_all(self, host3):
        """
        Takes args hostname from tables list and populates all
        tables with the hostname provided. 
        """
        cursor1 = self.connection.cursor()
        for i in self.tables:
            prestatement = "insert into %s " % i
            statement = ( prestatement + "(hostname) VALUE (%s)" )
            cursor1.execute(statement, host3)
            self.connection.commit()
            #print(cursor1._last_executed)
            #print statement
        cursor1.close()


    def add_host(self, host2, status="no_confs"):
        """
        Adds hostnames:
        Takes args:
        1. hostname ( NOTE: hostnames must be unique ) 
        2. optional: status 
        ( the status of the host (installed, waiting, install))
        defaults to installed:
        """
        #if self.check_host_exist(host2) == "failed":
        #    print "host already exists"
        #else:
        if self.check_host_exist(host2) == "fail":
            print "host already exists"
        else:
            statement = ("insert into host" 
                    "(hostname, status)"
                    "VALUES (%s, %s)" )
            datadd = (host2, status) 
            cursor3 = self.connection.cursor()
            cursor3.execute(statement, datadd) 
            self.connection.commit()
            self.add_host_all(host2) 
            cursor3.close()

    def update_host(self, hostn, orighost, status="installed"): 
        """
        Updates hostname from old to new:
        Takes args:
        1. mew hostname 
        2. old hostname 
        3. optiomal: status 
        ( the status of the host (installed, waiting, install)) 
        defaults to installed:
        """
        statement = ("update host set host.hostname=%s,"
                "host.status=%s where host.hostname=%s") 
        statement_values = (hostn, status, orighost) 
        cursor2 = self.connection.cursor()
        cursor2.execute(statement, statement_values)
        self.connection.commit()
        #uncomment the following to debug statements. 
        #print(cursor2._last_executed)
        cursor2.close()


    def add_host_interface(self, hostname, **kwargs): 
        """
        Updates host netowrk interfaces with mac address assignments:
        Takes args:
        1. hostname 
        2. in1mac=
        3. in1mac=
        4. in1mac=
        5. in1mac=
        5. pxe_ip= ( tmp pxe ip 10.177.75.x ) 
        5. perm_ip= ( must be available from vlans piped in ) 
        """
        self.int1mac1 = kwargs.get('int1mac')
        self.int2mac1 = kwargs.get('int2mac')
        self.int3mac1 = kwargs.get('int3mac')
        self.int4mac1 = kwargs.get('int4mac')
        self.pxe_ip1 = kwargs.get('pxe_ip')
        self.perm_ip1 = kwargs.get('perm_ip')

        statement = ("update netinterface set int1mac=%s,"
        "int2mac=%s, int3mac=%s, int4mac=%s, pxe_ip=%s,"
        "perm_ip=%s where hostname = %s") 

        statement_values = (self.int1mac1, self.int2mac1,
                self.int3mac1, self.int4mac1, self.pxe_ip1,
                self.perm_ip1, hostname )

        cursor = self.connection.cursor()
        cursor.execute(statement, statement_values) 
        self.connection.commit()
        cursor.close()
        self.update_host( hostname, hostname, status="waiting") 

    def add_vlans(self, hostname, **kwargs):
        for key, value in kwargs.iteritems():
            print "%s = %s" % (key, value)

    def add_system_info(self, hostname, **kwargs):
        """
        Updates host system specs:
        Takes args:
        1. hostname 
        2. cpu=
        3. memory=
        4. disk1=
        5. disk2=
        6. disk4=
        7. physlocation=  ( aws / SV2 ) 
        8. host_type=   ( physical / virtual[openstack/kvm/aws/kvm] / docker ) 
        """
        self.cpu = kwargs.get('cpu') 
        self.memory = kwargs.get('memory') 
        self.disk1 = kwargs.get('disk1') 
        self.disk2 = kwargs.get('disk2') 
        self.disk3 = kwargs.get('disk3') 
        self.physlocation = kwargs.get('physlocation') 
        self.host_type = kwargs.get('host_type') 

        statement = ("update system set cpu=%s, memory=%s, disk1=%s,"
        " disk2=%s, disk3=%s, physlocation=%s, host_type=%s where hostname"
        "=%s") 

        statement_values = ( self.cpu, self.memory, self.disk1, self.disk2,
                self.disk3, self.physlocation, self.host_type, hostname) 


        cursor = self.connection.cursor()
        cursor.execute(statement, statement_values) 
        self.connection.commit()
        #print(cursor._last_executed)
        cursor.close()
        self.update_host( hostname, hostname, status="waiting") 


    def add_updates(self, hostname):
        """
        Needs to be updated, currently no way of tracking db updates until this is 
        functioning.
        """
        print hostname

    def add_ks_templates(self, hostname, **kwargs):
        """
        Updates host kickstart template:
        Takes args:
        1. hostname 
        2. os = ( Centos / Ubuntu) 
        3. osv = ( main version of os eg.. cent7, ubuntu14 ) 
        4. disk = ( disk params kickstart will install to ) 
        5. template = ( kickstart template to build kickstart with ) 
        5. subtemp = ( subtemplate to append to kickstart config ) 
        """
        self.operating_system = kwargs.get('os') 
        self.os_version = kwargs.get('osv')
        self.disk = kwargs.get('disk') 
        self.subtemplate = kwargs.get('subtemp') 
        self.template = kwargs.get('template') 

        statement = ("update templates set operatingsystem=%s, osversion=%s,"
        "disk=%s, subtemplate=%s, template=%s where hostname = %s") 


        statement_values = ( self.operating_system, self.os_version, self.disk, 
                self.subtemplate, self.template, hostname) 


        cursor = self.connection.cursor()
        cursor.execute(statement, statement_values) 
        self.connection.commit()
        print(cursor._last_executed)
        self.update_host( hostname, hostname, status="deploy") 
        cursor.close()


    def add_ks_sub_template(self, hostname, template, subtemplate):
        """
        Place holder for future, no need to modify at this moment add_ks_template is doing 
        all the lifting here for now. 
        """
        print subtemplate 


    def check_host_exist(self, hostname):
        db_query = "select * from host"
        if self.query_db(db_query)[0]['hostname'] == hostname:
            return "fail"


