from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport
from typing import Type, TypeVar, Any, Union

T = TypeVar('T')  # Generic type variable


def thrift_to_dict(thrift_obj) -> Union[dict, list]:
    if isinstance(thrift_obj, list):
        return [thrift_to_dict(item) for item in thrift_obj]
    elif hasattr(thrift_obj, "__dict__"):
        return {key: thrift_to_dict(value) for key, value in thrift_obj.__dict__.items() if value is not None}
    else:
        return thrift_obj


def thrift_to_binary(thrift_obj):
    transport = TTransport.TMemoryBuffer()
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    thrift_obj.write(protocol)
    return transport.getvalue()


def thrift_read(binary_data: Any, thrift_class: Type[T]) -> T:
    transport = TTransport.TMemoryBuffer(binary_data)
    record = thrift_class()
    record.read(TBinaryProtocol.TBinaryProtocol(transport))
    return record
