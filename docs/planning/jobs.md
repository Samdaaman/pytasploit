# Jobs
Things that do something over a period of time and eventually finish and return success or failure (can contain return data as well)

## Encoding
### Requests
#### Start a Job:
```json5
{
  "message_type": "JOB_START_REQUEST",
  "data": {
    "job_type": "<job_type>",  // eg RUN_ENUM_SCRIPT
    "params": {
      // JSON object of job parameters (if any)
    }
  }
}
```

#### Get status of a Job:
```json5
{
  "message_type": "JOB_STATUS_REQUEST",
  "data": {
    "job_uid": "abc1234",  // unique string which identifies the command_request
  }
}
```

### Responses
```json5
{
  "message_type": "JOB_START_RESPONSE",
  "data": {
    "job_uid": "abc1234"  // uid which identifies the job
  },
}
```

#### Get status of a Job:
```json5
{
  "message_type": "JOB_STATUS_RESPONSE",
  "data": {
    "status": "created | running | error | done",
    "log": "string",  // printable log of Job progress (does not contain job result)
    "result": {
      // JSON object which is the result of the job
    }
  }
}
```

## List of Jobs
### Run enum script
```yaml
params:
  - enum_script_name: string # (eg linpeas)
returns:
  - output: string     # enum script output
```