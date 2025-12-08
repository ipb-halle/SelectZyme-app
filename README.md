# SelectZyme-app
Minimal demonstration of pre-calculated analyses to show usage and utility of SelectZyme.

## Install
Prerequisite for all installs is to clone the repository with the corresponding submodule SelectZyme.
```
git clone --recurse-submodules https://github.com/ipb-halle/SelectZyme-app.git
cd SelectZyme-app
```
*Troubleshooting:
if you forgot to clone with `--recurse-submodules` you can do it later via: `git submodule update --init`
if you want to leave the latest stable commit hash and use a newer version of SelectZyme (core functionality), update the submodule to the latest commit:
`git submodule update --recursive --remote`

### Docker
Requires cloning the repository (see above).
```
docker build -t ipb-halle/selectzyme-app:development .
```
#### Run all case studies (reproduces SelectZyme server)
```
docker-compose up
docker-compose down  # shut down services
```
Access the server from your browser at: `localhost/selectzyme/`


#### Run only individual Container
```
docker run -it --rm -p 8050:8050 ipb-halle/selectzyme-app:development --input_dir=/app/data/demo
```
Access the server for your analysis from your browser at: `localhost:8050`

### Local install
Install dependencies defined in the `pyproject.toml` and SelectZyme without dependencies.
```
pip install .
pip install --no-dependencies external/selectzyme/
```
Usage: 
```
python app.py  # runs example analysis by default
python app.py -i=/your/out_files/from/selectzyme_backend
```
Access the server for your analysis from your browser at: `localhost:8050`

## Architecture
```mermaid
graph TD;  
    B[Demo analysis] --> D[data/demo/:/app/data_container/];
    C[Petase analysis] --> E[data/petase/:/app/data_container/];
    
    A[Proxy - Nginx] -->|/selectzyme/demo/| B[Demo analysis];
    A[Proxy - Nginx] -->|/selectzyme/petase/| C[Petase analysis];
    
    subgraph Docker Network;
        A[Proxy - Nginx];
        B[Demo analysis];
        C[Petase analysis];
    end
```

## Server deployment @ IPB
Target server: [biocloud](https://biocloud.ipb-halle.de/)
Service: [SelectZyme](https://biocloud.ipb-halle.de/selectzyme/)

In order to automatically (re-)start the service (e.g. with a cronjob) please perform these steps:
```
./sz.sh install  # register service 1st time
./sz.sh start
systemctl status sz.service  # test status
./sz.sh stop  # stop service
```

```mermaid
sequenceDiagram
    actor User
    participant BP as Biocloud Proxy
    participant SDP as Selectzyme Demo Proxy (nginx)
    participant SDA as Selectzyme Demo App

    User->>+BP: Request resource
    BP->>+SDP: Forward request (e.g., to selectzyme-proxy.selectzyme-network)
    SDP->>+SDA: Proxy request to Selectzyme Demo App
    SDA-->>-SDP: App response
    SDP-->>-BP: Forward response
    BP-->>-User: Response
```
* Changes: Biocloud proxy sits on top of SelectZyme proxy


## Development
This project uses the following tools to improve code quality:
- [ruff](https://docs.astral.sh/ruff/tutorial/)

Ocean server development (ocean_ip)
http://ocean_ip/selectzyme/demo/


# License
MIT License