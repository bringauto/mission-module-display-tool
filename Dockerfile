FROM bringauto/python-environment:latest

WORKDIR /home/bringauto

COPY requirements.txt /home/bringauto/mission-module-display-tool/requirements.txt
RUN "$PYTHON_ENVIRONMENT_PYTHON3" -m pip install -r /home/bringauto/mission-module-display-tool/requirements.txt

COPY config/config-docker.json /home/bringauto/config/config-docker.json
COPY lib /home/bringauto/mission-module-display-tool/lib/
COPY templates /home/bringauto/mission-module-display-tool/templates/
COPY display-tool.py /home/bringauto/mission-module-display-tool/

EXPOSE 5000 5000

ENTRYPOINT ["bash", "-c", "$PYTHON_ENVIRONMENT_PYTHON3 /home/bringauto/mission-module-display-tool/display-tool.py $0 $@"]
CMD ["--config", "/home/bringauto/config/config-docker.json"]
