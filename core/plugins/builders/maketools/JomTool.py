# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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
from core.plugins.builders.maketools.MakeTool import MakeTool

class JomTool( MakeTool ):
	'''JomTool implements a class for the Nokia Jom makefile tool.'''

	def __init__( self ):
		MakeTool.__init__( self )
		searchPaths = [ "C:/Program Files/jom" ]
		self._setCommand( 'jom' )
		self._setCommandSearchPaths( searchPaths )
		self._setVersionParameter( '/version' )

	def getArguments( self ):
		return [ '/nologo', '/j{0}'.format( self._getJobs() ) ]
