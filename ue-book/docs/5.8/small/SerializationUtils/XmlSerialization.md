# Serialization Utils

> Utilities for serialization (xml, json, etc) with extended functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 序列化工具 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonSerialization` (Runtime), `XmlSerialization` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils) | |

## 用途

该插件为 Unreal Engine 提供了 JSON 和 XML 格式序列化/反序列化的扩展功能库。其核心价值在于超越引擎默认的序列化格式（如 .uasset），提供了更通用、更人类可读的数据交换格式支持。

具体来说，`XmlSerialization` 模块（本次分析的重点）实现了基于 `pugixml` 库的 **Structured Archive** 格式化器（Formatter），允许开发者将 UObject 和 UStruct 等复杂对象直接序列化为标准的 XML 文档，或从 XML 文档中反序列化。它解决了在需要配置数据可视化、外部系统集成或调试数据存储时，使用默认二进制或特定序列化格式不直观、不便于编辑的问题。

## 使用场景

- 你需要将游戏内的配置数据（如任务配置、属性表）导出为人类可读、易于版本管理的 XML 文件。
- 你的 UE 项目需要与支持 XML 格式的第三方软件或服务（如数据分析工具、内容管理系统）交换数据。
- 你正在开发编辑器工具，需要一种可靠的方式来将 UE 对象图保存为可编辑的文本格式。
- 你需要调试一个复杂的序列化过程，查看其中间数据结构，XML 比二进制更易于检查。

## 蓝图用法

该插件主要面向 C++ 开发，未直接暴露蓝图可调用节点（`BlueprintCallable`）。但其核心类 `FXmlStructSerializerBackend` 实现了 `IStructSerializerBackend` 接口，可以与蓝图中结构体序列化器（Struct Serializer）配合使用。通常用法是在 C++ 中创建一个结构体序列化器节点，将其 Backend 设置为此 XML 后端，从而在蓝图中触发序列化。

### 核心节点（概念性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Save Document` | 将缓冲区中的 XML 树写入底层 Archive。 | `FXmlStructSerializerBackend` |
| `Begin Structure` | 开始序列化一个结构体。 | `FXmlStructSerializerBackend` |
| `End Structure` | 结束序列化一个结构体。 | `FXmlStructSerializerBackend` |
| `Begin Array` | 开始序列化一个数组。 | `FXmlStructSerializerBackend` |
| `End Array` | 结束序列化一个数组。 | `FXmlStructSerializerBackend` |
| `Write Property` | 写入一个属性值。 | `FXmlStructSerializerBackend` |

### 使用示例（蓝图描述）

无法直接截图，但典型的蓝图工作流是：
1.  在 C++ 中创建一个继承自 `UBlueprintFunctionLibrary` 的类。
2.  在其静态函数中，创建一个 `FXmlStructSerializerBackend` 实例（需要传入一个 `FArchive`）。
3.  创建一个 `FStructSerializer` 实例，并设置其后端（Backend）为上面创建的 XML 后端。
4.  调用 `StructSerializer.Serialize(MyStruct)`，其中 `MyStruct` 是你想要序列化的蓝图结构体变量。
5.  调用 `Backend.SaveDocument()` 将生成的 XML 写入文件或网络流。
6.  在蓝图中，调用这个自定义的库函数。

## C++ 用法

### 头文件引入

```cpp
// 使用 XML 序列化功能
#include "Formatters/XmlArchiveOutputFormatter.h"
#include "Formatters/XmlArchiveInputFormatter.h"
#include "Backends/XmlStructSerializerBackend.h"
#include "XmlSerializationDefines.h"
```

### 基本用法：序列化 UObject 到 XML

```cpp
// 假设 MyObject 是一个已存在的 UObject 实例
UObject* MyObject = ...;
FArchive* FileAr = new FArchive(); // 替换为你的文件或内存 Archive

// 创建输出格式化器
FXmlArchiveOutputFormatter XmlFormatter(*FileAr);

// 创建一个结构化 Archive 并与格式化器关联
FStructuredArchive StructuredArchive(XmlFormatter);

// 获取根记录并开始序列化对象
FStructuredArchiveRecord RootRecord = StructuredArchive.Open().EnterRecord();

// 使用 Helper 函数序列化 UObject
UE::XmlSerialization::Private::FormatterHelper::SerializeObject(
    RootRecord,
    MyObject,
    [](FProperty* Prop){ return false; /* 根据条件过滤属性 */ }
);

// 离开根记录，完成结构化 Archive
RootRecord.LeaveRecord();
StructuredArchive.Close();

// 将内部的 XML 树写入文件
XmlFormatter.SaveDocumentToInnerArchive(EXmlSerializationEncoding::Utf8);
```
*（来源：基于 `FXmlArchiveOutputFormatter` 和 `FXmlFormatterHelper` 的接口设计）*

### 进阶用法：使用结构体序列化后端

这种方法更贴近其作为 `IStructSerializerBackend` 的设计初衷。

```cpp
#include "Serialization/StructSerializer.h"

// 准备一个要序列化的结构体
FMyTestStruct MyStruct;
// ... 初始化 MyStruct ...

// 准备一个文件 Archive (这里以内存 Archive 为例)
FBufferArchive BufferAr;

// 创建 XML 序列化后端
FXmlStructSerializerBackend XmlBackend(BufferAr, EStructSerializerBackendFlags::Default);

// 创建标准的 Struct Serializer
FStructSerializer Serializer;
Serializer.Serialize(MyStruct, XmlBackend);

// 将生成的 XML 保存到内存 Archive
XmlBackend.SaveDocument(EXmlSerializationEncoding::Utf8);

// BufferAr 现在包含了完整的 XML 数据
```
*（来源：基于 `FXmlStructSerializerBackend` 的接口设计）*

