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

from core.Exceptions import MomError, ConfigurationError, BuildError
from core.Plugin import Plugin
from core.Settings import Settings
from core.actions.ShellCommandAction import ShellCommandAction
from core.executomat.Step import Step
from core.helpers.GlobalMApp import mApp
from core.helpers.XmlReport import InstructionsXmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
from core.helpers.XmlUtils import xml_compare
from core.loggers.ConsoleLogger import ConsoleLogger
from core.plugins.helpers.XmlReportGenerator import XmlReportGenerator
from mom.tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
from mom.tests.helpers.TestUtils import replace_bound_method
import os.path
import unittest

try:
	from lxml import etree
except ImportError:
	try:
		# Python 2.5
		import xml.etree.cElementTree as etree
	except ImportError:
		try:
			# Python 2.5
			import xml.etree.ElementTree as etree
		except ImportError:
			try:
				# normal cElementTree install
				import cElementTree as etree
			except ImportError:
				try:
					# normal ElementTree install
					import elementtree.ElementTree as etree
				except ImportError, e:
					raise MomError( "Could not find a suitable XML module: {0}".format( e ) )

class XmlReportTests( MomBuildMockupTestCase ):

	EXCEPTION_LOCATION = ".//exception"

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useEnvironments = True )

	def tearDown( self ):
		self._runValidator()

		MomBuildMockupTestCase.tearDown( self )

	def _executeBuild( self, type = 'm' ):
		mApp().getSettings().set( Settings.ScriptLogLevel, 5 )
		mApp().getSettings().set( Settings.ProjectBuildType, type )

		#self.build.addLogger( ConsoleLogger() )
		self.build.buildAndReturn()

	def _testBasicDocumentAttributes( self, document ):
		"""\return Build element"""
		self.assertNotEquals( document.find( "./build" ), None )

	def _getXmlReport( self ):
		report = InstructionsXmlReport( self.build )
		return report

	def _runValidator( self ):
		schemaFileName = os.path.join( self.TEST_DATA_DIRECTORY, "xml2html-schema.xml" )
		xml = etree.parse( schemaFileName )
		schema = etree.XMLSchema( xml )
		parser = etree.XMLParser( schema = schema )
		etree.XML( self._getXmlReport().getReport(), parser )

	def testCreateXmlReport( self ):
		self._executeBuild()
		doc = etree.XML( self._getXmlReport().getReport() )

		self._testBasicDocumentAttributes( doc )
		self.assertNotEquals( doc.find( './/project' ), None )
		self.assertNotEquals( doc.find( './/environments' ), None )
		self.assertNotEquals( doc.find( './/configuration' ), None )
		self.assertNotEquals( doc.find( './/plugin' ), None )
		self.assertNotEquals( doc.find( './/step' ), None )
		self.assertNotEquals( doc.find( './/action' ), None )

		if etree.__name__ == "lxml.etree":
			self.assertNotEquals( doc.find( './/plugin[@name="DoxygenGenerator"]' ), None )

	def testEnvironmentExpand( self ):
		self._executeBuild( 'c' )
		doc = etree.XML( self._getXmlReport().getReport() )

		self.assertNotEquals( doc.find( './/environments/environment' ), None, "Did not find matching environments" )
		self.assertNotEquals( doc.find( './/environment/configuration' ), None )

	def testNoEnvironmentExpand( self ):
		self._executeBuild( 'm' )
		doc = etree.XML( self._getXmlReport().getReport() )

		self.assertNotEquals( doc.find( './/environments/configuration' ), None, )

	def testConvertXmlReportToHtml( self ):
		self._executeBuild()
		converter = XmlReportConverter( self._getXmlReport() )
		xmlString = converter.convertToHtml()

		if converter.hasXsltSupport(): # can convert to HTML
			self.assertNotEquals( xmlString, None )
		else: # cannot convert, should be None
			self.assertEquals( xmlString, None )
			return # quit test case, to HTML conversion is not possible here

		doc = etree.XML( xmlString )
		self.assertEqual( doc.tag, "{http://www.w3.org/1999/xhtml}html" ) # root
		self.assertNotEquals( doc.find( ".//{http://www.w3.org/1999/xhtml}table" ), None )
		self.assertNotEquals( doc.find( ".//{http://www.w3.org/1999/xhtml}td" ), None )

	def testConvertXmlReportToHtmlWithoutLxml( self ):
		# write a new method implementation
		def hasXsltSupport_new( self ):
			return False

		converter = XmlReportConverter( self._getXmlReport() )
		replace_bound_method( converter, converter.hasXsltSupport, hasXsltSupport_new ) # replace method

		xmlString = converter.convertToHtml()
		self.assertTrue( xmlString == None, "If no XSLT support is available, converting to HTML should not work" )

	def testConvertXmlReportToText( self ):
		self._executeBuild()
		converter = XmlReportConverter( self._getXmlReport() )
		text = converter.convertToText()

		self.assertTrue( len( text ) > 1000 )

	def testConvertXmlReportToTextSummary( self ):
		MomBuildMockupTestCase.setUp( self, useScm = True ) # enable SCM
		self._executeBuild()
		converter = XmlReportConverter( self._getXmlReport() )
		text = converter.convertToTextSummary()

		self.assertTrue( len( text ) > 100 )

	def testXmlReportGenerator( self ):
		generator = XmlReportGenerator()
		self.build.addPlugin( generator )
		self._executeBuild()

		reportContent = self._getXmlReport().getReport()
		filePath = generator.getReportFile()

		self.assertTrue( os.path.exists( filePath ), "Log file does not exist" )

		# check file content
		with open( filePath ) as file:
			fileContent = file.read()
			self.assertNotEqual( len( fileContent ), 0, "Log file is empty" )

