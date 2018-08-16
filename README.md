# snips-nlu-injection
## About
This script is an addon for https://snips.ai

Snips currently only supports injecting words to ASR, but not to NLU.\
This means, that snips will understand the words you added through asr injection, but it won't understand the meaning.

More precisely, it will detect that you said _"Switch NewDevice in NewRoom on"_.\
But it won't be able to assign _NewDevice_ to the **device** slot and _NewRoom_ to the **room** slot in your intent.\
Because of that, asr injection isn't as powerful as one might have hoped at the moment.\
I'm pretty sure the developers of snips.ai are already working on their own solution.

This script tries to fill the gap in the meantime.

## Dependencies
 - `paho` - python MQTT
 - `toml` - library to read the snips configuration file
 - `mpg123` - binary for converting the MP3s Polly responds with, into WAVs which Snips can process.


## Installation
copy _nlu-inject.py_ to _/opt/snips-nlu-inject/_\
copy _nlu-inject.service_ to _/etc/systemd/system/_

```
sudo chmod +x /opt/snips-nlu-inject/nlu-inject.py
sudo systemctl enable nlu-inject.service
sudo systemctl start nlu-inject.service
```

The script will listen to messages on the `hermes/asr/inject` topic\
and inject the values to nlu. (_nlu_engine.json_ and _intent_parser.json_)\
After that, the _snips-nlu.service_ gets restarted.

Injection has to be done again after you update/install a new version of your assitant.\
But this also applies to asr injection, so you should already be familier with that.

The script needs read write access to both files mentioned above.