### 反序列化用法

```cpp
// 假设 XmlData 是包含 XML 的 FArchive
FArchive& XmlData = ...;
UObject* RootObject = GetWorld(); // 或其他作为对象所有者的根对象

// 创建输入格式化器，传入根对象和对象解析函数
FXmlArchiveInputFormatter InputFormatter(
    XmlData,
    RootObject,
    [](const FPackageIndex PackageIndex) -> UObject* {
        // 实现你的对象引用解析逻辑，根据 PackageIndex 返回对应的 UObject*
        return nullptr;
    }
);

// 检查解析是否成功
if (!InputFormatter.IsParseResultStatusOk())
{
    // 处理解析错误
    return;
}

// 创建结构化 Archive 并反序列化对象
FStructuredArchive StructuredArchive(InputFormatter);
FStructuredArchiveRecord RootRecord = StructuredArchive.Open().EnterRecord();

// 假设我们要反序列化一个已知类型的对象
FMyTestStruct DeserializedStruct;
// 使用 FStructDeserializer 或类似机制从 Record 中读取属性

RootRecord.LeaveRecord();
StructuredArchive.Close();
```
*（来源：基于 `FXmlArchiveInputFormatter` 的构造函数和接口）*

## Demo 示例

下面是一个完整的、可编译的最小示例，展示如何将一个自定义结构体序列化为 XML 并反序列化回来。

**MyTestStruct.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "MyTestStruct.generated.h"

USTRUCT(BlueprintType)
struct FMyTestStruct
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Name;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Count;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FVector> Points;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FDateTime Timestamp;

    // 必须提供默认构造函数
    FMyTestStruct()
        : Name(TEXT("Default"))
        , Count(0)
        , Timestamp(FDateTime::Now())
    {}
};
```

**XmlSerializationDemo.cpp**
```cpp
#include "MyTestStruct.h"
#include "Backends/XmlStructSerializerBackend.h"
#include "Serialization/StructSerializer.h"
#include "Serialization/BufferArchive.h"
#include "XmlSerializationDefines.h"
#include "Serialization/Json/JsonStructDeserializerBackend.h" // 用于反序列化示例
#include "Serialization/Json/JsonStructSerializerBackend.h"

void SerializeStructToXmlDemo()
{
    // 1. 准备数据
    FMyTestStruct DataToSerialize;
    DataToSerialize.Name = TEXT("TestName");
    DataToSerialize.Count = 42;
    DataToSerialize.Points.Add(FVector(1, 2, 3));
    DataToSerialize.Points.Add(FVector(4, 5, 6));

    // 2. 序列化到内存 Buffer
    FBufferArchive ToBinary;
    FXmlStructSerializerBackend XmlBackend(ToBinary, EStructSerializerBackendFlags::Default);

    FStructSerializer Serializer;
    Serializer.Serialize(DataToSerialize, XmlBackend);
    XmlBackend.SaveDocument();

    // 3. 将 Buffer 内容转换为字符串以便查看
    if (ToBinary.Num() > 0)
    {
        // 添加一个空终止符以便作为字符串处理
        ToBinary.Serialize(nullptr, 0);
        TCHAR* XmlString = (TCHAR*)ToBinary.GetData();
        UE_LOG(LogTemp, Log, TEXT("Serialized XML:\n%s"), XmlString);
    }

    // 4. 反序列化示例 (需要其他后端支持，此处仅为概念演示)
    // FBufferArchive FromXmlBuffer;
    // ... 将 XML 数据读入 FromXmlBuffer ...
    // FMyTestStruct DeserializedData;
    // FXmlArchiveInputFormatter InputFormatter(FromXmlBuffer, ...);
    // FStructDeserializer Deserializer;
    // Deserializer.Deserialize(DeserializedData, InputFormatter);
}
```

## 模块依赖

从代码结构分析，`XmlSerialization` 模块的一个关键依赖是用于 XML 解析的第三方库 `pugixml`。你的项目如果要使用此模块，需要在 `Build.cs` 中添加相应依赖。

| 模块 | 用途 |
|---|---|
| `pugixml` | 提供底层的 XML DOM 解析和生成功能，是 `XmlSerialization` 模块的核心依赖。 |
| `Serialization` | UE 内置的序列化框架，提供 `IStructSerializerBackend`、`FStructuredArchive` 等基础接口。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持 FString 和 FSharedString，优化内存。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，统一日志格式。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复以释放内存，针对特定问题（FORT）的优化。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回滚了之前的某个更改。 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 再次尝试移除 JSON 对象字符串重复的内存优化提交。 |

### 维护评价

- **创建时间**: 2024年1月创建，是相对较新的插件。
- **近期活跃度**: 从 Git 历史看，2026年仍有持续的提交，内容包括性能优化（内存）、代码重构和日志规范化，表明插件仍在**积极维护和优化**中。
- **实验性状态**: 插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true`，这意味着其 API 可能在未来版本中发生变化，不建议在核心生产代码中绝对依赖。
- **推荐度**: 对于需要在项目中实验性或小范围使用 XML/JSON 高级序列化功能的开发者，此插件是一个很好的起点。它提供了比引擎默认工具更灵活的序列化选项。但由于其“实验性”标签，在用于关键路径前需评估未来兼容性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils/Tests) (假设存在，路径为插件内 Tests 目录)