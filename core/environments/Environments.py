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
from core.modules.ConfigurationBase import ConfigurationBase
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
import os
from core.Exceptions import MomError
from core.environments.Dependency import Dependency
from fnmatch import fnmatch
from core.environments.Environment import Environment

class Environments( ConfigurationBase ):
	'''Environments is a decorator for Configuration. It takes a configuration, and a list of required folders, and detects matches 
	of the required folders with those found in the environments base directory.
	The configuration is then cloned for every matching environment, if this functionality is enabled for the selected build type.
	'''

	def __init__( self, dependencies = None, name = None, parent = None ):
		ConfigurationBase.__init__( self, name, parent )
		self._setDependencies( dependencies )

	def _setDependencies( self, deps ):
		self.__dependencies = deps

	def addDependency( self, dep ):
		self.__dependencies.append( dep )

	def getDependencies( self ):
		return self.__dependencies

	def _setInstalledDependencies( self, deps ):
		self.__installedDeps = deps

	def _getInstalledDependencies( self ):
		return self.__installedDeps

	def buildConfiguration( self ):
		'''For every child found during setup, apply the child, and build the configuration.'''
		error = False
		for child in self.getChildren():
			assert isinstance( child, ConfigurationBase )
			if child.buildConfiguration() != 0:
				error = True
		if error:
			return 1
		else:
			return 0

	def runPreFlightChecks( self ):
		# discover matching environments:
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		if buildType not in mApp().getSettings().get( Settings.EnvironmentsApplicableBuildTypes ).lower():
			mApp().debugN( self, 2, 'environments will not be applied in build type {0}'.format( buildType ) )
			return
		configs = self.getChildren()[:]
		environments = self.findMatchingEnvironments()
		if environments:
			for config in configs:
				self.removeChild( config )
			for environment in environments:
				environment.setName( environment.makeDescription() )
				environment.cloneConfigurations( configs )
		ConfigurationBase.runPreFlightChecks( self )

	def _findMomDependencies( self, folder ):
		"""recursively find leaf nodes within folder"""
		leafNodes = []
		if os.path.isdir( folder ):
			elements = os.listdir( folder )
			for element in elements:
				mApp().debugN( self, 4, 'checking if {0} is a MOM dependency'.format( element ) )
				path = os.path.join( folder, element )
				dependency = Dependency( path )
				if dependency.verify():
					# if self._directoryIsLeafNode( path ):
					leafNodes.append( dependency )
				elif os.path.isdir( path ):
					leafNodes.extend( self._findMomDependencies( path ) )
		return leafNodes

	def detectMomDependencies( self ):
		momEnvironmentsRoot = mApp().getSettings().get( Settings.EnvironmentsBaseDir )
		detectedDependencies = self._findMomDependencies( momEnvironmentsRoot )
		deps = {}
		for dep in detectedDependencies:
			folder = os.path.normpath( os.path.abspath( dep.getFolder() ) )
			deps[ folder ] = dep
		self._setInstalledDependencies( deps )
		# mApp().debugN( self, 3, 'found MOM dependencies: {0}'.format( ', '.join( str( detectedDependencies ) ) ) )

	def calculateMatches( self, packages, remainingDependencies, folders ):
		matches = []
		if not folders:
			return None
		folder = folders[0]
		for dep in remainingDependencies:
			for item in os.listdir( folder ):
				path = os.path.join( folder, item )
				if not os.path.isdir( path ):
					continue
				if fnmatch( item, dep ):
					if path not in self._getInstalledDependencies():
						mApp().debugN( self, 4, 'dependency {0} matches, but is not enabled'.format( item ) )
						continue
					newPackages = list( packages )
					newPackages.append( path )
					newDeps = list( self.getDependencies() )
					newDeps.remove( dep )
					if newDeps:
						# there are still dependencies to find further up the path
						theseMatches = self.calculateMatches( newPackages, newDeps, folders[1:] )
						if theseMatches:
							matches.append( theseMatches )
					else:
						# yay, all dependencies have been found
						matches.append( newPackages )
		return matches

	def findMatchingEnvironments( self ):
		# find all leaf nodes:
		momEnvironmentsRoot = mApp().getSettings().get( Settings.EnvironmentsBaseDir )

		if not os.path.isdir( momEnvironmentsRoot ):
			mApp().debug( self, 'warning - MomEnvironments root not found at "{0}". Continuing.'.format( momEnvironmentsRoot ) )
			return []

		mApp().debugN( self, 3, 'MomEnvironments root found at "{0}"'.format( momEnvironmentsRoot ) )
		self.detectMomDependencies()
		# make set of installation nodes
		uniqueDependencyFolders = []
		for dep in self._getInstalledDependencies():
			uniqueDependencyFolders.append( self._getInstalledDependencies()[dep].getContainingFolder() )
		uniqueDependencyFolders = frozenset( uniqueDependencyFolders )
		allRawEnvironments = [] # these are the folders, that will be converted to Environment objects later
		for folder in uniqueDependencyFolders:
			# calculate the paths to look at
			folders = folder.split( os.sep )
			root = momEnvironmentsRoot.split( os.sep )
			if root != folders[:len( root )]:
				raise MomError( 'The MOM dependency is supposed to be a sub directory of the MOM environments folder!' )
			subTree = folders[len( root ):]
			reversePaths = [ momEnvironmentsRoot ]
			current = momEnvironmentsRoot
			for folder in subTree:
				current = os.path.join( current, folder )
				reversePaths.append( current )
			reversePaths.reverse()
			mApp().debugN( self, 5, 'incremental paths: {0}'.format( ', '.join( reversePaths ) ) )
			matches = self.calculateMatches( [], list( self.getDependencies() ), reversePaths )
			if matches:
				allRawEnvironments.extend( matches )
		# convert to Environment objects, make them unique, because the matching algorithm potentially finds duplicates:
		environments = []
		for env in allRawEnvironments:
			envs = []
			for path in env:
				envs.append( self._getInstalledDependencies()[ path ] )
			envs = frozenset( envs )
			match = Environment( parent = self )
			match.setDependencies( envs )
			environments.append( match )
		environments = frozenset( environments )
		return environments

	def createXmlNode( self, document ):
		node = document.createElement( "environment" )
		node.attributes["name"] = self.getName()

		return node

	def describe( self, prefix ):
		ConfigurationBase.describe( self, prefix )
		deps = '{0}- dependencies: {1}'.format( prefix, ', '.join( self.getDependencies() ) )
		print( deps )
