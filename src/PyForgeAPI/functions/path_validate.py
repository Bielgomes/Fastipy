def path_validate(self, path, method):
  if method not in self.routes[path]: return False

  full_path = self.path
  
  if '?' in full_path:
    full_path = full_path.split('?')[0]

  original_parts = full_path.split("/")
  path_parts = path.split("/")

  if len(original_parts) != len(path_parts): return False

  for i in range(len(original_parts)):
    if original_parts[i] == path_parts[i] or (path_parts[i].startswith(':') and original_parts[i]):
      continue
    else:
      return False

  return True