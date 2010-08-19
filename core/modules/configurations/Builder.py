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
from core.Plugin import Plugin
from core.Exceptions import AbstractMethodCalledError

class Builder( Plugin ):
	'''A Builder creates the actions to build a configuration for a project. 
	It needs to be assigned to a configuration.'''

	def __init__( self, name = None ):
		Plugin.__init__( self, name )

	def createPrepareSourceDirActions( self ):
		raise AbstractMethodCalledError()

	def createConfigureActions( self ):
		raise AbstractMethodCalledError()

	def createConfMakeActions( self ):
		raise AbstractMethodCalledError()

	def createConfMakeInstallActions( self ):
		raise AbstractMethodCalledError()

	def setup( self ):
		self.createPrepareSourceDirActions()
		self.createConfigureActions()
		self.createConfMakeActions()
		self.createConfMakeInstallActions()