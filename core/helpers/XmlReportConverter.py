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

from __future__ import unicode_literals

from core.Exceptions import ConfigurationError, MomError, returncode_to_description, BuildError
from core.MObject import MObject
from core.executomat.Step import Step
from core.helpers.GlobalMApp import mApp
from core.helpers.TimeKeeper import formatted_time_delta
from core.helpers.XmlUtils import string_from_node_attribute, string_from_node, float_from_node_attribute, \
	find_nodes_with_attribute_and_value
from datetime import datetime
from io import StringIO
from textwrap import TextWrapper
import codecs
import os.path
import sys
import traceback
import xml.etree.ElementTree


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

class ReportFormat:
	"""Enum-like structure for output format"""

	XML = 0 # no conversion, default
	TEXT = 1
	HTML = 2

	@staticmethod
	def toString( reportFormat ):
		if reportFormat == 0:
			return "XML"
		elif reportFormat == 1:
			return "Plain text"
		elif reportFormat == 2:
			return "HTML"
		else:
			return "Unknown format"

class _MyTextWrapper( TextWrapper ):
	"""TextWrapper Wrapper class ;)
	
	Provides easy access to indent and dedent methods"""

	def indent( self, level = 1, indentString = " " ):
		self.initial_indent = self.subsequent_indent = self.initial_indent + indentString * level

	def dedent( self, level = 1, indentString = " " ):
		self.initial_indent = self.subsequent_indent = self.initial_indent[:-len( indentString ) * level]

	def wrapAndFillLine( self, text, fillChar = '*' ):
		out = []
		out += self.wrap( text )

		# let's fill up the last line with fillChar
		if len( out ) > 0:
			out[-1] += ' ' + ( fillChar * ( self.width - len( out[-1] ) - 1 ) )

		return out

	def wrapMultiLine( self, text, drop_empty_lines = True ):
		out = []
		for line in text.splitlines():
			if not drop_empty_lines and len( line ) == 0:
				out += self.wrap( " " ) # newline
			out += self.wrap( line )

		return out

