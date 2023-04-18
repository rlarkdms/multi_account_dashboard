FROM python

COPY . . 

RUN apt-get update -y

CMD ["aws_change_resource_tag.py"]
ENTRYPOINT ["python3"]