# TooManyPorts

A lightweight Python library for port allocation, monitoring, and management.

## Installation

Install via pip:

```bash
pip install port-manager-pkg
```

## Usage

```python
from toomanyports import PortManager

pm = PortManager()
```

### Examples

#### Find a free port

Find a single available port starting from 3000:

```python
port = pm.find(3000, 1)[0]
```

#### Find multiple free ports

```python
ports = pm.find(3000, 2)
```

#### Kill a process on a specific port

```python
success = pm.kill(8080)
```

#### Kill processes on multiple ports

```python
results = pm.kill_all([8080, 8081])
```

#### List port usage

Retrieve the process IDs listening on ports 3000 through 3010:

```python
usage = pm.list_usage((3000, 3010))
```

#### Obtain a random ephemeral port

```python
random_port = pm.random_port()
```

#### Shorthand call

```python
free_port = pm(3000)
```

## Testing

Run the test suite with:

```bash
pytest tests_core.py
```

## License

This project is licensed under the MIT License.
