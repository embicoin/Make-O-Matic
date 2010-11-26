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

from __future__ import print_function

from core.plugins.sourcecode.SourceCodeProvider import SourceCodeProvider
from core.Settings import Settings
from core.Exceptions import MomError
from core.helpers.PathResolver import PathResolver
from core.helpers.GlobalMApp import mApp
import os
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction
from core.BuildInstructions import BuildInstructions
from core.plugins.sourcecode import getScm

class Project( BuildInstructions ):
	"""A Project represents an entity to build. 
	
	FIXME: documentation
	"""

	def __init__( self, projectName, parent = None ):
		"""Set up the build steps, parse the command line arguments."""
		BuildInstructions.__init__( self, projectName, parent )
		mApp().getSettings().set( Settings.ProjectName, projectName )
		self.__scm = None

	def getBuild( self ):
		from core.Build import Build
		assert isinstance( self.getParent(), Build )
		return self.getParent()

	def createScm( self, url ):
		scm = getScm( url )
		scm.setSrcDir( PathResolver( self.getSourceDir ) )
		scm.setRevision( mApp().getParameters().getRevision() )
		scm.setBranch( mApp().getParameters().getBranch() )
		scm.setTag( mApp().getParameters().getTag() )
		self.setScm( scm )

	def setScm( self, scm ):
		if self.getScm():
			raise MomError( 'The master SCM can only be set once!' )
		if not isinstance( scm, SourceCodeProvider ):
			raise MomError( 'SCMs need to re-implement the SourceCodeProvider class!' )
		self.__scm = scm
		self.addPlugin( scm )

	def getScm( self ):
		return self.__scm

	def __getNormPath( self, name ):
		path = os.path.join( self.getBaseDir(), mApp().getSettings().get( name ) )
		return os.path.normpath( path )

	def getSourceDir( self ):
		return self.__getNormPath( Settings.ProjectSourceDir )

	def getTempDir( self ):
		return self.__getNormPath( Settings.ProjectTempDir )

	def getDocsDir( self ):
		return self.__getNormPath( Settings.ProjectDocsDir )

	def setup( self ):
		super( Project, self ).setup()
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		assert len( buildType ) == 1
		mApp().debug( self, 'build type: {0} ({1})'
			.format( buildType.upper(), mApp().getSettings().getBuildTypeDescription( buildType ) ) )
		create = self.getStep( 'build-create-folders' )
		delete = self.getStep( 'build-cleanup' )
		for folder in ( self.getDocsDir(), self.getSourceDir(), self.getTempDir() ):
			create.addMainAction( MkDirAction( folder ) )
			delete.prependMainAction( RmDirAction( folder ) )

	def executeSteps( self ):
		for step in self.getSteps():
			self._executeStepRecursively( self, step.getName() )

	def execute( self ):
		with self.getTimeKeeper():
			self.executeSteps()
			super( Project, self ).execute()
