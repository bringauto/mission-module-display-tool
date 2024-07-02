# Mission module display tool

This tool is used to display the positions of the cars on the map using the [fleet protocol HTTP API](https://github.com/bringauto/fleet-protocol-http-api).

## Installation

```bash
git clone https://github.com/bringauto/mission-module-display-tool.git
cd mission-module-display-tool
mkdir logs
pip install -r requirements.txt
```

## Command line arguments

* `--config=<string>` - path to the JSON configuration file. If not set, the default path `./resources/config.json` is used.

## JSON configuration

* `api-url` - URL of the fleet protocol HTTP API.
* `api-key` - API key for the fleet protocol HTTP API.
* `port` - port on which the web server will run.

## Usage

Starting the tool with the default configuration:

```bash
python3 display-tool.py
```

Starting the tool with a custom configuration:

```bash
python3 display-tool.py --config=./resources/config.json
```

It will start web server on `http://localhost:5000/` and display the map with the cars.

## Running in docker

```bash
docker build -t mission-module-display-tool .
```

Replace `<network>` with the name of the container network where the HTTP API is running.

```bash
docker run -p 5000:5000 --network=<network> mission-module-display-tool --config=resources/config-docker.json
```

If option `--config` is not set, the default configuration file `resources/config-docker.json` is used.

### Example for use with [bringauto/etna](https://github.com/bringauto/etna)

To use the mission-module-display-tool with the bringauto/etna project, you can run the following commands:

```bash
docker build -t mission-module-display-tool .
```

```bash
docker run -p 5000:5000 --network=bring-emulator mission-module-display-tool --config=resources/config-docker.json
```

In this example, the network is set to `bring-emulator`, which is the network name used by the bringauto/etna project docker compose file.
