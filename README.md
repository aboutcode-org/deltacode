# Deltacode
```
Usage: deltacode [OPTIONS]

  This script identifies the changes that need to be made to the OLD scan
  file (-o or -old) in order to generate the NEW scan file (-n or -new). The
  results are written to a .csv file at a user-designated location (-c or
  -csv-file).

Options:
  -h, --help           Show this message and exit.
  -n, --new PATH       Identify the path to the "new" scan file  [required]
  -o, --old PATH       Identify the path to the "old" scan file  [required]
  -c, --csv-file PATH  Identify the path to the .csv output file  [required]
```

### How to use:
```
$ deltacode -n ~/postgresql-9.6.5.json -o ~/posgresql-10.0.json -c ~/psql-10.0-psql-9.6.5-delta.csv
```

### Notes:
* `deltacode` also collects statistical information, like # of files and other percentages. See https://github.com/nexB/spats/issues/166. Currently, this output is not present in the `csv` output
* We will be retiring the `csv` output in favor of a json output (see: https://github.com/nexB/spats/issues/150) 
* json output will be consumable by other utilities. There will also be a json -> csv converter in the future as well. 

### Future TODOs/additions:
* json output
* move to self-contained public repo
* Use `license` information from scan to determine deltas as well (As opposed to strictly fileinfo)
* Use `copyright` information from scan to determine deltas
