
Program
=======


Program

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes

Program Attributes
-------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**object_id**|string||Object identifier; Must be a valid UUID.|Yes|
|**action**|string; One of: ```['create', 'delete', 'update']```|```'create'```|Message action create, update, delete.|Yes|
|**persist**|boolean|```True```|Persist this object in the database.|Yes|
|**type**|string; Must be: ```program```|```'program'```|ARENA program data|Yes|
|**data**|[program](program)||Object data payload; Program config data.|Yes|

### Program Data Attributes

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**name**|string||Name of the program.|Yes|
|**affinity**|string; One of: ```['client', 'none']```|```'client'```|Indicates the module affinity (client=client's runtime; none or empty=any suitable/available runtime).|No|
|**instantiate**|string; One of: ```['single', 'client']```|```'client'```|Single instance of the program (=single), or let every client create a program instance (=client). Per client instance will create new uuid for each program.|Yes|
|**file**|string||The path to a `.wasm` file (e.g. `counter.wasm`, `user1/counter.wasm`) in the ARENA filestore, starting from the location field indicated below. See location. Example: user1/py/counter/counter.py should have file: `counter.py` and location: `user1/py/counter`. Note that the runtime will download all files in parent folder (e.g. you can add a requirements.txt)|Yes|
|~~**filename**~~|~~string~~||~~DEPRECATED: data.filename is deprecated for type: program, use data.file and data.location instead.~~|~~No~~|
|**location**|string||Filestore path starting at user home; Example: `user1/hello` for a program inside folder `hello` of user1. Should, at least be the user filesore home folder.|Yes|
|**filetype**|string; One of: ```['WA', 'PY']```|```'WA'```|Type of the program (WA=WASM or PY=Python).|Yes|
|**parent**|string; Must be: ```arena-rt1```|```'arena-rt1'```|Request the orchestrator to deploy to this runtime (can be a runtime name or UUID); Temporarily must be arena-rt1.|Yes|
|**args**|array||Command-line arguments (passed in argv). Supports variables: ${scene}, ${mqtth}, ${userid}, ${username}, ${runtimeid}, ${moduleid}, ${query-string-key}.|No|
|**env**|array|```['MID=${moduleid}', 'SCENE=${scene}', 'NAMESPACE=${namespace}', 'MQTTH=${mqtth}', 'REALM=realm']```|Environment variables. Supports variables: ${scene}, ${namespace}, ${mqtth}, ${userid}, ${username}, ${runtimeid}, ${moduleid}, ${query-string-key}.|Yes|
|**channels**|array|```[{'path': '/ch/${scene}', 'type': 'pubsub', 'mode': 'rw', 'params': {'topic': 'realm/s/${scene}/${namespace}'}}]```|Channels describe files representing access to IO from pubsub and client sockets (possibly more in the future; currently only supported for WASM programs).|No|
|**run_info**|object||Program execution info, added at runtime.|No|
