# Commands
Things that do something immediately (or within 3 sec) and return success or failure (can contain return data as well)

## Encoding
### Requests
```json5
{
  "type": "command_request",   // identifies that this is a command message
  "data": {
    "uid": "abc1234",          // unique string which identifies the command_request
    "type": "<command_type>",  // type of the command (eg "PING")  
    "params": {
      // JSON object of command parameters (if any)
    }
  },
}
```

### Responses
```json5
{
  "type": "command_response",  // identifies that this is a command message
  "data": {
    "request_uid": "abc1234",  // same uid from the command_request
    "params": {
      // JSON object of command return values (if any)
    }
  },
}
```

## List of Commands
### Ping
params: none  
returns: generic success

### OpenReverseShell
params: none  
returns generic success  
