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

from core.Plugin import Plugin
from core.helpers.XmlReport import XmlReport
import os.path
from core.Exceptions import ConfigurationError
from core.helpers.XmlReportConverter import ReportFormat, XmlReportConverter

class XmlReportGenerator( Plugin ):
	"""
	This plugin saves a instructions report in XML format.
	Attach to a Build object to get build-report.xml (recommended) in the toplevel build directory.
	
	\note Attached to a random instructions object it will produce "INSTRUCTIONSNAME-log.xml" in the corresponding directory.
	"""

	def __init__( self, reportFormat = ReportFormat.XML ):
		Plugin.__init__( self )

		self.__fileHandle = None
		self.__reportFile = None
		self.__reportFormat = reportFormat

		self.__finished = False

	def shutDown( self ):
		if self.__finished:
			return

		report = XmlReport( self.getInstructions() )
		report.prepare()

		self._openReportFile()
		self._writeReport( report )
		self._saveReportFile()

		self.__finished = True

	def getDescription( self ):
		return "Report saved to: {0}".format( self.getFileName() )

	def getReportFile( self ):
		return self.__reportFile

	def _openReportFile( self ):
		baseDirectory = self.getInstructions().getBaseDir()
		reportFileName = self.getFileName()

		if not os.path.isdir( baseDirectory ):
			raise ConfigurationError( 'Log directory at "{0}" does not exist.'.format( str( baseDirectory ) ) )

		try:
			self.__reportFile = baseDirectory + os.sep + reportFileName
			self.__fileHandle = open( self.__reportFile, 'w' )
		except IOError:
			raise ConfigurationError( 'Cannot open log file at "{0}"'.format( reportFileName ) )

	def _writeReport( self, report ):
		if self.__fileHandle and report:
			convertedText = self.convert( report )
			self.__fileHandle.write( convertedText )

	def _saveReportFile( self ):
		if self.__fileHandle:
			self.__fileHandle.close()

	def convert( self, report ):
		converter = XmlReportConverter( report )
		return converter.convertTo( self.__reportFormat )

	def getFileName( self ):
		return "{0}-report.{1}".format( self.getInstructions().getTagName(), self.getFileSuffix() )

	def getFileSuffix( self ):
		reportFormat = self.__reportFormat

		if reportFormat == ReportFormat.XML:
			return "xml"
		elif reportFormat == ReportFormat.HTML:
			return "html"
		elif reportFormat == ReportFormat.TEXT:
			return "txt"
