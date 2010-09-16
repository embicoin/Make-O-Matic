# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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

from core.Project import Project
from core.Settings import Settings
from core.environments.Environments import Environments
from core.modules.tools.cmake.CMakeBuilder import CMakeBuilder
from core.Configuration import Configuration
from core.modules.testers.CTest import CTest
from core.modules.packagers.CPack import CPack
from core.Build import Build
from tests.helpers.MomTestCase import MomTestCase
import os
import inspect
import sys
import shutil

class MomBuildMockupTestCase( MomTestCase ):
	'''MomTestCase is a base test case class that sets up and tears down the Build object.'''

	def setUp( self ):
		MomTestCase.setUp( self, False )

		myFile = inspect.getfile( inspect.currentframe() )
		myFilePath = os.path.split( myFile )
		myDir = myFilePath[0]
		testMomEnvironments = os.path.join( myDir, 'test-mom-environments' )
		sys.argv = [] # reset command line arguments

		build = Build( None, 'XmlReportTestBuild' )
		project = Project( 'XmlReportTestProject' )
		build.setProject( project )
		project.createScm( 'git:git://github.com/mirkoboehm/Make-O-Matic.git' )
		environments = Environments( [ 'Qt-4.[67].?-Shared-*' ], 'Qt 4', project )

		debug = Configuration( 'Debug', environments, )
		cmakeDebug = CMakeBuilder()
		debug.addPlugin( cmakeDebug )

		release = Configuration( 'Release', environments )
		cmakeRelease = CMakeBuilder()
		release.addPlugin( cmakeRelease )
		release.addPlugin( CTest() )
		release.addPlugin( CPack() )

		build.getSettings().set( Settings.ScriptLogLevel, 3 )
		build.getSettings().set( Settings.EnvironmentsBaseDir, testMomEnvironments )

		self.build = build

	def tearDown( self ):
		MomTestCase.tearDown( self )
		os.chdir( ".." )
		os.chdir( ".." )
		shutil.rmtree( "xmlreporttestbuild" )
