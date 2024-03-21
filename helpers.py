import json
from settings import settings

profilePath = settings['profile_url'] + settings['profile']

def load_profile():
	import os
	return json.loads(read_file(profilePath)) if os.path.exists(profilePath) else json.loads("{}")

def get_settings():
	profile = load_profile()
	if 'settings' in profile:
		for key in profile['settings']:
			settings[key] = profile['settings'][key]
	return settings

def run_command_output(CMD, option = True):
	import subprocess
	if option:
		print('\n============== Outputting Command: {}\n'.format(CMD))
	result = False
	if CMD != None:
		process = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		out, err = process.communicate()

		if err:
			print(err)
		
		else:
			result = out.decode('utf-8')

	return result

def path(TYPE):
	import os
	if TYPE == 'user':
		return os.path.expanduser('~/')
	elif TYPE == 'util' or TYPE == 'utility':
		return os.path.dirname(os.path.realpath(__file__))
	elif TYPE == 'current':
		return run_command_output('pwd', False).replace('\n', '')
	else:
		return False

def read_file(FILEPATH):
	FILE = open(FILEPATH, 'r')
	data = FILE.read()
	FILE.close()
	return data

def write_file(FILEPATH, DATA):
	with open(FILEPATH, 'w') as f: f.write(DATA)

def run_command(CMD, option = True):
	import subprocess
	shellStatus = True
	str = ''
	showCmd = CMD
	if isinstance(CMD, list):
		shellStatus = False
		for item in CMD:
			str += (' ' + item)
		showCmd = str
	if option:
		print('\n============== Running Command: {}\n'.format(showCmd))
	subprocess.call(CMD, shell=shellStatus)

def decorate(COLOR, STRING):
	bcolors = {
		 'lilac' : '\033[95m'
		,'blue' : '\033[94m'
		,'cyan' : '\033[96m'
		,'green' : '\033[92m'
		,'yellow' : '\033[93m'
		,'red' : '\033[91m'
		,'bold' : '\033[1m'
		,'underline' : '\033[4m'
		,'endc' : '\033[0m'
	}

	return bcolors[COLOR] + STRING + bcolors['endc']

def user_input(STRING):
	try:
		return raw_input(STRING)
	except:
		return input(STRING)

def list_expander(LIST):
    baseList = LIST.replace(' ', '').split(',')
    expandedList = []
    for item in baseList:
        if '-' in item:
            rangeList = item.split('-')
            tempList = [elem for elem in range(int(rangeList[0]), int(rangeList[1]) + 1)]
            expandedList += tempList
        else:
            expandedList.append(int(item))
    return expandedList

# generates a user selection session, where the passed in list is presented as numbered selections; selecting "x" or just hitting enter results in the string "exit" being returned. Any invaild selection is captured and presented with the message "Please select a valid entry"
def user_selection(DESCRIPTION, LIST, LIST_SELECT = False):
	import re
	str = ''
	for i, item in enumerate(LIST, start=1):
		str += '\n[{index}] {item}'.format(index=i, item=item)
	str += '\n\n[x] Exit\n'

	finalAnswer = False

	while True:
		print(str)
		selection = user_input('{}'.format(DESCRIPTION))
		pat = re.compile("[0-9,\- ]+") if LIST_SELECT else re.compile("[0-9]+")
		if pat.match(selection):
			selection = list_expander(selection) if LIST_SELECT else int(selection)
		if isinstance(selection, int) or isinstance(selection, list):
			finalAnswer = selection
			break
		elif selection == 'x':
			finalAnswer = 'exit'
			break
		elif selection == '':
			finalAnswer = 'exit'
			break
		else:
			print("\nPlease select a valid entry...")
	return finalAnswer

def arguments(ARGS, DIVIDER=':'):
	ARGS_FORMATTED = []
	for item in ARGS:
		if DIVIDER not in item:
			ARGS_FORMATTED.append('{}:t'.format(item))
		else:
			ARGS_FORMATTED.append(item)
	return dict(item.split('{}'.format(DIVIDER)) for item in ARGS_FORMATTED)

