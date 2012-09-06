"""Tools for building a personal archive in a canonical format."""

from collections import defaultdict
from datetime import date, timedelta
import os
import json
import re
import glob
import shutil

ArchiveDirectory = os.path.expanduser("~/Dropbox/Personal Archive")


def GetDirectoryForDay(d):
  """Returns path to (Personal Archive)/YYYY/MM/DD."""
  return '%s/%04d/%02d/%02d' % (ArchiveDirectory, d.year, d.month, d.day)


def MaybeMakeDirectory(day_dir):
  """Recursively create the path to a directory."""
  if os.path.exists(day_dir): return
  os.makedirs(day_dir)


def WriteSingleSummary(d=0, maker="", summary="", thumbnail="", url="", dry_run=False):
  """Write a single entry for a given date to disk.

  thumbnail is optional, all other arguments are mandatory."""
  assert d
  assert maker
  assert summary

  day_dir = GetDirectoryForDay(d)
  MaybeMakeDirectory(day_dir)
  filename = '%s/%s.json' % (day_dir, maker)

  data = {
    'summary': summary,
  }
  if thumbnail: data['thumbnail'] = thumbnail
  if url: data['url'] = url

  if dry_run:
    print 'Would write to %s:' % filename
    print json.dumps(data)
  else:
    json.dump(data, file(filename, 'w'))


def WriteOriginal(d=0, maker="", filename="", contents="", dry_run=False):
  """Write out some unsummarized data for a particular maker.
  
  All arguments are required.
  """
  assert d
  assert maker
  assert filename
  assert contents

  maker_dir = '%s/%s' % (GetDirectoryForDay(d), maker)
  MaybeMakeDirectory(maker_dir)
  path = '%s/%s' % (maker_dir, filename)
  if not dry_run:
    file(path, 'w').write(contents)
  else:
    print 'Would write %d bytes to %s' % (len(contents), path)


def SummarizeText(txt):
  """Cut text off at 160 characters and add '...' if necessary."""
  txt = re.sub(r'\n+', ' ', txt)
  if len(txt) < 160: return txt
  return txt[0:157] + '...'


def GetActiveDaysForMaker(maker):
  """Returns a sorted list of date objects which have data for the maker."""
  assert maker
  dates = []
  for path in glob.glob('%s/????/??/??/%s.json' % (ArchiveDirectory, maker)):
    m = re.search(r'(\d\d\d\d)/(\d\d)/(\d\d)/', path)
    assert m
    year, month, day = m.groups()
    dates.append(date(int(year), int(month), int(day)))

  dates.sort()
  return dates


def GetAllMakers():
  """Returns a list of all makers which have saved data in the archive."""
  makers = set()
  for path in glob.glob('%s/????/??/??/*.json' % ArchiveDirectory):
    maker_ext = os.path.basename(path)
    maker, ext = os.path.splitext(maker_ext)
    makers.add(maker)

  return list(makers)


def GetDailySummaries(dense=False):
  """Returns a date -> maker -> summary dict mapping."""
  days = defaultdict(lambda: {})

  for path in glob.glob('%s/????/??/??/*.json' % ArchiveDirectory):
    m = re.search(r'(\d\d\d\d)/(\d\d)/(\d\d)/([^.]+)', path)
    assert m
    year, month, day, maker = m.groups()
    d = date(int(year), int(month), int(day))
    days[d][maker] = json.load(file(path))

  if dense:
    d = date(2000, 1, 1)
    today = date.today()
    while d <= today:
      if d not in days:
        days[d] = {}
      d += timedelta(days=+1)

  return days


def removeEmptyFolders(path):
  if not os.path.isdir(path):
    return
 
  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath):
        removeEmptyFolders(fullpath)
 
  # if folder empty, delete it
  files = os.listdir(path)
  if len(files) == 0:
    print "Removing empty folder:", path
    os.rmdir(path)


def DeleteAllForMaker(maker):
  """Delete all traces of a particular maker in the archive directory."""
  files = glob.glob('%s/????/??/??/%s.json' % (ArchiveDirectory, maker))
  for path in files:
    print 'Deleting %s' % path
    os.remove(path)
  dirs = glob.glob('%s/????/??/??/%s' % (ArchiveDirectory, maker))
  for path in dirs:
    print 'Deleting directory %s' % path
    shutil.rmtree(path)

  removeEmptyFolders(ArchiveDirectory)
