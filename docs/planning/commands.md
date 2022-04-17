# Commands
Things that do something immediately (or within 3 sec) and return success or failure (can contain return data as well)

## Encoding
### Requests
```json5
{
  "message_type": "COMMAND_REQUEST",
  "data": {
    "uid": "abc1234",          // unique string which identifies the command_request
    "command_type": "<command_type>",  // type of the command (eg "PING")  
    "params": {
      // JSON object of command parameters (if any)
    }
  },
}
```

### Responses
```json5
{
  "message_type": "COMMAND_RESPONSE",
  "data": {
    "request_uid": "abc1234",  // same uid from the command_request
    "returns": {
      // JSON object of command return values (if any)
    }
  },
}
```

### Error Responses
```json5
{
  "message_type": "COMMAND_RESPONSE_ERROR",
  "data": {
    "request_uid": "abc1234",  // same uid from the command_request
    "error": "dang something"  // string to identify error
  }
}
```

## List of Commands
### Ping
```yaml
params: none  
returns: none
```

### Open Reverse Shell
```yaml
params: 
  - port: int
returns: none
```

### Self Destruct
```yaml
params: none
returns: none
```

### Run file
```yaml
params:
  - contents_b64: string
returns:
  - pid: int
```
