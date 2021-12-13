from message import *


def print_message(message: Message):
    json_str = message.encode()
    print(json_str)
    test = Message.decode(json_str)
    print(test.encode())
# for member in inspect.getmembers(request):
#     print(member)
# print(dir(request))
# print(message.Request.__dir__())


print_message(RunScriptRequest(script_name='yeet', script_args=["first", "second", "--third"]))
print_message(OpenReverseShellRequest(port=1234))

print_message(PingResponse(request_id='123'))
