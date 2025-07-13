FROM qgis/qgis:latest

RUN apt update && apt install -y python3-pip

COPY . /app

WORKDIR /app

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["python3", "src/main.py"]