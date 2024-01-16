# Python 3.11 runtime as a parent image
FROM python:3.11-slim

# working directory in the container
WORKDIR /app

# Copy contents into the container at /app
COPY . /app

# Install packages in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /.cache/huggingface/hub && \
    chmod -R 755 /.cache/huggingface/hub && \
    mkdir -p /.cache/torch/sentence_transformers && \
    chmod -R 755 /.cache/torch/sentence_transformers

EXPOSE 8501

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]