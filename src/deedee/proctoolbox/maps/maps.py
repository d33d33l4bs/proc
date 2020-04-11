
import re

from dataclasses import dataclass


#############
# Constants #
#############

# allows to parse proc maps files
_RE_MAPS = re.compile(
    r'^([0-9a-f]+)-([0-9a-f]+) ([rwxsp-]{4}) ([0-9a-f]+) ([^ ]+) (\d+)\s*([^ $]*?)$',
    flags=re.MULTILINE
)


###########
# Classes #
###########

@dataclass
class Mapping:
    '''Stores mappings information.

    A mapping corresponds to one line into a proc maps files.
    '''
    start_address : int
    end_address   : int
    size          : int
    perms         : str
    offset        : int
    dev           : str
    inode         : str
    pathname      : str


#############
# Functions #
#############

def get_maps(pid, filter_=None):
    '''Parses the maps file of a process.

    Parameters
    ----------
    pid : int
        The pid of the process.
    filter_ : callable, optional
        If defined, this one allows to filter the mappings.
        In order to facilitate the filtering, some filters are already defined:
        has_perms, has_path, size, etc.

    Examples
    --------
    Retrieving all the mappings of a process:
    >>> get_maps(1234)

    Retrieving only executable mappings:
    >>> get_maps(1234, lambda m: 'x' in m.perms)

    Retrieving only writable mapping with a size greater or equal to 4096:
    >>> get_maps(1234, lambda m: 'w' in m.perms and m.size >= 4096)
    '''
    maps_path = f'/proc/{pid}/maps'
    with open(maps_path, 'r') as f:
        maps = f.read()
    regions = []
    for m in _RE_MAPS.findall(maps):
        start_address = int(m[0], 16)
        end_address    = int(m[1], 16)
        size          = end_address - start_address
        offset        = int(m[3], 16)
        region        = Mapping(
            start_address,
            end_address,
            size,
            m[2],
            offset,
            m[4],
            m[5],
            m[6]
        )
        if filter_ is None or filter_(region):
            regions.append(region)
    return regions

