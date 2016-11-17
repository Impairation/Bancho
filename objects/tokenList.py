import threading
import time

from common.ripple import userUtils
from common.log import logUtils as log
from constants import serverPackets
from events import logoutEvent
from objects import glob
from objects import osuToken


class tokenList:
	"""
	List of connected osu tokens

	tokens -- dictionary. key: token string, value: token object
	"""

	def __init__(self):
		"""
		Initialize a tokens list
		"""
		self.tokens = {}

	def addToken(self, userID, ip = "", irc = False, timeOffset=0, tournament=False):
		"""
		Add a token object to tokens list

		userID -- user id associated to that token
		irc -- if True, set this token as IRC client
		return -- token object
		"""
		newToken = osuToken.token(userID, ip=ip, irc=irc, timeOffset=timeOffset, tournament=tournament)
		self.tokens[newToken.token] = newToken
		return newToken

	def deleteToken(self, token):
		"""
		Delete a token from token list if it exists

		token -- token string
		"""
		if token in self.tokens:
			# Delete session from DB
			if self.tokens[token].ip != "":
				userUtils.deleteBanchoSessions(self.tokens[token].userID, self.tokens[token].ip)

			# Pop token from list
			self.tokens.pop(token)

	def getUserIDFromToken(self, token):
		"""
		Get user ID from a token

		token -- token to find
		return -- false if not found, userID if found
		"""
		# Make sure the token exists
		if token not in self.tokens:
			return False

		# Get userID associated to that token
		return self.tokens[token].userID

	def getTokenFromUserID(self, userID, ignoreIRC=False):
		"""
		Get token from a user ID

		userID -- user ID to find
		return -- False if not found, token object if found
		"""
		# Make sure the token exists
		for _, value in self.tokens.items():
			if value.userID == userID:
				if ignoreIRC and value.irc:
					continue
				return value

		# Return none if not found
		return None

	def getTokenFromUsername(self, username, ignoreIRC=False, safe=False):
		"""
		Get an osuToken object from an username

		:param username: normal username or safe username
		:param ignoreIRC: if True, consider bancho clients only and skip IRC clients
		:param safe: if True, username is a safe username,
		compare it with token's safe username rather than normal username
		:return: osuToken object or None
		"""
		# lowercase
		who = username.lower() if not safe else username

		# Make sure the token exists
		for _, value in self.tokens.items():
			if (not safe and value.username.lower() == who) or (safe and value.safeUsername == who):
				if ignoreIRC and value.irc:
					continue
				return value

		# Return none if not found
		return None

	def deleteOldTokens(self, userID):
		"""
		Delete old userID's tokens if found

		userID -- tokens associated to this user will be deleted
		"""
		# Delete older tokens
		for key, value in list(self.tokens.items()):
			if value.userID == userID:
				# Delete this token from the dictionary
				self.tokens[key].kick("You have logged in from somewhere else. You can't connect to Bancho/IRC from more than one device at the same time.", "kicked, multiple clients")

	def multipleEnqueue(self, packet, who, but = False):
		"""
		Enqueue a packet to multiple users

		packet -- packet bytes to enqueue
		who -- userIDs array
		but -- if True, enqueue to everyone but users in who array
		"""
		for _, value in self.tokens.items():
			shouldEnqueue = False
			if value.userID in who and not but:
				shouldEnqueue = True
			elif value.userID not in who and but:
				shouldEnqueue = True

			if shouldEnqueue:
				value.enqueue(packet)

	def enqueueAll(self, packet):
		"""
		Enqueue packet(s) to every connected user

		packet -- packet bytes to enqueue
		"""
		for _, value in self.tokens.items():
			value.enqueue(packet)

	def usersTimeoutCheckLoop(self, timeoutTime = 100, checkTime = 100):
		"""
		Deletes all timed out users.
		If called once, will recall after checkTime seconds and so on, forever
		CALL THIS FUNCTION ONLY ONCE!

		timeoutTime - seconds of inactivity required to disconnect someone (Default: 100)
		checkTime - seconds between loops (Default: 100)
		"""
		log.debug("Checking timed out clients")
		timedOutTokens = []		# timed out users
		timeoutLimit = int(time.time())-timeoutTime
		for key, value in self.tokens.items():
			# Check timeout (fokabot is ignored)
			if value.pingTime < timeoutLimit and value.userID != 999 and value.irc == False and value.tournament == False:
				# That user has timed out, add to disconnected tokens
				# We can't delete it while iterating or items() throws an error
				timedOutTokens.append(key)

		# Delete timed out users from self.tokens
		# i is token string (dictionary key)
		for i in timedOutTokens:
			log.debug("{} timed out!!".format(self.tokens[i].username))
			self.tokens[i].enqueue(serverPackets.notification("Your connection to the server timed out."))
			logoutEvent.handle(self.tokens[i], None)

		# Schedule a new check (endless loop)
		threading.Timer(checkTime, self.usersTimeoutCheckLoop, [timeoutTime, checkTime]).start()

	def spamProtectionResetLoop(self):
		"""
		Reset spam rate every 10 seconds.
		CALL THIS FUNCTION ONLY ONCE!
		"""
		# Reset spamRate for every token
		for _, value in self.tokens.items():
			value.spamRate = 0

		# Schedule a new check (endless loop)
		threading.Timer(10, self.spamProtectionResetLoop).start()

	def deleteBanchoSessions(self):
		"""
		Truncate bancho_sessions table.
		Call at bancho startup to delete old cached sessions
		"""
		glob.db.execute("TRUNCATE TABLE bancho_sessions")

	def tokenExists(self, username = "", userID = -1):
		"""
		Check if a token exists (aka check if someone is connected)

		username -- Optional.
		userID -- Optional.
		return -- True if it exists, otherwise False

		Use username or userid, not both at the same time.
		"""
		if userID > -1:
			return True if self.getTokenFromUserID(userID) is not None else False
		else:
			return True if self.getTokenFromUsername(username) is not None else False
