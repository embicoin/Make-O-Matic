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
from buildcontrol.common.BuildStatus import BuildStatus
from buildcontrol.common.BuildInfo import BuildInfo
from test.test_iterlen import len
import tempfile
import os

class BuildStatusPersistenceTests( unittest.TestCase ):
	def getTemporaryDatabaseFilename( self ):
		return tempfile.mkstemp( '.sqlite', '_{0}'.format( self.__class__.__name__ ) )

	def testPersistBuildInfo( self ):
		bs = BuildStatus()
		filename = self.getTemporaryDatabaseFilename()[1]
		bs.setDatabaseFilename( filename )
		bi = BuildInfo()
		bi.setProjectName( bs.getName() )
		bi.setPriority( 0 )
		bi.setBuildStatus( BuildInfo.Status.NewRevision )
		bi.setBuildType( 'm' )
		bi.setRevision( 'abcdef' )
		bi.setUrl( '0123456789' )
		bi.setBuildScript( 'dummy.py' )
		bs.saveBuildInfo( [ bi ] )
		revs = bs.loadBuildInfo( BuildInfo.Status.NewRevision )
		self.assertTrue( len( revs ) == 1 )
		self.assertEqual( revs[0].__dict__, bi.__dict__ )
		os.remove( filename )

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
