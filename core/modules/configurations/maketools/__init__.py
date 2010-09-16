# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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
import sys
from core.modules.configurations.maketools.NMakeTool import NMakeTool
from core.modules.configurations.maketools.GNUMakeTool import GNUMakeTool
from core.modules.configurations.maketools.JomTool import JomTool

def getMakeTool():
	#FIXME Look in the path rather than doing this per-platform
	if sys.platform == 'win32':
		jom = False
		if jom:
			return JomTool()
		else:
			return NMakeTool()
	else:
		return GNUMakeTool()