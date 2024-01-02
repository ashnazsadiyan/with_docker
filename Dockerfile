FROM public.ecr.aws/lambda/python:3.11

# Install necessary tools
RUN yum install -y wget tar xz

RUN if [ -d /tmp ]; then chmod 1777 /tmp; fi

# Download and extract FFmpeg
RUN wget https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz && \
    tar -xf ffmpeg-git-amd64-static.tar.xz && \
    mv ffmpeg-git-*-amd64-static/ffmpeg /usr/share/ffmpeg && \
    rm -rf ffmpeg-git-*-amd64-static* ffmpeg-git-*-amd64-static.tar.xz

# Set /tmp as the default directo
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"


# Copy function code
COPY main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]