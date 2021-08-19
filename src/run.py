import message_processor
import web_server
import terminal

message_processor.process_new_messages_forever()
web_server.start(False)

print(f'{"-" * 30}\ncurl -L 127.0.0.1:{web_server.PORT}|sh\n{"-" * 30}\n')
terminal.App()
