FROM bringauto/python-environment
WORKDIR /mission-module-display-tool

COPY . /mission-module-display-tool

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000 8080

ENTRYPOINT ["python3", "display-tool.py"]
CMD ["--config", "resources/config-docker.json"]
