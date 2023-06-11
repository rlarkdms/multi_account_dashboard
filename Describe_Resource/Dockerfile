FROM ubuntu:18.04

WORKDIR /home/app

RUN pwd && ls -l

COPY ./Describe_Resource/Describe_Resource.sh .

RUN chmod +x ./Describe_Resource.sh

CMD ["./Describe_Resource.sh"]