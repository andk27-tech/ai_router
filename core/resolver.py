def resolve_call(name, import_map):
    return import_map.get(name, name)
