
Program Data
============


Object data payload; Program config data.

Program Data Attributes
------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|name|string||Name of the program in the format namespace/program-name.|Yes|
|affinity|string; One of: ```['client', 'none']```|```'client'```|Indicates the module affinity (client=client's runtime; none or empty=any suitable/available runtime).|No|
|instantiate|string; One of: ```['single', 'client']```|```'client'```|Single instance of the program (=single), or let every client create a program instance (=client). Per client instance will create new uuid for each program.|Yes|
|filename|string||Filename of the entry binary.|Yes|
|filetype|string; One of: ```['WA', 'PY']```|```'WA'```|Type of the program (WA=WASM or PY=Python).|Yes|
|parent|string|```'pytest'```|Request the orchestrator to deploy to this runtime (can be a runtime name or UUID); usually left blank.|Yes|
|args|array||Command-line arguments (passed in argv). Supports variables: ${scene}, ${mqtth}, ${cameraid}, ${username}, ${runtimeid}, ${moduleid}, ${query-string-key}.|No|
|env|array|```['MID=${moduleid}', 'SCENE=${scene}', 'NAMESPACE=${namespace}', 'MQTTH=${mqtth}', 'REALM=realm']```|Environment variables. Supports variables: ${scene}, ${namespace}, ${mqtth}, ${cameraid}, ${username}, ${runtimeid}, ${moduleid}, ${query-string-key}.|Yes|
|channels|array|```[{'path': '/ch/${scene}', 'type': 'pubsub', 'mode': 'rw', 'params': {'topic': 'realm/s/${scene}'}}]```|Channels describe files representing access to IO from pubsub and client sockets (possibly more in the future; currently only supported for WASM programs).|No|
|run_info|object||Program execution info, added at runtime.|No|
