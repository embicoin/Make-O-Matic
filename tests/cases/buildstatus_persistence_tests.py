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
from tempfile import NamedTemporaryFile
import os
from tests.helpers.MomTestCase import MomTestCase

class BuildStatusPersistenceTests( MomTestCase ):
	def testPersistBuildInfo( self ):
		status = BuildStatus()
		filename = NamedTemporaryFile( suffix = '.sqlite' ).name
		status.setDatabaseFilename( filename )
		info = BuildInfo()
		info.setProjectName( status.getName() )
		info.setPriority( 0 )
		info.setBuildStatus( BuildInfo.Status.NewRevision )
		info.setBuildType( 'm' )
		info.setRevision( 'abcdef' )
		info.setUrl( '0123456789' )
		info.setBuildScript( 'dummy.py' )
		status.saveBuildInfo( [ info ] )
		revs = status.loadBuildInfo( BuildInfo.Status.NewRevision )
		self.assertTrue( len( revs ) == 1 )
		self.assertEqual( revs[0].__dict__, info.__dict__ )
		os.remove( filename )

if __name__ == "__main__":
	unittest.main()
