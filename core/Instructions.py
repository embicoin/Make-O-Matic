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

from copy import deepcopy, copy
from core.Exceptions import ConfigurationError, MomError, BuildError
from core.InstructionsBase import InstructionsBase
from core.MObject import MObject
from core.Settings import Settings
from core.executomat.Step import Step
from core.helpers.Enum import Enum
from core.helpers.EnvironmentSaver import EnvironmentSaver
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.helpers.GlobalMApp import mApp
from core.helpers.TimeKeeper import TimeKeeper
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_nonempty_string, check_for_path_or_none
import os
import traceback
import types

class Instructions( InstructionsBase ):
	"""
	Instructions is the base class for anything that can be built by Make-O-Matic, including the packages and reports locations.
	
	- The Build object is a singleton that represents the build script run.
	- Projects are Instructions to build a Project.
	- Configurations are Instructions to build a configuration of a Project.
	- Instructions implement the phased approach to executing the build script, and the\n
      idea of plug-ins that implement certain functionality.

	The idea is to have a hierarchical structure like this:

	- Build
	  - Project
	    - Configuration1 (a set of dependencies)
	      - Instruction1.1 (a set of steps including actions, e.g. "./configure")
	      - Instruction1.2
	    - Configuration2
	      - Instruction2.1
	"""

	class Phase( Enum ):
		'''Enumerated values representing the phases of the application run.'''
		Start, Prepare, PreFlightCheck, Setup, Execute, WrapUp, Report, Notify, ShutDown = range ( 9 )
		_Descriptions = [ '_start', 'prepare', 'preFlightCheck', 'setup', 'execute', 'wrapup', 'report', 'notify', 'shutDown' ]

	def __init__( self, name = None, parent = None ):
		super( Instructions, self ).__init__( name )

		self._setBaseDir( None )
		self.setLogDir( None )
		self.deleteLogDirOnShutdown( False )
		self.setPackagesDir( None )
		self.setParent( None )
		self._setCurrentPhase( self.Phase.Start )

		self.__plugins = []
		self.__instructions = []
		self.__steps = []
		self.__timeKeeper = TimeKeeper()

		if parent: # the parent instructions object
			parent.addChild( self )

	def __deepcopy__( self, memo ):
		'''Customize the behaviour of deepcopy to not include the parent object.'''
		# make shallow copy:
		clone = copy( self )
		# plug-ins and instructions need to be deep-copied
		clone.__plugins = deepcopy( self.__plugins, memo )
		for plugin in clone.__plugins:
			plugin.setInstructions( clone )
		clone.__instructions = deepcopy( self.__instructions, memo )
		clone.__timeKeeper = deepcopy( self.__timeKeeper, memo )
		clone.__steps = deepcopy( self.__steps, memo )
		return clone

	def setParent( self, parent ):
		assert parent == None or isinstance( parent, Instructions )
		self.__parent = parent

	def getParent( self ):
		return self.__parent

	def _setBaseDir( self, folder ):
		check_for_nonempty_string_or_none( folder, 'The instructions base directory must be a folder name, or None!' )
		self.__baseDir = folder

	def getBaseDir( self ):
		check_for_nonempty_string( self.__baseDir, 'basedir can only be queried after preFlightCheck!' )
		return self.__baseDir

	def getRelativeBaseDir( self ):
		if not self.getBaseDir():
			return None

		buildBaseDir = mApp().getBaseDir()
		return os.path.relpath( self.getBaseDir(), buildBaseDir )

	def setLogDir( self, path ):
		"""Set the directory where all log information is stored."""
		check_for_path_or_none( path, "The log directory name must be a string containing a path name." )
		self.__logDir = path

	def getLogDir( self ):
		"""Return the log directory.
		The log directory is the full path the the location where log output of the step should be saved. It is usually located
		under the log/ sub-directory of the build object, outside of the build tree."""
		return self.__logDir

	def deleteLogDirOnShutdown( self, onOff ):
		"""If set to true, the log directory structure will be deleted in the shut down phase. 
		This setting defaults to true, and will be disabled if an exception occurs. Reporters can set it back to true if, 
		for example, all necessary information is part of the reports and needed locally after the report has been published."""
		self.__deleteLogDir = onOff

	def getDeleteLogDirOnShutdown( self ):
		"""Return whether the log directory structure will be deleted during the shutdown phase."""
		return self.__deleteLogDir

	def setPackagesDir( self, path ):
		'''Return the packages directory for this object. 
		All data files produced by the build should be stored in the packages directory.'''
		check_for_path_or_none( path, "The packages directory name must be a string containing a path name." )
		self.__packagesDir = path

	def getPackagesDir( self ):
		'''Get the packages directory.'''
		return self.__packagesDir

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		mApp().debugN( self, 4, "Adding plugin: {0}".format( plugin.getName() ) )

		plugin.setInstructions( self )
		self.__plugins.append( plugin )

	def getChildren( self ):
		return self.__instructions

	def addChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		if instructions in self.getChildren():
			raise MomError( 'A child can be added to the same instruction object only once (offending object: {0})!'
				.format( instructions.getName() ) )
		instructions.setParent( self )
		self.__instructions.append( instructions )

	def removeChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		if instructions in self.getChildren():
			self.getChildren().remove( instructions )
		else:
			raise MomError( 'Cannot remove child {0}, I am not it\'s parent {1}!'
				.format( instructions.getName(), self.getName() ) )

	def getTimeKeeper( self ):
		'''\return TimeKeeper object to measure execution time.'''
		return self.__timeKeeper

	def getFailedSteps( self ):
		'''\return List of steps that failed during execution'''

		return [step for step in self.getSteps() if step.getResult() == Step.Result.Failure]

	def hasFailed( self ):
		"""Returns True if this instructions instance has failed steps"""
		return len( self.getFailedSteps() ) > 0

	def hasFailedRecursively( self ):
		'''Returns True in the following cases:
		* if any step for this object has failed
		* or if any instance of the children has failed'''

		for child in self.getChildren():
			if child.hasFailedRecursively():
				return True

		return self.hasFailed()

	def __hasStep( self, stepName ):
		'''Returns True if a step with the specified name already exists.'''
		try:
			self.getStep( stepName )
			return True
		except MomError:
			return False

	def addStep( self, newStep ):
		"""Add a newStep identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( newStep, Step ):
			raise MomError( 'only Step instances can be added to the queue' )
		check_for_nonempty_string( newStep.getName(), "Every step must have a name!" )
		if self.__hasStep( newStep.getName() ):
			raise MomError( 'A step with the name {0} already exists for this Instructions object!'.format( newStep.getName() ) )
		self.__steps.append( newStep )

	def getSteps( self ):
		'''Return the list of build steps for the object.
		It is a list, not a dictionary, because the steps are a sequence and cannot be reordered.'''
		return self.__steps

	def getStep( self, identifier ):
		"""Find the step with this identifier and return it."""
		for step in self.getSteps():
			if step.getName() == identifier:
				return step

		raise MomError( 'No such step "{0}" in "{1}" object'.format( identifier, self.getName() ) )

	def calculateBuildSequence( self ):
		'''Define the build sequence for this object.
		By the default, the build sequence is identical for every BuildInstructions object. Command line parameters that
		enable or disable steps are applied by this method.'''
		buildSteps = self._setupBuildSteps( Settings.ProjectBuildSequence )
		# apply customizations passed as command line parameters:
		mApp().getParameters().applyBuildSequenceSwitches( buildSteps )
		return buildSteps

	def describe( self, prefix, details = None, replacePatterns = True ):
		if not details:
			basedir = '(not set)'
			try:
				basedir = self.getBaseDir()
			except ConfigurationError:
				pass
			details = ' {1}'.format( prefix, basedir )
		super( Instructions, self ).describe( prefix, details, replacePatterns )
		subPrefix = prefix + '    '
		for plugin in self.getPlugins():
			plugin.describe( subPrefix )
		for step in self.getSteps():
				step.describe( prefix + '    ' )

	def createXmlNode( self, document, recursive = True ):
		node = super( Instructions, self ).createXmlNode( document )

		node.attributes["timing"] = str( self.getTimeKeeper().deltaString() )
		# FIXME Kevin: better use Step.getStatus() and Step.getResult()
		node.attributes["failed"] = str( self.hasFailedRecursively() )

		if recursive:
			# loop through plugins
			pluginsElement = document.createElement( "plugins" )
			for plugin in self.getPlugins():
				element = plugin.createXmlNode( document )
				pluginsElement.appendChild( element )
			node.appendChild( pluginsElement )

		# loop through steps
		stepsElement = document.createElement( "steps" )
		for step in self.getSteps():
			element = step.createXmlNode( document )
			stepsElement.appendChild( element )
		node.appendChild( stepsElement )

		return node

	def describeRecursively( self, prefix = '' ):
		'''Describe this instruction object in human readable form.'''
		self.describe( prefix )
		prefix = '    {0}'.format( prefix )
		for child in self.getChildren():
			child.describeRecursively( prefix )

	def _setupBuildSteps( self, buildStepsSetting ):
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		allBuildSteps = mApp().getSettings().get( buildStepsSetting, True )
		buildSteps = []
		for buildStep in allBuildSteps:
			# FIXME maybe this could be a unit test?
			assert len( buildStep ) == 3
			name, types, ignorePreviousFailure = buildStep
			assert types.lower() == types
			stepName = Step( name )
			stepName.setEnabled( buildType in types )
			stepName.setIgnorePreviousFailure( ignorePreviousFailure )
			buildSteps.append( stepName )
		return buildSteps

	def getIndex( self, instructions ):
		index = 0
		for child in self.getChildren():
			if child == instructions:
				return index
			index = index + 1
		raise MomError( 'Unknown child {0}'.format( instructions ) )

	def _setCurrentPhase( self, phase ):
		self.__currentPhase = phase

	def getCurrentPhase( self ):
		return self.__currentPhase

	def _getBaseDirName( self ):
		myIndex = None
		if self.getParent():
			myIndex = self.getParent().getIndex( self ) + 1
		if self.getName() == self.__class__.__name__:
			baseDirName = '{0}'.format( myIndex )
		else:
			index = myIndex or ''
			spacer = '_' if myIndex else ''
			baseDirName = '{0}{1}{2}'.format( index, spacer, make_foldername_from_string( self.getName() ) )
		return baseDirName

	def _runPhase( self, phase ):
		self._setCurrentPhase( phase )

		with EnvironmentSaver():
			methodName = self.Phase.getDescription( phase )

			mApp().debugN( self, 1, 'Running phase: {0}'.format( methodName ) )
			method = getattr( self, methodName )
			method()

			for child in self.getChildren():
				child._runPhase( phase )

			for plugin in self.getPlugins():
				if plugin.isEnabled():
					catchExceptions = False
					if plugin.isOptional():
						# do not abort build if optional plugins crash
						catchExceptions = True
					if phase in [self.Phase.Report, self.Phase.Notify, self.Phase.ShutDown]:
						# do not abort build when plugins crash in these phases
						catchExceptions = True

					self._call( plugin, methodName, catchExceptions = catchExceptions )

	def runPrepare( self ):
		self._runPhase( self.Phase.Prepare )

	def runPreFlightChecks( self ):
		self._runPhase( self.Phase.PreFlightCheck )

	def runSetups( self ):
		self._runPhase( self.Phase.Setup )

	def runExecute( self ):
		self._runPhase( self.Phase.Execute )

	def _stepsShouldExecute( self ):
		'''Return if the steps should be executed for this object. 
		By default, steps should be executed if no error happened so far. Steps with the execute-on-failure property set to True
		will execute even if this method returns False.'''
		return mApp().getReturnCode() == 0

	def _executeStepRecursively( self, instructions, name ):
		'''Execute one step of the build sequence recursively, for this object, and all child objects.'''
		self.executeStep( name )
		for child in instructions.getChildren():
			child._executeStepRecursively( child, name )

	def executeStep( self, stepName ):
		'''Execute one individual step.
		This method does not recurse to child objects.'''
		mApp().debugN( self, 2, "Executing step: {0}".format( stepName ) )
		step = self.getStep( stepName )
		try:
			if not step.execute( self ):
				mApp().registerReturnCode( BuildError( 'dummy' ).getReturnCode() )
		finally:
			if not step.isEmpty():
				noOfActions = len( step.getPreActions() ) + len( step.getMainActions() ) + len( step.getPostActions() )
				mApp().debug( self, '{0}: actions: {1}, status: {2}, result: {3}, duration: {4}'.format( 
					step.getName(),
					noOfActions,
					Step.Status.getDescription( step.getStatus() ),
					Step.Result.getDescription( step.getResult() ),
					step.getTimeKeeper().deltaString() ) )

	def runWrapups( self ):
		self._runPhase( self.Phase.WrapUp )

	def runReports( self ):
		self._runPhase( self.Phase.Report )

	def runNotifications( self ):
		notificationsEnabled = mApp().getSettings().get( Settings.ScriptEnableNotifications )
		if not notificationsEnabled:
			mApp().debug( self, "Not running notify phase, disabled by settings (Settings.ScriptEnableNotifications)" )
			return

		self._runPhase( self.Phase.Notify )

	def runShutDowns( self ):
		self._runPhase( self.Phase.ShutDown )

	def _call( self, mObject, methodName, catchExceptions = False ):
		"""Run method on mObject

		\param mObject MObject instance
		\param catchExceptions Catch exceptions thrown by mObject.methodName()
		"""

		assert isinstance( mObject, MObject )

		# run
		try:
			method = getattr( mObject, methodName )
			method()
		except Exception as e:
			text = u'''\
An error occurred during {0}: "{1}"
Offending module: "{2}"'''.format( method.__name__,
		unicode( e ),
		mObject.getName()
 )
			mApp().error( self, text )
			mApp().error( self, traceback.format_exc() )

			if not catchExceptions:
				raise # re-raise
