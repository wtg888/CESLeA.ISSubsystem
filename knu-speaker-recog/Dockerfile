# Arguments for Nvidia-Docker
# all combination set in CUDA, cuDNN, Ubuntu is not Incompatible please check REFERENCE OF NVIDIA-DOCKER
# REFERENCE OF NVIDIA-DOCKER 
# https://hub.docker.com/r/nvidia/cuda/

# Global arguments registry & additional package
ARG ADDITIONAL_PACKAGE
ARG REGISTRY
ARG PYTHON_VERSION

# Global arguments for Watcher
ARG GRPC_PYTHON_VERSION=1.4.0
ARG WATCHER_VERSION=0.1.0

ARG handler_file=handler.py
ARG handler_name=Handler
ARG handler_dir=/dcf/handler
ARG handler_file_path=${handler_dir}/src/${handler_file}

# Global arguments for Nvidia-docker
ARG CUDA_VERSION=10.0
ARG CUDNN_VERSION=7
ARG UBUNTU_VERSION=16.04

# ARG variable was changed after passing `FROM`
# So, it need copy other ARG variable
ARG CUDA_VERSION_BACKUP=${CUDA_VERSION}

# == MutiStage Build ==
# 1-Stage
# Get watcher - if watcher is uploaded on github, remove this line.
FROM ${REGISTRY}/watcher:${WATCHER_VERSION}-python3 as watcher

# Arguments for Watcher
ARG GRPC_PYTHON_VERSION
ARG handler_dir
ARG handler_file
ARG handler_name
ARG handler_file_path

# Watcher Setting
RUN mkdir -p ${handler_dir}
WORKDIR ${handler_dir}
COPY . .
RUN touch ${handler_dir}/src/__init__.py && \
    cp -r /dcf/watcher/* ${handler_dir}

# 2-Stage
FROM spk

# Arguments for Nvidia-Docker
ARG CUDA_VERSION
ARG CUDNN_VERSION
ARG CUDA_VERSION_BACKUP

# Copy Watcher
ARG GRPC_PYTHON_VERSION
ARG handler_dir
ARG handler_file
ARG handler_name
ARG handler_file_path

ENV HANDLER_DIR=${handler_dir}
ENV HANDLER_FILE=${handler_file_path}
ENV HANDLER_NAME=${handler_name}

RUN mkdir -p ${HANDLER_DIR}
WORKDIR ${HANDLER_DIR}
COPY . .
COPY --from=0 ${HANDLER_DIR} .

RUN pip3 install --default-timeout=500 --upgrade pip==9.0.3 &&\
    pip3 install --default-timeout=500 setuptools && \
    pip3 install --default-timeout=500 grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION} && \
    pip3 install --default-timeout=500 -r requirements.txt

HEALTHCHECK --interval=1s CMD [ -e /tmp/.lock ] || exit 1

ENTRYPOINT ["python3"]
CMD ["server.py"]
