# wes-chirpstack-tracker
Tracks lorawan devices sending payloads to a Chirpstack Server to report to a Django app.

- Chirpstack Server: [wes-chirpstack](https://github.com/waggle-sensor/waggle-edge-stack/tree/main/kubernetes/wes-chirpstack) 
- Django App: [waggle-auth-app](https://github.com/waggle-sensor/waggle-auth-app)
>NOTE: The Django App encompasses the models, serializers, and views necessary for facilitating API calls within `app/django_client/`

## Running Individual Packages
The packages in `app/` can be used invidually by running the main file. Example:
```sh
python3 app/chirpstack_client/client.py --debug --chirpstack-account-email test@email.com --chirpstack-account-password test --chirpstack-api-interface localhost:8080
```
>NOTE: the main file name will be different based on the package

## Test Suite

To run the test suite download the requirements in the test folder, then run the following command
```
pytest
```

> TODO: include notes on running scalene


## More Information
- A "Manifest" refers to a JSON file stored within a node that provides information about its hardware specifications, project details, and other relevant data.
- Chirpstack APIs
    - https://www.chirpstack.io/docs/chirpstack/api/grpc.html
    - https://github.com/chirpstack/chirpstack/tree/master/api/proto/api
- MQTT
    - https://pypi.org/project/paho-mqtt/