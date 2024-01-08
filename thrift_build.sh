thrift --gen py -out .\ .\thrift\com.inference.common.thrift
thrift --gen py -out .\ .\thrift\com.inference.rest.thrift
thrift --gen py -out .\ .\thrift\com.inference.ws.thrift

thrift --gen html -out .\html .\thrift\com.inference.common.thrift
thrift --gen html -out .\html .\thrift\com.inference.ws.thrift
thrift --gen html -out .\html .\thrift\com.inference.rest.thrift
thrift --gen html -out .\html .\thrift\com.inference.thrift