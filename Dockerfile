FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app

RUN pip install .

# do not install dependencies from SelectZyme but only import code
RUN git submodule add https://github.com/fmoorhof/SelectZyme external/selectzyme

# Expose the port Dash will run on
EXPOSE 8050

# Run the Dash app
CMD ["python", "app.py"]