class XmlReportConverter( MObject ):
	"""Converts a XmlReport instance to HTML, plain text and maybe others

	This is done in multiple ways at the moment
	\li XML: No actions required
	\li Plain text: Deserialize the XML content, generate text output using the lxml classes
	\li others: Use XSL stylesheets to convert XML to the desired format.
	"""

	_XSL_STYLESHEETS = {
		ReportFormat.HTML : "xmlreport2html.xsl",
	}

	def __init__( self, xmlReport ):
		MObject.__init__( self )

		mApp().debugN( self, 4, "Using following etree implementation: {0}. XSLT support: {1}".format( etree.__name__, self.hasXsltSupport() ) )
		if not self.hasXsltSupport():
			mApp().debug( self, "Lacking support for XSLT transformations. Support for HTML conversion not available. Please install the python-lxml package." )

		self.__xmlReport = xmlReport

		# ElementTree.fromstring requires encoded data, fails otherwise
		encodedData = xmlReport.getReport().encode( "utf-8" )
		self.__elementTree = xml.etree.ElementTree.fromstring( encodedData ) # cache ElementTree object

		self.__xslTemplateSnippets = {}
		self.__xmlTemplateFunctions = {}
		self.__registeredPlugins = []

		self._initializeXslTemplates()
		self._fetchTemplates( mApp() )

	def convertTo( self, destinationReportFormat ):
		"""Converts the report to destinationFormat, which is one of the keys in _XSL_STYLESHEETS"""

		if destinationReportFormat == ReportFormat.XML:
			return self.__xmlReport.getReport()
		elif destinationReportFormat == ReportFormat.HTML:
			return self.convertToHtml()
		elif destinationReportFormat == ReportFormat.TEXT:
			return self.convertToText()

	def _initializeXslTemplates( self ):
		"""Load stylesheets from _XSL_STYLESHEETS into memory"""

		for key, value in self._XSL_STYLESHEETS.items():
			try:
				fileName = os.path.dirname( __file__ ) + '/xslt/{0}'.format( value )
				f = codecs.open( fileName, 'r', encoding = "utf-8" )
				parser = etree.XMLParser()
				self.__xslTemplateSnippets[key] = etree.parse( StringIO( f.read() ), parser )
				f.close()
			except KeyError:
				raise MomError( "XSL Stylesheet missing: {0}".format( value ) )
			except etree.XMLSyntaxError, e:
				raise MomError( "XSL Stylesheet for {0} is malformed: {1}".format( ReportFormat.toString( key ), e ) )

	def _fetchTemplates( self, instructions ):
		"""Fetches templates from all registered plugins in the Instruction object
		
		Loops through all plugins from this object and its children recursively."""

		for plugin in instructions.getPlugins():
			# prevent infinite loop on circular plugin dependencies
			if plugin in self.__registeredPlugins:
				mApp().debug( self, "XSLT template already added for plugin {0}".format( plugin.getName() ) )
				continue

			self.__registeredPlugins.append( plugin )

			self._addXslTemplate( plugin )
			self._addXmlTemplate( plugin )

		for child in instructions.getChildren():
			self._fetchTemplates( child ) # enter recursion

	def _addXslTemplate( self, plugin ):
		"""Adds the XSL template to stylesheet if plugin provides one
		
		Merges templates from plugins into the stylesheets provided by XSL_STYLESHEETS."""

		if not self.hasXsltSupport():
			mApp().debugN( self, 5, "Cannot add XSL template, lacking support for XSLT transformations. Please install the python-lxml package." )
			return

		# iterate trough the dict from getXslTemplates(), add each template to the corresponding stylesheet
		for destinationReportFormat, markup in plugin.getXslTemplates().items():
			if not destinationReportFormat in self.__xslTemplateSnippets.keys():
				continue # invalid key, no stylesheet registered for that type of XSL

			# search for place to register new plugin templates
			stylesheet = self.__xslTemplateSnippets[destinationReportFormat]
			pluginTemplate = stylesheet.find( ".//{http://www.w3.org/1999/XSL/Transform}template[@match='plugin']" )
			placeholder = pluginTemplate.find( ".//{http://www.w3.org/1999/XSL/Transform}choose" )

			# create new element with markup provided from plugin
			try:
				element = etree.XML( """<xsl:when xmlns:xsl="http://www.w3.org/1999/XSL/Transform"	
					 xmlns="http://www.w3.org/1999/xhtml"
					 test="@name = '{0}'">{1}</xsl:when>""".format( plugin.getName(), markup ) )
			except etree.XMLSyntaxError:
				raise ConfigurationError( "XSL template of {0} plugin malformed.".format( plugin.getName() ) )

			# insert new element in the placeholder from the stylesheet
			placeholder.insert( 0, element )

	def _addXmlTemplate( self, plugin ):
		"""Adds lxml conversion code if plugin provides one
		
		Adds function pointers to the Plugin.getXmlTemplate() methods so that their parameter list can be evaluated when actually 
		parsing the tree"""

		functionPointer = plugin.getXmlTemplate
		self.__xmlTemplateFunctions[plugin.getName()] = functionPointer

	def getXslTemplate( self, destinationReportFormat ):
		"""Get the current (modified) XSL stylesheet for the requested format

		\return A etree.Element object or None

		\note May return None if format has no XSL stylesheet associated"""

		# text and XML report format do not have a XSL stylesheet, return None
		if not destinationReportFormat in self.__xslTemplateSnippets:
			return None

		return self.__xslTemplateSnippets[destinationReportFormat]

	@classmethod
	def hasXsltSupport( self ):
		return ( etree.__name__ == "lxml.etree" )

	def convertToHtml( self, summaryOnly = False, enableCrossLinking = False ):
		"""Converts the report to HTML using the XSL stylesheet for HTML

		\note Be very sure to catch all exceptions here!"""

		if not self.hasXsltSupport():
			mApp().debugN( self, 5, "Cannot convert to HTML. Lacking support for XSLT transformations. Please install the python-lxml package." )
			return None

		# transform only accepts bytes, we have to "escape" the enableCrossLinking parameter
		summaryOnly = "1" if summaryOnly else "0"
		enableCrossLinkingParam = "1" if enableCrossLinking else "0"

		try:
			def readFile( filePath ):
				f = codecs.open( filePath, 'r', encoding = "utf-8" )
				content = f.read()

				# Note: bug in python-lxml affecting win32: if content contains CR-chars, XSLT.strparam() will HTML-encode these.
				# We don't want that, obviously. Strip out CRs.
				content = content.replace( '\r\n', '\n' )

				f.close()
				return content

			javaScriptFilePath = os.path.join( os.path.dirname( __file__ ), "xslt", "xmlreport2html.js" )
			cssFilePath = os.path.join( os.path.dirname( __file__ ), "xslt", "xmlreport2html.css" )

			transform = etree.XSLT( self.__xslTemplateSnippets[ ReportFormat.HTML ] )
			result = unicode( transform( etree.XML( self.__xmlReport.getReport() ),
					summaryOnly = etree.XSLT.strparam( summaryOnly ),
					enableCrossLinking = etree.XSLT.strparam( enableCrossLinkingParam ),
					javaScriptContent = etree.XSLT.strparam( readFile( javaScriptFilePath ) ),
					cssContent = etree.XSLT.strparam( readFile( cssFilePath ) ) )
			)
		except Exception, e:
			innerTraceback = "".join( traceback.format_tb( sys.exc_info()[2] ) )
			result = """
<html><body><pre>
Could not create HTML report. Caught exception:\n {0}\nTraceback:\n{1}
</pre></body></html>""".format( e, innerTraceback )

		return result

	def convertToText( self, short = False ):
		"""Converts the report to plain text using the recursive _toText() method

		\note Be very sure to catch all exceptions here!"""

		wrapper = _MyTextWrapper( width = 1000 )

		if short:
			ignoredTags = ["traceback"]
		else:
			ignoredTags = []

		try:
			result = "\n".join( self._toText( self.__elementTree, wrapper, ignoredTags ) )
		except Exception, e:
			innerTraceback = "".join( traceback.format_tb( sys.exc_info()[2] ) )
			result = "Could not create report. Caught exception:\n {0}\nTraceback:\n{1}".format( e, innerTraceback )
		return result

	def convertToTextSummary( self ):
		"""Converts the report to plain text summary by using the _non-recursive_ _toTextSummary() method

		\note Be very sure to catch all exceptions here!"""

		wrapper = _MyTextWrapper( replace_whitespace = False, drop_whitespace = False, width = 1000 )

		try:
			result = self._toTextSummary( wrapper )
		except Exception, e:
			innerTraceback = "".join( traceback.format_tb( sys.exc_info()[2] ) )
			result = "Could not create report summary. Caught exception:\n {0}\nTraceback:\n{1}".format( e, innerTraceback )
		return result

	def _toTextSummary( self, wrapper ):
		buildNode = self.__elementTree.find( "build" )

		# calculate round trip time from commit to report
		startTime = float_from_node_attribute( buildNode, "pluginInfo", "commitTime" )
		timeDelta = datetime.utcnow() - datetime.utcfromtimestamp( startTime )

		# TODO: Replace this by timedelta.total_seconds() once we're depending on Python 2.7
		# This is a work around for Python < 2.7 to get the total seconds of a timedelta
		total_seconds = timeDelta.days * 86400 + timeDelta.seconds

		if total_seconds > 0:
			roundTripTime = formatted_time_delta( timeDelta )
		else:
			# something went wrong calculating the RTT. is the systime correct?
			roundTripTime = "N/A"

		out = []

		# START: Summary
		out += wrapper.wrap( "*** Build report: {0}, {1} ***".format( 
				buildNode.attrib["name"],
				buildNode.attrib["sys-shortname"] ),
		)

		wrapper.indent()

		# show failed steps if any
		failedSteps = set( [] )
		for node in find_nodes_with_attribute_and_value( buildNode, "step", "result", "Failure" ):
			failedSteps.add( node.attrib["name"] )

		out += wrapper.wrap( "Build status: {0} {1}".format( 
				"success" if int( buildNode.attrib["returncode"] ) == 0 else "ERROR",
				"({0} failed)".format( ", ".join( failedSteps ) ) if len ( failedSteps ) > 0 else ""
				) )

		# only show exception description if there actually is an exception 
		if buildNode.find( "exception" ) != None:
			out += wrapper.wrap( "Description:  {0}".format( string_from_node( buildNode, "exception/description" ) ) )

		# show client information
		out += wrapper.wrap( "Client:       {0}, {1}".format( buildNode.attrib["sys-platform"], buildNode.attrib["sys-platform-details"] ) )

		# only show detailed summary on success or build error
		returnCode = int ( buildNode.attrib["returncode"] )
		if returnCode in ( 0, BuildError.getReturnCode() ):
			out += wrapper.wrap( "Commit:       {0}, revision: {1}".format( 
					string_from_node_attribute( buildNode, "pluginInfo", "committerName" ),
					string_from_node_attribute( buildNode, "pluginInfo", "revision" ) ) )
			out += wrapper.wrap( "Time:         {0}".format( 
					string_from_node_attribute( buildNode, "pluginInfo", "commitTimeReadable" ) ) )

			wrapper.indent( indentString = "| " )
			out += wrapper.wrapMultiLine( string_from_node( buildNode, "commitMessage" ), drop_empty_lines = False )
			wrapper.dedent( indentString = "  " )

			# additional plugin info
			out += " "
			out += wrapper.wrap( "Additional plugin info:" )
			wrapper.indent( indentString = "* " )
			publisherNodes = find_nodes_with_attribute_and_value( buildNode, "plugin", "pluginType", "publisher" )
			for publisherNode in publisherNodes:
				out += wrapper.wrap( "{0}: {1}".format( 
					publisherNode.attrib["name"],
					string_from_node( publisherNode, "objectstatus" )
				) )
			wrapper.dedent( indentString = "  " )

		wrapper.dedent()

		out += wrapper.wrap( "*** Build time: {0}, round trip time: {1} ***".format( 
				string_from_node_attribute( buildNode, "build", "timing" ),
				roundTripTime ),
		)
		# END: Summary

		out += " "

		return "\n".join( out )

	def convertToFailedStepsLog( self ):
		# no wrapper needed

		out = []
		element = self.__elementTree

		failedSteps = find_nodes_with_attribute_and_value( element, "step", "result", "Failure" )
		for step in failedSteps:
			out += ["*** Step failed: {0} ***".format( step.attrib["name"] )]

			failedActions = step.findall( 'action' )
			for action in failedActions:
				if action.attrib["returncode"] == "0":
					continue # do not show successful actions

				out += ["* Action: {0} *".format( action.find( "logdescription" ).text )]
				out += ["STDOUT:"]
				out += [action.find( "stdout" ).text or ""]
				out += ["STDERR:"]
				out += [action.find( "stderr" ).text or ""]
				out += " "
			out += " "

		return "\n".join( out )

	@classmethod
	def _statesToStringList( self, element ):
		states = []
		if element.attrib["isEnabled"] == "False":
			states.append( "disabled" )
		if element.attrib["isOptional"] == "True":
			states.append( "optional" )
		return states

	def _toText( self, element, wrapper, ignoredTags ):
		"""Recursive method for parsing an ElementTree and converting it to plain text"""

		out = []

		if element.tag in ignoredTags:
			return out

		# exception stuff
		if element.tag == "exception":
			out += " "
			out += wrapper.wrap( "Exception: {1} (returned {0})".format( element.attrib["returncode"], element.attrib["type"] ) )
		elif element.tag == "description":
			out += wrapper.wrapMultiLine( "Description: {0}".format( element.text ) )
		elif element.tag == "traceback":
			out += wrapper.wrapMultiLine( element.text )

		elif element.tag == "build":
			out += wrapper.wrap( "Build: {0}".format( element.attrib["name"] ) )
			out += " "
			wrapper.indent()
			out += wrapper.wrap( "Platform:     {0} ({1})".format( element.attrib["sys-platform"], element.attrib["sys-platform-details"] ) )
			out += wrapper.wrap( "Architecture: {0}".format( element.attrib["sys-architecture"] ) )
			out += wrapper.wrap( "Node name:    {0}".format( element.attrib["sys-nodename"] ) )
			out += " "
			out += wrapper.wrap( "Build status: {0}".format( returncode_to_description( int( element.attrib["returncode"] ) ) ) )
			out += " "
			out += wrapper.wrap( "Build time: {0}".format( element.attrib["timing"] ) )
			wrapper.dedent()

		elif element.tag == "project":
			out += " "
			out += wrapper.wrap( "Project: {0}".format( element.attrib["name"] ) )

		elif element.tag == "plugins": # container element
			if len( element.getchildren() ) > 0:
				out += " "
				out += wrapper.wrap( "Plugins:" )

		elif element.tag == "plugin":
			# show plugin info like optional or disabled status
			states = self._statesToStringList( element )
			if len( states ) > 0:
				name = "{0} [{1}]".format( element.attrib["name"], ", ".join( states ) )
			else:
				name = element.attrib["name"]

			# show description if any
			description = element.find( "objectstatus" ).text
			if description:
				out += wrapper.wrap( "{0}: {1}".format( name, description ) )
			else:
				out += wrapper.wrap( name )

			# evaluate plugin specific getXmlTemplate method here to show extra information
			pluginInfo = element.find( "pluginInfo" )

			if name in self.__xmlTemplateFunctions:
				wrapper.indent()
				try:
					text = self.__xmlTemplateFunctions[name]( pluginInfo, wrapper )
				except Exception, e:
					mApp().debug( self, "Exception in getXmlTemplate function for plugin {0}: {1}".format( name, e ) )
					mApp().debug( self, traceback.format_exc() )
					text = wrapper.wrap( "(Exception while getting plugin report, see log)" )
				wrapper.dedent()

				if text is not None:
					out += text

		elif element.tag == "configuration":
			out += " "
			out += wrapper.wrap( "Configuration: {0} [{1}]".format( 
					element.attrib["name"],
					"success" if element.attrib["failed"] == "False" else "FAILED"
			) )

		elif element.tag == "environments":
			out += " "

			states = self._statesToStringList( element )
			if len( states ) > 0:
				name = "{0} [{1}]".format( element.attrib["name"], ", ".join( states ) )
			else:
				name = element.attrib["name"]

			out += wrapper.wrap( "Environments: {0} ({1})".format( 
					name,
					element.find( "objectstatus" ).text
			) )

			# if there are no configurations attached: hide environments content, stop recursion here
			if len( element.getchildren() ) == 0:
				return out

		elif element.tag == "environment":
			out += " "
			out += wrapper.wrap( "Environment: {0} [{1}]".format( 
					element.attrib["name"],
					"success" if element.attrib["failed"] == "False" else "FAILED"
			) )

		elif element.tag == "steps": # container element
			if len( element.getchildren() ) > 0:
				out += " "
				out += wrapper.wrap( "Steps:" )

		elif element.tag == "step":
			if element.attrib["isEmpty"] == "True":
				return out # do not show empty step

			out += wrapper.wrap( '{0} [{1}]: Step "{2}" (took {3})'.format( 
				Step.Status.getDescriptionFromKey( element.attrib["status"] ),
				Step.Result.getDescriptionFromKey( element.attrib["result"] ),
				element.attrib["name"] ,
				element.attrib["timing"]
			) )

			if element.attrib["result"] == "Success":
				return out # do not show children if result is okay

		wrapper.indent()
		for childElement in element.getchildren():
			out += self._toText( childElement, wrapper, ignoredTags ) # enter recursion
		wrapper.dedent()

		return out
