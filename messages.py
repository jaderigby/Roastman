import helpers, json

actionList = json.loads(helpers.read_file('{}/{}'.format(helpers.path('util'), 'action-list.json')))

def statusMessage():
	if len(actionList['actions']) > 0:
		print("")
		for item in actionList['actions']:
			print('''[ {} {} ]\t\t{}'''.format(actionList['alias'], item['name'], item['description']))
		print("")
	else:
		print('''
Roastman is working successfully!
''')

def done():
	print('''
[ Process Completed ]
''')

def example():
	print('''
process working!
''')
	
def exiting():
	print('''
Exiting ...
''')
	
def running(ITEM):
	print('''
Currently running: {}
'''.format(ITEM))

def now_running(ITEM):
	print('''
===========================================
	Now running: {}()
===========================================
'''.format(ITEM))

def not_runnable(ITEM):
	print('''
===========================================
	Error: {}() is not runnable
===========================================
'''.format(ITEM))

def curl_result(ITEM):
	parsed = json.loads(ITEM)
	result = json.dumps(parsed, indent=4)
	print('''{}
'''.format(helpers.decorate('green', result)))

def response_error(ITEM):
	print('\n{}\n'.format(helpers.decorate('yellow', ITEM)))

def running_from(ITEM):
	print('\n{}: {}\n'.format(
		helpers.decorate('bold', 'Running Roastman Collections from'),
		helpers.decorate('yellow', ITEM)
	))

def request_selection(ITEM):
	print('\nRunning request: {}\n'.format(helpers.decorate('green', ITEM)))
