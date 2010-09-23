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
from core.MApplication import MApplication
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
from buildcontrol.mom.Parameters import Parameters
import sys
from buildcontrol.mom.Remotebuilder import RemoteBuilder
from core.modules.scm.RevisionInfo import RevisionInfo

class MomRemoteRunner( MApplication ):
	'''MomRemoteRunner takes the location descriptor of a remote build script, fetches the build script, 
	and executes it locally.'''

	def __init__( self ):
		MApplication.__init__( self, name = 'mom' )
		self.__parameters = Parameters()

	def getToolName( self ):
		return 'mom'

	def getParameters( self ):
		return self.__parameters

	def execute( self ):
#		mApp().debugN( self, 2, 'now invoking the build script {0} with options {1}'.format( 
#			self.getParameters().getBuildscriptName(),
#			' '.join( self.getParameters().getBuildScriptOptions() ) ) )
		revInfo = RevisionInfo()
		revInfo.revision = self.getParameters().getRevision()
		remote = RemoteBuilder( revisionInfo = revInfo,
			location = self.getParameters().getUrl(),
			path = self.getParameters().getPath(),
			script = self.getParameters().getBuildscriptName() )
		# FIXME add a timeout?
		runner = remote.invokeBuild( self.getParameters().getBuildScriptOptions() )
		if runner.getStdOut():
			print( runner.getStdOut().decode() )
		self.registerReturnCode( runner.getReturnCode() )

	def build( self ):
		self.__parameters.parse( sys.argv )
		settings = self.getSettings()
		self.addLogger( ConsoleLogger() )
		settings.evalConfigurationFiles( self.getToolName() )
		MApplication.build( self )

if __name__ == "__main__":
	mom = MomRemoteRunner()
	mom.build()

