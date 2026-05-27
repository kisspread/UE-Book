# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 资产、材质模板、蓝图资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 是 Unreal Engine 的 Universal Scene Description (USD) 格式支持插件。它解决了以下核心问题：

- **USD 文件导入**：支持将 Pixar USD 格式（.usd、.usda、.usdc、.usdz）的场景资产导入到 UE 中
- **场景层级保持**：保留 USD 文件中的 Prim 层级结构，通过 `AUsdStageActor` 在 UE 中重现 USD Stage
- **材质和几何体转换**：将 USD 的材质和几何体数据转换为 UE 可用的格式
- **蓝图集成**：支持基于 USD Stage Actor 创建蓝图派生类，扩展 USD 导入逻辑
- **控制绑支持**：支持独立于蓝图的控制绑定（Control Rig）分配
- **LOD 支持**：支持 USD 的多级细节（LOD）变体系统

该插件由 Epic Games 官方维护，是 UE5 中处理 USD 工作流的核心基础设施。

## 使用场景

- 你在使用 Pixar USD 工作流（如从 Maya、Houdini、Blender 导出 USD 场景）→ 用 USDImporter 导入场景
- 你需要在 UE 中实时同步 USD 文件的变更 → 用 AUsdStageActor 加载 USD Stage
- 你需要将 USD 资产转换为 UE 原生资产（StaticMesh、Material）→ 用 USD Stage Importer 进行烘焙
- 你需要在蓝图中自定义 USD 导入逻辑 → 继承 AUsdStageActor 并覆写其行为
- 你需要从 UE 导出 USD 格式 → 使用 USDExporter 模块
- 你需要导入 USDZ 格式的 AR 资产 → USDImporter 也支持 .usdz 格式

## ⚠️ 重要提示：实验性插件

本插件默认**未启用**（`EnabledByDefault: false`），且标记为**实验性**（`IsBetaVersion: true`）。

启用方法：
1. 打开 Edit → Plugins
2. 搜索 "USD Importer"
3. 勾选启用并重启编辑器

## 模块结构

本插件包含 9 个模块，各自职责如下：

| 模块 | 类型 | 职责 |
|---|---|---|
| `USDSchemas` | Runtime | USD 核心 Schema 定义，将 USD Prim 映射到 UE 类型 |
| `USDStage` | Runtime | USD Stage 管理，提供 `AUsdStageActor` 核心 Actor |
| `USDStageImporter` | Runtime | USD Stage 资产导入器，负责文件导入流程 |
| `USDStageEditor` | Runtime | USD Stage 编辑器 UI，提供 Details 面板和操作菜单 |
| `USDStageEditorViewModels` | Runtime | USD Stage 编辑器的 ViewModel 层，MVVM 架构支持 |
| `USDClassesEditor` | Runtime | USD 相关类的编辑器扩展 |
| `USDExporter` | Runtime | USD 导出功能，支持从 UE 导出 USD 格式 |
| `GeometryCacheUSD` | Runtime | USD 几何缓存支持，处理动画几何体 |
| `USDTests` | Runtime | 内部测试辅助函数（已废弃） |

## 蓝图用法

> **注意**：USDTests 模块中的所有蓝图函数均已标记为 `UE_DEPRECATED`，仅用于内部测试，将在未来版本中移除。以下函数**不推荐在生产环境使用**。

### 核心节点（USDTests - 已废弃）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileBlueprintStageActor` | 重新编译蓝图派生的 Stage Actor | `UUSDTestsBlueprintLibrary` |
| `DirtyStageActorBlueprint` | 标记 Stage Actor 蓝图为脏（需要重新编译） | `UUSDTestsBlueprintLibrary` |
| `GetSubtreeVertexCount` | 获取指定 Prim 子树的顶点总数 | `UUSDTestsBlueprintLibrary` |
| `GetSubtreeMaterialSlotCount` | 获取指定 Prim 子树的材质槽总数 | `UUSDTestsBlueprintLibrary` |
| `SetUsdStageCpp` | 设置 Stage Actor 的 USD Stage 根层路径 | `UUSDTestsBlueprintLibrary` |
| `ClearTransactionHistory` | 清除事务历史（用于测试回退功能） | `UUSDTestsBlueprintLibrary` |

### 使用示例（蓝图描述）

以下示例展示如何使用 `GetSubtreeVertexCount` 检查 USD Stage 中某个 Prim 的顶点数量（仅用于测试目的）：

1. 获取场景中的 `AUsdStageActor` 引用
2. 调用 `GetSubtreeVertexCount`，传入 StageActor 和 PrimPath（如 `"/Root/MyMesh"`）
3. 返回值为 `int64`，表示该 Prim 及其所有子 Prim 的顶点总数

```
[Get Stage Actor] → [Get Subtree Vertex Count] → [Print String (Vertex Count)]
                         ↑ PrimPath: "/Root/MyMesh"
```

## C++ 用法

> **警告**：USDTests 模块的公开 API 已全部废弃，以下代码仅用于理解测试框架内部实现。

### 头文件引入

```cpp
#include "USDTestsBlueprintLibrary.h"
#include "USDTestsModule.h"
```

### 基本用法

从测试蓝图库获取 USD Stage Actor 的子树统计信息（已废弃 API）：

