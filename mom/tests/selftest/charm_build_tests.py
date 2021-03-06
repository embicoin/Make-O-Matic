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
from mom.tests.helpers.MomTestCase import MomTestCase
import os
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface
from core.Settings import Settings
import unittest

class CharmBuildTests( MomTestCase ):
	'''CharmBuildTests executes the example_charm build script with revisions known to work.'''

	ThisFilePath = os.path.realpath( os.path.dirname( __file__ ) )
	BuildScriptName = os.path.join( ThisFilePath, '..', 'buildscripts', 'example_charm.py' )

	def tearDown( self ):
		MomTestCase.tearDown( self )

	def testQueryCharmProjectName( self ):
		buildDirectory = "charm_build"
		if os.path.isdir( buildDirectory ):
			self.fail( "Stale directory exists before the test starts: {0}".format( buildDirectory ) )
		iface = BuildScriptInterface( CharmBuildTests.BuildScriptName )
		projectNameQueryResult = iface.querySetting( Settings.ProjectName )
		self.assertTrue( projectNameQueryResult )
		# FIXME make the base dir queryable, so that we do not rely on a hardcoded name
		# the base directory should *NOT* have been created during the query:
		self.assertTrue( not os.path.isdir( "charm_build" ) )

if __name__ == "__main__":
	unittest.main()
