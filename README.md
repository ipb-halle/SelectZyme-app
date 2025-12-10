# SelectZyme-app
Web application to host the pre calculated analyses by SelectZyme.

## Install
Prerequisite for all installs is to clone the code and data repositories.
```
git clone https://github.com/ipb-halle/SelectZyme-app.git
cd SelectZyme-app
git clone https://huggingface.co/datasets/fmoorhof/selectzyme-app-data data
```
After these steps you should have the directory 'SelectZyme-app' and 'SelectZyme-app/data', where the 'data' folder contains the pre-calualated analyses from SelectZyme.

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
Access the server for your analysis from your browser at: `localhost:8050`. Replace `data/demo` with the path to the desired analysis.

### Local install
Install dependencies defined in the `pyproject.toml` and SelectZyme without dependencies.
```
pip install .
pip install --no-dependencies git+https://github.com/ipb-halle/SelectZyme.git@1069532
```
Usage: 
```
python app.py  # runs example analysis 'demo' by default
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