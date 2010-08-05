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

from core.Exceptions import AbstractMethodCalledError, MomError
from core.helpers.TypeCheckers import check_for_nonempty_string, check_for_path
from core.Plugin import Plugin
from core.helpers.GlobalMApp import mApp

class SourceCodeProvider( Plugin ):

	def __init__( self, name = None ):
		"""Constructor"""
		Plugin.__init__( self, name )
		self.__url = None
		self.__revision = None
		self.__committer = None
		self.__commitTime = None
		self.__commitMessage = None
		self.__srcDir = None
		self.__description = None

	def getIdentifier( self ):
		raise AbstractMethodCalledError

	def setUrl( self, url ):
		self.__url = url

	def getUrl( self ):
		return self.__url

	def setSrcDir( self, dir ):
		check_for_path( dir, 'The course folder needs to be a non-empty string!' )
		self.__srcDir = dir

	def getSrcDir( self ):
		return self.__srcDir

	def getDescription( self ):
		return self.__description

	def _setDescription( self, description ):
		check_for_nonempty_string( description, "The SCM description needs to be a non-empty string." )
		self.__description = description

	def setRevision( self, revision ):
		self.__revision = revision

	def getRevision( self ):
		return self.__revision

	def getCommitter( self ):
		if not self.__committer:
			self._getRevisionInfo()
		return self.__committer

	def getCommitTime( self ):
		if not self.__commitTime:
			self._getRevisionInfo()
		return self.__commitTime

	def getCommitMessage( self ):
		if not self.__commitMessage:
			self._getRevisionInfo()
		return self.__commitMessage

	def _getRevisionInfo( self ):
		"""Set __committer, __commitMessage, __commitTime and __revision"""
		raise AbstractMethodCalledError

	def _checkInstallation( self, instructions ):
		"""Check if this SCM can be used. Should check, for example, if the SCM is actually installed."""
		raise AbstractMethodCalledError

	def printRevisionsSince( self, options ):
		"""Print revisions committed since the specified revision."""
		if not options:
			raise MomError( 'No revision specified to start with!' )
		if len( options ) > 2:
			raise MomError( 'Error, extra options. Specify revision and optionally the maximum number of revisions to print.' )
		revision = options[0]
		cap = None
		if len( options ) == 2:
			cap = int( options[1] )

		revisions = self._getRevisionsSince( revision, cap )
		lines = []
		for revision in revisions:
			line = '{0} {1} {2}:{3}'.format( revision[0], revision[1], self.getIdentifier(), revision[2] )
			lines.append( line )
		return '\n'.join( lines )

	def _getRevisionsSince( self, revision, cap = None ):
		"""Return revisions committed since the specified revision."""
		raise AbstractMethodCalledError

	def printCurrentRevision( self, options ):
		"""Print current (most recent) revision."""
		if options:
			raise MomError( 'print current-revision does not understand any extra options!' )
		revision = self._getCurrentRevision()
		return revision

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		raise AbstractMethodCalledError

	def makeCheckoutStep( self, instructions ):
		"""Create steps to check out the source code"""
		raise AbstractMethodCalledError()

	def makeExportStep( self, instructions, targetDir ):
		"""Create a Step that will export the source code to the target directory."""
		raise AbstractMethodCalledError()

	def makePackageStep( self, instructions, ):
		"""Create a src archive of the project and put it into the packages directory."""
		raise AbstractMethodCalledError()

	def preFlightCheck( self, instructions ):
		"""Overload"""
		self._checkInstallation( instructions )
		mApp().debug( self, 'SCM module initialized: {0}'.format( self.getDescription() ) )

	def setup( self, instructions ):
		"""Setup is called after the build steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeCheckoutStep( instructions )
		self.makePackageStep( instructions )
		# FIXME it needs to be decided by the builder if this gets called!
		# self.makeExportStep( project )

	def wrapUp( self, instructions ):
		"""WrapUp is called when the last step has finished. It could be used to publish 
		the reports, for example."""
		pass

	def shutDown( self, instructions ):
		"""Shutdown is called right before the build ends. It could be used to close
		files or network connections.
		ShutDown is called from the finally block of the build method, so in all normal cases, it will be called 
		before the build script ends."""
		pass
