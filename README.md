# indico-fetcher
[![Test Indico fetcher](https://github.com/unibonn/indico-fetcher/actions/workflows/test.yml/badge.svg)](https://github.com/unibonn/indico-fetcher/actions/workflows/test.yml)

Utility to fetch contributions to [Indico](https://getindico.io/) attachments and store them in a structured manner.

This tool fetches an Indico event and stores the files in a structure such as:
```
2019-07-03/2.001/10:00:00_10:05:00/1562043626_sometalk.pdf
2019-07-03/2.003/11:00:00_11:40:00/1562137411_another_talk.pdf
...
```
Notably, the talks are sorted by date, room (if available), time slot of the contribution and finally the filename prefixed with the unix timestamp of the last modification. 

## Use case

This tool was written with the following use case in mind:
* A large conference in multiple rooms is being held, using multiple conference laptops.
* A common cloud file storage solution is available.
* Talks should be downloaded automatically and appear in a given folder for the corresponding room.

Using such an approach noticeably reduces the handover time between talks. 

## Development status

This project is still in its early stages, notably, it is still missing many basics:
* Error handling
* More extensive CI
* Commandline argument handling

Contributions are very welcome!
