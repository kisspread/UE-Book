# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源与蓝图） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 插件为虚幻引擎提供了导入通用场景描述（Universal Scene Description, USD）格式文件的能力。它包含一系列运行时和编辑器模块，用于解析 USD 舞台、生成静态网格体、动画、材质等游戏资产，并支持在编辑器中直接打开、浏览和编辑 USD 文件。

**USDTests 模块** 是本插件中的测试辅助模块，提供了一组可通过 Python 脚本或蓝图调用的函数，用于测试其他 USD 功能（如蓝图重编译、顶点计数查询、事务历史清除等）。**注意：所有这些函数已在 UE 5.4 中弃用，仅用于内部测试，不推荐在新项目中使用。**

## 使用场景

- **USD 工作流集成**：将 USD 格式的 3D 场景（角色、环境、动画）导入虚幻引擎作为资产，用于游戏、影视或建筑可视化。
- **自动测试开发**：开发 USD 相关功能时，需要编写自动化测试验证蓝图重编译、舞台打开/关闭、资产引用等行为，可通过 `USDTestsBlueprintLibrary` 中的函数在 Python 测试脚本中执行关键操作。
- **编辑器扩展**：通过 `USDStageEditor` 模块提供的编辑器 UI 直接浏览 USD 舞台结构，无需手动导入每个资产。

## 蓝图用法

`USDTestsBlueprintLibrary` 中的所有函数均可通过蓝图调用，但均在 UE 5.4 中被标记为 **已弃用 (Deprecated)**。不建议依赖它们构建新功能。以下列出这些函数以供测试迁移参考：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileBlueprintStageActor` | 触发一个源自蓝图类的舞台 Actor 的蓝图重新编译，并返回编译是否成功 | `USDTestsBlueprintLibrary` |
| `DirtyStageActorBlueprint` | 故意弄脏舞台 Actor 蓝图（标记需重新编译），用于测试 PIE 过渡时的行为 | `USDTestsBlueprintLibrary` |
| `GetSubtreeVertexCount` | 通过舞台 Actor 的信息缓存查询指定 prim 子树的总顶点数，失败返回 -1 | `USDTestsBlueprintLibrary` |
| `GetSubtreeMaterialSlotCount` | 查询子树材质槽位数，失败返回 -1 | `USDTestsBlueprintLibrary` |
| `SetUsdStageCpp` | 通过 C++ 后端打开指定舞台并设置到舞台 Actor 上（等同于 C++ `SetRootLayer`） | `USDTestsBlueprintLibrary` |
| `ClearTransactionHistory` | 清空编辑器事务历史（常用于垃圾回收前检查多余引用） | `USDTestsBlueprintLibrary` |

### 使用示例（蓝图描述）

以 `GetSubtreeVertexCount` 为例：
1. 在关卡中放置一个 `AUsdStageActor`（来自 `USDStage` 模块），并设置其 `RootLayer` 指向一个 USD 文件。
2. 在蓝图事件图表中，连接一个 `GetSubtreeVertexCount` 节点，将 `StageActor` 引脚连接到该舞台 Actor，`PrimPath` 输入要查询的 prim 路径（如 `"/Root/Mesh"`）。
3. 输出 `Return Value`（int64）即可获得顶点数。

因为所有节点均已弃用，蓝图编辑器会显示警告折线，建议在 Python 测试脚本中直接调用 C++ 函数替代。

## C++ 用法

测试函数通常通过 Python 脚本调用，但也可以在 C++ 代码中静态调用。以下示例基于 `USDTestsBlueprintLibrary` 的公开接口。

### 头文件引入

```cpp
#include "USDTestsBlueprintLibrary.h"
```

### 基本用法

```cpp
// 清空事务历史（用于垃圾回收前检测）
USDTestsBlueprintLibrary::ClearTransactionHistory();

// 获取子树顶点数
int64 VertexCount = USDTestsBlueprintLibrary::GetSubtreeVertexCount(MyStageActor, TEXT("/Root/Mesh"));
check(VertexCount >= 0);

// 重新编译蓝图舞台 Actor（弃用）
bool bSuccess = USDTestsBlueprintLibrary::RecompileBlueprintStageActor(MyBlueprintDerivedStageActor);
```

### 进阶用法

测试脚本通常需要组合多个操作：先打开舞台，然后查询计数，再触发重编译，最后清理事务历史。例如一个自动化测试 GIVEN/WHEN/THEN 模式：

```cpp
#include "Misc/AutomationTest.h"
#include "USDTestsBlueprintLibrary.h"
#include "USDStageActor.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUsdTestVertexCount, "USD.VertexCount", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FUsdTestVertexCount::RunTest(const FString& Parameters)
{
    // GIVEN a stage actor with a known USD file
    AUsdStageActor* StageActor = ...; // Spawn or find

    // WHEN we query vertex count
    int64 VertexCount = USDTestsBlueprintLibrary::GetSubtreeVertexCount(StageActor, TEXT("/Root/Mesh"));

    // THEN it matches expected value
    TestEqual(TEXT("Vertex count should be 1024"), VertexCount, 1024);

    return true;
}
```

## Demo 示例

一个最小测试示例，演示如何通过 C++ 调用 `GetSubtreeVertexCount` 并验证结果。

**TestUsdCounts.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTestUsdCounts, "USD.Tests.Counts", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
```

**TestUsdCounts.cpp**
```cpp
#include "TestUsdCounts.h"
#include "USDTestsBlueprintLibrary.h"
#include "USDStageActor.h"

bool FTestUsdCounts::RunTest(const FString& Parameters)
{
    // Note: These functions are deprecated since 5.4, this is for migration/testing only
    AUsdStageActor* StageActor = ...; // Obtain valid actor (e.g., via FActorSpawnParameters)
    if (!StageActor) { return false; }

    int64 VertCount = USDTestsBlueprintLibrary::GetSubtreeVertexCount(StageActor, TEXT("/Root/Mesh"));
    TestTrue(TEXT("Vertex count should be non-negative"), VertCount >= 0);

    return true;
}
```

## 模块依赖

**USDTests 模块**的依赖项（从插件组织推断，未提供 Build.cs）包括：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供舞台 Actor 和数据模型 |
| `USDSchemas` | 提供 USD 模式解析与资产生成 |
| `USDStageImporter` | 提供导入逻辑，测试中可能用到 |
| `Core`、`CoreUObject`、`Engine` | 标准基础设施 |

其他模块（如 `GeometryCacheUSD`、`USDExporter`）在使用 USDTests 时通常无需直接依赖。

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b71 [Backout] - CL47041219
- 2025-10-17 7ab79237 USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 d887bd60 USD: Use the default collision profile for generated static meshes.
- 2025-10-01 b4449c58 Anim In Engine: Fix broken linked anim sequences.

### 维护评价

- **创建时间**：2025-10-01（约 0 年前），是一个非常新的插件。
- **更新频率**：截至 2025-10-22 有活跃的日常维护，主要涉及 USD 底层分配器调整和静态网格体碰撞配置。
- **活跃度**：当前处于活跃开发中，但 USDTests 模块中的蓝图函数早在 5.4 版本就已弃用，未来可能移除。
- **推荐使用**：**对于导入 USD 文件的核心功能**，该插件是官方推荐方案。但 **USDTests 测试辅助函数已废弃**，建议使用 Python 脚本直接调用底层 USD API 进行测试，而不是依赖 `USDTestsBlueprintLibrary`。
- **已知限制**：实验性插件，API 可能不稳定；弃用函数应尽快迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/unreal-engine-usd-importer/)（USD Importer 官方文档）