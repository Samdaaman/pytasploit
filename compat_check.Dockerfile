FROM silverlogic/python3.6

WORKDIR /src
COPY ./src .

ENV PYTERPRETER_LOCAL_IP=127.0.0.1

CMD [ "python3", "-c", "import pyterpreter" ]