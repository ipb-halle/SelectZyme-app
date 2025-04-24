# todo: The image contains 1 high vulnerability, consider action
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app

# todo: not working yet: make sure submodule SelectZyme is always 'latest'
# RUN apt-get update && apt-get install -y git
# RUN git submodule update --init --recursive --remote

RUN pip install -r requirements.txt
RUN pip install .
RUN pip install --no-dependencies external/selectzyme/

# Expose the port Dash will run on
EXPOSE 8050

# Run the Dash app [stack size (-s) in kbytes] 
ENTRYPOINT ["bash", "-c", "ulimit -s 32768000 && exec python app.py \"$@\"", "--"]