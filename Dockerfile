FROM python:3.8-slim as base
FROM base as builder

RUN  apt update && apt -y install --no-install-recommends git
COPY requirements.txt /tmp/requirements.txt
RUN  pip install --no-cache-dir --user -r /tmp/requirements.txt
COPY  ./ /square-integration
WORKDIR /square-integration


FROM base

ENV PYTHONUNBUFFERED 1

COPY --from=builder /root/.local /usr/local
COPY --from=builder /square-integration /square-integration

WORKDIR /square-integration
ENTRYPOINT ["python", "main.py"]
