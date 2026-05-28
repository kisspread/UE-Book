# Serialization Utils

> Utilities for serialization (xml, json, etc) with extended functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 序列化工具 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonSerialization` (Runtime), `XmlSerialization` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils) | |

## 用途

此插件旨在为 Unreal Engine 的 **结构化存档系统 (Structured Archive System)** 提供 **增强的序列化格式化器 (Formatters)**，主要用于 JSON 和 XML 格式。它扩展了引擎默认的序列化功能，提供了更灵活的控制选项，例如允许将对象或软引用直接序列化到其当前值位置（“原地序列化”），而不是序列化为一个外部引用。这对于数据迁移、自定义数据交换格式或需要特定序列化行为的场景非常有用。

## 使用场景

- **自定义资产数据迁移工具**: 当你需要将一组 Unreal 对象导出为可读的 JSON/XML 文件，用于跨引擎版本或跨项目传输数据时，可以使用此插件提供的扩展格式化器来精细控制序列化过程。
- **生成用于调试或分析的序列化数据**: 当你希望将游戏运行时对象的状态以 JSON 格式输出，用于离线分析或日志记录，且需要控制对象是否应被序列化为引用或内联值。
- **非标准序列化需求**: 如果你的项目需要特殊的序列化逻辑（例如，某些特定类型的对象总是以某种方式序列化），可以通过继承或配置这些格式化器来实现。

## 蓝图用法

此插件提供的核心功能（`FJsonArchiveInputFormatterEx` 和 `FJsonArchiveOutputFormatterEx`）是纯 C++ 类，用于扩展 `FStructuredArchiveFormatter`。它们**不包含任何蓝图可调用节点 (`UFUNCTION(BlueprintCallable)`) 或蓝图属性 (`UPROPERTY(BlueprintReadWrite)`)**。要使用它们，必须通过 C++ 代码进行集成。

## C++ 用法

此插件的核心是提供两个扩展的 JSON 序列化格式化器。

### 头文件引入

```cpp
#include "Formatters/JsonArchiveOutputFormatterEx.h" // 用于序列化输出
#include "Formatters/JsonArchiveInputFormatterEx.h"  // 用于反序列化输入
```

### 基本用法：使用输出格式化器进行序列化

使用 `FJsonArchiveOutputFormatterEx` 可以将 Unreal 对象序列化为 JSON 格式。

```cpp
// 来源: Public/Formatters/JsonArchiveOutputFormatterEx.h
#include "Serialization/StructuredArchive.h"
#include "Formatters/JsonArchiveOutputFormatterEx.h"
#include "HAL/FileManager.h"

// 假设我们要序列化一个 UObject (例如 AActor, UDataAsset 等)
UObject* ObjectToSerialize = ...;

// 1. 创建输出存档和格式化器
TUniquePtr<FArchive> FileWriter(IFileManager::Get().CreateFileWriter(TEXT("Output.json")));
TSharedRef<FJsonArchiveOutputFormatterEx> JsonFormatter = MakeShared<FJsonArchiveOutputFormatterEx>(*FileWriter);

// 2. (可选) 配置格式化器行为
// 例如，将对象直接序列化为其内部数据，而不是序列化一个路径引用
JsonFormatter->SerializeObjectsInPlace(true);

// 3. 创建结构化存档并执行序列化
FStructuredArchive StructuredArchive(*JsonFormatter);
FStructuredArchive::FRecord RootRecord = StructuredArchive.Open();
// 此处写入你的对象数据，具体方式取决于你要序列化的对象类型。
// 例如，你可以调用对象的 Serialize 方法，或者手动写入字段。
// RootRecord.EnterField(TEXT("MyData")) << MyObjectData;
// ...
RootRecord.Close();
StructuredArchive.Close();

FileWriter->Close();
```

### 进阶用法：使用输入格式化器进行反序列化

使用 `FJsonArchiveInputFormatterEx` 可以从 JSON 格式的数据中反序列化出 Unreal 对象或数据。

```cpp
// 来源: Public/Formatters/JsonArchiveInputFormatterEx.h
#include "Serialization/StructuredArchive.h"
#include "Formatters/JsonArchiveInputFormatterEx.h"
#include "HAL/FileManager.h"

// 1. 创建输入存档和格式化器
TUniquePtr<FArchive> FileReader(IFileManager::Get().CreateFileReader(TEXT("Input.json")));
// 第三个参数是一个用于解析对象引用的函数（如果 JSON 中包含了对象路径引用）
TSharedRef<FJsonArchiveInputFormatterEx> JsonFormatter = MakeShared<FJsonArchiveInputFormatterEx>(
    *FileReader,
    /* InRootObject = */ nullptr, // 如果不需要指定根对象，可为nullptr
    /* InResolveObject = */ [](const FPackageIndex Index) -> UObject* {
        // 在此实现根据 FPackageIndex 解析出 UObject* 的逻辑
        // 例如，可以从加载的包或世界中查找
        return nullptr;
    }
);

// 2. 创建结构化存档并执行反序列化
FStructuredArchive StructuredArchive(*JsonFormatter);
FStructuredArchive::FRecord RootRecord = StructuredArchive.Open();
// 此处读取你的对象数据，方式与序列化时写入的逻辑对应。
// 例如:
// UObject* LoadedObject = nullptr;
// RootRecord.EnterField(TEXT("MyData")) << LoadedObject;
// ...
RootRecord.Close();
StructuredArchive.Close();

