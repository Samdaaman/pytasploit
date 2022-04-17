```json5
{
  "message_type": "EVENT",
  "data": {
    "event_type": "<event_type>",  // type of the event
    "data": {
      // JSON object of event data (if any)
    }
  },
}
```

## Event types
### Run file finish
```yaml
data:
  - command_uid: string
  - exit_code: int 
  - output_b64: string
```
