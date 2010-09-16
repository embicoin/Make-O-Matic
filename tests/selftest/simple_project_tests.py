# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# 
# make-o-matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# make-o-matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
import sys
from core.Settings import Settings
from core.helpers.RunCommand import RunCommand
from core.helpers.GlobalMApp import mApp
from tests.helpers.MomTestCase import MomTestCase
import shutil
import glob

class SimpleProjectTests( MomTestCase ):
	'''SimpleProjectTests runs the example_mom_builscript in the three major run modes.
	It assumes that it is executed in the tests/ sub-directory of the mom repository.'''

	BuildScriptName = os.path.abspath( os.path.join( sys.path[0], 'buildscripts', 'example_mom_buildscript.py' ) )

	def tearDown( self ):
		MomTestCase.tearDown( self )
		removeDirectories = glob.glob( "makeomatic*" )
		for directory in removeDirectories:
			shutil.rmtree( directory )

	def querySetting( self, name ):
		cmd = [ sys.executable, SimpleProjectTests.BuildScriptName, 'query', name ]
		runner = RunCommand( cmd )
		runner.run()
		return runner

	def testUsageHelp( self ):
		cmd = [ sys.executable, SimpleProjectTests.BuildScriptName, '-h' ]
		runner = self.runCommand( cmd, 'build script usage help' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testQueryProjectName( self ):
		runner = self.querySetting( Settings.ProjectName )
		self.assertEquals( runner.getReturnCode(), 0 )
		line = runner.getStdOut().decode().strip()
		self.assertEquals( line, 'project.name: MakeOMatic' )

	def testQueryMomVersion( self ):
		runner = self.querySetting( Settings.MomVersionNumber )
		self.assertEquals( runner.getReturnCode(), 0 )
		line = runner.getStdOut().decode().strip()
		expectedVersion = mApp().getSettings().get( Settings.MomVersionNumber )
		self.assertEquals( line, '{0}: {1}'.format( Settings.MomVersionNumber, expectedVersion ) )

	def testPrintCurrentRevision( self ):
		cmd = [ sys.executable, SimpleProjectTests.BuildScriptName, 'print', 'current-revision' ]
		runner = RunCommand( cmd )
		runner.run()
		self.assertEquals( runner.getReturnCode(), 0 )
		line = runner.getStdOut().decode().strip()
		# we cannot know what the current revision is, but if the return code is not zero, it should not be empty:
		self.assertTrue( line )

	def runTestBuild( self, buildType ):
		cmd = [ sys.executable, SimpleProjectTests.BuildScriptName, '-v', '-t', buildType ]
		self.runCommand( cmd, "Make-O-Matic buildscript: build type {0}".format( buildType ) )

	def testEBuild( self ):
		self.runTestBuild( 'E' )

	def testMBuild( self ):
		self.runTestBuild( 'M' )

	def testCBuild( self ):
		self.runTestBuild( 'C' )

	def testDBuild( self ):
		self.runTestBuild( 'D' )

	def testSBuild( self ):
		self.runTestBuild( 'S' )

	def testHBuild( self ):
		self.runTestBuild( 'H' )

	def testPBuild( self ):
		self.runTestBuild( 'P' )

	def testFBuild( self ):
		self.runTestBuild( 'F' )

if __name__ == "__main__":
	unittest.main()
