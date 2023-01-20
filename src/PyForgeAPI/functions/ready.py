def ready(application, host, port, debug):
  open_browser = f"| Open http://{host}:{port}"
  py_forge_api = "| PyForgeAPI Server Running"
  debug_mode = "| Debug mode > True"
  finish = "| Control + C to exit"
  application_port = f"| {application} on port > {port}"

  if len(application_port) < len(open_browser):
    longest = len(open_browser)
  else:
    longest = len(application_port)
    
  top_down = "+" + "-"*(longest) + "+"

  def add_pipe(string):
    return string + " "*(longest - len(string) + 1) + "|"
  
  print('\n'+top_down)
  print(add_pipe(py_forge_api))

  if debug:
    print(add_pipe(debug_mode))

  print(add_pipe(application_port))
  print(add_pipe(open_browser))

  print(add_pipe("|"))
  print(add_pipe(finish))

  print(top_down+'\n')