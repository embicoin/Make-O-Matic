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

from core.Parameters import Parameters
import sys

class SimpleCiParameters( Parameters ):

	def __init__( self ):
		super( SimpleCiParameters, self ).__init__()

		self.setBuildScripts( None )
		self.setControlDir( None )
		self.setPerformTestBuilds( False )
		self.setSlaveMode( False )
		self.setFindRevisions( True )
		self.setPerformBuilds( True )
		self.setDelay( None )
		self.setInstanceName( None )

	def setControlDir( self, controlDir ):
		self.__controlDir = controlDir

	def getControlDir( self ):
		return self.__controlDir

	def setPerformTestBuilds( self, doIt ):
		self.__performTestBuilds = doIt

	def getPerformTestBuilds( self ):
		return self.__performTestBuilds

	def setSlaveMode( self, onoff ):
		self.__slaveMode = onoff

	def getSlaveMode( self ):
		return self.__slaveMode

	def setFindRevisions( self, doIt ):
		self.__find = doIt

	def getFindRevisions( self ):
		return self.__find

	def setPerformBuilds( self, doIt ):
		self.__build = doIt

	def getPerformBuilds( self ):
		return self.__build

	def setDelay( self, delay ):
		self.__delay = delay

	def getDelay( self ):
		return self.__delay

	def setBuildScripts( self, scripts ):
		self.__buildScripts = scripts

	def getBuildScripts( self ):
		return self.__buildScripts

	def setInstanceName( self, name ):
		self.__instanceName = name

	def getInstanceName( self ):
		return self.__instanceName

	def _initParser( self, parser ):
		super( SimpleCiParameters, self )._initParser( parser )

		group = parser.add_option_group( "Simple CI options" )
		group.add_option( "-c", "--control-folder", type = "string", dest = "control_dir",
			help = "select control folder that contains the build scripts" )
		group.add_option( "-d", "--test-run", action = "store_true", dest = "test_run",
			help = "compile the last revision of every product for testing" )
		group.add_option( "-f" , "--no-find", action = "store_true", dest = "no_find",
			help = "do not try to discover new revisions for the projects (default: do try)" )
		group.add_option( "-b", "--no-build", action = "store_true", dest = "no_build",
			help = "do not start build jobs for new revisions (default: do build)" )
		group.add_option( "-s", "--slave", action = "store_true", dest = "slaveMode",
			help = "run in slave mode (the one that actually does the builds)" )
		group.add_option( "-n", "--instance-name", type = "string", dest = "instance_name",
			help = "the instance name is used to locate the configuration and database files (see debug output)" )
		group.add_option( '-p', '--pause', type = 'int', dest = 'delay',
			help = 'pause after every slave run, in seconds' )

	def parse( self ):
		"""Parse command line options, give help"""

		super( SimpleCiParameters, self ).parse()

		( options, args ) = self.getParser().parse_args( sys.argv )
		if options.control_dir:
			self.setControlDir( str( options.control_dir ) )
		if options.test_run:
			self.setPerformTestBuilds( True )
		if options.slaveMode:
			self.setSlaveMode( True )
		if options.no_find:
			self.setFindRevisions( False )
		if options.no_build:
			self.setPerformBuilds( False )
		if options.delay:
			self.setDelay( options.delay )
		if options.instance_name:
			self.setInstanceName( options.instance_name )

		self.setBuildScripts( args[1:] )
