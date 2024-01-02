FROM public.ecr.aws/lambda/python:3.11

# Enable the EPEL repository and install necessary tools
RUN yum install -y wget tar xz

COPY ffmpeg /usr/share/ffmpeg
# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY main.py ${LAMBDA_TASK_ROOT}
CMD [ "main.handler" ]