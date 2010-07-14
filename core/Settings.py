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
from core.Defaults import Defaults
import os
from core.Exceptions import ConfigurationError

class Settings( MObject ):
	"""Settings stores all configurable values for a build script run."""

	def __init__( self ):
		'''Constructor'''
		MObject.__init__( self )
		defaults = Defaults()
		self._setProjectBuildSteps( defaults.getProjectBuildSteps() )
		self._setDefaultBuildSteps( defaults.getProjectDefaultBuildSteps() )

	def evalConfigurationFiles( self, project ):
		filename = 'config.py'
		globalConfigFile = os.path.join( '/', 'etc', 'mom', filename )
		homeDir = os.environ['HOME']
		localConfigFile = os.path.join( homeDir, '.mom', filename )
		configFiles = [ globalConfigFile, localConfigFile]
		for configFile in configFiles:
			if not os.path.isfile( configFile ):
				project.debug( self, 'Configuration file "{0}" does not exist, continuing.'.format( configFile ) )
				continue
			project.debugN( self, 2, 'Loading configuration file "{0}"'.format( configFile ) )
			try:
				globals = { 'project' : project }
				with open( configFile ) as f:
					code = f.read()
					exec( code, globals )
				project.debug( self, 'Configuration file "{0}" loaded successfully'.format( configFile ) )
			except SyntaxError as e:
				raise ConfigurationError( 'The configuration file "{0}" contains a syntax error: "{1}"'.format( configFile, str( e ) ) )
			except Exception as e: # we need to catch all exceptions, since we are calling user code 
				raise ConfigurationError( 'The configuration file "{0}" contains an error: "{1}"'.format( configFile, str( e ) ) )
			except: # we need to catch all exceptions, since we are calling user code 
				raise ConfigurationError( 'The configuration file "{0}" contains an unknown error!'.format( configFile ) )

	def _setProjectBuildSteps( self, steps ):
		self.__projectBuildSteps = steps

	def getProjectBuildSteps( self ):
		return self.__projectBuildSteps

	def _setDefaultBuildSteps( self, stepsDict ):
		self.__defaultSteps = stepsDict
