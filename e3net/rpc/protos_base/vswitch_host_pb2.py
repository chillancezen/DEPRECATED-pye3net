# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vswitch_host.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='vswitch_host.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x12vswitch_host.proto\"\x06\n\x04null\"<\n\x07req_key\x12\x10\n\x08per_uuid\x18\x01 \x01(\x08\x12\x11\n\thost_name\x18\x02 \x01(\t\x12\x0c\n\x04uuid\x18\x03 \x01(\t\"g\n\x10res_vswitch_host\x12\n\n\x02id\x18\x01 \x01(\t\x12\x13\n\x0bhost_status\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x0c\n\x04name\x18\x04 \x01(\t\x12\x0f\n\x07host_ip\x18\x05 \x01(\t2\xb0\x02\n\x0cvswitch_host\x12\x35\n\x14rpc_get_vswitch_host\x12\x08.req_key\x1a\x11.res_vswitch_host\"\x00\x12:\n\x15rpc_list_vswitch_host\x12\x08.req_key\x1a\x11.res_vswitch_host\"\x00(\x01\x30\x01\x12\x44\n\x1arpc_register_vswiitch_host\x12\x11.res_vswitch_host\x1a\x11.res_vswitch_host\"\x00\x12\x30\n\x1brpc_unregister_vswitch_host\x12\x08.req_key\x1a\x05.null\"\x00\x12\x35\n\x17rpc_update_vswitch_host\x12\x11.res_vswitch_host\x1a\x05.null\"\x00\x62\x06proto3')
)




_NULL = _descriptor.Descriptor(
  name='null',
  full_name='null',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=22,
  serialized_end=28,
)


_REQ_KEY = _descriptor.Descriptor(
  name='req_key',
  full_name='req_key',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='per_uuid', full_name='req_key.per_uuid', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='host_name', full_name='req_key.host_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='uuid', full_name='req_key.uuid', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=90,
)


_RES_VSWITCH_HOST = _descriptor.Descriptor(
  name='res_vswitch_host',
  full_name='res_vswitch_host',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='res_vswitch_host.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='host_status', full_name='res_vswitch_host.host_status', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='res_vswitch_host.description', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='res_vswitch_host.name', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='host_ip', full_name='res_vswitch_host.host_ip', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=92,
  serialized_end=195,
)

DESCRIPTOR.message_types_by_name['null'] = _NULL
DESCRIPTOR.message_types_by_name['req_key'] = _REQ_KEY
DESCRIPTOR.message_types_by_name['res_vswitch_host'] = _RES_VSWITCH_HOST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

null = _reflection.GeneratedProtocolMessageType('null', (_message.Message,), dict(
  DESCRIPTOR = _NULL,
  __module__ = 'vswitch_host_pb2'
  # @@protoc_insertion_point(class_scope:null)
  ))
_sym_db.RegisterMessage(null)

req_key = _reflection.GeneratedProtocolMessageType('req_key', (_message.Message,), dict(
  DESCRIPTOR = _REQ_KEY,
  __module__ = 'vswitch_host_pb2'
  # @@protoc_insertion_point(class_scope:req_key)
  ))
_sym_db.RegisterMessage(req_key)

res_vswitch_host = _reflection.GeneratedProtocolMessageType('res_vswitch_host', (_message.Message,), dict(
  DESCRIPTOR = _RES_VSWITCH_HOST,
  __module__ = 'vswitch_host_pb2'
  # @@protoc_insertion_point(class_scope:res_vswitch_host)
  ))
_sym_db.RegisterMessage(res_vswitch_host)



_VSWITCH_HOST = _descriptor.ServiceDescriptor(
  name='vswitch_host',
  full_name='vswitch_host',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=198,
  serialized_end=502,
  methods=[
  _descriptor.MethodDescriptor(
    name='rpc_get_vswitch_host',
    full_name='vswitch_host.rpc_get_vswitch_host',
    index=0,
    containing_service=None,
    input_type=_REQ_KEY,
    output_type=_RES_VSWITCH_HOST,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='rpc_list_vswitch_host',
    full_name='vswitch_host.rpc_list_vswitch_host',
    index=1,
    containing_service=None,
    input_type=_REQ_KEY,
    output_type=_RES_VSWITCH_HOST,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='rpc_register_vswiitch_host',
    full_name='vswitch_host.rpc_register_vswiitch_host',
    index=2,
    containing_service=None,
    input_type=_RES_VSWITCH_HOST,
    output_type=_RES_VSWITCH_HOST,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='rpc_unregister_vswitch_host',
    full_name='vswitch_host.rpc_unregister_vswitch_host',
    index=3,
    containing_service=None,
    input_type=_REQ_KEY,
    output_type=_NULL,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='rpc_update_vswitch_host',
    full_name='vswitch_host.rpc_update_vswitch_host',
    index=4,
    containing_service=None,
    input_type=_RES_VSWITCH_HOST,
    output_type=_NULL,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_VSWITCH_HOST)

DESCRIPTOR.services_by_name['vswitch_host'] = _VSWITCH_HOST

# @@protoc_insertion_point(module_scope)
