def thrift_to_dict(thrift_obj):
    if isinstance(thrift_obj, list):
        return [thrift_to_dict(item) for item in thrift_obj]
    elif hasattr(thrift_obj, "__dict__"):
        return {key: thrift_to_dict(value) for key, value in thrift_obj.__dict__.items() if value is not None}
    else:
        return thrift_obj

