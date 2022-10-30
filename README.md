# R3E Python API
This package will allow you to easily read data from RaceRoom's Shared Memory API using Python.

## Usage:
```python
from r3e_api import R3ESharedMemory
import time

shared_memory = R3ESharedMemory()
shared_memory.update_offsets() # only needed once

while True:
    shared_memory.update_buffer()
    print(shared_memory.get_value('Player'))

    time.sleep(0.5)
```

The method `R3ESharedMemory.get_value()` accepts one string field. If you want to retrieve a sub-field, you can use dot notation, for example, `R3ESharedMemory.get_value('Player.Velocity')`.
