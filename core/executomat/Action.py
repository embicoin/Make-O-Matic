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
from core.MObject import MObject
from core.helpers.TypeCheckers import check_for_string, check_for_nonnegative_int
from core.Exceptions import AbstractMethodCalledError, MomError, MomException, BuildError
import os
from core.helpers.TimeKeeper import TimeKeeper

class Action( MObject ):
	"""Action is the base class for executomat actions.
	Every action has a working directory, and an integer result. A result of zero (0) indicates success.
	The output is registered separately for (potentially imaginary) stdout and stderr streams, and can be 
	saved to a log file. 
	"""

	def run( self, project ):
		raise AbstractMethodCalledError()

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		raise AbstractMethodCalledError()

	def __init__( self, name = None ):
		"""Constructor"""
		MObject.__init__( self, name )
		self.__timeKeeper = TimeKeeper()
		self.__workingDir = None
		self.__started = False
		self.__finished = False
		self.__result = None
		self.__stdOut = None
		self.__stdErr = None

	def setWorkingDirectory( self, dir ):
		"""Set the directory to execute the command in."""
		check_for_string( dir, "The working directory parameter must be a string containing a directory name." )
		self.__workingDir = dir

	def getWorkingDirectory( self ):
		"""Return the working directory."""
		return self.__workingDir

	def _aboutToStart( self ):
		self.__started = True

	def wasStarted( self ):
		return self.__started != False

	def _finished( self ):
		self.__finished = True

	def didFinish( self ):
		return self.__finished != False

	def _setResult( self, result ):
		check_for_nonnegative_int( result, 'The result of an action must be a non-negative integer!' )
		self.__result = result

	def getResult( self ):
		return self.__result

	def getExitCode( self ):
		"""Returns the actions integer exit code. Can only be called after execution."""
		if not self.didFinish():
			raise MomError( 'exitCode() queried before the command was finished' )
		return self.__exitCode

	def getStdErr( self ):
		"""Returns the stderr output of the action. Can only be called after execution."""
		if not self.didFinish():
			raise MomError( 'stdErr() queried before the action was finished' )
		return self.__stdErr

	def getStdOut( self ):
		"""Returns the stdout output of the action. Can only be called after execution."""
		if not self.didFinish():
			raise MomError( 'stdOut() queried before the action was finished' )
		return self.__stdOut

	def executeAction( self, project, executomat, step ):
		try:
			self.__timeKeeper.start()
			return self._executeActionTimed( project, executomat, step )
		finally:
			self.__timeKeeper.stop()
			project.debugN( self, 2, '{0} duration: {1}'.format( self.getLogDescription(), self.__timeKeeper.deltaString() ) )

	def _executeActionTimed( self, project, executomat, step ):
		oldPwd = None
		try:
			executomat.log( '# {0}'.format( self.getLogDescription() ) )
			if self.getWorkingDirectory():
				oldPwd = os.getcwd()
				executomat.log( '# changing directory to "{0}"'.format( self.getWorkingDirectory() ) )
				try:
					os.chdir( self.getWorkingDirectory() )
				except ( OSError, IOError ) as e:
					raise BuildError( str( e ) )
			self._aboutToStart()
			self._setResult( 0 )
			result = self.run( project )
			self._finished()
			if step.getLogfileName():
				file = open( step.getLogfileName(), 'a' )
				if file:
					if self.getStdOut():
						file.writelines( self.getStdOut().decode() )
					else:
						file.writelines( '(The action "{0}" did not generate any output.)\n'.format( self.getLogDescription() ) )
					file.close()
				else:
					raise MomError( 'cannot write to log file "{0}"'.format( step.getLogfileName() ) )
			return result
		except MomException as e:
			project.debug( self, 'execution failed: "{0}"'.format( str( e ) ) )
			self._setResult( e.getReturnCode() )
			return False
		finally:
			if oldPwd:
				executomat.log( '# changing back to "{0}"'.format( oldPwd ) )
				os.chdir( oldPwd )
