with open('one_file_2.py') as fh:
    source_code = fh.read()  # TODO get from web server

with open('one_file_1.py') as fh:
    source_code_temp = fh.read()  # TODO get from web server

globals()['__source_code__'] = source_code_temp

exec(source_code, globals())
