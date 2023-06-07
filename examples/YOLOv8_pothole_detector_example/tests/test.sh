#!/bin/bash

FILENAME=image_0.jpg

FILENAME=image_0.jpg

# Function to perform inference with params
function infer_with_params {
  curl -X 'POST' \
    'http://localhost:5000/infer' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F "input_file=@$FILENAME;type=image/jpg" \
    -F 'params=[{"name":"model_name", "value":"tiny"}, {"name":"input_type", "value":"text_input"}]' \
    --output output_potholes_labeled.jpg
}

# Function to perform inference with query params
function infer_with_query_params {
  curl -X 'POST' \
    'http://localhost:5000/infer?model_name=tiny' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F "input_file=@$FILENAME;type=image/jpg" \
    --output output_potholes_labeled.jpg
}

# Call the functions
infer_with_params
#infer_with_query_params
