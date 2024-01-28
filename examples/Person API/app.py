import uvicorn

if __name__ == "__main__":
  config = uvicorn.Config('main:app', log_level='debug', port=3000)
  server = uvicorn.Server(config)
  server.run()