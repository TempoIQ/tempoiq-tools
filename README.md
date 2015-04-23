# TempoIQ Tools

This repository contains various tools for importing, exporting, and 
generating data with TempoIQ. 

Currently most tools are written in Python and rely on our 
[Python library](https://github.com/TempoIQ/tempoiq-python).
Feel free to submit PRs with additional tools in other languages, though.

A common convention in these tools is to use environment variables for
TempoIQ API credentials. This way, you don't need to pass them in on the 
command line for every invocation, and you can easily create shell scripts
to populate the environment variables for dev/staging/production backends.
For example:

```
#!/bin/sh
export TIQ_HOST=my-host.backend.tempoiq.com
export TIQ_KEY=1234567890abcdef1234567890abcdef
export TIQ_SECRET=1234567890abcdef1234567890abcdef
```