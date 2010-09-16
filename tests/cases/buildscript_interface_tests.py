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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface
from tests.helpers.MomTestCase import MomTestCase
import os
from core.Settings import Settings
import unittest
from core.helpers.GlobalMApp import mApp
import shutil
import sys

class BuildScriptInterfaceTests( MomTestCase ):

	BuildScriptName = os.path.abspath( os.path.join( sys.path[0], 'buildscripts', 'example_mom_buildscript.py' ) )

	def setUp( self ):
		MomTestCase.setUp( self )
		self.iface = BuildScriptInterface( BuildScriptInterfaceTests.BuildScriptName )

	def tearDown( self ):
		MomTestCase.tearDown( self )
		shutil.rmtree( "makeomatic" )

	def testQuerySetting( self ):
		variable = self.iface.querySetting( Settings.MomVersionNumber )
		self.assertEquals( variable, mApp().getSettings().get( Settings.MomVersionNumber ) )

	def testPrintCurrentRevision( self ):
		variable = self.iface.queryCurrentRevision()
		self.assertTrue( variable )

	def testPrintRevisionsSince( self ):
		revisions = self.iface.queryRevisionsSince( '8c758c1f1de2bcc19bda516f1acadf869ba28ee4' )
		self.assertTrue( len( revisions ) >= 5 )


if __name__ == "__main__":
	unittest.main()
