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

from core.Exceptions import ConfigurationError
from core.Parameters import Parameters
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
import optparse

class MomParameters( Parameters ):
	'''Parse the parameters of an invocation of the mom tool.'''

	def __init__( self, name = None ):
		super( MomParameters, self ).__init__( name )

	def getRevision( self ):
		return self.__revision

	def getBuildScriptOptions( self ):
		return self.__buildScriptOptions

	def getUrl( self ):
		return self.__url

	def getPath( self ):
		return self.__path

	def getBuildscriptName( self ):
		return self.__name

	def _createOptionParser( self ):
		parser = optparse.OptionParser()
		parser.add_option( '-r', '--revision', action = 'store', dest = 'revision',
			help = 'build script revision to be retrieved' )
		parser.add_option( '-u', '--scm-url', action = 'store', dest = 'url',
			help = 'SCM location including SCM identifier' )
		parser.add_option( '-p', '--path', action = 'store', dest = 'buildscriptPath', default = 'admin',
			help = 'path of the build script in the specified repository, without the build script' )
		parser.add_option( '-n', '--name', action = 'store', dest = 'buildscriptName', default = 'buildscript.py',
			help = 'filename of the build script' )
		parser.add_option( '-v', '--verbosity', action = 'count', dest = 'verbosity', default = 0,
			help = 'level of debug output' )
		return parser

	def parse( self, arguments ):
		'''The mom command line contains two parts, a set of options for the mom tool itself, and a set of options for the 
		invoked build script. The latter are ignored by mom, and will be passed down to the build script only. Both sections are 
		separated by a single dash. If the single dash is not found, it is assumed that all parameters are to be parsed by the mom 
		tool. Example: 
		mom -vv -u git://github.com/KDAB/Make-O-Matic.git -p mom/buildscript.py -r4711 - -vv -t H -r4711
		'''

		super( MomParameters, self ).parse()

		# make a copy to avoid accidentally modifying sys.args
		momOptions = arguments[:]
		# split up the command line into the two sections: 
		index = 0
		self.__buildScriptOptions = []
		for item in arguments:
			if item.strip() == '-':
				momOptions = arguments[0:index]
				self.__buildScriptOptions = arguments[index + 1:]
				break
			index = index + 1
		mApp().debugN( self, 2, 'mom tool options: {0}'.format( ' '.join( arguments ) ) )

		# parse options:
		( options, args ) = self.getParser().parse_args( momOptions )
		if options.revision:
			self.__revision = options.revision
		else:
			self.__revision = None
			mApp().message( self, 'no revision specified, using the equivalent of HEAD' )
		if options.url:
			self.__url = options.url
		else:
			raise ConfigurationError( 'No SCM URL specified!' )
		if options.buildscriptPath:
			self.__path = options.buildscriptPath
		else:
			self.__path = 'admin'
			mApp().message( self, 'no build script path specified, using "{0}"'.format( self.__path ) )
		if options.buildscriptName:
			self.__name = options.buildscriptName
		else:
			self.__name = 'buildscript.py'
			mApp().message( self, 'no build script name specified, using "{0}"'.format( self.__name ) )
		if options.verbosity:
			mApp().getSettings().set( Settings.ScriptLogLevel, options.verbosity )
		if len( args ) > 1: # the one element is the program path
			raise ConfigurationError( 'The mom tool does not understand any extra arguments (arguments found: {0})!'
				.format( ' '.join( args ) ) )
