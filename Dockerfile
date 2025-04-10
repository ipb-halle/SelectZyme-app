# todo: The image contains 1 high vulnerability, consider action
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app

RUN pip install .
RUN pip install --no-dependencies external/selectzyme/

# this is deprecated since cloning is done with submodules directly
# RUN apt-get update && apt-get install -y git
# RUN git clone --recurse-submodules https://github.com/fmoorhof/SelectZyme-demo-app.git

# Expose the port Dash will run on
EXPOSE 8050

# Run the Dash app
CMD ["python", "app.py"]
