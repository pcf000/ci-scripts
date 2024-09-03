import os
import jenkins

# Common server connection support.

servers = [{'host' : 'http://ml-ci.amd.com:21096',
            'passwordfile' : '.jenkins.ml-ci',
            'builds' : [('MLIR/check-mlir-nightly-all', 'non-xdlops nightly'),
                        ('MLIR/mlir-weekly', 'non-xdlops weekly')]},
           {'host' : 'http://ml-ci-internal.amd.com:8080',
            'passwordfile' : '.jenkins.ml-ci-internal',
            'builds' : [('mlir/mlir-nightly-all', 'xdlops nightly'),
                        ('mlir/mlir-weekly', 'xdlops weekly')]}
]

def init_servers(servers):
    for server in servers:
        with open(os.path.expanduser(f"~/{server['passwordfile']}")) as f:
            user,password = f.readlines()[0].rstrip().split(':')
            server['connection'] = jenkins.Jenkins(server['host'], timeout=60,
                                                   username=user,
                                                   password=password)
    return servers