def kv_set(DICT, KEY, DEFAULT = False):
	if KEY in DICT:
		DICT[KEY] = 't' if DICT[KEY] == 'true' else 'f' if DICT[KEY] == 'false' else DICT[KEY]
		return DICT[KEY]
	else:
		return DEFAULT


# custom helpers start here
# =========================
def extract_json(STRING, FROM='{', TO='}'):
    import json, re
		
    payload_match = re.search(r'{}.*{}'.format(FROM, TO), STRING)
    extracted_payload = False

    if payload_match:
        extracted_payload = json.loads(payload_match.group())
    else:
        print("JSON data not found.")
    
    return extracted_payload

def curl_cmd(URL, CONFIGS={}):
	ctype = ''

	if 'headers' in CONFIGS.keys():
		if not 'Content-Type' in CONFIGS['headers'].keys():
			ctype = "\n--header 'Content-Type: application/json' \\"

	prefix = '''curl --location '{}' \\{}'''.format(URL, ctype)
	suffix = "\n-s"
	contentStr = ''
	if 'headers' in CONFIGS.keys():
		for key, val in CONFIGS['headers'].items():
			contentStr += "\n--header '{}: {}' \\".format(key, val)
	if 'body' in CONFIGS.keys():
		bodyPrefix = '''\n--data '{'''
		bodySuffix = "}' \\"
		contentStr += bodyPrefix
		total_items = len(CONFIGS['body'])
		for index, (key, val) in enumerate(CONFIGS['body'].items()):
			if type(val) == str:
				val = '"{}"'.format(val)
			if index == total_items - 1:
				contentStr += '''\n\t"{}": {}\n'''.format(key, val)
			else:
				contentStr += '''\n\t"{}": {},'''.format(key, val)
		contentStr += bodySuffix
	return prefix + contentStr + suffix

def marked_val(VAL):
	import json
	
	if VAL is None:
		return '___markedVal({})'.format('null')
	elif VAL is True:
		return '___markedVal({})'.format('true')
	elif VAL is False:
		return '___markedVal({})'.format('false')
	else:
		return VAL

def resolve_marked_val(VAL):
	import re, json

	pat = '__markedVal(.*)'
	formattedVal = VAL

	if type(VAL) == str:
		match = re.search(pat, VAL)
		if match:
			formattedVal = match.group().strip('___markedVal\(').strip('\)')
	
	return formattedVal

def curl_cmd2(URL, CONFIGS = {}, METHOD="get", option = True):
	curlList = []

	methodDef = ''

	if METHOD == 'post':
		methodDef = '--request POST '
	elif METHOD == 'put':
		methodDef = '--request PUT '

	curlPrefix = """curl -s --location {}'{}' \\""".format(methodDef, URL)
	curlSuffix = "\n-D -"

	headerList = []
	bodyList = []

	headerType = """\n--header 'Content-Type: application/json' \\"""
	headerList.append(headerType)

	if CONFIGS != None:

		if 'headers' in CONFIGS.keys():
			for key, val in CONFIGS['headers'].items():
				markedVal = marked_val(val)
				formattedVal = resolve_marked_val(markedVal)
				headerList.append("\n--header '{}: {}' \\".format(key, formattedVal))
		if 'body' in CONFIGS.keys():
			bodyPrefix = '''\n--data '{'''
			bodySuffix = "}' \\"
			bodyList.append(bodyPrefix)
			total_items = len(CONFIGS['body'])

			for index, (key, val) in enumerate(CONFIGS['body'].items()):

				if type(val) == str:
					val = '"{}"'.format(val)

				markedVal = marked_val(val)
				formattedVal = resolve_marked_val(markedVal)
					
				if index == total_items - 1:
					bodyList.append('''\n\t"{}": {}\n'''.format(key, formattedVal))
				else:
					bodyList.append('''\n\t"{}": {},'''.format(key, formattedVal))
			bodyList.append(bodySuffix)
		
	curlList.append(curlPrefix)
	curlList.append(headerList)
	curlList.append(bodyList)
	curlList.append(curlSuffix)

	curlString = ''

	for item in curlList:
		if type(item) == list:
			for i in item:
				curlString += i
		else:
			curlString += item
	
	if option:
		print('''
{}

{}

============================

'''.format(decorate('bold', '============== cURL Command:'), decorate('cyan', curlString)))
	
	return curlString