```cpp
// 获取 USD Stage Actor 某个 Prim 子树的顶点数
// 来源: Public/USDTestsBlueprintLibrary.h
#include "USDTestsBlueprintLibrary.h"

// 获取 Stage Actor 上某个 Prim 的子树顶点总数
AUsdStageActor* StageActor = /* 获取场景中的 Stage Actor */;
FString PrimPath = TEXT("/Root/MyMesh");
int64 VertexCount = UUSDTestsBlueprintLibrary::GetSubtreeVertexCount(StageActor, PrimPath);
UE_LOG(LogTemp, Log, TEXT("Subtree vertex count: %lld"), VertexCount);

// 获取材质槽数量
int64 MaterialSlotCount = UUSDTestsBlueprintLibrary::GetSubtreeMaterialSlotCount(StageActor, PrimPath);
UE_LOG(LogTemp, Log, TEXT("Subtree material slot count: %lld"), MaterialSlotCount);
```

### 进阶用法

在自动化测试中使用测试蓝图库进行 Blueprint Stage Actor 测试：

```cpp
// 在测试中编译和操作蓝图派生的 Stage Actor
// 来源: Public/USDTestsBlueprintLibrary.h
#include "USDTestsBlueprintLibrary.h"

// 设置 USD Stage 的根层
AUsdStageActor* StageActor = /* 获取 Stage Actor */;
FString NewStageRootLayer = TEXT("/path/to/my_stage.usd");
UUSDTestsBlueprintLibrary::SetUsdStageCpp(StageActor, NewStageRootLayer);

// 标记蓝图为脏（触发重新编译）
UUSDTestsBlueprintLibrary::DirtyStageActorBlueprint(StageActor);

// 重新编译蓝图派生的 Stage Actor
bool bSuccess = UUSDTestsBlueprintLibrary::RecompileBlueprintStageActor(StageActor);
check(bSuccess);

// 测试完成后清除事务历史
UUSDTestsBlueprintLibrary::ClearTransactionHistory();
```

## Demo 示例

以下是一个最小化的测试辅助模块实现，展示如何定义一个类似的测试蓝图库：

```cpp
// MyUSDTestHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyUSDTestHelper.generated.h"

class AUsdStageActor;

UCLASS(MinimalAPI)
class UMyUSDTestHelper : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 获取指定 Prim 子树的顶点总数
    UFUNCTION(BlueprintCallable, Category = "USD Testing")
    static int64 GetSubtreeVertexCount(AUsdStageActor* StageActor, const FString& PrimPath);

    // 获取指定 Prim 子树的材质槽数量
    UFUNCTION(BlueprintCallable, Category = "USD Testing")
    static int64 GetSubtreeMaterialSlotCount(AUsdStageActor* StageActor, const FString& PrimPath);
};
```

```cpp
// MyUSDTestHelper.cpp
#include "MyUSDTestHelper.h"
#include "UsdStageActor.h"

int64 UMyUSDTestHelper::GetSubtreeVertexCount(AUsdStageActor* StageActor, const FString& PrimPath)
{
    if (!StageActor)
    {
        return 0;
    }

    // 实际实现会遍历 USD Stage 中的 Prim 层级
    // 并聚合所有 Mesh 类型 Prim 的顶点数
    return 0; // 占位实现
}

int64 UMyUSDTestHelper::GetSubtreeMaterialSlotCount(AUsdStageActor* StageActor, const FString& PrimPath)
{
    if (!StageActor)
    {
        return 0;
    }

    // 实际实现会遍历 USD Stage 中的 Prim 层级
    // 并统计所有绑定的材质槽数量
    return 0; // 占位实现
}
```

## 模块依赖

USDTests 模块的依赖关系（基于 Build.cs 推断）：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 `AUsdStageActor` 核心 Actor 类 |
| `USDSchemas` | 提供 USD Schema 映射和类型转换 |
| `USDStageImporter` | 提供 USD 文件导入功能 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 添加支持分配独立于蓝图的控制绑定（Control Rig） |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 修复 USD 26.03 更新导致 LOD 变体切换时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数类型不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 修复曝光动画轨道的所有帧烘焙问题 |

### 维护评价

**整体评价：活跃维护中**

- **创建时间**：2018 年 11 月，已运行约 7 年
- **更新频率**：近期（2026 年 4-5 月）有多次实质性更新，包括功能增强和 Bug 修复
- **实验性状态**：仍标记为 `IsBetaVersion: true`，说明 API 可能不稳定
- **USDTests 模块状态**：该模块的所有公开 API 均已标记为 `UE_DEPRECATED`，明确将在未来版本中移除
- **USD 版本跟进**：插件在持续跟进 USD 库的更新（如 USD 26.03）

**⚠️ 关于 USDTests 模块的警告**：
该模块中的所有函数（`RecompileBlueprintStageActor`、`DirtyStageActorBlueprint`、`GetSubtreeVertexCount`、`GetSubtreeMaterialSlotCount`、`SetUsdStageCpp`、`ClearTransactionHistory`）均已废弃。这些函数仅用于 Epic Games 内部测试，**不应在生产代码中使用**。

**推荐程度**：
- **USDImporter 整体**：✅ 推荐用于 USD 工作流，虽然是实验性但仍在活跃维护
- **USDTests 模块**：❌ 不推荐使用，API 已全部废弃，仅供内部测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]()（未提供）

---

> **注意**：本文档主要聚焦于 USDTests 子模块。USDImporter 插件包含 9 个模块，完整的 USD 导入/导出工作流文档需要覆盖所有子模块。如需了解 AUsdStageActor、USD Schema 映射、USD Stage Importer 等核心功能的详细用法，请参考对应模块的独立文档。