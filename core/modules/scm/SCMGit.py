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
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.Exceptions import AbstractMethodCalledError, ConfigurationError, MomError
from core.helpers.RunCommand import RunCommand
from core.executomat.ShellCommandAction import ShellCommandAction
from core.executomat.Action import Action
import os
from core.helpers.FilesystemAccess import make_foldername_from_string
import re
from core.helpers.GlobalMApp import mApp

class _UpdateHiddenCloneAction( Action ):
	def __init__( self, scmgit ):
		Action.__init__( self )
		assert scmgit
		self.__scmgit = scmgit

	def run( self ):
		self.__scmgit._updateHiddenClone()
		return 0

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return self.getName()

class SCMGit( SourceCodeProvider ):
	"""Git SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )
		# FIXME platformdefs for home
		self.__cloneArmy = os.environ['HOME'] + os.sep + '.cloneArmy'

	def getIdentifier( self ):
		return 'git'

	def getCloneArmyDir( self ):
		return self.__cloneArmy

	def _getRevisionInfo( self ):
		"""Set __committer, __commitMessage, __commitTime and __revision"""
		raise AbstractMethodCalledError

	def _checkInstallation( self ):
		"""Check if this SCM can be used. Should check, for example, if the SCM is actually installed."""
		runner = RunCommand( 'git --version' )
		runner.run()
		if runner.getReturnCode() != 0:
			raise ConfigurationError( "SCMGit::checkInstallation: git not found." )
		else:
			lines = runner.getStdOut().decode().split( '\n' )
			self._setDescription( lines[0].rstrip() )
			mApp().debugN( self, 4, 'git found: "{0}"'.format( self.getDescription() ) )

	def _getRevisionsSince( self, revision, cap = None ):
		"""Print revisions committed since the specified revision."""
		self._updateHiddenClone()
		runner = RunCommand( 'git log {1}..'.format( cap or '', revision ), 3600 )
		runner.setWorkingDir( self._getHiddenClonePath() )
		runner.run()

		if runner.getReturnCode() == 0:
			output = runner.getStdOut().decode()
			revisions = []
			lines = output.split( '\n' )
			for line in lines:
				if re.match( '^commit.+', line ):
					parts = line.split( ' ' )
					hash = parts[1].strip()
					if hash == revision:
						break
					else:
						data = ( 'C', hash, self.getUrl() )
						revisions.append( data )
			if cap:
				return revisions[-cap:]
			else:
				return revisions
		elif runner.getTimedOut() == True:
			raise ConfigurationError( 'Getting git log for "{0}" timed out.'.format( self.url() ) )
		else:
			raise ConfigurationError( 'Getting git log failed, is there no git in the path?' )

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		self._updateHiddenClone()
		runner = RunCommand( 'git log -n1' )
		runner.setWorkingDir( self._getHiddenClonePath() )
		runner.run()

		if runner.getReturnCode() == 0:
			output = runner.getStdOut().decode()
			lines = output.split( '\n' )
			line1 = lines[0].strip()
			parts = line1.split()
			assert len( parts ) == 2 and parts[0] == 'commit'
			return parts[1]
		else:
			raise ConfigurationError( 'cannot get log for the clone of "{0}" at "{1}"'
				.format( self.getUrl(), self._getHiddenClonePath() ) )

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""
		assert self.getInstructions()
		step = self.getInstructions().getStep( 'project-checkout' )
		updateHiddenCloneAction = _UpdateHiddenCloneAction( self )
		step.addMainAction( updateHiddenCloneAction )
		updateClone = ShellCommandAction( 'git clone --local --depth 1 {0} .'.format ( self._getHiddenClonePath() ) )
		updateClone.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( updateClone )
		revision = self.getRevision() or 'HEAD'
		checkout = ShellCommandAction( 'git checkout {0}'.format( revision ) )
		checkout.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( checkout )

	def _getHiddenClonePath( self ):
		clonename = make_foldername_from_string( self.getUrl() )
		hiddenClone = os.path.join( self.getCloneArmyDir(), clonename )
		return hiddenClone

	def _updateHiddenClone( self ):
		# FIXME should this be a bare repository clone?
		hiddenClone = self._getHiddenClonePath()
		# check if the clone directory exists, create if necessary: 
		if os.path.exists( hiddenClone ):
			if not os.path.isdir( hiddenClone ):
				raise MomError( 'hidden clone exists at "{0}", but is not a directory. Help!'.format( hiddenClone ) )
			# FIXME get timeout value from settings
			runner = RunCommand( 'git pull --all', 1200, True )
			runner.setWorkingDir( hiddenClone )
			runner.run()
			if runner.getReturnCode() == 0:
				mApp().debugN( self, 4, 'updated the hidden clone at "{0}"'.format( hiddenClone ) )
			else:
				raise MomError( 'cannot update the clone of "{0}" at "{1}"'.format( self.getUrl(), hiddenClone ) )
		else:
			runner = RunCommand( 'git clone {0} {1}'.format( self.getUrl(), hiddenClone ), 1200, True )
			runner.run()
			if runner.getReturnCode() == 0:
				mApp().debugN( self, 2, 'Created a hidden clone at "{0}"'.format( hiddenClone ) )
			else:
				raise MomError( 'cannot create clone of "{0}" at "{1}"'.format( self.getUrl(), hiddenClone ) )

