# Serialization Utils

> Utilities for serialization (xml, json, etc) with extended functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 序列化工具 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonSerialization` (Runtime), `XmlSerialization` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils) | |

## 用途

Serialization Utils 插件为 Unreal Engine 提供了基于 **pugixml** 的 XML 序列化与反序列化能力（Json 部分另由 `JsonSerialization` 模块实现）。其核心模块 `XmlSerialization` 实现了标准 UE 的 `FStructuredArchiveFormatter` 接口（`FXmlArchiveOutputFormatter` / `FXmlArchiveInputFormatter`），以及 `IStructSerializerBackend` 接口（`FXmlStructSerializerBackend`），从而允许用户以 XML 格式读写 `UObject` 和任意 `UStruct`。

> ⚠️ 该插件当前标记为实验性，API 和功能可能随引擎版本变化。

该插件解决了以下问题：
- **将游戏对象导出/导入为 XML 文本**，用于编辑、配置、数据交换等场景。
- **支持多种 XML 编码**（UTF‑8、UTF‑16、UTF‑32 等）。
- **与 UE 现有的结构化存档（`FStructuredArchive`）机制无缝集成**，只需替换底层的 Formatter 即可。
- **提供比 UE 内置 `FXmlFile` 更丰富的结构化序列化能力**（支持嵌套对象、属性、数组、Map、引用解析等）。

## 使用场景

- 你正在开发一个编辑器工具，需要将 `UObject` 保存为易读的 XML 文件（例如关卡编辑器、数据表格编辑器）。
- 你需要将游戏配置或模组数据以 XML 格式导出/导入，并希望利用 UE 原生的序列化路径（`FArchive` / `FObjectAndNameAsStringProxyArchive` 等）。
- 你希望创建自定义的 XML 消息格式，用于服务器与客户端之间的数据交换。
- 你需要在 C++ 层次快速将一个 `UStruct` 实例转为 XML 字符串，或从 XML 还原。

## 蓝图用法

该模块所有序列化类均为 C++ 级别，**未公开 BlueprintCallable 函数**。若需在蓝图中使用，建议封装成自定义蓝图函数库（C++ 实现），内部调用 `FXmlArchiveOutputFormatter` 等类。

## C++ 用法

### 头文件引入

```cpp
#include "Formatters/XmlArchiveOutputFormatter.h"
#include "Formatters/XmlArchiveInputFormatter.h"
#include "Backends/XmlStructSerializerBackend.h"
```

### 基本用法：将 UObject 序列化为 XML 文件

```cpp
// 来源：自行构造，遵循 API 使用模式

// 假设有一个 AActor 子类实例 MyObject
UObject* MyObject = ...;

// 1. 创建一个 FBufferArchive 用于暂存二进制数据（实际使用 FArchive 包装 XML 输出）
FBufferArchive Buffer;

// 2. 创建 FXmlArchiveOutputFormatter 并绑定到 Buffer
FXmlArchiveOutputFormatter OutputFormatter(Buffer);

// 3. 创建一个 FStructuredArchive 并将 Formatter 传给它
FStructuredArchive Archive(EArchiveType::Object, OutputFormatter);

// 4. 用结构化存档写入对象（实际会调用 OutputFormatter 的 EnterRecord/Serialize 等）
Archive.GetRoot() << MyObject;

// 5. 将内存中的 XML DOM 写入内层 Archive（即 Buffer）
EXmlSerializationEncoding Encoding = EXmlSerializationEncoding::Utf8;
OutputFormatter.SaveDocumentToInnerArchive(Encoding);

// 6. 此时 Buffer 中包含完整 XML 文本，可保存到文件
FFileHelper::SaveArrayToFile(Buffer, *FPaths::ProjectSavedDir() / TEXT("MyObject.xml"));
```

### 基本用法：从 XML 文件反序列化 UObject

```cpp
// 来源：类似上面，反向操作

// 1. 读取文件到 FBufferArchive
TArray<uint8> FileData;
FFileHelper::LoadFileToArray(FileData, *FPaths::ProjectSavedDir() / TEXT("MyObject.xml"));
FMemoryReader Reader(FileData);

// 2. 创建 FXmlArchiveInputFormatter（需指定根对象和引用解析函数）
UObject* RootObject = GetTransientPackage();
auto ResolveObject = [](const FPackageIndex& Index) -> UObject* { return nullptr; };
FXmlArchiveInputFormatter InputFormatter(Reader, RootObject, ResolveObject);

// 3. 检查 xml 解析是否成功
if (!InputFormatter.IsParseResultStatusOk())
{
    // 处理错误
    return;
}

// 4. 创建 FStructuredArchive 进行读取
FStructuredArchive Archive(EArchiveType::Object, InputFormatter);
UObject* Deserialized = ...; // 需要提前创建空对象
Archive.GetRoot() << Deserialized;
```

### 进阶用法：使用 FXmlStructSerializerBackend 序列化 UStruct

```cpp
// 来源：基于 FXmlStructSerializerBackend API 构建

