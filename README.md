This package contains client code and API documentation for Cobalt's ASR (automatic speech recognition) service. Cobalt will provide interested customers an endpoint URL for a demo ASR model to use with this client package.  Please contact us at http://cobaltspeech.com/contact-us.html to obtain it.

The demo service is not meant to serve as part of any production system. There are no performance or support service level agreements for this service. While our goal is to provide a stable interface, Cobalt reserves the right to change the API and endpoint URL at any time. The demo recognizes 16khz mono-channel audio, sent as 16 bit PCM samples. It is for general conversational uni-speaker English spoken in a noise-free background.  Please contact us at (http://cobaltspeech.com/contact-us.html) if you are interested in different audio formats, a production quality service, domain/application-specific models with improved accuracy/speed, other languages, speaker diarization, or any customization. 

Requirement: This package requires python2.7, and the requests package: http://docs.python-requests.org/en/master/
The py/client directory contains an example python client.
You will need to install python's requests module to use the example client.

See the github wiki at https://github.com/cobaltspeech/cobalt-client/wiki
for documentation on how to use this client with our API and result objects: "ASR Web API" and "Result Objects Model".

The audio directory contains a single 16khz audio file.

Run the client as:

python py/client.py audio/hello_world_16khz.wav --url http://<url provided by Cobalt>

Expected results:

{"message": "returning results", "results": [{"status": "partial", "version": "1", "cobalt_object": "stt_result", "features": null, "nbest": [{"confidence": 1000, "hypothesis": [{"confidence": 1000, "type": "token", "features": null, "value": "Hello"}]}]}, {"status": "final", "version": "1", "cobalt_object": "stt_result", "features": null, "nbest": [{"confidence": 1000, "hypothesis": [{"confidence": 1000, "type": "token", "features": null, "value": "Hello"}, {"confidence": 1000, "type": "token", "features": null, "value": "World"}]}]}]}

