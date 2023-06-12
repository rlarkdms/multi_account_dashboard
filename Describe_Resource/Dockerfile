FROM ubuntu:latest

WORKDIR /home/app

RUN apt-get update \
    && apt-get install -y \
        curl \
        unzip \
        python3 \
        python3-pip \
        groff \
        less \
        jq \
    && pip3 install --upgrade pip \
    && apt-get clean

RUN pip3 install awscli --upgrade

COPY ./Describe_Resource/Describe_Resource.sh .

RUN chmod +x ./Describe_Resource.sh

CMD ["./Describe_Resource.sh"]