#		f1 = open( "/tmp/workfile1", 'w' )
#		f2 = open( "/tmp/workfile2", 'w' )
#		f1.write( reportContent )
#		f2.write( fileContent )

		doc1 = etree.XML( reportContent )
		doc2 = etree.XML( fileContent )

		self.assertTrue( xml_compare( doc1, doc2 ), "Report file content differs from report output" )

	def testXmlReportOnStepFailure( self ):
		self._executeBuild()

		def failed_new( self ):
			return Step.Result.Failure

		step = self.project.getStep( 'cleanup' )
		replace_bound_method( step, step.getResult, failed_new )

		converter = XmlReportConverter( self._getXmlReport() )
		logText = converter.convertToFailedStepsLog()

		self.assertTrue( "cleanup" in logText )

	def testXmlReportOnException( self ):
		# Covers runSetups phase

		def runSetups_new( self ):
			raise MomError( "Test Error" )

		# inject erroneous method
		replace_bound_method( self.build, self.build.runSetups, runSetups_new )

		self._executeBuild()
		doc = etree.XML( self._getXmlReport().getReport() )

		e = self.EXCEPTION_LOCATION
		self._testBasicDocumentAttributes( doc )
		self.assertNotEquals( doc.find( e ), None )
		self.assertNotEquals( doc.find( "{0}/description".format( e ) ), None )
		self.assertNotEquals( doc.find( "{0}/traceback".format( e ) ), None )

		self.assertTrue( "self.runSetups()" in doc.find( "{0}/traceback".format( e ) ).text )

		if etree.__name__ == "lxml.etree":
			self.assertNotEquals( doc.find( '{0}[@returncode="{1}"]'.format( e, MomError.getReturnCode() ) )
								, None, "Wrong returncode in exception" )

	def testXmlReportOnException1( self ):
		# Covers runPreflightChecks phase

		# inject erroneous method
		def runPreFlightChecks_new( self ):
			raise ConfigurationError( "Test Error" )
		replace_bound_method( self.build, self.build.runPreFlightChecks, runPreFlightChecks_new )

		self._executeBuild()
		doc = etree.XML( self._getXmlReport().getReport() )

		e = self.EXCEPTION_LOCATION
		self._testBasicDocumentAttributes( doc )
		self.assertNotEquals( doc.find( e ), None )
		self.assertNotEquals( doc.find( "{0}/description".format( e ) ), None )
		self.assertNotEquals( doc.find( "{0}/traceback".format( e ) ), None )

		self.assertTrue( "self.runPreFlightChecks()" in doc.find( "{0}/traceback".format( e ) ).text )

		if etree.__name__ == "lxml.etree":
			self.assertNotEquals( doc.find( '{0}[@returncode="{1}"]'.format( e, ConfigurationError.getReturnCode() ) )
								, None, "Wrong returncode in exception" )

	def testXmlReportOnException2( self ):
		# Covers run phase

		# inject erroneous method
		def runExecute_new( self ):
			raise BuildError( "Test Error" )
		replace_bound_method( self.build, self.build.runExecute, runExecute_new )

		self._executeBuild()
		doc = etree.XML( self._getXmlReport().getReport() )

		# only minor checks, rest already covered in previous tests
		e = self.EXCEPTION_LOCATION
		self._testBasicDocumentAttributes( doc )
		self.assertNotEquals( doc.find( e ), None )

		self.assertTrue( "self.runExecute()" in doc.find( "{0}/traceback".format( e ) ).text )

	def testXmlReportOnUnicodeOutput( self ):
		# inject plugin producing unicode strings
		class TestPlugin( Plugin ):
			def setup( self ):
				raise MomError( u"äöü" )

		self.build.addPlugin( TestPlugin() )

		self._executeBuild()

		converter = XmlReportConverter( self._getXmlReport() )
		text = converter.convertToText()

		self.assertTrue( u"äöü" in text )

	def testXmlReportOnUnicodeFromApplicationOutput( self ):

		class TestPlugin( Plugin ):
			EXECUTABLE = ['python', os.path.join( self.MY_DIRECTORY, '..', 'scripts', 'print_unicode_output.py' )]

			def setup( self ):
				step = self.getInstructions().getStep( 'cleanup' )
				action = ShellCommandAction( command = self.EXECUTABLE )
				step.addMainAction( action )

		self.build.addPlugin( TestPlugin() )
		self._executeBuild()

		converter = XmlReportConverter( self._getXmlReport() )
		converter.convertToText() # test if conversion does not crash something

		self.assertTrue( self.build.getReturnCode() == 0 )

	def testXmlReportOnExceptionInXmlReportGeneration( self ):
		# inject invalid XML template function into plugin
		def command_new( self ):
			raise MomError( "Test Error" )
		logger = ConsoleLogger()
		self.build.addPlugin( logger )
		replace_bound_method( logger, logger.getObjectStatus, command_new )

		self._executeBuild()

		converter = XmlReportConverter( self._getXmlReport() )
		text = converter.convertToText()

		self.assertTrue( "Exception" in text )

if __name__ == "__main__":
	unittest.main()
