# todo: The image contains 1 high vulnerability, consider action
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install --no-dependencies git+https://github.com/fmoorhof/SelectZyme.git

COPY . /app
RUN pip install .

# Expose the port Dash will run on
EXPOSE 8050

# Run the Dash app [stack size (-s) in kbytes] 
ENTRYPOINT ["bash", "-c", "ulimit -s 11040 && exec gunicorn app:server --bind 0.0.0.0:8050 --workers 1"]
# ENTRYPOINT ["bash", "-c", "ulimit -s 10240 && exec python app.py \"$@\"", "--"]  # old argparsing
