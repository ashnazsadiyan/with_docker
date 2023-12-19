FROM public.ecr.aws/lambda/python:3.11

# Enable the EPEL repository and install FFmpeg
COPY ffmpeg /usr/bin/

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"


# Copy function code
COPY main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]