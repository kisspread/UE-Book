# USD Importer (USDTests 模块文档)

> USD Importer 的子模块文档，聚焦 USDTests 测试工具模块

## 文档结构

本插件规模较大（187 源文件），按子模块拆分文档：

- **[index.md](#usd-importer-1)** ← 插件总览页（见下方）
- **USDTests.md** ← 本模块文档

---

# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageImporter` (Runtime), `USDExporter` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDClassesEditor` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

为 Unreal Engine 提供完整的 USD (Universal Scene Description) 工作流支持，包括：

- **导入**：将 `.usd`、`.usda`、`.usdc` 文件导入为 UE 内容资产
- **Stage Actor**：提供 `AUsdStageActor` 在场景中实时引用 USD Stage，支持层级管理和 Prim 映射
- **导出**：将 UE 场景内容导出为 USD 格式
- **Schemas**：定义 USD Prim 与 UE Actor/Component 之间的映射关系
- **Geometry Cache**：支持 USD 的动画几何体缓存
- **编辑器集成**：提供 USD Stage 大纲视图、属性面板等编辑器工具

## 使用场景

- 你正在用 Maya/Houdini/Blender 制作资产，需要导入 UE → 用 USD 导入
- 你需要在 UE 中实时引用 USD 文件，随源文件更新 → 用 AUsdStageActor
- 你需要将 UE 关卡内容导出到 DCC 工具 → 用 USD Exporter
- 你使用 USD 做管线资产交换格式 → 用完整的 USD 插件工作流

## 子模块概览

| 模块 | 用途 | 文档 |
|---|---|---|
| `USDSchemas` | USD Prim 到 UE 类型的 Schema 映射 | TODO |
| `USDStage` | Stage Actor 和 Stage 管理核心 | TODO |
| `USDStageImporter` | USD 文件导入逻辑 | TODO |
| `USDExporter` | UE 内容导出为 USD | TODO |
| `USDStageEditor` | USD Stage 编辑器面板 | TODO |
| `USDStageEditorViewModels` | 编辑器 MVVM ViewModel | TODO |
| `USDClassesEditor` | 编辑器扩展类 | TODO |
| `GeometryCacheUSD` | USD 几何缓存支持 | TODO |
| `USDTests` | 测试工具库（已废弃） | [USDTests.md](#usd-tests) |

## 模块依赖

本插件的模块间依赖关系复杂，整体依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `USDSchemas` | 核心 Schema 定义，被大多数模块依赖 |
| `USDStage` | Stage 管理核心 |
| `USDClasses` | USD 相关基础类定义 |
| `GeometryCache` | 几何缓存引擎支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double-to-float 截断警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持分配独立于蓝图的控制绑定 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 修复 USD 26.03 更新导致的 LOD 变化时 AnimQuery 内部引用失效问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位/64 位格式化说明符不匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙曝光动画轨道的所有帧 |

### 维护评价

**活跃维护**。USD Importer 虽然标记为实验性（IsBetaVersion=true）且默认不启用，但持续收到实质性功能更新和 bug 修复。从 2018 年创建至今已约 7 年，近期内仍保持活跃开发节奏（每周都有提交）。主要更新集中在：
- USD 版本升级兼容性（26.03）
- 动画系统集成改进
- 代码质量修复

⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。IsBetaVersion=true 表明 API 可能不稳定。

---

# USD Tests

> 内部测试工具模块，提供 USD 测试辅助函数。

| 属性 | 值 |
|---|---|
| 中文名 | USD 测试工具 |
| 分类 | Importers (USDImporter 子模块) |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) | |

## 用途

USDTests 模块是 USD Importer 的**内部测试辅助库**，为自动化测试提供 USD Stage Actor 的操控接口。该模块的所有公开 API 均已标记为 `UE_DEPRECATED`，明确标注"These functions were meant for internal testing only and will be removed in a future release"。

**这不是一个面向用户的功能模块**，仅供引擎内部自动化测试框架使用。

## 使用场景

- ❌ **不推荐用于项目开发** — 这是内部测试工具
- 仅在编写 USD 相关自动化测试时可能参考其用法

## 蓝图用法

### ⚠️ 废弃警告

所有蓝图节点均已标记为 `UE_DEPRECATED`，将在未来版本中移除。以下文档仅供了解 USD 测试用法参考：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileBlueprintStageActor` | 重新编译蓝图派生的 Stage Actor | `UUSDTestsBlueprintLibrary` |
| `DirtyStageActorBlueprint` | 标记 Stage Actor 蓝图为脏（需要重新编译） | `UUSDTestsBlueprintLibrary` |
| `GetSubtreeVertexCount` | 获取指定 Prim 子树的顶点总数 | `UUSDTestsBlueprintLibrary` |
| `GetSubtreeMaterialSlotCount` | 获取指定 Prim 子树的材质插槽总数 | `UUSDTestsBlueprintLibrary` |
| `SetUsdStageCpp` | 设置 Stage Actor 的根层路径 | `UUSDTestsBlueprintLibrary` |
| `ClearTransactionHistory` | 清除编辑器事务历史 | `UUSDTestsBlueprintLibrary` |

### 使用示例

```
[Get Subtree Vertex Count]
    ├── Stage Actor: 引用场景中的 AUsdStageActor
    ├── Prim Path: "/Root/Geometry"
    └── Output → (int64 顶点数)
```

```
[Set USD Stage Cpp]
    ├── Stage Actor: 引用 AUsdStageActor
    └── New Stage Root Layer: "D:/Assets/MyScene.usd"
```

## C++ 用法

### 头文件引入

```cpp
#include "USDTestsBlueprintLibrary.h"
```

### 基本用法

> ⚠️ 所有 API 已废弃，仅作为 USD 内部测试参考。

```cpp
// 获取 Stage Actor 子树顶点数（用于验证导入结果）
int64 VertexCount = UUSDTestsBlueprintLibrary::GetSubtreeVertexCount(
    StageActor,
    TEXT("/Root/Geometry/Mesh")
);

// 获取材质插槽数量（用于验证材质映射）
int64 MaterialSlotCount = UUSDTestsBlueprintLibrary::GetSubtreeMaterialSlotCount(
    StageActor,
    TEXT("/Root/Materials")
);
```

### 进阶用法

```cpp
// 测试蓝图派生的 Stage Actor 生命周期
UUSDTestsBlueprintLibrary::DirtyStageActorBlueprint(BlueprintDerivedStageActor);
UUSDTestsBlueprintLibrary::RecompileBlueprintStageActor(BlueprintDerivedStageActor);

// 切换 USD Stage 文件（测试不同 USD 文件的导入）
UUSDTestsBlueprintLibrary::SetUsdStageCpp(StageActor, TEXT("NewPath/Scene.usd"));

// 测试完成后清除事务历史
UUSDTestsBlueprintLibrary::ClearTransactionHistory();
```

## Demo 示例

该模块为内部测试工具，不提供独立示例。相关测试用法可参考 `USDTests.Build.cs` 中的依赖配置：

```cpp
// USDTestsModule.h
class IUsdTestsModule : public IModuleInterface
{
    // 无额外接口，仅模块注册
};
```

```cpp
// USDTestsBlueprintLibrary.h - 所有函数已废弃
UCLASS(MinimalAPI, meta = (ScriptName = "USDTestingLibrary"))
class UE_DEPRECATED(all, "These functions were meant for internal testing only and will be removed in a future release")
    USDTestsBlueprintLibrary : public UBlueprintFunctionLibrary
{
    // 所有函数均为 static，标记 UE_DEPRECATED
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 AUsdStageActor 类定义 |
| `USDClasses` | USD 基础类 |
| `AutomationController` | 自动化测试框架支持 |
| `FunctionalTesting` | 功能测试框架 |

## 维护状态

### 近期更新

该模块随 USDImporter 主插件一起维护，近期无独立更新。最近的 commit 均为主插件功能和修复。

### 维护评价

**不推荐使用**。所有公开 API 已标记为 `UE_DEPRECATED`，属于内部测试工具，未来版本将被移除。如需编写 USD 相关的自动化测试，建议参考引擎内部测试代码的模式，但不要直接依赖此模块。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com)（请搜索 USD 相关页面）
- [USD 官方网站](https://openusd.org/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)