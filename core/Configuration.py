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
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
import core
from core.modules.ConfigurationBase import ConfigurationBase
import os
from core.actions.filesystem.MkDirAction import MkDirAction
from core.helpers.PathResolver import PathResolver
from core.actions.filesystem.RmDirAction import RmDirAction

class Configuration( ConfigurationBase ):
	'''Configuration represents a variant of how a project is built.
	It is always related to a project.'''

	def __init__( self, configName, parent = None ):
		ConfigurationBase.__init__( self, configName, parent )

	def _setProject( self, project ):
		assert isinstance( project, core.Project.Project )
		self.__project = project

	def _getNormPath( self, name ):
		path = os.path.join( self.getBaseDir(), mApp().getSettings().get( name ) )
		return os.path.normpath( os.path.abspath( path ) )

	def getBuildDir( self ):
		return self._getNormPath( Settings.ConfigurationBuildDir )

	def getTargetDir( self ):
		return self._getNormPath( Settings.ConfigurationTargetDir )

	def runSetups( self ):
		ConfigurationBase.runSetups( self )
		settings = mApp().getSettings()
		folders = [ settings.get( Settings.ConfigurationBuildDir ), settings.get( Settings.ConfigurationTargetDir ) ]
		create = self.getStep( 'conf-create-folders' )
		cleanup = self.getStep( 'conf-cleanup' )
		for folder in folders:
			create.addMainAction( MkDirAction( PathResolver( self.getBaseDir, folder ) ) )
		folders.reverse()
		for folder in folders:
			cleanup.addMainAction( RmDirAction( PathResolver( self.getBaseDir, folder ) ) )
