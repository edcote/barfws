#!/usr/bin/env python

import os
import shutil
import logging

class WSGen(object):
    def __init__(self,args):
        """ Creates object of type WSGen """
        self.args = args

    def gen_path(self,path):
        """ Creates specified directory in file system """
        logging.info('Creating directory '+path)
        os.makedirs(path)

    def gen_comp_yml(self,path,name,files='',requires='',options=''):
        """ Make template BARF script """
        f = open(path+'/comp.yml','w')

        barf = '''\
name: comp_{name}
files: [{files}]
options: [{options}]
requires: [{requires}]
'''.format(name=name,files=files,requires=requires,options=options)
        f.write(barf)
        f.close()

    def gen_top_v(self,path,name):
        """ Make template top """
        f = open('{}/{}.v'.format(path,name),'w')
        top = """\
module {name} (
    input clk,
    input rst_n
);

endmodule
""".format(name=name)
        f.write(top)
        f.close()

    def gen_tb_sv(self,path,name):
        """ Make TB template """
        f = open('{}/{}_tb.sv'.format(path,name),'w')
        tb_top = """\
module {name}_tb;
// ----------------------------------------------------------------------------
// Clock generator
// ----------------------------------------------------------------------------
bit clk = 0;
initial
    forever #5 clk = !clk;

// ----------------------------------------------------------------------------
// Reset generator
// ----------------------------------------------------------------------------
bit rst = 0;
wire rst_n = !rst;

initial begin
    @(negedge clk);
    rst = 1;
    @(negedge clk);
    rst = 0;
end

// ----------------------------------------------------------------------------
// DUT
// ----------------------------------------------------------------------------

{name} u_{name} (.*);

endmodule : {name}_tb
""".format(name=name)
        f.write(tb_top)
        f.close()

    def gen_env_pkg_sv(self,path,name):
        """ Generates environment package template """
        f = open('{}/{}_env_pkg.sv'.format(path,name),'w')
        tb_top = """\
package {name}_tb_pkg;
endpackage : {name}_tb_pkg
""".format(name=name)
        f.write(tb_top)
        f.close()

    def make_core(self,ws_path,name):
        base_path = ws_path+'/cores/'+name+'/'

        # make directory for RTL design
        path = base_path+'rtl/'
        self.gen_path(path)
        self.gen_top_v(path,name)
        self.gen_comp_yml(path,name,name+'.v') 

        # make directory for environment component
        path = base_path+'sim/env/'
        self.gen_path(path)
        self.gen_env_pkg_sv(path,name)
        self.gen_comp_yml(path,name+'_env',name+'_env_pkg.sv','comp_uvm')

        # make directory for simulation TB
        path = base_path+'sim/tb/'
        self.gen_path(path)
        self.gen_tb_sv(path,name)
        self.gen_comp_yml(path,name+'_tb',name+'_tb.sv',
                          "comp_uvm,comp_{0},comp_{0}_env".format(name))

        # directory for design synthesis
        path = base_path+'syn/'
        self.gen_path(path)

    def execute(self):
        """ Generates workspace """
        ws_path = self.args.root+'/'+self.args.name

        # Remove directory, if enabled
        if self.args.purge and os.path.isdir(ws_path):
            logging.info('Removing directory ' + ws_path)
            shutil.rmtree(ws_path)

        # Create tmp directory
        os.makedirs(ws_path+'/tmp')

        # Make base directories
        self.gen_path(ws_path+'/cores')
        self.gen_path(ws_path+'/libs')

        # Generate template for each core
        for c in args.cores:
            self.make_core(ws_path,c)

        # Generate template for UVM library component
        path = ws_path+'/libs/uvm'
        self.gen_path(path)
        self.gen_comp_yml(path,'uvm','"${UVM_HOME}/uvm_pkg.sv"',
                          options='"+incdir+${UVM_HOME}"')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Workspace Generator 1.0')
    parser.add_argument('-n','--name',
                        help='Name of workspace',required=True)
    parser.add_argument('-c','--cores', nargs='+',
                        help='List of cores')
    parser.add_argument('-r','--root',
                        help='Root directory to create workspace',required=True)
    parser.add_argument('-p','--purge',
                        help='Purge previous workspace, if exists',action='store_true')
    parser.add_argument('-v','--verbose',
                        help='Verbose output',action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    wsgen = WSGen(args)
    wsgen.execute()