def stitch_roastman_obj(STRING):
	import ast

	tempString = STRING
	tempDict = ast.literal_eval(STRING)

	if "variables" in tempDict.keys():
		for key, val in tempDict['variables'].items():
			varPlaceholder = '{' + key + '}'
			tempString = tempString.replace(
				varPlaceholder,
				val
			)

	formattedObj = ast.literal_eval(tempString)

	return formattedObj

def stitch_config2(DATA1, DATA2):
	import re

	if DATA1:
		pat = '<% .* %>'
		
		for key, value in DATA1['headers'].items():
			match = re.search(pat, value)
			
			if match:
				placeholder_key = match.group().strip('<% | %>')

				returnVal = False

				if ':' in placeholder_key:
					parts = placeholder_key.split(':')
					ref = ''
					TEMP = DATA2
					for index, elem in enumerate(parts):
						if type(TEMP) is dict and index < (len(parts) - 1):
							ref = TEMP[elem]
							TEMP = ref
						elif type(TEMP) is dict:
							ref = TEMP[elem]
							returnVal = ref
						else:
							cookieObj = TEMP.split('; ')[0]
							newObj = {}
							cookieVal = cookieObj.split('=')
							newObj[cookieVal[0]] = cookieVal[1]
							if elem in newObj:
								returnVal = value.replace(match.group(), newObj[elem])
					
					if returnVal:
						DATA1['headers'][key] = returnVal

				else:
					DATA1['headers'][key] = DATA2['body'][placeholder_key]

	return DATA1

def stitch_url(URL, DATA):
	formattedUrl = ''
	if DATA and 'path' in DATA:
		if '{'in URL:
			URL.split("{")[1].split("}")[0]
			formattedUrl = URL.format(**DATA['path'])
		else:
			formattedUrl = URL
	else:
		formattedUrl = URL
	return formattedUrl

def format_response(RESPONSE):
	import re

	newObj = {}
	responseCodePat = ' [0-9]*'

	responseContent = [line.strip('\r') for line in RESPONSE.split('\n') if line.strip('\r')]
	firstLine = responseContent[0]
	responseCode = int(re.findall(responseCodePat, firstLine)[0].strip(' '))
	
	#= with response code captured above, remove response code line and continue with rest of data
	responseContent.pop(0)

	bodyContent = responseContent[len(responseContent) - 1]

	#= with body captured as last line in response, remove last line
	responseContent.pop(len(responseContent) - 1)

	newObj['responseCode'] = responseCode
	newObj['responseHeaders'] = {}

	iter = 1

	for item in responseContent:
		keyval = item.split(': ')
		if keyval[0] in newObj['responseHeaders']:
			iter += 1
			newObj['responseHeaders'][keyval[0] + str(iter)] = keyval[1]
		else:
			newObj['responseHeaders'][keyval[0]] = keyval[1]
	
	try:
		newObj['body'] = json.loads(bodyContent)
	except:
		newObj['body'] = bodyContent

	return newObj

def list_files(directory):
	import os

	visible_only_sorted = []

	if os.path.isdir(directory):
		visible_only = [file for file in os.listdir(directory) if not file.startswith('.')]
		visible_only_sorted = sorted(visible_only)

	return visible_only_sorted

def handle_yaml_record(DATA):
	import yaml, json

	preppedData = {}
	preppedData['responseCode'] = DATA['responseCode']
	preppedData['responseHeaders'] = DATA['responseHeaders']

	formattedData = yaml.safe_dump(preppedData, sort_keys=False, indent=4)
	joinedData = '''{}
body: |
{}
'''.format(formattedData, json.dumps(DATA['body'], indent=4))
	
	return joinedData