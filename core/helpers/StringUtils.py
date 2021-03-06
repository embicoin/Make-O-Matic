# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

from optparse import IndentedHelpFormatter
import textwrap

# not our code, let pylint ignore this
# pylint: disable-all
class IndentedHelpFormatterWithNL( IndentedHelpFormatter ):
	"""Workaround for optparse not accepting newlines in the description string

	\author Tim Chase
	\see http://groups.google.com/group/comp.lang.python/browse_frm/thread/6df6e6b541a15bc2/09f28e26af0699b1"""

	def format_description( self, description ):
		if not description: return ""
		desc_width = self.width - self.current_indent
		indent = " " * self.current_indent
# the above is still the same
		bits = description.split( '\n' )
		formatted_bits = [
			textwrap.fill( bit,
				desc_width,
				initial_indent = indent,
				subsequent_indent = indent )
			for bit in bits]
		result = "\n".join( formatted_bits ) + "\n"
		return result

	def format_option( self, option ):
		# The help for each option consists of two parts:
		#	 * the opt strings and metavars
		#	 eg. ("-x", or "-fFILENAME, --file=FILENAME")
		#	 * the user-supplied help string
		#	 eg. ("turn on expert mode", "read data from FILENAME")
		#
		# If possible, we write both of these on the same line:
		#	 -x		turn on expert mode
		#
		# But if the opt string list is too long, we put the help
		# string on a second line, indented to the same column it would
		# start in if it fit on the first line.
		#	 -fFILENAME, --file=FILENAME
		#			 read data from FILENAME
		result = []
		opts = self.option_strings[option]
		opt_width = self.help_position - self.current_indent - 2
		if len( opts ) > opt_width:
			opts = "%*s%s\n" % ( self.current_indent, "", opts )
			indent_first = self.help_position
		else: # start help on same line as opts
			opts = "%*s%-*s	" % ( self.current_indent, "", opt_width, opts )
			indent_first = 0
		result.append( opts )
		if option.help:
			help_text = self.expand_default( option )
# Everything is the same up through here
			help_lines = []
			for para in help_text.split( "\n" ):
				help_lines.extend( textwrap.wrap( para, self.help_width ) )
# Everything is the same after here
			result.append( "%*s%s\n" % ( 
				indent_first, "", help_lines[0] ) )
			result.extend( ["%*s%s\n" % ( self.help_position, "", line )
				for line in help_lines[1:]] )
		elif opts[-1] != "\n":
			result.append( "\n" )
		return "".join( result )

def to_unicode_or_bust( obj, encoding = 'utf-8' ):
	if isinstance( obj, basestring ):
		if not isinstance( obj, unicode ):
			obj = unicode( obj, encoding )
	return unicode( obj )

def make_posixpath( path ):
	"""Convenience method for replacing windows path separators to unix separators"""

	if not path:
		return None

	return path.replace( "\\", "/" )
