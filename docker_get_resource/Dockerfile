FROM python

COPY . . 

RUN \
    apt-get update -y && \
    pip3 install boto3
CMD ["cronjob_eks.py"]
ENTRYPOINT ["python3"]