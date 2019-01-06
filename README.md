Description
===========

I'm tired of console measuring of memory usage
```bash
while true; do
ps -C <ProgramName> -o pid=,%mem=,vsz= >> /tmp/mem.log
gnuplot /tmp/show_mem.plt
sleep 1
done &
```

Installation
============

`pip install mem_usage_ui`

Usage
=====

- Run in shell: `dsmyk$ mem_usage_ui`
- Go to `http://localhost:8080`



![alt text](https://raw.githubusercontent.com/parikls/mem_usage_ui/master/mem_usage_ui.png)
