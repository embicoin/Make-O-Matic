#!/usr/bin/env python

# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# 
# Make-O-Matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Make-O-Matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from tests.cases.preprocessor_tests import PreprocessorTest
from tests.cases.environment_saver_tests import EnvironmentSaverTest
from tests.cases.buildstatus_persistence_tests import BuildStatusPersistenceTests
from tests.cases.path_resolver_tests import PathResolverTest
from tests.cases.run_mode_print_tests import RunModePrintTests
from tests.cases.run_timeout_tests import RunWithTimeoutTest
from tests.cases.scm_factory_tests import ScmFactoryTests
from tests.cases.buildscript_interface_tests import BuildScriptInterfaceTests
from tests.cases.build_environment_tests import BuildEnvironmentTests
from tests.selftest.simple_project_tests import SimpleProjectTests
from tests.selftest.simple_ci_tests import SimpleCITests
from tests.selftest.charm_build_tests import CharmBuildTests
from tests.cases.xml_report_tests import XmlReportTests
from tests.cases.scm_modules_tests import ScmModulesTests
from tests.cases.email_reporter_tests import EmailReporterTest
from tests.cases.run_mode_describe_tests import RunModeDescribeTests
#from tests.cases.emailer_tests import EmailerTest
from tests.cases.settings_tests import SettingsTests
from tests.selftest.environment_setup_tests import EnvironmentSetupTests
import sys

CLASSES = [
	# self tests first
	CharmBuildTests,
	EnvironmentSetupTests,
	SimpleProjectTests,
	SimpleCITests,

	# others
	BuildEnvironmentTests,
	BuildScriptInterfaceTests,
	BuildStatusPersistenceTests,
#	EmailerTest,
	EmailReporterTest,
	EnvironmentSaverTest,
	PathResolverTest,
	PreprocessorTest,
	RunModePrintTests,
	RunModeDescribeTests,
	RunWithTimeoutTest,
	ScmFactoryTests,
	ScmModulesTests,
	XmlReportTests,
	SettingsTests
]

def main():
	suite = unittest.TestSuite( map( unittest.TestLoader().loadTestsFromTestCase, CLASSES ) )
	result = unittest.TextTestRunner( verbosity = 2 ).run( suite )
	sys.stderr.flush()
	sys.stdout.flush()
	if result.wasSuccessful():
		print( 'Tests completed successfully.' )
		sys.exit( 0 )
	else:
		print( 'Tests failed.' )
		sys.exit( 1 )

if __name__ == "__main__":
	main()
