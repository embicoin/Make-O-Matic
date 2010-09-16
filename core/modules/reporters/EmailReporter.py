# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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

from core.modules.Reporter import Reporter
from core.modules.reporters.XmlReport import XmlReport
from core.helpers.GlobalMApp import mApp
from core.helpers.Emailer import Email, Emailer
from core.helpers.XmlReportConverter import XmlReportConverter
from core.Build import Build
from core.Settings import Settings
from core.Exceptions import MomError, BuildError, ConfigurationError

class EmailReporter( Reporter ):

	def __init__( self, name = None ):
		Reporter.__init__( self, name )

	def wrapUp( self ):
		instructions = mApp()
		assert isinstance( instructions, Build )

		# get settings
		reporterDefaultRecipients = mApp().getSettings().get( Settings.EmailReporterDefaultRecipients )
		reporterConfigurationErrorRecipients = mApp().getSettings().get( Settings.EmailReporterConfigurationErrorRecipients )
		reporterMomErrorRecipients = mApp().getSettings().get( Settings.EmailReporterMomErrorRecipients )
		reporterSender = mApp().getSettings().get( Settings.EmailReporterSender )
		reporterEnableHtml = mApp().getSettings().get( Settings.EmailReporterEnableHtml )

		# get project info
		returnCode = mApp().getReturnCode()
		scm = instructions.getProject().getScm()
		info = scm.getRevisionInfo()

		# header
		email = Email()
		email.setSubject( 'Build report for {0}, revision {1}'.format( instructions.getName(), info.revision ) )
		email.setFromAddress( reporterSender )
		email.setToAddresses( [reporterDefaultRecipients] )

		if returnCode == 0: # no error
			pass

		elif returnCode == BuildError.getReturnCode():
			if mApp().getSettings().get( Settings.EmailReporterNotifyCommitterOnFailure ):
				email.addToAddress( info.committerEmail )

		elif returnCode == ConfigurationError.getReturnCode():
			if reporterConfigurationErrorRecipients:
				email.addToAddress( reporterConfigurationErrorRecipients )

		elif returnCode == MomError.getReturnCode():
			if reporterMomErrorRecipients is not None:
				email.addToAddress( reporterMomErrorRecipients )

		if len( email.getToAddresses() ) == 0:
			mApp().debug( self, 'Not sending mail, no recipients added' )
			return

		# body
		report = XmlReport( instructions )
		report.prepare()
		conv = XmlReportConverter( report )

		if reporterEnableHtml:
			email.addHtmlPart( conv.convertToHtml() )
		else:
			email.addTextPart( conv.convertToText() )

		# send mail
		e = Emailer( 'Emailer' )
		try:
			e.setup()
			e.send( email )
			e.quit()
			mApp().debug( self, 'Sent E-Mail to following recipients: {0}'.format( ", ".join( email.getToAddresses() ) ) )
		except Exception as e:
			mApp().debug( self, 'Sending E-Mail failed: {0}'.format( e ) )
