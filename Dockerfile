FROM python:3.9

WORKDIR /usr/src/Metro_API

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "app._main:app", "--host", "0.0.0.0", "--port", "8000" ]
