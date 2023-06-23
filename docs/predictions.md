# Running Inference

Run inference on models deployed on the CX platform. You can run inference on models you uploaded yourself, or publicly available ones hosted by CX. 

## Command Line Interface
Run predictions directly from the commandline with the `cx predict` command. 

`cx predict` arguments:
* `--app` the name of the deployed app
* `--data` the payload that the model is expecting
* `--is-public` a boolean (default `False`). This will be `True` if you are accessing a publicly hosted model by CX, and `False` if your org is hosting it.
* `--is-serverless` a boolean (default `False`). This will be `True` if the app was deployed as serverless.

```console
cx predict --app starcoder --data '{"prompt": "def helloworld():"}' --is-public True
```

## cURL Request
Alternatively, you can run inference through a cURL request as well:

```console
$ export CX_API_KEY=<your-api-key>

$ curl -X 'POST' \
  'https://api.computex.co/api/v1/deployments/template-03db38d/infer' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $CX_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_file=@<filename-to-upload>;type=<mime type>' \
  -F 'params=[{"name":"<your-param-name>", "value":"<your-param-value>"}, {"name":"<your-param-name>", "value":"<your-param-value>"}]'
```
Update the payload in `-F` to match your desired inference configuration. 