FileReader->Close();
```

### 配置格式化器行为

`FJsonArchiveOutputFormatterEx` 提供了额外的控制方法：

- `SerializeObjectsInPlace(bool bEnabled)`: 设为 `true` 时，序列化器会尝试将 UObject 直接写入当前存档位置，而不是写入一个外部引用。这对于内联嵌套对象数据很有用。
- `SerializeSoftObjectsInPlace(bool bEnabled)`: 类似地，控制软对象引用 (`FSoftObjectPath`, `FSoftObjectPtr`) 是否以内联方式序列化。
- `SetObjectIndicesMap(...)`: 提供一个 `UObject*` 到 `FPackageIndex` 的映射表，用于序列化时快速查找对象的包索引。

## Demo 示例

下面是一个最小的控制台程序示例，演示如何将一个简单的结构体序列化为 JSON 字符串，然后再从该字符串反序列化回来。

**SerializationUtilsDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"

// 一个简单的测试结构体
USTRUCT()
struct FMyDemoData
{
    GENERATED_BODY()

    UPROPERTY()
    int32 Health = 100;

    UPROPERTY()
    FString Name = TEXT("Default");
};
```

**SerializationUtilsDemo.cpp**
```cpp
#include "SerializationUtilsDemo.h"
#include "Serialization/StructuredArchive.h"
#include "Formatters/JsonArchiveOutputFormatterEx.h"
#include "Formatters/JsonArchiveInputFormatterEx.h"
#include "Serialization/BufferArchive.h"
#include "Serialization/MemoryReader.h"

void DemoSerializeAndDeserialize()
{
    // 准备原始数据
    FMyDemoData OriginalData;
    OriginalData.Health = 42;
    OriginalData.Name = TEXT("Hero");

    // === 序列化为 JSON 字符串 ===
    FBufferArchive ToBinary;
    TSharedRef<FJsonArchiveOutputFormatterEx> OutputFormatter = MakeShared<FJsonArchiveOutputFormatterEx>(ToBinary);
    // 配置为原地序列化（这里是为了确保结构体数据直接写出）
    OutputFormatter->SerializeObjectsInPlace(true);

    FStructuredArchive StructuredArchive(*OutputFormatter);
    FStructuredArchive::FRecord Record = StructuredArchive.Open();
    // 直接序列化结构体
    Record.EnterField(TEXT("Data")) << OriginalData;
    Record.Close();
    StructuredArchive.Close();

    // 从二进制缓冲区获取 JSON 字符串
    FString JsonString;
    ToBinary.Seek(0);
    JsonString = FString(ToBinary.Num(), (const TCHAR*)ToBinary.GetData());

    UE_LOG(LogTemp, Log, TEXT("Serialized JSON:\n%s"), *JsonString);

    // === 从 JSON 字符串反序列化 ===
    FMyDemoData LoadedData;
    FMemoryReader FromBinary((const uint8*)*JsonString, JsonString.Len() * sizeof(TCHAR));
    TSharedRef<FJsonArchiveInputFormatterEx> InputFormatter = MakeShared<FJsonArchiveInputFormatterEx>(FromBinary, nullptr);

    FStructuredArchive StructuredArchive2(*InputFormatter);
    FStructuredArchive::FRecord Record2 = StructuredArchive2.Open();
    Record2.EnterField(TEXT("Data")) << LoadedData;
    Record2.Close();
    StructuredArchive2.Close();

    UE_LOG(LogTemp, Log, TEXT("Deserialized Health: %d, Name: %s"), LoadedData.Health, *LoadedData.Name);
}
```

## 模块依赖

由于是实验性插件且未提供 `Build.cs` 详细内容，根据其功能推断，使用此插件的模块可能需要依赖以下非核心模块：

| 模块 | 用途 |
|---|---|
| `Json` | 插件中 JSON 功能的核心依赖，用于解析和生成 JSON 数据。 |
| `Xml` | 插件中 XML 功能的核心依赖（尽管当前展示的是 JSON 模块）。 |
| `Serialization` | 核心序列化框架，包含 `FStructuredArchive` 等基础类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和共享字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏以使用格式化版本 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复以优化内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退一次之前的提交 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复以优化内存 |

### 维护评价

该插件创建于 2024 年初，相对较新。从近期的 Git 提交记录看（截至 2026 年 4 月），它仍然在**活跃维护**，主要进行的是**底层优化和重构**（如内存优化、日志现代化）。这些改动表明 Epic Games 的团队仍在关注其性能和代码质量，但并非添加新功能。

- **优点**: 仍在维护，代码在持续优化。
- **风险与注意事项**:
    1.  **实验性状态**: `.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，意味着 API 可能不稳定，未来版本中可能发生变化或被移除。
    2.  **功能局限**: 从提供的头文件看，它主要扩展了 `FStructuredArchive` 的 JSON 格式化器，XML 模块的功能未在此次分析中展示。
    3.  **使用复杂性**: 需要使用者对 Unreal 的结构化存档系统有较深的理解。

**推荐**：如果你需要一个比引擎默认 JSON 序列化更灵活（例如支持原地序列化对象）的方案，并且愿意承担实验性 API 变化的风险，可以尝试使用。对于生产环境的核心功能，建议密切关注其更新状态或准备好自定义方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现)