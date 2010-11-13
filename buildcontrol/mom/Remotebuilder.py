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
import os
from core.MObject import MObject
from core.Exceptions import ConfigurationError
from core.plugins.sourcecode import getScm
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface

class RemoteBuilder( MObject ):
	def __init__( self, revision = None, location = None, path = None, script = None, name = None ):
		MObject.__init__( self, name )
		self.setRevision( revision )
		self.setBuildscript( script )
		self.setLocation( location )
		self.setPath( path )

	def setRevision( self, revision ):
		self.__revision = revision

	def getRevision( self ):
		return self.__revision

	def setLocation( self, location ):
		self.__location = location

	def getLocation( self ):
		return self.__location

	def setPath( self, path ):
		self.__path = path

	def getPath( self ):
		return self.__path

	def setBuildscript( self, script ):
		self.__buildscript = script

	def getBuildscript( self ):
		return self.__buildscript

	def fetchBuildScript( self ):
		# create SCM implementation:
		scm = getScm( self.getLocation() )
		scm.setRevision( self.getRevision() )
		path = scm.fetchRepositoryFolder( self.getPath() )
		localBuildscript = os.path.join( path, self.getBuildscript() )
		if os.path.exists( localBuildscript ):
			return localBuildscript
		else:
			raise ConfigurationError( 'The build script {0} was not found at the path {1} in the repository at revision {2}'.format( 
				self.getBuildscript(), self.getPath(), self.getRevision() ) )

	def invokeBuild( self, args, timeout = None ):
		path = self.fetchBuildScript()
		iface = BuildScriptInterface( path )
		runner = iface.executeWithArgs( timeout = timeout, args = args )
		return runner
