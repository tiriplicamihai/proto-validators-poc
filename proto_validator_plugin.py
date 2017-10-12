#!/usr/bin/env python
import itertools
import json
import sys

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto

import hello_pb2

def traverse(proto_file):

    def _traverse(package, items):
        for item in items:
            yield item, package

            if isinstance(item, DescriptorProto):
                for enum in item.enum_type:
                    yield enum, package

                for nested in item.nested_type:
                    nested_package = package + item.name

                    for nested_item in _traverse(nested, nested_package):
                        yield nested_item, nested_package

    return itertools.chain(
        _traverse(proto_file.package, proto_file.enum_type),
        _traverse(proto_file.package, proto_file.message_type),
    )


def generate_code(request, response):

    output = ""
    for proto_file in request.proto_file:
        # Parse request
        for item, package in traverse(proto_file):
            if package == "google.protobuf":
                continue

            if not isinstance(item, DescriptorProto):
                continue


            func_lines = ['def validate_%s(message):' % item.name]
            for field in item.field:
                if not field.options.HasExtension(hello_pb2.required):
                    continue

                if not field.options.Extensions[hello_pb2.required]:
                    continue

                # Check field exists
                func_lines.append(
                    '\tif not message.%s:\n\t\treturn False\n' % field.name)

                # If the field is a message, check if it's valid.
                if field.type == field.TYPE_MESSAGE:
                    type_name = field.type_name.split('.')[-1]
                    func_lines.append(
                        '\tif not validate_%s(message.%s):\n\t\treturn False\n' % (type_name, field.name)
                    )


            func_lines.append('\treturn True\n')

            func = '\n'.join(func_lines)

            output = output + func + '\n'

        # Fill response
        f = response.file.add()
        f.name = '%s_validators.py' % proto_file.name.split('.')[0]
        f.content = output


if __name__ == '__main__':
    # Read request message from stdin
    data = sys.stdin.read()

    #with open("/tmp/data.out", "r") as f:
    #    data = f.read()

    # Parse request
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_code(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.write(output)
