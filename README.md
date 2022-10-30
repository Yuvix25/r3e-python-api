# R3E Python API
This package will allow you to easily read data from RaceRoom's Shared Memory API using Python.

## Usage:
```python
import r3e-api as r3e
import mmap, time

mmap_file = mmap.mmap(-1, 40960, "Local\\$R3E",  access=mmap.ACCESS_READ) # read the shared memory file

while True:
    mmap_file.seek(0)
    data = mmap_file.read()
    print(r3e.get_value(data, "DriverInfo")) # for more valid keys, take a look at data.cs
    time.sleep(0.1)
```