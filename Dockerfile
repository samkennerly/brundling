FROM python:3.7.5
LABEL description="Python development sandbox"
LABEL maintainer="samkennerly@gmail.com"

# Install system packages
RUN apt-get -y update && apt-get -y install \
    cmake gcc less tree tidy=2:5.6.0-10

# Install Python packages
COPY requirements.txt /tmp
RUN pip install --upgrade pip && pip install --requirement /tmp/requirements.txt

# Create user and context folder
RUN useradd --create-home kos
ENV PYTHONPATH=/context/code
WORKDIR /context

CMD ["/bin/bash"]
