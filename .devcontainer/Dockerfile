FROM debian:bookworm

ARG HOST_UID=1000
ARG HOST_GID=1000
ARG USERNAME=developer
ARG GROUPNAME=deltodon

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

USER root

# Install system dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    # Basic utilities
    git \
    curl \
    wget \
    ca-certificates \
    bash-completion \
    sudo \
    # Build tools
    build-essential \
    make \
    # pyenv dependencies for building Python from source
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    # Ruby for Jekyll documentation
    ruby \
    ruby-dev \
    # Other useful tools
    vim \
    less \
 && rm -rf /var/lib/apt/lists/*

# Install bundler for Jekyll
RUN gem install bundler

# Create non-root user with host-matching UID/GID
RUN groupadd --gid ${HOST_GID} ${GROUPNAME} \
 && useradd --uid ${HOST_UID} --gid ${HOST_GID} -m -s /bin/bash ${USERNAME} \
 && mkdir -p /home/${USERNAME}/.cache \
 && chown -R ${USERNAME}:${GROUPNAME} /home/${USERNAME} \
 && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/${USERNAME} \
 && chmod 0440 /etc/sudoers.d/${USERNAME}

# Switch to non-root user for remaining installations
USER ${USERNAME}
WORKDIR /home/${USERNAME}

# Install pyenv
ENV PYENV_ROOT="/home/${USERNAME}/.pyenv"
ENV PATH="${PYENV_ROOT}/bin:${PATH}"

RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
 && echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /home/${USERNAME}/.bashrc \
 && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /home/${USERNAME}/.bashrc \
 && echo 'eval "$(pyenv init -)"' >> /home/${USERNAME}/.bashrc

# Install Python 3.11 via pyenv
RUN ${PYENV_ROOT}/bin/pyenv install 3.11 \
 && ${PYENV_ROOT}/bin/pyenv global 3.11 \
 && ${PYENV_ROOT}/bin/pyenv rehash

# Update PATH for current build context
ENV PATH="${PYENV_ROOT}/shims:${PATH}"

# Upgrade pip and install common Python packages
RUN python -m pip install --upgrade pip setuptools wheel

# Install nvm
ENV NVM_DIR="/home/${USERNAME}/.nvm"
ENV NODE_VERSION="20"

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash \
 && . ${NVM_DIR}/nvm.sh \
 && nvm install ${NODE_VERSION} \
 && nvm alias default ${NODE_VERSION} \
 && nvm use default

# Add nvm to bashrc (already done by install script, but ensuring it's there)
RUN echo 'export NVM_DIR="$HOME/.nvm"' >> /home/${USERNAME}/.bashrc \
 && echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> /home/${USERNAME}/.bashrc \
 && echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> /home/${USERNAME}/.bashrc

# Update PATH for current build context
ENV PATH="${NVM_DIR}/versions/node/v${NODE_VERSION}.*/bin:${PATH}"

# Set up local bin directory
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Set working directory
WORKDIR /workspaces

# Configure git to be safe with the workspace directory
RUN git config --global --add safe.directory /workspaces/*

# Default command (overridden by docker-compose)
CMD ["/bin/bash"]
