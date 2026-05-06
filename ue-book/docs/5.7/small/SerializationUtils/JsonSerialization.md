# SerializationUtils

> Utilities for serialization (xml, json, etc) with extended functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 序列化工具集 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonSerialization` (Runtime), `XmlSerialization` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 0.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils) | |

## 用途

UE 内置的 JSON / XML 序列化（通过 `FJsonObject`、`FArchive` 等方式）在处理复杂 UObject 图、嵌套对象、软引用（`FSoftObjectPtr`）时能力有限。该插件提供了两个继承自 `FStructuredArchiveFormatter` 的自定义格式化器：`FJsonArchiveInputFormatterEx` 和 `FJsonArchiveOutputFormatterEx`，在标准 JSON 序列化基础上增加了 **原地序列化对象**（inline object serialization）、**软对象引用序列化**（inline soft object pointer）以及 **外部对象索引映射** 等扩展功能，使序列化更加灵活，特别适用于需要手动控制 JSON 输出结构或处理非标准 FArchive 的场景。

`XmlSerialization` 模块提供类似的 XML 序列化扩展，但当前文档覆盖整个插件的架构和 JSON 相关模块。

## 使用场景

- 需要将 UObject 或结构体导出为定制 JSON 格式，并保留内部对象引用、软引用或嵌套对象。
- 构建自定义存档系统（如游戏存档、配置导出），需要跳过 UE 默认 JSON 格式的限制（例如无法序列化 `FText` 的本地化标志）。
- 在编辑器工具或单元测试中，希望以 JSON/XML 字符串形式验证对象数据，又需要精确控制序列化行为（如是否展开内联对象）。
- 需要将序列化的对象与大包（Package）索引结合，用于跨 Package 的对象引用恢复。

## 蓝图用法

该插件未暴露任何蓝图可调用节点。`FStructuredArchiveFormatter` 类层次在 C++ 层面工作，与蓝图不直接交互。

## C++ 用法

### 头文件引入

```cpp
#include "Formatters/JsonArchiveOutputFormatterEx.h"
#include "Formatters/JsonArchiveInputFormatterEx.h"
```

### 基本用法

#### 序列化对象到 JSON 缓冲区

```cpp
// 创建一个内存写入存档
FBufferArchive Buffer;

// 使用扩展输出格式化器
FJsonArchiveOutputFormatterEx OutputFormatter(Buffer);

// 可选：启用内联对象序列化（默认关闭）
OutputFormatter.SerializeObjectsInPlace(true);
OutputFormatter.SerializeSoftObjectsInPlace(true);

// 创建结构化存档并写入
FStructuredArchive Archive(OutputFormatter);
Archive.GetRoot().EnterRecord();

// 写入字段
int32 Value = 42;
Archive.EnterField(TEXT("MyInt"));
Archive.GetRoot() << Value;
Archive.LeaveField();

// 完成
Archive.GetRoot().LeaveRecord();

// Buffer 此时包含 JSON 文本
```

#### 从 JSON 缓冲区反序列化

```cpp
// 假设已有的 FArchive（如 FBufferReader）包含 JSON 文本
FBufferReader Reader(Buffer, false); // 不拥有数据

// 使用扩展输入格式化器，需指定根对象和可选的对象解析器
UObject* RootObject = GetTransientPackage();
TFunction<UObject*(const FPackageIndex)> Resolver = nullptr; // 可自定义对象解析

FJsonArchiveInputFormatterEx InputFormatter(Reader, RootObject, Resolver);

FStructuredArchive Archive(InputFormatter);
Archive.GetRoot().EnterRecord();

int32 Value = 0;
Archive.EnterField(TEXT("MyInt"));
Archive.GetRoot() << Value;
Archive.LeaveField();

check(Value == 42);
```

### 进阶用法

#### 序列化嵌套 UObject（原地）

```cpp
// 输出端启用内联序列化
OutputFormatter.SerializeObjectsInPlace(true);

// 序列化一个 UObject* 属性
UObject* SubObject = LoadObject<UObject>(nullptr, TEXT("/Game/MySubObject"));
Archive.EnterField(TEXT("SubObject"));
Archive.GetRoot() << SubObject; // 会将 SubObject 的完整数据展开到 JSON 中
Archive.LeaveField();
```

#### 提供对象索引映射（用于跨 Package 引用）

```cpp
// 构建对象到 PackageIndex 的映射表
TMap<UObject*, FPackageIndex> ObjectMap;
ObjectMap.Add(SomeObject, FPackageIndex::FromExportIndex(5));

// 输出时设置映射
OutputFormatter.SetObjectIndicesMap(&ObjectMap);

