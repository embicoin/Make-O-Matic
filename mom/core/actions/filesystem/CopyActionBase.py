# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

from mom.core.actions.Action import Action
from mom.core.helpers.TypeCheckers import check_for_path_or_none

class CopyActionBase( Action ):

	def __init__( self, sourceLocation = None, targetLocation = None, name = None ):
		Action.__init__( self, name )

		self.setSourcePath( sourceLocation )
		self.setDestinationPath( targetLocation )

	def setSourcePath( self, path ):
		check_for_path_or_none( path, "Please specify a valid source path" )
		self.__sourceLocation = path

	def getSourcePath( self ):
		return self.__sourceLocation

	def setDestinationPath( self, path ):
		check_for_path_or_none( path, "Please specify a valid destination path" )
		self.__targetLocation = path

	def getDestinationPath( self ):
		return self.__targetLocation
