FROM archlinux:latest

RUN pacman -Sy --noconfirm \
    base-devel \
    git \
    rust \
    cargo \
    python-build \
    python-installer \
    python-hatchling \
    python-requests \
    python-matplotlib \
    python-pillow \
    python-yaml \
    python-rich \
    python-typer

RUN useradd -m builder

WORKDIR /repo

ENTRYPOINT ["bash", "/repo/docker/ci_aur.sh"]
