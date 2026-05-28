# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `USDSchemas` (Runtime), `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 是 Unreal Engine 对 Pixar Universal Scene Description (USD) 格式的完整支持插件。它不仅提供 USD 文件的**导入**能力，还包含**导出**、**Stage 管理**、**几何缓存**和**编辑器集成**等完整工作流。

该插件的核心价值在于：
- **跨软件资产交换**：USD 是工业光魔(ILM)、皮克斯等工作室制定的开放标准，被 Maya、Houdini、Blender 等主流 DCC 工具广泛支持
- **非破坏性引用工作流**：通过 USD Stage Actor 引用 USD 文件，可在 UE 内实时反映源文件变更
- **多用途模块化架构**：9 个模块覆盖导入、导出、模式定义、编辑器可视化等完整生命周期

> ⚠️ 注意：该插件默认未启用（`EnabledByDefault: false`）且标记为 Beta（`IsBetaVersion: true`），属于实验性功能。

## 使用场景

- 你从 Maya/Houdini 等 DCC 工具导出了 USD 场景 → 用 USDImporter 导入到 Unreal Engine
- 你需要在 UE 中引用外部 USD 文件并实时更新 → 用 USDStage 的 Stage Actor 工作流
- 你需要将 UE 场景导出为 USD 格式供其他 DCC 工具使用 → 用 USDExporter
- 你需要处理 USD 的几何缓存动画数据 → 用 GeometryCacheUSD

## 子模块概览

| 模块 | 用途 | 详细文档 |
|---|---|---|
| USDSchemas | USD 类型/属性的 UE Schema 映射定义 | 待补充 |
| GeometryCacheUSD | USD 几何缓存资产支持 | 待补充 |
| USDClassesEditor | USD 相关编辑器类 | 待补充 |
| USDExporter | USD 格式导出功能 | 待补充 |
| USDStage | USD Stage 核心运行时逻辑 | 待补充 |
| USDStageEditor | USD Stage 编辑器 UI | 待补充 |
| USDStageEditorViewModels | Stage 编辑器的 MVVM 视图模型 | 待补充 |
| USDStageImporter | USD Stage 导入管线 | 待补充 |
| USDTests | 内部测试辅助函数 | [📄 文档](#usdtests-模块) |

---

# USDTests 模块

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 测试模块 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) | |

## 用途

USDTests 是 USDImporter 插件的**内部测试辅助模块**。它提供一组用于自动化测试的蓝图函数库，方便测试框架操控 USD Stage Actor 的行为，如重编译蓝图、获取子树顶点数、设置 Stage 路径等。

> ⚠️ **重要警告**：该模块中的所有公开函数均已被标记为 `UE_DEPRECATED`，官方明确说明"These functions were meant for internal testing only and will be removed in a future release"。**不应在正式项目中使用这些 API**。

该模块仅包含 2 个头文件，是整个 USDImporter 插件中规模最小的模块。

## 蓝图用法

所有函数均已在 `USDTestsBlueprintLibrary` 类中被标记为废弃。以下列出仅供了解，**不可用于生产代码**。

### 核心节点（已废弃）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileBlueprintStageActor` | 重新编译蓝图派生的 Stage Actor | `USDTestsBlueprintLibrary` |
| `DirtyStageActorBlueprint` | 标记 Stage Actor 蓝图为脏（触发重新编译） | `USDTestsBlueprintLibrary` |
| `GetSubtreeVertexCount` | 获取指定 Prim 路径下子树的顶点总数 | `USDTestsBlueprintLibrary` |
| `GetSubtreeMaterialSlotCount` | 获取指定 Prim 路径下子树的材质槽总数 | `USDTestsBlueprintLibrary` |
| `SetUsdStageCpp` | 设置 Stage Actor 的 USD Stage 根层路径 | `USDTestsBlueprintLibrary` |
| `ClearTransactionHistory` | 清除事务历史（Undo/Redo 栈） | `USDTestsBlueprintLibrary` |

### 使用示例（蓝图描述）

以下为测试蓝图中的典型用法流程：

