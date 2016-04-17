#!/usr/bin/python 

from update_host import DbConnect
from build_attributes import AttribBuild



def setup_host():
    print "test"



def build_chef_atrributes():
    """
    Searches through the inframan database for hosts that have the status of deploy, 
    and builds infrastructure.rb in the attributes section of dhcp_mod cookbook.
    NOTE: if a host does not have its status set to deploy , its system metadata
    will not be added to infrastructure.rb 

    build_json has default paremeters set 
    attributes_dir = /var/chef/cookbooks/dhcp_mod/attributes/
    attributes_file = infrastructure.rb
    template_file = build.rb 
    """
    attrib01 = AttribBuild()
    attrib01.build_json()
    

if __name__ == '__main__':

    build_chef_atrributes()
