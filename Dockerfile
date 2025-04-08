FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app

RUN pip install .

# todo: Q: still needed when submodules are included already??
# do not install dependencies from SelectZyme but only import code
# RUN apt-get update && apt-get install -y git
# RUN git submodule add https://github.com/ipb-halle/SelectZyme.git external/selectzyme

# Expose the port Dash will run on
EXPOSE 8050

# Run the Dash app
CMD ["python", "app.py"]
