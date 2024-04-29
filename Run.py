import messages as msg
import helpers, ast, json, yaml, re

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
	here = helpers.kv_set(argDict, 'here')
	path = helpers.kv_set(argDict, 'path')

	collectionsPath = ''

	if here == 't':
		collectionsPath = '{}/roastman_collections'.format(
			helpers.run_command_output('pwd', False).strip('\n')
		)
		msg.running_from(collectionsPath)
	elif here:
		collectionsPath = '{}/roastman_collections'.format(
			here
		)
		msg.running_from(collectionsPath)
	else:
		collectionsPath = '{}/profiles/{}'.format(
			helpers.path('utility'),
			settings['roastman']
		)

	options = helpers.list_files(collectionsPath)
	
	if select == 't':
		selection = helpers.user_selection("Select: ", options)
		if selection != 'exit':
			rn = options[selection - 1]
	elif select:
		if select.isnumeric():
			rn = options[int(select) - 1]
		else:
			rn = select

	if add:	
		newRequest = {}
		newRequest['url'] = ""
		newRequest['method'] = ""
		newRequest['config'] = '{REQUEST}_config.yaml'.format(
			REQUEST = add
		)
		
		DATA = helpers.read_file('{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FOLDER}.py'.format(
			ROASTMAN_COLLECTIONS = collectionsPath,
			MAIN_FOLDER = rn
		))

		DATA_FORMATTED = ast.literal_eval(DATA)

		DATA_FORMATTED['requests'][add] = newRequest

		helpers.write_file('{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FOLDER}.py'.format(
			ROASTMAN_COLLECTIONS = collectionsPath,
			MAIN_FOLDER = rn
		), json.dumps(DATA_FORMATTED, indent=4))

		helpers.write_file('{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{REQUEST}_config.yaml'.format(
			ROASTMAN_COLLECTIONS = collectionsPath,
			MAIN_FOLDER = rn,
			REQUEST = add
		), '')

		helpers.run_command('open -a "{ROASTMAN_CONFIG_EDITOR}" {ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{REQUEST}_config.yaml'.format(
			ROASTMAN_CONFIG_EDITOR = settings['roastmanConfigEditor'],
			ROASTMAN_COLLECTIONS = collectionsPath,
			MAIN_FOLDER = rn,
			REQUEST = add
		))

	else:

		if rn:
			settingsFile = '{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FILE}.py'.format(
				ROASTMAN_COLLECTIONS = collectionsPath, 
				MAIN_FOLDER = rn,
				MAIN_FILE = rn
			)
			roastmanStr = helpers.read_file(settingsFile)
			roastmanObj = helpers.stitch_roastman_obj(roastmanStr, path)

			formattedPayload = {}

			if 'token' in roastmanObj:
				configFile = '{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FILE}'.format(
					ROASTMAN_COLLECTIONS = collectionsPath,
					MAIN_FOLDER = rn,
					MAIN_FILE = roastmanObj['token']['config']
				)
				config = yaml.safe_load(helpers.read_file(configFile))

				if 'show' in roastmanObj['token'] and roastmanObj['token']['show'] == True:
					rnCmd = helpers.curl_cmd2(roastmanObj['token']['url'], config, roastmanObj['token']['method'])

					payload = helpers.run_command_output(rnCmd, False)
					formattedPayload = helpers.format_response(payload)

					msg.curl_result(json.dumps(formattedPayload['body'], indent=4))

					if 'record' in roastmanObj['token']:
						tokenResultFile = '{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{TOKEN_RECORD}'.format(
							ROASTMAN_COLLECTIONS = collectionsPath,
							MAIN_FOLDER = rn,
							TOKEN_RECORD = roastmanObj['token']['record']
						)
						joinedData = helpers.handle_yaml_record(formattedPayload)
						helpers.write_file(tokenResultFile, joinedData)
				else:
					rnCmd = helpers.curl_cmd2(roastmanObj['token']['url'], config, roastmanObj['token']['method'], False)

					payload = helpers.run_command_output(rnCmd, False)
					formattedPayload = helpers.format_response(payload)

			optionSelectionName = False
			optionSelection = False

			if use:
				if use.isnumeric():
					useFormatted = int(use)
					optionList = list(roastmanObj['requests'].keys())
					optionSelectionName = optionList[useFormatted - 1]
					msg.request_selection(optionSelectionName)
				else:
					optionSelectionName = use
			else:
				optionList = list(roastmanObj['requests'].keys())
				optionSelection = helpers.user_selection('Select a Request: ', optionList)

			if optionSelection != 'exit' or optionSelectionName:
				optionSelectionName = optionSelectionName if optionSelectionName else optionList[optionSelection - 1]
				configData = helpers.read_file('{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FILE}'.format(
					ROASTMAN_COLLECTIONS = collectionsPath,
					MAIN_FOLDER = rn,
					MAIN_FILE = roastmanObj['requests'][optionSelectionName]['config'])
				)
				secondConfig = yaml.safe_load(configData)

				formattedConfig = helpers.stitch_config(secondConfig, formattedPayload)
				formattedUrl = helpers.stitch_url(roastmanObj['requests'][optionSelectionName]['url'], secondConfig, path)

				rnSecondCmd = helpers.curl_cmd2(formattedUrl, formattedConfig, roastmanObj['requests'][optionSelectionName]['method'])

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
						
						resultFile = '{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{RECORD_FOLDER}'.format(
							ROASTMAN_COLLECTIONS = collectionsPath,
							MAIN_FOLDER = rn,
							RECORD_FOLDER = roastmanObj['requests'][optionSelectionName]['record']
						)
						helpers.write_file(resultFile, joinedData)
						helpers.run_command('open -a "{}" {}'.format(settings['roastmanRecordApp'], resultFile), False)
					else:
						msg.curl_result(json.dumps(formattedResult['body'], indent=4))

					if 'out' in roastmanObj['requests'][optionSelectionName]:
						joinedData = helpers.handle_file_out(data)

						ifRootPat = re.compile('^/.*$')
						outFile = roastmanObj['requests'][optionSelectionName]['out']

						resultFile = '{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{OUT_FOLDER}'.format(
								ROASTMAN_COLLECTIONS = collectionsPath,
								MAIN_FOLDER = rn,
								OUT_FOLDER = roastmanObj['requests'][optionSelectionName]['out']
							)

						if ifRootPat.match(outFile):
							resultFile = '{HERE_FOLDER}/{OUT_FOLDER}'.format(
								HERE_FOLDER = collectionsPath.replace('/roastman_collections', ''),
								OUT_FOLDER = roastmanObj['requests'][optionSelectionName]['out']
							)

						helpers.write_file(resultFile, joinedData)
		
		elif config:
			settingsFile = '{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/token_config.yaml'.format(
				ROASTMAN_COLLECTIONS = collectionsPath,
				MAIN_FOLDER = config
			)
			roastmanStr = helpers.read_file(settingsFile)
			helpers.run_command('open -a "{ROASTMAN_CONFIG_EDITOR}" {ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/token_config.yaml'.format(
				ROASTMAN_CONFIG_EDITOR = settings['roastmanConfigEditor'],
				ROASTMAN_COLLECTIONS = collectionsPath,
				MAIN_FOLDER = config
			))

		elif nw:
			collectionContent = '''{
	"variables": {
	}
	,"token" : {
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
			helpers.run_command('mkdir {ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}'.format(
				ROASTMAN_COLLECTIONS = collectionsPath,
				MAIN_FOLDER = nw
			))
			helpers.run_command('mkdir {ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/records'.format(
				ROASTMAN_COLLECTIONS = collectionsPath,
				MAIN_FOLDER = nw
			))
			helpers.write_file('{ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/{MAIN_FOLDER}.py'.format(
				CONTENT = collectionContent,
				ROASTMAN_COLLECTIONS = collectionsPath,
				MAIN_FOLDER = nw,
				TOKEN_CONTENT = tokenContent
			), collectionContent)
			helpers.run_command('touch {ROASTMAN_COLLECTIONS}/{MAIN_FOLDER}/token_config.yaml'.format(
				ROASTMAN_COLLECTIONS = collectionsPath,
				MAIN_FOLDER = nw,
				TOKEN_CONTENT = tokenContent
			))

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