# PlainProps

> New Serialization Stack Prototype

| 属性 | 值 |
|---|---|
| 中文名 | 普通属性序列化 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlainProps` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainProps) | |

## 用途

**PlainProps** 是 UE 官方正在实验中的新一代序列化堆栈原型。它提供了一套完全基于 C++ 编译期反射（CTTI）的自定义序列化框架，旨在替代或补充 UE 传统的 `FArchive` / `FProperty` 体系，为高性能、低内存开销的序列化需求提供新的选择。

**核心特点**：

- 使用宏 `PP_REFLECT_STRUCT` 和 `PP_REFLECT_ENUM` 声明结构体和枚举的反射信息（类型名、成员偏移、基类等）。
- 通过**模板 CTTI** 在编译期自动生成类型的元数据（名称、成员列表、偏移量），无需 UHT（Unreal Header Tool）。
- 支持**叶子类型**（bool、整数、浮点、枚举、Unicode 字符）、**结构体**（含继承、动态多态）和**范围类型**（容器、数组）。
- 提供**二进制序列化**（紧凑、可版本化、支持增量/差异存储）和 **YAML 文本序列化**（用于调试和配置）。
- 内置**结构差异比较**，可生成差异路径供版本管理或增量保存使用。
- 支持**命名空间和参数化类型索引**（如 `TArray<FVector>`），实现全局类型 ID 的唯一性。

**当前状态**：非常早期的实验性项目，仅在 Win64 平台启用，API 不稳定，不适合生产使用。

## 使用场景

- 你需要一种**无需 UHT 预处理**的轻量级 C++ 序列化方式（仅头文件 + 宏）。
- 你需要对已有 C++ 结构体进行**紧凑二进制打包**，且要求**向前/向后兼容**（通过版本号）。
- 你需要实现**增量保存**（delta save），仅序列化与默认值不同的部分。
- 你需要**结构体级差异比较**，用于网络同步或存档合并。
- 你正在探索 UE 未来序列化方向，愿意参与早期实验和反馈。

## 蓝图用法

**PlainProps 目前仅提供 C++ API，未暴露任何蓝图节点。**  
后续可能会提供蓝图支持，但当前所有功能都需通过 C++ 代码调用。

## C++ 用法

### 头文件引入

根据需要的功能包含相应的模块头文件：

```cpp
#include "PlainPropsBind.h"       // 绑定相关
#include "PlainPropsBuild.h"      // 构建中间表示
#include "PlainPropsSave.h"       // 保存（序列化）
#include "PlainPropsLoad.h"       // 加载（反序列化）
#include "PlainPropsDiff.h"       // 差异比较
#include "PlainPropsWrite.h"      // 写入二进制流
#include "PlainPropsRead.h"       // 读取二进制流
#include "PlainPropsParse.h"      // 解析 YAML
#include "PlainPropsPrint.h"      // 打印 YAML / 差异
#include "PlainPropsIndex.h"      // 类型索引
#include "PlainPropsDeclare.h"    // 声明类型
```

### 基本用法：反射声明与序列化

1. **使用 `PP_REFLECT_STRUCT` 宏声明结构体**（无需 UHT）：

```cpp
// 来自 PlainPropsUeCoreBindings.h 的示例
PP_REFLECT_STRUCT(
    UE::Math,          // 命名空间（可省略）
    FVector,           // 类型名称
    void,              // 基类（void 表示无基类）
    X, Y, Z            // 成员列表
);
```

2. **创建类型索引并注册声明**：

```cpp
#include "PlainPropsIndex.h"
#include "PlainPropsDeclare.h"

using namespace PlainProps;

// 初始化 ID 索引器
FIdIndexerBase Indexer;

// 注册 FVector 的声明
Indexer.IndexStruct(FType{ /* 从 CTTI 获取 */ });
```

3. **构建 Schema 并序列化到二进制流**：

```cpp
#include "PlainPropsBuild.h"
#include "PlainPropsBuildSchema.h"
#include "PlainPropsWrite.h"

// 假设已获得声明集合和 ID 索引器
const IDeclarations& Declarations = ...;
const FIds& AllIds = ...;
FScratchAllocator Scratch;

FSchemasBuilder Builder(AllIds, Declarations, Scratch, ESchemaFormat::Latest);
FBuiltSchemas Schemas = Builder.Build();

