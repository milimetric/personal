import os

GlobalRootDirectory = os.path.abspath(os.path.dirname(__file__))
GlobalIsInDebug = os.environ['SERVER_SOFTWARE'].startswith('Dev')
#GlobalSettings = { 'someSetting' : 'someValue' }
