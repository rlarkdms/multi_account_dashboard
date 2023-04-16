FROM python

COPY . . 

RUN apt-get update -y
RUN pip install -r requirements.txt
CMD ["aws_resource_tag_check.py"]
ENTRYPOINT ["python3"]

