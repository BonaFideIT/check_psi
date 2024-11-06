# check_psi
A nagios plugin for checking pressure stall information values provided by the kernel for cpu, io and memory

```
usage: check_psi.py [-h] {cpu,io,memory} ...

Nagios plugin to monitor current pressure stall information against desired thresholds

positional arguments:
  {cpu,io,memory}
    cpu            Override default values for cpu pressure.
    io             Override default values for io pressure.
    memory         Override default values for memory pressure.

options:
  -h, --help       show this help message and exit
```

You can override all default thresholds with sensible values of your own for warning and critical values like in this example for "io", cpu and memory are used exactly the same:

```
usage: check_psi.py io [-h] [--full-avg10 WARN:CRIT] [--full-avg60 WARN:CRIT] [--full-avg300 WARN:CRIT] [--some-avg10 WARN:CRIT] [--some-avg60 WARN:CRIT] [--some-avg300 WARN:CRIT]

options:
  -h, --help            show this help message and exit
  --full-avg10 WARN:CRIT
                        Override thresholds for warning and critical for avg10 time window for "full" values
  --full-avg60 WARN:CRIT
                        Override thresholds for warning and critical for avg60 time window for "full" values
  --full-avg300 WARN:CRIT
                        Override thresholds for warning and critical for avg300 time window for "full" values
  --some-avg10 WARN:CRIT
                        Override thresholds for warning and critical for avg10 time window for "some" values
  --some-avg60 WARN:CRIT
                        Override thresholds for warning and critical for avg60 time window for "some" values
  --some-avg300 WARN:CRIT
                        Override thresholds for warning and critical for avg300 time window for "some" values
```

# installation

1. clone repository to /usr/local/bin/
2. create virtualenv
3. install pipenv via pip
4. pipenv sync
5. test
