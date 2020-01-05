FROM python:3.7.5
LABEL description="Python development sandbox"
LABEL maintainer="samkennerly@gmail.com"

# Install system packages
RUN apt-get -y update && apt-get -y install \
    cmake gcc less tree tidy=2:5.6.0-10

# Install core Python packages
RUN pip install --upgrade pip && pip install \
    jupyter==1.0.0 \
    scipy==1.3.3

# Install extra Python packages
COPY requirements.txt /tmp
RUN pip install --upgrade pip && pip install --requirement /tmp/requirements.txt

# Create user and context folder
RUN useradd --create-home kos
ENV PYTHONPATH=/context/code
WORKDIR /context

CMD ["/bin/bash"]
