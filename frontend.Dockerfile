FROM python:3.9-slim-buster

RUN apt-get update && \
    apt-get install -y curl && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN /root/.local/bin/poetry config virtualenvs.create false \
  && /root/.local/bin/poetry install --no-dev --no-interaction --no-ansi

RUN groupadd -r streamlit && useradd -r -g streamlit streamlit

COPY . .

RUN /root/.local/bin/poetry install --no-dev --no-interaction --no-ansi &&\
    chown -R streamlit:streamlit /app

USER streamlit

EXPOSE 80

CMD ["streamlit", "run", "yretain/webapp/ui.py", "--server.port", "80"]
