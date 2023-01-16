def path_validate(original_path, path):
  original_parts = original_path.split("/")
  path_parts = path.split("/")

  if len(original_parts) != len(path_parts): return False

  for i in range(len(original_parts)):
    if original_parts[i] == path_parts[i] or (path_parts[i].startswith(':') and original_parts[i]):
      continue
    else:
      return False

  return True