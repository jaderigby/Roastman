import messages as msg
import helpers, ast, json, yaml, os

settings = helpers.get_settings()

def execute(ARGS):
	argDict = helpers.arguments(ARGS)
	select = helpers.kv_set(argDict, 'select')
	rn = helpers.kv_set(argDict, 'run')
	config = helpers.kv_set(argDict, 'config')
	nw = helpers.kv_set(argDict, 'new')
	add = helpers.kv_set(argDict, 'add')
	booyah = helpers.kv_set(argDict, 'booyah')
	use = helpers.kv_set(argDict, 'use')

	if select == 't':
		options = helpers.list_files('{}/profiles/{}'.format(helpers.path('utility'), settings['roastman']))
		selection = helpers.user_selection("Select: ", options)
		if selection != 'exit':
			rn = options[selection - 1]
	elif select:
		rn = select

	if add:	

		newRequest = {}
		newRequest['url'] = ""
		newRequest['method'] = ""
		newRequest['config'] = '{REQUEST}_config.yaml'.format(
			REQUEST = add
		)
		
		DATA = helpers.read_file('{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FOLDER}.py'.format(
			ROOT = helpers.path('utility'),
			ROASTMAN_COLLECTIONS = settings['roastman'],
			MAIN_FOLDER = rn
		))

		DATA_FORMATTED = ast.literal_eval(DATA)

		DATA_FORMATTED['requests'][add] = newRequest

		helpers.write_file('{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FOLDER}.py'.format(
			ROOT = helpers.path('utility'),
			ROASTMAN_COLLECTIONS = settings['roastman'],
			MAIN_FOLDER = rn
		), json.dumps(DATA_FORMATTED, indent=4))

		helpers.write_file('{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{REQUEST}_config.yaml'.format(
			ROOT = helpers.path('utility'),
			ROASTMAN_COLLECTIONS = settings['roastman'],
			MAIN_FOLDER = rn,
			REQUEST = add
		), '')

		helpers.run_command('open -a "{ROASTMAN_CONFIG_EDITOR}" {ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{REQUEST}_config.yaml'.format(
			ROASTMAN_CONFIG_EDITOR = settings['roastmanConfigEditor'],
			ROOT = helpers.path('utility'),
			ROASTMAN_COLLECTIONS = settings['roastman'],
			MAIN_FOLDER = rn,
			REQUEST = add
		))

	else:

		if rn:
			settingsFile = '{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FILE}.py'.format(
				ROOT = helpers.path('utility'), 
				ROASTMAN_COLLECTIONS = settings['roastman'], 
				MAIN_FOLDER = rn,
				MAIN_FILE = rn
			)
			roastmanStr = helpers.read_file(settingsFile)
			roastmanObj = ast.literal_eval(roastmanStr)
			configFile = '{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FILE}'.format(
				ROOT = helpers.path('utility'), 
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = rn,
				MAIN_FILE = roastmanObj['token']['config']
			)
			config = yaml.safe_load(helpers.read_file(configFile))

			if 'show' in roastmanObj['token'] and roastmanObj['token']['show'] == True:
				rnCmd = helpers.curl_cmd2(roastmanObj['token']['url'], config)

				payload = helpers.run_command_output(rnCmd, False)
				formattedPayload = helpers.format_response(payload)

				msg.curl_result(json.dumps(formattedPayload['body'], indent=4))

				if 'record' in roastmanObj['token']:
					tokenResultFile = '{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{TOKEN_RECORD}'.format(
						ROOT = helpers.path('utility'),
						ROASTMAN_COLLECTIONS = settings['roastman'],
						MAIN_FOLDER = rn,
						TOKEN_RECORD = roastmanObj['token']['record']
					)
					joinedData = helpers.handle_yaml_record(formattedPayload)
					helpers.write_file(tokenResultFile, joinedData)
			else:
				rnCmd = helpers.curl_cmd2(roastmanObj['token']['url'], config, False)

				payload = helpers.run_command_output(rnCmd, False)
				formattedPayload = helpers.format_response(payload)
			
			optionList = list(roastmanObj['requests'].keys())

			optionSelectionName = False

			if use:
				optionSelectionName = use
				optionSelection = False
			else:
				optionSelection = helpers.user_selection('Select a Request: ', optionList)

			if optionSelection != 'exit' or optionSelectionName:
				optionSelectionName = optionSelectionName if optionSelectionName else optionList[optionSelection - 1]
				configData = helpers.read_file('{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FILE}'.format(
					ROOT = helpers.path('utility'), 
					ROASTMAN_COLLECTIONS = settings['roastman'],
					MAIN_FOLDER = rn,
					MAIN_FILE = roastmanObj['requests'][optionSelectionName]['config'])
				)
				secondConfig = yaml.safe_load(configData)

				# def stitch_config(DATA1, DATA2):
				# 	import re
				# 	pattern = r'<% (\w+) %>'

				# 	def replace(match):
				# 		key = match.group(1)
				# 		return DATA2.get(key, match.group())

				# 	updated_data1_str = re.sub(pattern, replace, DATA1)

				# 	return updated_data1_str

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

				formattedConfig = stitch_config2(secondConfig, formattedPayload)
				formattedUrl = stitch_url(roastmanObj['requests'][optionSelectionName]['url'], secondConfig)

				rnSecondCmd = helpers.curl_cmd2(formattedUrl, formattedConfig, True)

				valid = True
				result = helpers.run_command_output(rnSecondCmd, False)
				formattedResult = helpers.format_response(result)
				#= TODO: Status:Brittle = Needs a better check than just "valid json structure"
				try:
					data = formattedResult
				except:
					valid = False
					msg.response_error(json.dumps(formattedResult['body'], indent=4))
				
				if valid:
					if 'record' in roastmanObj['requests'][optionSelectionName]:
						joinedData = helpers.handle_yaml_record(data)
						
						# formattedData = json.dumps(data, indent=4)
						resultFile = '{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{RECORD_FOLDER}'.format(
							ROOT = helpers.path('utility'),
							ROASTMAN_COLLECTIONS = settings['roastman'],
							MAIN_FOLDER = rn,
							RECORD_FOLDER = roastmanObj['requests'][optionSelectionName]['record']
						)
						helpers.write_file(resultFile, joinedData)
						helpers.run_command('open -a "{}" {}'.format(settings['roastmanRecordApp'], resultFile), False)
					else:
						msg.curl_result(json.dumps(formattedResult['body'], indent=4))
		
		elif config:
			settingsFile = '{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/token_config.yaml'.format(
				ROOT = helpers.path('utility'), 
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = config
			)
			roastmanStr = helpers.read_file(settingsFile)
			helpers.run_command('open -a "{ROASTMAN_CONFIG_EDITOR}" {ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/token_config.yaml'.format(
				ROASTMAN_CONFIG_EDITOR = settings['roastmanConfigEditor'],
				ROOT = helpers.path('utility'), 
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = config
			))

		elif nw:
			collectionContent = '''{
	"token" : {
		"url": ""
		,"method": ""
		,"config": "token_config.yaml"
	}
	,"requests" : {
		"sampleRequest": {
		"url": ""
		,"method": ""
		,"config": "sampleRequest_config.yaml"
		,"record": "records/sample.json"
		}
	}
	}
	'''
			tokenContent = '''
	'''
			helpers.run_command('mkdir {ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}'.format(
				ROOT = helpers.path('utility'),
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = nw
			))
			helpers.run_command('mkdir {ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/records'.format(
				ROOT = helpers.path('utility'),
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = nw
			))
			helpers.write_file('{ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FOLDER}.py'.format(
				CONTENT = collectionContent,
				ROOT = helpers.path('utility'),
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = nw,
				TOKEN_CONTENT = tokenContent
			), collectionContent)
			helpers.run_command('touch {ROOT}/profiles/{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/token_config.yaml'.format(
				ROOT = helpers.path('utility'),
				ROASTMAN_COLLECTIONS = settings['roastman'],
				MAIN_FOLDER = nw,
				TOKEN_CONTENT = tokenContent
			))

			# - add new item to roastman list
			# - create new folder
			# - create base file (py)
			# 	- include config file reference for "config" value
			# - create config file
		elif booyah:
			print('''
  _____                 _                         
 |  __ \               | |                        
 | |__) |___   __ _ ___| |_ _ __ ___   __ _ _ __  
 |  _  // _ \ / _` / __| __| '_ ` _ \ / _` | '_ \ 
 | | \ \ (_) | (_| \__ \ |_| | | | | | (_| | | | |
 |_|  \_\___/ \__,_|___/\__|_| |_| |_|\__,_|_| |_|
                                                  
''')

	msg.done()