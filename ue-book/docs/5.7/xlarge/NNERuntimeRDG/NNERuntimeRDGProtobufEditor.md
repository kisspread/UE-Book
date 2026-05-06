# NNERuntimeRDGProtobufEditor

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | Protobuf 编辑器库 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方库头文件及预编译库） |
| 模块 | `NNERuntimeRDGProtobufEditor` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

本模块将 Google Protocol Buffers（protobuf）库编译为 Unreal Engine 可用的编辑器版本，提供完整的 protobuf 头文件和预编译库。在 NNERuntimeRDG 生态中，它被 `NNERuntimeRDGOnnxEditor` 等模块依赖，用于解析 ONNX 模型文件（`.onnx` 文件以 protobuf 格式存储）。通过本模块，开发者可以在编辑器环境中直接读取、修改或序列化 ONNX 模型的结构化数据。

## 使用场景

- **ONNX 模型解析**：在编辑器工具中加载 `.onnx` 模型，提取网络结构、权重等元信息。
- **模型编辑与转换**：修改 ONNX 模型中的特定节点或属性，然后重新序列化保存。
- **自定义模型格式处理**：任何需要 protobuf 序列化/反序列化功能的编辑器扩展。

## 蓝图用法

本模块为纯 C++ 第三方库，不提供任何蓝图可调用节点。所有功能需在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "google/protobuf/descriptor.h"
#include "google/protobuf/message.h"
// 其他 protobuf 头文件按需引入
```

### 基本用法

以下示例展示如何从原始字节流中解析一个 `google::protobuf::FileDescriptorProto`（这是 ONNX 模型的基本组成部分）。

```cpp
// 假设 OnnxData 是包含完整 ONNX 文件内容的 TArray<uint8>
TArray<uint8> OnnxData = /* 从文件读取 */;

// 构建 FileDescriptorProto
google::protobuf::FileDescriptorProto FileProto;
if (FileProto.ParseFromArray(OnnxData.GetData(), OnnxData.Num()))
{
    // 成功解析，可访问其字段
    UE_LOG(LogTemp, Log, TEXT("Parsed proto message type: %s"), UTF8_TO_TCHAR(FileProto.GetTypeName().c_str()));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Failed to parse protobuf data."));
}
```

### 进阶用法

结合 `Importer` 和 `DynamicMessageFactory`，可以在运行时动态创建并操作任意 protobuf 消息类型。

```cpp
#include "google/protobuf/compiler/importer.h"
#include "google/protobuf/dynamic_message.h"

// 创建一个基于磁盘的源树，加载 .proto 文件
google::protobuf::compiler::DiskSourceTree SourceTree;
SourceTree.MapPath("", FPaths::ProjectDir() / "Protos");

google::protobuf::compiler::Importer Importer(&SourceTree, nullptr);
const google::protobuf::FileDescriptor* FileDesc = Importer.Import("my_message.proto");
if (!FileDesc) return;

// 获取消息类型
const google::protobuf::Descriptor* MsgDesc = FileDesc->FindMessageTypeByName("MyMessage");
if (!MsgDesc) return;

// 使用 DynamicMessageFactory 创建消息实例
google::protobuf::DynamicMessageFactory Factory;
std::unique_ptr<google::protobuf::Message> Message(Factory.GetPrototype(MsgDesc)->New());

const google::protobuf::Reflection* Reflection = Message->GetReflection();
const google::protobuf::FieldDescriptor* Field = MsgDesc->FindFieldByName("my_field");
if (Field && Field->cpp_type() == google::protobuf::FieldDescriptor::CPPTYPE_INT32)
{
    Reflection->SetInt32(Message.get(), Field, 42);
}
```

## Demo 示例

创建一个编辑器模块，从 `.onnx` 文件中提取模型的所有节点名称并打印。

```cpp
// MyOnnxUtils.h
#pragma once
#include "CoreMinimal.h"

class FMyOnnxUtils
{
public:
    static bool PrintOnnxModelNodeNames(const FString& OnnxFilePath);
};

// MyOnnxUtils.cpp
#include "MyOnnxUtils.h"
#include "google/protobuf/io/zero_copy_stream_impl.h"
#include "google/protobuf/io/coded_stream.h"
#include "onnx/onnx_pb.h"  // 假设有 ONNX protobuf 生成的 C++ 文件（需自行生成）

bool FMyOnnxUtils::PrintOnnxModelNodeNames(const FString& OnnxFilePath)
{
    // 打开文件
    int32 FileHandle = open(TCHAR_TO_UTF8(*OnnxFilePath), O_RDONLY);
    if (FileHandle < 0) return false;

    google::protobuf::io::FileInputStream FileStream(FileHandle);
    google::protobuf::io::CodedInputStream CodedStream(&FileStream);

    // 解析 ONNX 模型（使用 onnx.proto 生成的 OnnxProto::ModelProto）
    OnnxProto::ModelProto Model;
    if (!Model.ParseFromCodedStream(&CodedStream))
    {
        close(FileHandle);
        return false;
    }
    close(FileHandle);

    // 遍历所有节点
    const auto& Graph = Model.graph();
    for (const auto& Node : Graph.node())
    {
        UE_LOG(LogTemp, Log, TEXT("Node: %s (op_type: %s)"),
            UTF8_TO_TCHAR(Node.name().c_str()),
            UTF8_TO_TCHAR(Node.op_type().c_str()));
    }
    return true;
}
```

**注意**：实际使用中需要自行生成 ONNX protobuf 的 C++ 类定义（通过 `protoc` 编译 `onnx.proto` 并链接）。

## 模块依赖

本模块作为独立的第三方库，不依赖其他 UE 模块（除了编译系统隐式依赖的 `Core` 等）。但它通常被 `NNERuntimeRDGOnnxEditor` 等模块间接使用。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | — |

## 维护状态

### 近期更新

- 2025-06-12 `d9dba260` — [NNE] NNERuntimeRDGHlsl arm64 support（涉及 protobuf 编译脚本调整）
- 2025-06-03 `d31855b9` — Fixup build script for libprotobuf-lite & add windows arm64 version（直接更新本模块）
- 2025-05-29 `8cfef610` — Added Greater.h include to files which use TGreater（引擎侧改动，间接影响）

### 维护评价

该模块基于广泛使用的 Google Protobuf 库（版本 3.20+），功能稳定，近期获得 ARM64 支持更新，表明 Epic 仍在积极维护 NNERuntimeRDG 相关的 protobuf 依赖。由于是第三方库封装，没有新增业务逻辑，更新主要跟随引擎编译需求。推荐在需要处理 ONNX 模型时使用。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/neural-network-engine-in-unreal-engine/)（NNE 整体文档）
- [Google Protobuf 官方文档](https://developers.google.com/protocol-buffers/docs/cpptutorial)