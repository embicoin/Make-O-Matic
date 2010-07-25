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

class BuildInfo( MObject ):
	'''BuildInfo represents a single build script run.'''

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__projectName = None
		self.__buildType = None
		self.__revision = None
		self.__url = None
		self.__buildScript = None

	def getProjectName( self ):
		return self.__projectName

	def setProjectName( self, name ):
		self.__projectName = name

	def getBuildType( self ):
		return self.__buildType

	def setBuildType( self, buildType ):
		self.__buildType = buildType

	def getRevision( self ):
		return self.__revision

	def setRevision( self, revision ):
		self.__revision = revision

	def getUrl( self ):
		return self.__url

	def setUrl( self, url ):
		self.__url = url

	def getBuildScript( self ):
		return self.__buildScript

	def setBuildScript( self, script ):
		self.__buildScript = script