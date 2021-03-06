# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# 
# Make-O-Matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Make-O-Matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.

from core.MObject import MObject
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP, SMTPHeloError, SMTPAuthenticationError, SMTPException, SMTPRecipientsRefused
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.Exceptions import ConfigurationError
from email.header import Header
from email.mime.base import MIMEBase
import bz2
from email import Encoders

class Email( MObject ):
	""" Convenience class for sending Emails

	Note: Use UTF-8 encoding for all entities! """

	def __init__( self, name = None ):
		MObject.__init__( self, name )

		self.__mixedPart = MIMEMultipart( 'mixed' )
		self.__mixedPart.set_charset( "utf-8" )

		self.__recipients = []

	def _getMessage( self ):
		return self.__mixedPart

	def setCustomHeader( self, key, value ):
		""" Set custom X-tag

		Usage: setCustomHeader("MOM-Version", "0.1")
		Result: X-MOM-Version: 0.1 in resulting E-Mail"""

		self._getMessage()[ 'X-{0}'.format( key ) ] = value

	def setFromAddress( self, address ):
		self._getMessage()[ 'From' ] = address

	def getFromAddress( self ):
		return self._getMessage()[ 'From' ]

	def addToAddresses( self, addresses ):
		assert isinstance( addresses, list )
		self.setToAddresses( self.getToAddresses() + addresses )

	def setToAddresses( self, addresses ):
		self.__recipients = list( set( addresses ) ) # remove duplicates

	def getToAddresses( self ):
		return self.__recipients

	def setSubject( self, subject ):
		"""\warning Can only be set once!"""

		assert( not self._getMessage()['Subject'] )

		# Need to use Header class to use UTF-8 encoded text
		# see http://docs.python.org/library/email.header.html
		h = Header( subject, 'utf-8' )
		self._getMessage()['Subject'] = h

	def getSubject( self ):
		return unicode( self._getMessage()['Subject'] )

	def addTextAttachment( self, text, filename, useCompression = False ):
		if useCompression:
			part = MIMEBase( 'application', 'bzip2' )
			part.set_payload( bz2.compress( text.encode( "utf-8" ) ) )
			Encoders.encode_base64( part )
			filename += ".bz2"
		else:
			part = MIMEText( 'plain' )
			part.set_payload( text.encode( "utf-8" ) )
		part.add_header( 'Content-Disposition', 'attachment; filename={0}'.format( filename ) )
		self.__mixedPart.attach( part )

	def attachTextPart( self, text ):
		part = MIMEText( text.encode( "utf-8" ), 'plain', _charset = 'utf-8' )
		self.__mixedPart.attach( part )

	def attachAlternativeTextPart( self, textString, htmlString ):
		"""Attach a multipart part to this message.

		If htmlString is None, only a text part is added."""

		if not htmlString:
			self.attachTextPart( textString )
			return

		part1 = MIMEText( ( textString or '' ).encode( "utf-8" ), 'plain', _charset = 'utf-8' )
		part2 = MIMEText( ( htmlString or '' ).encode( "utf-8" ), 'html', _charset = 'utf-8' )
		alternativePart = MIMEMultipart( 'alternative' )
		alternativePart.attach( part1 )
		alternativePart.attach( part2 )
		self.__mixedPart.attach( alternativePart )

	def getMessageText( self, recipient ):
		"""Get final message text for recipient

		\param recipient is a string containing an E-Mail address"""

		message = self._getMessage()

		# finalize Email at the end, the 'To'-field can only be set once
		del message['To'] # must be deleted before being re-set
		message['To'] = recipient

		return message.as_string()

class Emailer( MObject ):

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__server = None

	def setup( self ):
		server = mApp().getSettings().get( Settings.EmailerSmtpServer, False )
		if not server:
			raise ConfigurationError( 'No emailer SMTP server specified, please check configuration!' )
		self.__server = SMTP( server )
		#self.__server.set_debuglevel( 3 )
		if mApp().getSettings().get( Settings.EmailerUseTls, False ):
			self.__server.starttls()
			self.__server.ehlo()
		if mApp().getSettings().get( Settings.EmailerDoLogin, False ):
			user = mApp().getSettings().get( Settings.EmailerUsername )
			password = mApp().getSettings().get( Settings.EmailerPassword )
			try:
				self.__server.login( user, password )
			except SMTPHeloError as e:
				raise ConfigurationError( 'The SMTP server rejected the connection: {0}'.format( e ) )
			except SMTPAuthenticationError as e:
				raise ConfigurationError( 'Emailer error, login failed: {0}'.format( e ) )
			except SMTPException as e:
				raise ConfigurationError( 'Emailer error, no suitable authentication method was found: {0}'.format( e ) )


	def send( self, email ):
		addresses = email.getToAddresses()
		if email.getFromAddress() and len( addresses ) > 0:
			# for each address send out an unique mail with only one 'To' recipient
			for address in addresses:
				try:
					self.__server.sendmail( email.getFromAddress(), address, email.getMessageText( address ) )
				except SMTPRecipientsRefused:
					mApp().debugN( self, 3, "Recipient refused: {0}".format( email.getFromAddress() ) )
		else:
			raise ConfigurationError( 'Sender/recipient addresses missing, cannot send mail!' )

	def quit( self ):
		self.__server.quit()

