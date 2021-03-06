# -*- coding: utf-8 -*-
"""
    Sycamore - Datasets

    Datasets are used by the DataBrowserWidget, and with the
    statistics code.

    @copyright: 2002 by J�rgen Hermann <jh@web.de>
    @license: GNU GPL, see COPYING for details.
"""

class Column:
    """
    Meta-data for a column.
    """
    _SLOTS = [
        ('label', ''),
        ('sortable', 0),
        ('hidden', 0),
        ('align', ''),
        ]

    def __init__(self, name, **kw):
        self.name = name
        for slot, defval in self._SLOTS:
            setattr(self, slot, kw.get(slot, defval))

class Dataset:
    """
    Holds a 2-dimensional data set (m rows of n columns)
    and associated meta-data (column titles, etc.)
    """
    def __init__(self):
        self.columns = []
        self.data = []
        self._pos = 0

    def __len__(self):
        return len(self.data)

    def reset(self):
        """
        Reset iterator to start.
        """
        self._pos = 0

    def next(self):
        """
        Return next row as a tuple, ordered by columns.
        """
        if self._pos >= len(self):
            return None

        row = self.data[self._pos]
        self._pos += 1
        return row

    def addRow(self, row):
        """
        Add a row to the dataset.
        """
        self.data.append(row)


class TupleDataset(Dataset):
    """
    A dataset that stores tuples.
    """
    pass


class DictDataset(Dataset):
    """
    A dataset that stores dicts as the rows.
    """
    def next(self):
        row = Dataset.next(self)
        return tuple([row[col.name] for col in self.columns])

class DbDataset(Dataset):
    pass