// 此后序列化 SomeObject 时，会写入 PackageIndex 而非完整对象数据
```

#### 嵌套对象加载（输入时）

```cpp
// 输入端可设置回调，根据 FPackageIndex 解析对象
TFunction<UObject*(const FPackageIndex)> Resolver = [](const FPackageIndex& Index) -> UObject*
{
    // 自定义逻辑：从指定包加载或返回现有对象
    return nullptr;
};

FJsonArchiveInputFormatterEx InputFormatter(Reader, RootObject, Resolver);
```

## Demo 示例

以下是一个完整的、可编译的 C++ 示例，展示如何将简单的 UObject 子类序列化为 JSON 字符串，并读回。

### .h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Formatters/JsonArchiveOutputFormatterEx.h"
#include "Formatters/JsonArchiveInputFormatterEx.h"
#include "Serialization/BufferArchive.h"
#include "Serialization/BufferReader.h"
#include "Serialization/StructuredArchive.h"
#include "Serialization/MemoryArchive.h"
#include "TestObject.generated.h"

UCLASS()
class UTestObject : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY()
    FString Name;

    UPROPERTY()
    int32 Value;
};

// 声明测试函数
void RunJsonFormatterDemo();
```

### .cpp

```cpp
#include "TestObject.h"

void RunJsonFormatterDemo()
{
    // 创建测试对象
    UTestObject* Obj = NewObject<UTestObject>();
    Obj->Name = TEXT("Demo");
    Obj->Value = 100;

    // --- 序列化 ---
    FBufferArchive Buffer(/*bSerializedData*/ true);
    FJsonArchiveOutputFormatterEx OutputFormatter(Buffer);
    OutputFormatter.SerializeObjectsInPlace(true);

    FStructuredArchive OutArchive(OutputFormatter);
    // 写入一个记录
    OutArchive.GetRoot().EnterRecord();
    {
        OutArchive.EnterField(TEXT("TestObject"));
        const UObject* ObjPtr = Obj;
        OutArchive.GetRoot() << const_cast<UObject*&>(ObjPtr);
        OutArchive.LeaveField();
    }
    OutArchive.GetRoot().LeaveRecord();

    // 获取 JSON 字符串
    Buffer.Add(0); // 添加 null 终止
    ANSICHAR* JsonPtr = (ANSICHAR*)Buffer.GetData();
    FString JsonString(JsonPtr); // 实际使用需注意编码

    // --- 反序列化 ---
    FBufferReader Reader(Buffer, false);
    FJsonArchiveInputFormatterEx InputFormatter(Reader, GetTransientPackage());
    FStructuredArchive InArchive(InputFormatter);

    UTestObject* NewObj = nullptr;
    InArchive.GetRoot().EnterRecord();
    {
        InArchive.EnterField(TEXT("TestObject"));
        UObject* ObjPtr = nullptr;
        InArchive.GetRoot() << ObjPtr;
        NewObj = Cast<UTestObject>(ObjPtr);
        InArchive.LeaveField();
    }
    InArchive.GetRoot().LeaveRecord();

    if (NewObj)
    {
        check(NewObj->Name == TEXT("Demo"));
        check(NewObj->Value == 100);
        UE_LOG(LogTemp, Log, TEXT("Demo passed: Name=%s, Value=%d"), *NewObj->Name, NewObj->Value);
    }
}
```

## 模块依赖

根据 `Build.cs` 分析，本模块无特殊依赖。两个模块仅依赖标准 UE 基础模块（Core、CoreUObject、Engine），无需额外依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine 等 |

## 维护状态

### 近期更新

- 2025-06-16 `7581937a` — Fixes to be able to compile UnrealGame with include-what-you-use
- 2025-04-07 `c985b7b8` — SerializationUtils, SVGImporter: use standalone installation of pugixml
- 2025-03-28 `9711ddbd` — Deprecated FPlatformType::CHAR32 and added FPlatformType::UTF32CHAR instead
- 2025-03-25 `5685fe1b` — Undo changelist 41010118
- 2025-03-25 `e573f0dc` — Undo changelist 41010890

### 维护评价

该插件创建于 2025 年 3 月，属于全新插件。近期（2025 年 6 月）仍有编译修复，表明正在积极维护。但由于是实验性模块（`IsExperimentalVersion=true`），API 可能还不够稳定，文档和测试覆盖有待完善。目前看起来功能集中在 JSON 序列化扩展，XmlSerialization 模块尚不明确。推荐在非生产项目中试用，若需稳定方案建议等待正式版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils)
- [官方文档](https://docs.unrealengine.com/)（本插件未提供独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils/Tests)（可能位于插件目录下，但未提供具体路径）