FROM ubuntu

RUN apt update && apt install -y \
    curl \
    gcc \
    net-tools \
    netcat \
    python3

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh
