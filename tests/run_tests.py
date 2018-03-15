
from __future__ import print_function

import os, sys, unittest, importlib
sys.path.insert(0,".")
# for dev - sucks
sys.path.insert(0,"..")

modules = [
    "test_general_geometry",
    "test_positioners"
]

HERE = os.getcwd()
print( "HERE",HERE )

for M in modules:
    os.chdir(HERE)
    print("="*80)
    print("Running suite for ",M)
    if M.find(".")>-1:
        path = M.split(".")
        for direc in path[:-1]:
            os.chdir( direc )
        M = path[-1]
    MOD = importlib.import_module(M)
    mySuite = unittest.loader.findTestCases( MOD )
    runner = unittest.TextTestRunner()
    try:
        runner.run(mySuite)
    except:
        raise
