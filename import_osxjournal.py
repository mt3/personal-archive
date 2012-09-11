#!/usr/bin/python2.7

from dateutil import parser
import plistlib
import journal
import os
import re
import utils
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter

import StringIO

dry_run = False

def Run():
  this_dir = os.path.dirname(__file__)
  journal_file = os.path.join(this_dir, '../old journal app/journal.dat')
  raw_entries = plistlib.readPlist(journal_file)

  acc = utils.EntryAccumulator(lambda x: x['date'])
  for k, v in raw_entries.iteritems():
    if not v: continue
    # 12/29/2001 -> 2001-12-29
    new_k = re.sub(r'(\d\d)/(\d\d)/(\d\d\d\d)', r'\3-\1-\2', k)
    d = parser.parse(new_k)

    if isinstance(v, plistlib.Data):
      f = StringIO.StringIO(v.data)
      doc = Rtf15Reader.read(f)
      txt = PlaintextWriter.write(doc).getvalue()
      acc.add({
        'date': d,
        'rtf': v.data,
        'text': txt
      })
    else:
      acc.add({
        'date': d,
        'text': v
      })

  for day, entries in acc.iteritems():
    assert len(entries) == 1
    entry = entries[0]

    summary = utils.SummarizeText(entry['text'])
    utils.WriteSingleSummary(day, maker='osxapp', summary=summary, dry_run=dry_run)
    if 'rtf' in entry:
      utils.WriteOriginal(day, maker='osxapp', contents=entry['rtf'], filename='journal.rtf', dry_run=dry_run)
    else:
      utils.WriteOriginal(day, maker='osxapp', contents=entry['text'].encode('utf8'), filename='journal.txt', dry_run=dry_run)


if __name__ == '__main__':
  Run()
