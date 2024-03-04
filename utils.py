import gzip
import os
import codecs
import datetime

def get_timestamp(line):

  try:
    timestamp_str = line.split(' ')[0] + ' ' + line.split(' ')[1]
  except IndexError:
    return None

  try:
    return datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S:%f')
  except Exception:
    return None

def filter_by_time(lines, start_time, end_time):
  filtered_lines = []
  is_timestamp_extracted = False

  for line in lines:
    timestamp = get_timestamp(line)

    if timestamp is None:
      if is_timestamp_extracted:
        filtered_lines[-1] += '\n' + line
      else:
        continue
    elif start_time <= timestamp <= end_time:
      filtered_lines.append(line)
      is_timestamp_extracted = True
    else:
      is_timestamp_extracted = False
      continue

  if is_timestamp_extracted:
    filtered_lines.append('\n')

  return filtered_lines

def find_pattern(pattern, path, start_time, end_time):
    matches = []
    for filename in os.listdir(path):
        if filename.endswith('.log') or filename.endswith('.gz'):
            full_path = os.path.join(path, filename)
            if filename.endswith('.gz'):
                with gzip.open(full_path, 'rt', 'utf-8', errors='replace') as f:
                    file_content = f.read()
            else:
                with codecs.open(full_path, 'r', 'utf-8', errors='replace') as f:
                    file_content = f.read()

            lines = file_content.splitlines()
            lines = filter_by_time(lines, start_time, end_time)

            for line in lines:
                if pattern in line:
                    timestamp = get_timestamp(line)
                    matches.append({'timestamp': timestamp, 'message': line, 'file_path': full_path})

    return matches
