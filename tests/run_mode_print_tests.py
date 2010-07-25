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
from core.Project import Project
from core.Settings import Settings

class RunModePrintTests( unittest.TestCase ):

	def testPrintRevisionsSince( self ):
		revision = '57307ee83930c089d0eb9b4e7342c87784257071'
		result = self._getRevisions( revision, 1 )
		self.assertEqual( len( result ), 1, 'The test asked for only one revision to be listed.' )
		line = result[0]
		expected = '795a9394bf3e4f7c46a88c81446cc691a662ec9b'
		self.assertEqual( line[1], expected,
			'The next revision after {0} should be {1}'.format( revision, expected ) )
		self.assertEqual( line[0].lower(), 'c', 'Revision {0} should be a C type build!'.format( expected ) )

	def testPrintAllRevisionsSince( self ):
		result = self._getRevisions( '57307ee83930c089d0eb9b4e7342c87784257071' )
		self.assertTrue( len( result ) > 1, 'The test asked for only one revision to be listed.' )

	def testPrintCurrentRevision( self ):
		project = Project( 'ScmFactoryTest' )
		project.getSettings().set( Settings.ScriptLogLevel, 3 )
		project.createScm( 'git:git@gitorious.org:make-o-matic/mom.git' )
		result = project.getScm()._getCurrentRevision( project )
		self.assertTrue( result, 'The current revision cannot be None.' )

	def _getRevisions( self, revision, count = None ):
		project = Project( 'ScmFactoryTest' )
		project.getSettings().set( Settings.ScriptLogLevel, 3 )
		project.createScm( 'git:git@gitorious.org:make-o-matic/mom.git' )
		if count:
			result = project.getScm()._getRevisionsSince( project, revision, count )
		else:
			result = project.getScm()._getRevisionsSince( project, revision )
		return result

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()