// 写入 Schema 到二进制
FWriter Writer(AllIds, Declarations, Schemas, ESchemaFormat::Latest);
TArray64<uint8> OutSchema;
Writer.WriteSchemas(OutSchema);
```

4. **保存具体结构体实例**：

```cpp
#include "PlainPropsSave.h"
#include "PlainPropsBind.h"

FVector MyVec(1.0f, 2.0f, 3.0f);

// 创建保存上下文
FSaveContext SaveCtx = MakeSaveContext<TRuntime>(Scratch);

// 保存结构体（返回 BuiltStruct 中间表示）
FBuiltStruct* Built = SaveStruct(&MyVec, FBindId(0), SaveCtx);

// 将中间表示写入二进制流
TArray64<uint8> OutData;
Writer.WriteMembers(OutData, FStructId(0), *Built);
```

5. **加载二进制流恢复结构体**：

```cpp
#include "PlainPropsLoad.h"
#include "PlainPropsRead.h"

// 先加载 schema 批次
FMemoryView SchemaView(OutSchema.GetData(), OutSchema.Num());
const FSchemaBatch* Batch = ValidateSchemas(SchemaView);
FSchemaBatchId BatchId = MountReadSchemas(Batch);

// 创建加载计划
FCustomBindings Customs;
FSchemaBindings SchemasBindings;
TArray<FStructId> RuntimeIds {FStructId(0)};
FLoadBatchPtr LoadBatch = CreateLoadPlans(BatchId, Customs, SchemasBindings, RuntimeIds, ESchemaFormat::Latest);

// 构造并加载目标结构体
FVector LoadedVec;
FByteReader Reader(OutData);
ConstructAndLoadStruct(&LoadedVec, Reader, FStructSchemaId(0), *LoadBatch);
```

### 进阶用法：结构差异比较

```cpp
#include "PlainPropsDiff.h"

FVector A(1.0f, 2.0f, 3.0f);
FVector B(4.0f, 5.0f, 6.0f);

// 使用 FDiffContext 跟踪差异路径
FDiffContext DiffCtx;
bool bDifferent = DiffStructs(&A, &B, FBindId(0), DiffCtx);

if (bDifferent)
{
    // 打印差异
    FYamlBuilderPtr YamlBuilder = MakeYamlBuilder(OutString);
    PrintDiff(OutString, AllIds, DiffCtx.Out);
}
```

### 自定义绑定

对于 UE 特有类型（如 `FName`, `FString`, `TArray` 等），PlainProps 提供 `PlainPropsUeCoreBindings.h` 中的预定义绑定，通过 `PP_REFLECT_STRUCT_TEMPLATE` 和专门的序列化器支持。

```cpp
// FVector 的绑定已在 UE::Math 命名空间中提供
// 自定义结构的反射示例：
struct FMyData
{
    int32 Value;
    FString Name;
    TArray<float> Floats;
};

PP_REFLECT_STRUCT(
    ,                // 全局命名空间（省略）
    FMyData,         // 类型名称
    void,            // 无基类
    Value, Name, Floats
);
```

## Demo 示例

以下是一个完整的最小示例，展示如何序列化和反序列化一个简单结构体。

**MyData.h**:

```cpp
#pragma once
#include "PlainPropsCtti.h"

struct FMyData
{
    int32 Count = 0;
    double Ratio = 0.0;
    bool bActive = false;
};

// 反射声明（必须写在全局作用域或命名空间内）
PP_REFLECT_STRUCT(
    ,            // 命名空间（空表示全局）
    FMyData,     // 类型
    void,        // 基类
    Count,       // 成员
    Ratio,
    bActive
);
```

**Demo.cpp**:

```cpp
#include "MyData.h"
#include "PlainPropsIndex.h"
#include "PlainPropsDeclare.h"
#include "PlainPropsBuild.h"
#include "PlainPropsBuildSchema.h"
#include "PlainPropsWrite.h"
#include "PlainPropsSave.h"
#include "PlainPropsLoad.h"
#include "PlainPropsRead.h"
#include "PlainPropsBind.h"

using namespace PlainProps;

// 模拟运行时，提供类型、Schema、自定义绑定等
struct FMyRuntime
{
    static const FIds& GetTypes() { static FIds Ids; return Ids; }
    static const FSchemaBindings& GetSchemas() { static FSchemaBindings S; return S; }
    static const FCustomBindings& GetCustoms() { static FCustomBindings C; return C; }
    static IDefaultStructs* GetDefaults() { return nullptr; }
};