1. 创建一个继承自 `AUsdStageActor` 的蓝图子类 `BP_MyStageActor`
2. 调用 `SetUsdStageCpp` → 将 `BP_MyStageActor` 的 Stage 根层设置为指定 USD 文件路径
3. 调用 `GetSubtreeVertexCount` → 传入 StageActor 和 PrimPath（如 `"/root/mesh"`），验证导入的顶点数量是否符合预期
4. 调用 `GetSubtreeMaterialSlotCount` → 验证材质槽分配是否正确
5. 调用 `DirtyStageActorBlueprint` → 强制蓝图标记为脏
6. 调用 `RecompileBlueprintStageActor` → 重新编译并验证编译结果
7. 测试结束时调用 `ClearTransactionHistory` → 清理 Undo 栈

## C++ 用法

> ⚠️ 以下代码仅用于理解测试模块的设计意图，**不应在生产代码中使用**。

### 头文件引入

```cpp
#include "USDTestsBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何在自动化测试中使用这些函数。来源：`Source/USDTests/Public/USDTestsBlueprintLibrary.h`

```cpp
// 测试用例：验证 USD Stage 的顶点导入数量
// 注意：所有函数均已标记为 UE_DEPRECATED，仅供内部测试

// 1. 获取子树顶点计数
AUsdStageActor* StageActor = /* 获取场景中的 Stage Actor */;
FString PrimPath = TEXT("/root/geometry/mesh");
int64 VertexCount = USDTestsBlueprintLibrary::GetSubtreeVertexCount(StageActor, PrimPath);
// 验证: VertexCount 应该等于预期的顶点数

// 2. 获取材质槽数量
int64 SlotCount = USDTestsBlueprintLibrary::GetSubtreeMaterialSlotCount(StageActor, PrimPath);
// 验证: SlotCount 应该等于预期的材质槽数

// 3. 设置新的 USD Stage 根层
FString NewStagePath = TEXT("D:/Assets/MyScene.usd");
USDTestsBlueprintLibrary::SetUsdStageCpp(StageActor, NewStagePath);
```

### 进阶用法

结合蓝图重编译功能进行完整的工作流测试：

```cpp
// 测试蓝图派生的 Stage Actor 的编译行为
AUsdStageActor* BlueprintDerivedStageActor = /* 继承自 AUsdStageActor 的蓝图实例 */;

// 先标记蓝图为脏
USDTestsBlueprintLibrary::DirtyStageActorBlueprint(BlueprintDerivedStageActor);

// 重新编译并检查结果
bool bSuccess = USDTestsBlueprintLibrary::RecompileBlueprintStageActor(BlueprintDerivedStageActor);
// 验证: bSuccess 应为 true

// 测试完成后清理事务历史，避免影响其他测试
USDTestsBlueprintLibrary::ClearTransactionHistory();
```

## 模块依赖

从 `USDTests.Build.cs` 的依赖关系推断：

| 模块 | 用途 |
|---|---|
| `USDStage` | 核心 Stage Actor 类（`AUsdStageActor` 所在模块） |
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | — |

## 维护状态

### 近期更新

以下为影响 USDImporter 插件目录的最近提交：

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持分配独立于蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 修复 26.03 更新导致 LOD 变化时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位/64 位格式化说明符匹配错误 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 支持烘焙曝光动画轨道的所有帧 |

### 维护评价

**整体插件（USDImporter）**：
- ✅ **活跃维护**：最近 6 个月内有持续的功能性更新和 bug 修复
- ✅ 从 2018 年创建至今仍在持续迭代，从最初的导入功能发展为包含导出、Stage 管理等完整工作流
- ⚠️ 仍标记为 Beta (`IsBetaVersion: true`)，表明 API 可能仍有变动
- ⚠️ 默认未启用 (`EnabledByDefault: false`)，需手动在 Plugins 面板中启用

**USDTests 模块**：
- ⚠️ **已废弃**：所有公开 API 均标记为 `UE_DEPRECATED`，官方明确表示将在未来版本移除
- 该模块仅为内部自动化测试设计，功能极其有限（仅 2 个头文件）
- ❌ **不推荐使用**：生产项目中不应依赖此模块的任何函数

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [USDTests 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)
- [USDTestsBlueprintLibrary 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests/Public/USDTestsBlueprintLibrary.h)