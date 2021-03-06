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

from mom.tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
import unittest

class RunModePrintTests( MomBuildMockupTestCase ):

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useScm = True )

	def testPrintRevisionsSince( self ):
		revision = '57307ee83930c089d0eb9b4e7342c87784257071'
		result = self._getRevisions( revision, 1 )
		self.assertEqual( len( result ), 1, 'The test asked for only one revision to be listed.' )
		expected = '795a9394bf3e4f7c46a88c81446cc691a662ec9b'
		info = result[0]
		self.assertEqual( info.getRevision(), expected,
			'The next revision after {0} should be {1}'.format( revision, expected ) )
		self.assertEqual( info.getBuildType().lower(), 'c', 'Revision {0} should be a C type build!'.format( expected ) )

	def testPrintAllRevisionsSince( self ):
		result = self._getRevisions( '57307ee83930c089d0eb9b4e7342c87784257071' )
		self.assertTrue( len( result ) > 1, 'The test asked for only one revision to be listed.' )

	def testPrintCurrentRevision( self ):
		result = self.project.getScm()._getCurrentRevision()
		self.assertTrue( result, 'The current revision cannot be None.' )

	def _getRevisions( self, revision, count = None ):
		if count:
			result = self.project.getScm()._getRevisionsSince( revision, count )
		else:
			result = self.project.getScm()._getRevisionsSince( revision )
		return result

if __name__ == "__main__":
	unittest.main()