FBufferArchive Buffer;
FXmlStructSerializerBackend Backend(Buffer, EStructSerializerBackendFlags::Default);

// 设置要序列化的结构体实例
FMyStruct MyStruct;
MyStruct.Name = TEXT("Example");
MyStruct.Value = 42;

// 使用 FStructSerializer 进行序列化
FStructSerializer::Serialize(MyStruct, Backend, FStructSerializerPolicies());

// 将 xml 文档刷新到 Buffer
Backend.SaveDocument(EXmlSerializationEncoding::Utf8);

// 保存文件
FFileHelper::SaveArrayToFile(Buffer, *FPaths::ProjectSavedDir() / TEXT("Struct.xml"));
```

## Demo 示例

以下是一个完整的控制台命令示例，展示将简单 UObject 序列化为 XML 并写回。

**MyXmlSerializer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyXmlSerializer.generated.h"

UCLASS()
class UMyXmlSerializer : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

    UFUNCTION(exec)
    static void TestXmlSerialize(UObject* WorldContextObject);
};
```

**MyXmlSerializer.cpp**
```cpp
#include "MyXmlSerializer.h"
#include "Formatters/XmlArchiveOutputFormatter.h"
#include "Formatters/XmlArchiveInputFormatter.h"
#include "Serialization/BufferArchive.h"
#include "Serialization/MemoryReader.h"
#include "Serialization/StructuredArchive.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"

void UMyXmlSerializer::TestXmlSerialize(UObject* WorldContextObject)
{
    // 创建一个测试用 UObject（简单继承自 UObject 的类）
    UObject* TestObj = NewObject<UObject>(GetTransientPackage(), TEXT("XmlTestObj"));
    TestObj->SetFlags(RF_Transactional); // 仅为测试

    // 序列化
    {
        FBufferArchive Buffer;
        FXmlArchiveOutputFormatter OutputFormatter(Buffer);
        FStructuredArchive Archive(0, OutputFormatter);
        Archive.GetRoot() << TestObj;
        OutputFormatter.SaveDocumentToInnerArchive(EXmlSerializationEncoding::Utf8);
        FFileHelper::SaveArrayToFile(Buffer, *FPaths::ProjectSavedDir() / TEXT("TestObj.xml"));
        UE_LOG(LogTemp, Log, TEXT("Saved XML to %s"), *FPaths::ProjectSavedDir() / TEXT("TestObj.xml"));
    }

    // 反序列化
    {
        TArray<uint8> Data;
        FFileHelper::LoadFileToArray(Data, *FPaths::ProjectSavedDir() / TEXT("TestObj.xml"));
        FMemoryReader Reader(Data);
        UObject* RootObj = GetTransientPackage();
        FXmlArchiveInputFormatter InputFormatter(Reader, RootObj);
        if (InputFormatter.IsParseResultStatusOk())
        {
            UObject* NewObj = NewObject<UObject>(RootObj, TEXT("DeserializedTestObj"));
            FStructuredArchive Archive(0, InputFormatter);
            Archive.GetRoot() << NewObj;
            UE_LOG(LogTemp, Log, TEXT("Deserialized object: %s"), *NewObj->GetName());
        }
    }
}
```

在控制台输入 `TestXmlSerialize` 即可测试。

## 模块依赖

**XmlSerialization** 模块是运行时模块，其独特依赖如下：

| 模块 | 用途 |
|---|---|
| `Serialization` | 提供 `IStructSerializerBackend`、`FStructSerializer` 等结构体序列化框架 |
| `pugixml`（第三方库）| 底层 XML 解析/生成引擎，已内置于插件内无需手动安装 |

> 常见依赖（Core、CoreUObject、Engine、Slate 等）未列出。

## 维护状态

### 近期更新

| 日期 | Hash | Commit |
|---|---|---|
| 2025-06-16 | `7581937a` | Fixes to be able to compile UnrealGame with include-what-you-use |
| 2025-04-07 | `c985b7b8` | SerializationUtils, SVGImporter: use standalone installation of pugixml |
| 2025-03-28 | `9711ddbd` | Deprecated FPlatformType::CHAR32 and added FPlatformType::UTF32CHAR instead... |
| 2025-03-25 | `5685fe1b` | Undo changelist 41010118 |
| 2025-03-25 | `e573f0dc` | Undo changelist 41010890 |

### 维护评价

- **创建时间**：2025 年 3 月 25 日（距今约 6 个月）。
- **近期更新**：2025 年 6 月仍有编译修复，2025 年 4 月调整了 pugixml 引用方式，表明插件处于活跃开发中。
- **API 稳定性**：实验性标记意味着 API 可能发生变化，但核心架构已较为完整。
- **已知问题**：当前未发现严重缺陷；依赖 pugixml 库，在跨平台编译时需确保该库正确配置。
- **推荐度**：对于需要 XML 序列化的项目可放心使用，但需注意 API 的潜在变动，建议锁定引擎版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils)
- [官方文档](https://docs.unrealengine.com/)（搜索 "Serialization Utils"）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils/Tests)