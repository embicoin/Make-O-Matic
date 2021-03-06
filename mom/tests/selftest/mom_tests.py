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

from buildcontrol.mom.MomParameters import MomParameters
from buildcontrol.mom.Remotebuilder import RemoteBuilder
from mom.tests.helpers.MomTestCase import MomTestCase
import os
import sys
import unittest

class MomTests( MomTestCase ):
	'''MomTests tests the mom remote runner tool.'''

	def testParseParameters( self ):
		'''Verify that the parser passes the correct subset of arguments to the remote build script.'''
		buildscriptArgs = [ '-vv', '-t', 'H', '-r', '4711' ]
		momArgs = [ sys.argv[0], '-vv', '-u', 'git://github.com/KDAB/Make-O-Matic.git',
			'-p', 'mom/buildscript.py', '-r', '4711', '-' ]
		args = momArgs + buildscriptArgs
		params = MomParameters()
		params.parse( args )
		self.assertEqual( buildscriptArgs, params.getBuildScriptOptions() )

	def testFetchRemoteBuildscript( self ):
		name = 'buildscript.py'
		path = 'admin'
		location = 'git://github.com/KDAB/Make-O-Matic.git'
		remote = RemoteBuilder( 'HEAD', location = location, path = path, script = name )

		# run
		path, temps = remote.fetchBuildScript()
		self.assertTrue( os.path.exists( path ) )
		del temps

	def testExecuteRemoteHBuild( self ):
		name = 'buildscript.py'
		path = 'admin'
		location = 'git:git://github.com/KDAB/Make-O-Matic.git'
		remote = RemoteBuilder( 'HEAD', location = location, path = path, script = name )

		# run
		remote.invokeBuild( args = [ '-vv', '-t', 'H', '-s', 'disable-test,disable-create-docs'] )

if __name__ == "__main__":
	unittest.main()