void Demo()
{
    // 1. 注册类型
    FIdIndexerBase Indexer;
    FStructId StructId = Indexer.IndexStruct(FType(/* 从 CttiOf<FMyData> 构建 */));
    
    // 2. 声明结构体
    FEnumDeclarations EnumDecls(NullDebugIds);
    FStructDeclarations StructDecls(EnumDecls, NullDebugIds);
    TArray<FMemberDeclaration> Members;
    // ... 填充成员（此处省略构建细节）
    FStructId DeclaredId = StructDecls.Declare(StructId, ...);
    
    // 3. 构建 Schema
    FScratchAllocator Scratch;
    FSchemasBuilder Builder(Indexer, StructDecls, Scratch, ESchemaFormat::Latest);
    FBuiltSchemas Schemas = Builder.Build();
    
    // 4. 保存
    FMyData Data{42, 3.14, true};
    FSaveContext SaveCtx = MakeSaveContext<FMyRuntime>(Scratch);
    FBuiltStruct* Built = SaveStruct(&Data, FBindId(StructId.Idx), SaveCtx);
    
    TArray64<uint8> OutSchema;
    FWriter Writer(Indexer, StructDecls, Schemas, ESchemaFormat::Latest);
    Writer.WriteSchemas(OutSchema);
    
    TArray64<uint8> OutData;
    Writer.WriteMembers(OutData, StructId, *Built);
    
    // 5. 加载
    const FSchemaBatch* Batch = ValidateSchemas(FMemoryView(OutSchema.GetData(), OutSchema.Num()));
    FSchemaBatchId BatchId = MountReadSchemas(Batch);
    
    FCustomBindings Customs;
    FSchemaBindings SchemasBindings;
    TArray<FStructId> RuntimeIds{StructId};
    FLoadBatchPtr LoadBatch = CreateLoadPlans(BatchId, Customs, SchemasBindings, RuntimeIds, ESchemaFormat::Latest);
    
    FMyData Loaded;
    FByteReader Reader(OutData);
    ConstructAndLoadStruct(&Loaded, Reader, FStructSchemaId(0), *LoadBatch);
    
    // 验证结果
    check(Loaded.Count == 42);
    check(Loaded.Ratio == 3.14);
    check(Loaded.bActive == true);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础容器、内存管理、断言 |
| `CoreUObject` | `FName`、`FString`、数学类型（FVector 等）绑定 |
| `Engine` | 部分数学类型（FTransform、FQuat）绑定 |

**无特殊依赖**——上述模块是几乎所有运行时插件都会依赖的标准模块，此处仅列出独特关联。实际构建时 `PlainProps.Build.cs` 会自动处理。

## 维护状态

### 近期更新

```
- 2025-09-12 5f19e03c [Backout] - CL45790694
- 2025-09-12 820dcbc0 [Backout] - CL45785126
- 2025-09-12 c40b5a4d [Core] Add support to compile switch between using sparse or compact sets as the default set contain
- 2025-08-29 cc10997b PlainProps: Namespace compile fix for ::UE::PreciseFPEqual()
- 2025-08-29 d43d3714 PlainProps: WIP: Save and load source packages to and from memory using FLinkerLoad and FLinkerSave
```

### 维护评价

- **创建时间**：2025年8月29日，距今不足1个月。
- **近期活动**：项目处于非常早期的开发阶段，主要提交为初始实现和编译修复，还有对核心容器的依赖调整（Backout）。
- **活跃度**：开发活动频繁（数天内有多次提交），但属于实验性质。
- **稳定性**：`IsExperimentalVersion=true`，API 尚未定型，可能随时更改，不推荐生产使用。
- **风险**：不支持非 Win64 平台；不提供蓝图节点；序列化格式尚未版本化；缺少全面的错误处理。
- **建议**：仅适合对 UE 序列化底层感兴趣的高级开发者进行预研和反馈，不建议在正式项目中使用。

## 相关链接

- [源码 (UE 5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainProps)
- [官方文档](https://docs.unrealengine.com/)（目前无独立文档，仅 .uplugin 描述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainProps/Source/Private)（内部测试头文件 `PlainPropsInternalTest.h`）