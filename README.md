# Roastman #

≈≈≈ Made With Bacon!

Licensed under MIT

## Description ##

An api tester/manager similar to Postman.

## Setup ##

The easiest way to setup Roastman is to first install [bacon](https://github.com/jaderigby/bacon).  Once bacon is installed, then run the following command:

```
cd ~/Documents/bacon-bits && git clone https://github.com/jaderigby/Roastman.git && bacon alias && bacon set
```

To verify that the setup was successful, run `roastman`. You should see the commands available to you in Roastman, as a result.

__You are all set!__

## Options ##

`roastman - select`: Lists the available collections (must create at least 1 collection, first)

`roastman - select:exampleCollection`: Demonstrates using `select` to pass the value, rather than selecting from a numeric list. __Note:__ You can also just pass the numric value, as well, such as `roastman - select:2`

`roastman - select:exampleCollection add:someRequest`: Add a new request.

`roastman - select:exampleCollection use:someRequest`: Demonstrates using `use` to pass a value, rather than selecting the request from a numeric list. __Note:__ You can also just pass the numric value, as well, such as `roastman - select:2 use:3`

`roastman - here`: By default, your roastman collections are located at `Roastman > profiles > roastman_collections`.  But if you want to include a specific set of collections in, say, your personal repo, you can!  First, create a folder called "roastman_collections" at the root of the repo.  Then, cd to that directory and add "here" to the command, such as `roastman - here select`.  You can add a new collection, run requests, etc, like you would normally.  The only difference is that the `here` command will run it from your current working directory.

## Settings File Features ##

A collection's Settings file (the python file in the collection folder) can take the following parameters:

- Show token call: You can add `"show": "true"` to the Token settings, if you want the token call, or "handshake" to output to the command line.  Below is an example of a token configured in this way:

```
{
    "token" : {
        "url": "https://api.optconnect.com/summit/beta/accounts/login/app_secret"
        ,"method": "post"
        ,"config": "token_config.yaml"
        ,"show": "true"
    }
    ,"requests" : {
        ...
```

- Token record: In addition, you can output the token call to a record file, like so:

```
{
    "token" : {
        "url": "https://api.optconnect.com/summit/beta/accounts/login/app_secret"
        ,"method": "post"
        ,"config": "token_config.yaml"
        ,"show": "true"
        ,"record": "records/token.yaml"
    }
    ,"requests" : {
        ...
```

- Variables: You can add variables, and then use them in the settings, such as to simplify the request calls. See below:

```
{
    "variables" : {
        "baseUrl": "https://someAPiUrl.com/api/v1"
    }
    ...
    ,"requests" : {
        "getDevices": {
            "url": "{baseUrl}/devices"
            ,"method": "get"
            ,"config": "getDevices_config.yaml"
            ,"record": "records/devices.yaml"
        }
    }
}
```

- Path configs:  If you want to add specific values to a request path, such as adding an ID number to the request path `https://someAPiUrl.com/api/v1/devices/{deviceId}`, you can do this by adding the key/value pair, under path, to the config file.  Here's an example:

someRequest_config.yaml
```
headers:
    accountId: 115
    token: eyagurealliou55125abc
path:
    deviceId: 567123890
```

Upon executing `https://someAPiUrl.com/api/v1/devices/{deviceId}`, the `{deviceId}` placeholder will be injected with the value in the config file matching that key, in this case `567123890`.  You can do this for any similar param in the url of a given request.

- Token handoff: For the token call, you can do substitution by using placeholders, such as `<% apiKey %>`.   So, for example, let's say your token call returns the following body:

```
apiKey: 555777888123
token: eyagurealliou55125abc
```

You can then pass those values on to the request by putting the following in you request config:

someRequest_config.yaml
```
headers:
    x-api-key: <% apiKey %>
    Authentication: <% token %>
```

In addition, let's say what you are looking for is in the token's response headers as a cookie ... ooh, tricky, tricky!  Actually, it's fairly simple: Reference the path all the way down to the cookie value, like so:

someRequest_config.yaml
```
headers:
  Jwt: "Bearer <% responseHeaders:set-cookie:token %>"
```

So, here, it looks in the `responseHeaders` of the token call, for the first cookie set (`set-cookie`), and then requests the value for `token`, the name of the cookie.

[Note: Roastman numbers the `set-cookie` calls, so that you can reference them, like we're doing here.  So the first cookie would be labelled `set-cookie`, the second would be `set-cookie2`, the third `set-cookie3`, and so on.]

One final note: You can also use "variables" to inject values into request urls, as well, rather than the `path` param in your config file, such as doing:

someApi.py
```
{
    "variables" : {
        "baseUrl": "https://someAPiUrl.com/api/v1"
        "deviceId": 567123890
    }
    ...
    ,"requests" : {
        "getDevices": {
            "url": "{baseUrl}/devices/{devideId}"
            ,"method": "get"
            ,"config": "getDevices_config.yaml"
            ,"record": "records/devices.yaml"
        }
    }
}
```

... where the variable "deviceId" was used.  Just be careful in naming your variables: You'll want to avoid duplicate names.