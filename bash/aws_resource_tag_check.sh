# !/bin/bash

aws ec2 describe-tags --filters "Name=resource-type,Values=instance"