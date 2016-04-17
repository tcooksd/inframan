#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
import os
from update_host import DbConnect


class AttribBuild(object):


    attributes_dir="/var/chef/cookbooks/dhcp_mod/attributes/"

    def __init__(self, **kwargs):
        # Capture our current directory
        self.db = kwargs.get('db')


    def chef_attrib_builder(self):
        db1 = DbConnect(db="inframan")
        dbq = ("SELECT c.hostname, a.int1mac, a.pxe_ip, a.perm_ip,"
        "b.template, b.osversion, b.operatingsystem from netinterface a,"
        "templates b, host c where c.status = 'deploy' and a.hostname = c.hostname and b.hostname = c.hostname" )
        return db1.query_db(dbq) 


    def build_json(self, attributes_dir = attributes_dir, attributes_file="infrastructure.rb", template_file="build.rb"):
        """
        produces a file from a template, in a specific location based off 
        database query results . 
        parameters default to the following , but can be modified. 

        attributes_dir = /var/chef/cookbooks/dhcp_mod/attributes/
        attributes_file = infrastructure.rb
        template_file = build.rb
        """
        THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        dbset = self.chef_attrib_builder()
        j2_env = Environment(loader=FileSystemLoader(THIS_DIR + "/templates/"), trim_blocks=True)
        template1 = j2_env.get_template(template_file)
        output_from_parsed =  template1.render(values = dbset)

        with open( attributes_dir + attributes_file, "wb") as fh:
                    fh.write(output_from_parsed)



