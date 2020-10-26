# sen-api ![GitHub](https://img.shields.io/github/license/marcovolpato00/sen-api)

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

## Installing
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
