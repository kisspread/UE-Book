# Interchange Common Parser

The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 通用解析器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeCommonParser` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Parsers/CommonParser) | |

## 用途

`InterchangeCommonParser` 模块是 Interchange 框架中用于存储和传递**解析后公共载荷数据**的轻量级数据结构库。它定义了各类文件解析器（如 FBX、GLTF）与后续导入管线之间交换的中间数据格式，避免每个解析器单独定义结构。主要提供：

- 动画载荷数据（关键帧曲线、步进曲线、烘焙变换）
- 时间描述与查询结构
- 公共序列化方法
- 哈希工具函数

该模块本身不包含任何导入逻辑，仅作为数据契约被其他模块引用。

## 使用场景

- 开发自定义文件解析器时，需要将动画数据传递给标准导入管线
- 在 Interchange 管线中编写自定义工厂节点，读取并解析动画载荷数据
- 需要序列化/反序列化中间动画数据结构（例如用于缓存或传递）

## 蓝图用法

本模块未暴露任何直接可供蓝图调用的函数或类。所有结构体（`FAnimationPayloadData`、`FAnimationTimeDescription`、`FAnimationPayloadQuery`）与哈希函数均为 C++ 内部使用，不生成蓝图节点。

如需在蓝图中访问 Interchange 导入流程，请通过 `InterchangeImport` 或 `InterchangePipelines` 模块提供的公开接口间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeCommonAnimationPayload.h"
#include "InterchangeCommonParserModule.h"
```

若仅需模块接口，可引入：

```cpp
#include "InterchangeCommonParserModule.h"
```

### 基本用法

```cpp
// 实例化动画载荷数据
FString NodeUID = TEXT("MyNode");
FInterchangeAnimationPayLoadKey PayloadKey;
PayloadKey.Type = EInterchangeAnimationPayLoadType::BAKED;
PayloadKey.UniqueID = TEXT("Take_001");

UE::Interchange::FAnimationPayloadData AnimData(NodeUID, PayloadKey);
AnimData.BakeFrequency = 30.0;
AnimData.RangeStartTime = 0.0;
AnimData.RangeEndTime = 2.0;

// 填充变换数据（假设已通过解析获得）
AnimData.Transforms.Add(FTransform::Identity);
// ...

// 序列化到存档
FBufferArchive BinaryArchive;
AnimData.SerializeBaked(BinaryArchive);

// 从存档反序列化（通过另一个 FAnimationPayloadData 对象）
FMemoryReader Reader(BinaryArchive);
FAnimationPayloadData DeserializedData(NodeUID, PayloadKey);
DeserializedData.SerializeBaked(Reader);
```

**来源文件**: `Engine/Plugins/Interchange/Runtime/Source/Parsers/CommonParser/Public/InterchangeCommonAnimationPayload.h`

### 进阶用法：数据类型转换

```cpp
// 假设已有 STEP_CURVE 数据，需要转为 BAKED
FAnimationPayloadData StepData(NodeUID, PayloadKey);
StepData.StepCurves.Add(/* 步进曲线 */);
StepData.PayloadKey.Type = EInterchangeAnimationPayLoadType::STEPCURVE;

// 调用转换方法
const FTransform DefaultTransform = FTransform::Identity;
StepData.CalculateDataFor(EInterchangeAnimationPayLoadType::BAKED, DefaultTransform);

// 转换后 StepData.Transforms 将被填充
check(StepData.Transforms.Num() > 0);
```

### 使用时间描述

```cpp
UE::Interchange::FAnimationTimeDescription TimeDesc(30.0, 0.0, 2.0);
uint32 Hash = TimeDesc.GetHash(); // 用于缓存唯一性

// 与载荷查询结合
FAnimationPayloadQuery Query;
Query.SceneNodeUniqueID = NodeUID;
Query.PayloadKey = PayloadKey;
Query.TimeDescription = TimeDesc;
```

## Demo 示例

以下是一个完整的命令行测试示例（无需 GUI），演示 `FAnimationPayloadData` 的序列化与反序列化。

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "InterchangeCommonAnimationPayload.h"
#include "Serialization/MemoryArchive.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInterchangeCommonParserDemoTest, "Interchange.CommonParser.Demo",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

bool FInterchangeCommonParserDemoTest::RunTest(const FString& Parameters)
{
    using namespace UE::Interchange;

    // 1. 创建载荷数据
    FString NodeUID = TEXT("Cube_001");
    FInterchangeAnimationPayLoadKey Key;
    Key.Type = EInterchangeAnimationPayLoadType::BAKED;
    Key.UniqueID = TEXT("Take0");

    FAnimationPayloadData SourceData(NodeUID, Key);
    SourceData.BakeFrequency = 24.0;
    SourceData.RangeStartTime = 0.0;
    SourceData.RangeEndTime = 1.0;
    SourceData.Transforms = {
        FTransform(FQuat::Identity, FVector(0,0,0), FVector::OneVector),
        FTransform(FQuat::Identity, FVector(10,0,0), FVector::OneVector)
    };

    // 2. 序列化
    TArray<uint8> Bytes;
    FMemoryWriter Writer(Bytes);
    SourceData.SerializeBaked(Writer);

    // 3. 反序列化到新对象
    FAnimationPayloadData DestData(NodeUID, Key);
    FMemoryReader Reader(Bytes);
    DestData.SerializeBaked(Reader);

    // 4. 验证
    TestEqual("BakeFrequency", DestData.BakeFrequency, 24.0);
    TestEqual("TransformCount", DestData.Transforms.Num(), 2);
    TestEqual("FirstTransformLocation", DestData.Transforms[0].GetLocation(), FVector::ZeroVector);
    TestEqual("SecondTransformLocation", DestData.Transforms[1].GetLocation(), FVector(10, 0, 0));

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 使用 `FRichCurve`、`FTransform`、`FArchive` 等核心引擎类型 |
| `InterchangeNodes` | 引用 `EInterchangeAnimationPayLoadType`、`FInterchangeAnimationPayLoadKey`、`FInterchangeStepCurve`、`FInterchangeAnimationTrackSetNode` |
| `CoreUObject` | 序列化基础（自动引入） |

**无特殊依赖（仅标准 Core/Engine 及项目内部模块）**。

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` Fixed editor hanging when level reimporting a file containing skeletal meshes
- 2025-10-23 `0158cf6a` Removing unintended LOD specialization from named LOD Groups
- 2025-10-21 `63c630c0` Fixing missing animation sequence import for LevelSequence on StaticMesh imported with Interchange
- 2025-10-17 `765b3a10` Fixed compilation error with NonUnity InterchangeWorker
- 2025-10-17 `2c91170f` Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial with /Interchange/...

### 维护评价

Interchange 框架是 UE5 新推出的统一导入系统，处于积极开发阶段。`InterchangeCommonParser` 模块创建于 2025 年 10 月，至今（约 1 年）有持续的功能性修复和更新，最近一次更新在 2025 年 12 月，表明仍在活跃维护。该模块数据结构稳定，无已知废弃标记。推荐在基于 Interchange 的导入流程中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Parsers/CommonParser)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/interchange-framework-in-unreal-engine/)（文档版本可能更新）
- [Interchange 总体模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)