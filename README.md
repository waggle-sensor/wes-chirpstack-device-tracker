# wes-chirpstack-tracker
Tracks lorawan devices sending payloads to a Chirpstack Server to report to a Django app.

- Chirpstack Server: [wes-chirpstack](https://github.com/waggle-sensor/waggle-edge-stack/tree/main/kubernetes/wes-chirpstack) 
- Django App: [waggle-auth-app](https://github.com/waggle-sensor/waggle-auth-app)
>NOTE: The Django App encompasses the models, serializers, and views necessary for facilitating API calls within `app/django_client/`

## Production Deployment
- When deploying an update, initiate a release process.
- wes-chirpstack-tracker is deployed to nodes via waggle-edge-stack:
    - [waggle-edge-stack wes-chirpstack-tracker-deployment.yaml](https://github.com/waggle-sensor/waggle-edge-stack/blob/main/kubernetes/wes-chirpstack/wes-chirpstack-tracker-deployment.yaml)

## Running Individual Packages
The packages in `app/` can be used invidually by running the main file. Example:
```sh
python3 app/chirpstack_client/client.py --debug --chirpstack-account-email test@email.com --chirpstack-account-password test --chirpstack-api-interface localhost:8080
```
>NOTE: the main file name will be different based on the package

## Test Suite

### Unit Test
To run unit tests download the requirements in `/test/`, then run the following command
```
pytest
```

### Integration Test
- To test wes-chirpstack-tracker in a k3s cluster use the yaml files in `/test/kubernetes/`.
    - If you need to use `secret.yaml`, make sure you add your base 64 encoded token to it
- One way to test an update's image build is to open a PR.
    - Open a PR which builds a some-image:pr-x for every push you do to help testing.
    - if you're iterating on the image, you would mostly use the explicit image:tag@shasum
        - ![PR](/images/PR.png)
            - Here you can see the image:tag@shasum
            - If you want to pull the image you would use image:tag@shasum

## More Information
- A "Manifest" refers to a JSON file stored within a node that provides information about its hardware specifications, project details, and other relevant data.
- Chirpstack APIs
    - https://www.chirpstack.io/docs/chirpstack/api/grpc.html
    - https://github.com/chirpstack/chirpstack/tree/master/api/proto/api
- MQTT
    - https://pypi.org/project/paho-mqtt/
