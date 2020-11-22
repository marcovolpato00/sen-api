# sen-api ![GitHub](https://img.shields.io/github/license/marcovolpato00/sen-api) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/marcovolpato00/sen-api/Upload%20Python%20Package)

A command-line tool to interact with **S**ervizio **E**lettrico **N**azionale web services.

## Features
Currently implemented:
- *Bills* informations and download in *PDF* format
- Some *client informations*
- *Consumption readings*
- Optional *JSON* output

Implementing in the future:
- More *client informations*
- Other stuff (***see below**)

*Interacting with *SEN* web services is a real pain since it's such badly designed so I don't really know if I will
keep adding more features.

## Getting started
### Obtaining an account
You can obtain an account to access *SEN* web services [here](https://www.servizioelettriconazionale.it/it-IT/saa/registrazione?app=ESE_AREA_CLIENTI&rreg=classica&group=PF_ESE_USR).
Of course, you should have an active electricity supply contract with Servizio Elettrico Nazionale.

### Installing
From source:
```
python setup.py install --user
```
Or in editable mode:
```
pip install -e ./
```
From pip:
```
pip install sen-api
```

## Usage
```
Usage: sen-api [OPTIONS] COMMAND [ARGS]...

Options:
  --version      Show the version and exit.
  -v, --verbose  Enable verbose logs.
  -j, --json     Print in JSON format when possible.
  --help         Show this message and exit.

Commands:
  authenticate
  bills
  client-info
  readings
```

#### Authentication
```
Usage: sen-api authenticate [OPTIONS]

Options:
  -u, --username TEXT
  -p, --password TEXT
  -f, --force          Force authentication using saved credentials.
  --help               Show this message and exit.
```

#### Bills
![bills example](examples/bills.svg)

#### Readings
![readings example](examples/readings.svg)
