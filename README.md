This package contains client code and API documentation for Cobalt's ASR service. Cobalt will provide interested customers an endpoint for our speech demo.

Requirement: This package requires python2.7, and the requests package: http://docs.python-requests.org/en/master/

The demo service is not meant to serve as part of any production system. The service recognizes 16khz audio, sent as 16 bit PCM samples. There are no performance or support service level agreements for this service. While our goal is to provide a stable interface, Cobalt reserves the right to change the API and endpoint URL at any time. Please contact us (http://www.cobaltspeech.com/contact-us.html) if you are interested in a production quality service.

Directory structure:

The docs directory contains HTML documentation for our API and objects: "ASR Web Api.html" describes and "Result Objects Model.html" describes the results object model.

The py/client directory contains an example python client. You will need to install python's requests module to use the example client.

The audio directory contains a single 16khz audio file.

Run the client as:

python py/client.py audio/hello_world_16khz.wav --url http://<url provided by Cobalt>

Expected results:

{"message": "returning results", "results": [{"status": "partial", "version": "1", "cobalt_object": "stt_result", "features": null, "nbest": [{"confidence": 1000, "hypothesis": [{"confidence": 1000, "type": "token", "features": null, "value": "Hello"}]}]}, {"status": "final", "version": "1", "cobalt_object": "stt_result", "features": null, "nbest": [{"confidence": 1000, "hypothesis": [{"confidence": 1000, "type": "token", "features": null, "value": "Hello"}, {"confidence": 1000, "type": "token", "features": null, "value": "World"}]}]}]}
