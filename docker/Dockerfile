FROM python 

COPY . . 

RUN \
    apt-get update && \
    pip3 install boto3
CMD ["cronjob_eks.py"]
ENTRYPOINT ["python3"]