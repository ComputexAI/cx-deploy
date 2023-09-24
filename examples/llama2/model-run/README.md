# Model Run

Build the image locally then push it to your registry
```
docker build -t registry.computex.ai/computex/model-run-mpt-7b:13 .
docker push registry.computex.ai/computex/model-run-mpt-7b:13 
kubectl apply -f tensorizer.yaml
```

Once it is successfully deployed, curl the endpoint created by the isvc (use http not https)
```
curl -X POST -H "Content-Type: application/json" -d '{"instances":["Hello, how are you?"]}' http://mpt7b-dev.tenant-934db3-cx.knative.chi.coreweave.com/v1/models/mpt-7b:predict
```
