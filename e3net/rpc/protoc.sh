#! /bin/sh


for f in `ls protos/*.proto`
do
    echo "compiling:$f"
    python3 -m grpc_tools.protoc -Iprotos --python_out=protos_base/ --grpc_python_out=protos_base/ $f
done
