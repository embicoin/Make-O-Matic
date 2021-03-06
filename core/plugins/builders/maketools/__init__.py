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
import sys
from core.plugins.builders.maketools.NMakeTool import NMakeTool
from core.plugins.builders.maketools.GNUMakeTool import GNUMakeTool
from core.plugins.builders.maketools.JomTool import JomTool
from core.plugins.builders.maketools.MingwMakeTool import MingwMakeTool
from core.Exceptions import ConfigurationError

def getMakeTools():
	return [ JomTool, NMakeTool, MingwMakeTool, GNUMakeTool ]

def getMakeToolNames():
	return [ tool().getCommand() for tool in getMakeTools() ]

def getMakeTool():
	for MakeTool in getMakeTools():
		tool = MakeTool()
		try:
			tool.resolveCommand()
		except ConfigurationError:
			pass
		else:
			return tool

	raise ConfigurationError( 'Cannot find any valid make tool. Looked for: {0}'.format( '/'.join( getMakeToolNames() ) ) )
