FROM python:3.10.4-slim-buster
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app9
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .
CMD [ "python", "./your_python_code.py" ]
