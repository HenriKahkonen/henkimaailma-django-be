def environment(request):
    host = request.get_host().split(":")[0]  # strip port, e.g. "localhost:8000" -> "localhost"
    return {"is_local_env": host in ("localhost", "127.0.0.1")}