#
# Autogenerated by Thrift Compiler (0.19.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys

from thrift.transport import TTransport
all_structs = []


class SinglePrompt(object):
    """
    Attributes:
     - request_id
     - prompt

    """


    def __init__(self, request_id=None, prompt=None,):
        self.request_id = request_id
        self.prompt = prompt

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.request_id = iprot.readString().decode('utf-8', errors='replace') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.prompt = iprot.readString().decode('utf-8', errors='replace') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('SinglePrompt')
        if self.request_id is not None:
            oprot.writeFieldBegin('request_id', TType.STRING, 1)
            oprot.writeString(self.request_id.encode('utf-8') if sys.version_info[0] == 2 else self.request_id)
            oprot.writeFieldEnd()
        if self.prompt is not None:
            oprot.writeFieldBegin('prompt', TType.STRING, 2)
            oprot.writeString(self.prompt.encode('utf-8') if sys.version_info[0] == 2 else self.prompt)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        if self.request_id is None:
            raise TProtocolException(message='Required field request_id is unset!')
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class GenerationConfig(object):
    """
    Attributes:
     - num_beams
     - do_sample
     - temperature
     - top_p
     - top_k
     - max_new_tokens
     - repetition_penalty
     - length_penalty

    """


    def __init__(self, num_beams=None, do_sample=None, temperature=None, top_p=None, top_k=None, max_new_tokens=None, repetition_penalty=None, length_penalty=None,):
        self.num_beams = num_beams
        self.do_sample = do_sample
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_new_tokens = max_new_tokens
        self.repetition_penalty = repetition_penalty
        self.length_penalty = length_penalty

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I32:
                    self.num_beams = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.BOOL:
                    self.do_sample = iprot.readBool()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.DOUBLE:
                    self.temperature = iprot.readDouble()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.DOUBLE:
                    self.top_p = iprot.readDouble()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.I32:
                    self.top_k = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.I32:
                    self.max_new_tokens = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 7:
                if ftype == TType.DOUBLE:
                    self.repetition_penalty = iprot.readDouble()
                else:
                    iprot.skip(ftype)
            elif fid == 8:
                if ftype == TType.DOUBLE:
                    self.length_penalty = iprot.readDouble()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('GenerationConfig')
        if self.num_beams is not None:
            oprot.writeFieldBegin('num_beams', TType.I32, 1)
            oprot.writeI32(self.num_beams)
            oprot.writeFieldEnd()
        if self.do_sample is not None:
            oprot.writeFieldBegin('do_sample', TType.BOOL, 2)
            oprot.writeBool(self.do_sample)
            oprot.writeFieldEnd()
        if self.temperature is not None:
            oprot.writeFieldBegin('temperature', TType.DOUBLE, 3)
            oprot.writeDouble(self.temperature)
            oprot.writeFieldEnd()
        if self.top_p is not None:
            oprot.writeFieldBegin('top_p', TType.DOUBLE, 4)
            oprot.writeDouble(self.top_p)
            oprot.writeFieldEnd()
        if self.top_k is not None:
            oprot.writeFieldBegin('top_k', TType.I32, 5)
            oprot.writeI32(self.top_k)
            oprot.writeFieldEnd()
        if self.max_new_tokens is not None:
            oprot.writeFieldBegin('max_new_tokens', TType.I32, 6)
            oprot.writeI32(self.max_new_tokens)
            oprot.writeFieldEnd()
        if self.repetition_penalty is not None:
            oprot.writeFieldBegin('repetition_penalty', TType.DOUBLE, 7)
            oprot.writeDouble(self.repetition_penalty)
            oprot.writeFieldEnd()
        if self.length_penalty is not None:
            oprot.writeFieldBegin('length_penalty', TType.DOUBLE, 8)
            oprot.writeDouble(self.length_penalty)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(SinglePrompt)
SinglePrompt.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'request_id', 'UTF8', None, ),  # 1
    (2, TType.STRING, 'prompt', 'UTF8', None, ),  # 2
)
all_structs.append(GenerationConfig)
GenerationConfig.thrift_spec = (
    None,  # 0
    (1, TType.I32, 'num_beams', None, None, ),  # 1
    (2, TType.BOOL, 'do_sample', None, None, ),  # 2
    (3, TType.DOUBLE, 'temperature', None, None, ),  # 3
    (4, TType.DOUBLE, 'top_p', None, None, ),  # 4
    (5, TType.I32, 'top_k', None, None, ),  # 5
    (6, TType.I32, 'max_new_tokens', None, None, ),  # 6
    (7, TType.DOUBLE, 'repetition_penalty', None, None, ),  # 7
    (8, TType.DOUBLE, 'length_penalty', None, None, ),  # 8
)
fix_spec(all_structs)
del all_structs
