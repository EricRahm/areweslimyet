#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2012 Mozilla Corporation

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "benchtester")))

execfile(os.path.join(os.path.dirname(sys.argv[0]), "slimtest_config.py"))

# Load
import BenchTester
tester = BenchTester.BenchTester()

# Load modules for tests we have
for test in AreWeSlimYetTests.values():
  if not tester.load_module(test['type']):
    sys.exit(1)

# Parse command line arguments
args = tester.parse_args(sys.argv[1:])
if not args:
  sys.exit(1)

batchnum = int(args.get('batchnum'))
print "BATCHNUM = %d" % batchnum

if not tester.setup({
        'buildname': args['buildname'],
        'binary': args['binary'],
        'buildtime': args['buildtime'],
        'sqlitedb': args['sqlitedb'],
        'logfile': 'logs/%s.test.log' % args['buildname'],
        'gecko_log': 'logs/%s.gecko.log' % args['buildname'],
        'marionette_port': 24242 + batchnum }):
    sys.exit(1)

display = ":%u" % (batchnum + 9,)
# kill this display if its already running for some reason
try:
    subprocess.check_output([ "vncserver", "-kill", display ])
except:
    pass

# Start VNC display
subprocess.check_output([ "vncserver", display ])
os.environ['DISPLAY'] = display

# Run tests
for testname, testinfo in AreWeSlimYetTests.items():
  if not tester.run_test(testname, testinfo['type'], testinfo['vars']):
    sys.stderr.write("SlimTest: Failed at test %s -- Errors: %s -- Warnings: %s\n" % (testname, tester.errors, tester.warnings))
    sys.exit(1)

if len(tester.warnings):
  sys.stderr.write("SlimTest: Generated %u warnings: %s" % (len(tester.warnings), tester.warnings))
if len(tester.errors):
  sys.stderr.write("!! SlimTest: Completed with %u errors: %s" % (len(tester.errors), tester.errors))
  sys.exit(1)

sys.stderr.write("SlimTest: Test run successful")
