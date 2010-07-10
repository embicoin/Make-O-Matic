# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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
import datetime

def formattedTimeDelta( t ):
	return formattedDuration( t.seconds + 60 * 60 * 24 * t.days )

def formattedDuration( noOfSeconds ):
	"""Returns a printable string that contains the duration in readable format"""
	# static definitions: 
	Second = 1
	Minute = 60 * Second
	Hour = 60 * Minute
	Day = 24 * Hour
	# make the string: 
	Days = int( noOfSeconds / Day )
	Hours = int( noOfSeconds / Hour ) % 24
	Minutes = int( noOfSeconds / Minute ) % 60
	Seconds = noOfSeconds % 60
	text = ''
	if Days > 0:
		text += str( Days ) + 'd '
	if Hours > 0:
		text += str( Hours ) + 'h '
	if Minutes > 0:
		text += str( Minutes ) + 'min '
	text += str( Seconds )
	if Seconds == 1:
		text += 'sec'
	else:
		text += 'secs'
	if not text:
		text = '---'
	return text

class TimeKeeper( object ):
	'''TimeKeeper records the time an operation took.'''

	def __init__( self ):
		'''	Constructor'''
		self.__startTime = None
		self.__stopTime = None

	def start( self ):
		self.__startTime = datetime.datetime.utcnow()

	def getStartTime( self ):
		return self.__startTime

	def stop( self ):
		self.__stopTime = datetime.datetime.utcnow()

	def getStopTime( self ):
		return self.__stopTime

	def delta( self ):
		if not self.getStartTime() or not self.getStopTime():
			return 0
		return self.getStopTime() - self.getStartTime()

	def deltaString( self ):
		if not self.getStartTime() or not self.getStopTime():
			return '[--:--.---]'
		return formattedTimeDelta( self.delta() )

