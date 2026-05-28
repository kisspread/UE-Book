# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产定义、编辑器工具） |
| 模块 | `USDSchemas` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

此插件为虚幻引擎提供了完整的 USD (Universal Scene Description) 文件格式支持。它不仅仅是一个简单的文件导入器，而是一个包含数据模型（Schemas）、资产缓存、编辑器集成（Stage编辑器和资产查看器）、导出功能以及专用的几何缓存支持的综合性工具链。其主要目标是支持复杂资产、场景层级和动画序列的导入与管理，特别是用于影视级制作（VFX）和高级游戏开发工作流。该插件在2018年从实验性目录移至正式导入器目录，标志着其向稳定工具的转变。

## 使用场景

- **游戏资产导入**：你需要从DCC工具（如Maya, Blender）中导入包含复杂材质、骨骼动画和场景层级的USD资产。
- **高级动画工作流**：你使用USD来交换包含动画曲线、时间采样等复杂数据的动画序列。
- **场景组织与管理**：你需要处理由USD阶段（Stage）定义的、由多个资产组合而成的复杂场景布局。
- **资产管线集成**：你需要在一个集中的资产缓存（USD Asset Cache）中管理导入的USD资产及其派生资源（如网格体、材质），以便跟踪和更新。
- **双向工作流**：你不仅需要从USD导入资产到虚幻引擎，还需要将虚幻引擎中的资产或场景导出为USD格式。

## 蓝图用法

`USDClassesEditor` 模块提供了编辑器扩展功能，其公开的蓝图可调用API较少。主要的蓝图交互节点可能分布在其他模块（如 `USDStageImporter`）中，用于控制USD文件的导入流程和参数。基于提供的源码，当前模块主要提供资产定义和编辑器工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （本模块无直接公开的BlueprintCallable函数） | `USDClassesEditor` 主要提供编辑器后台支持，如资产定义、缓存资产编辑器 | N/A |

### 使用示例（蓝图描述）

蓝图用户主要通过资产浏览器（Content Browser）的右键菜单或拖拽操作来使用USD资产。例如，你可以创建一个 `UsdAssetCache3` 资产，然后将其指定给USD导入流程，以便集中管理导入过程中生成的所有资源。具体的USD导入设置蓝图节点通常由 `USDStageImporter` 模块提供。

## C++ 用法

该模块主要为USD资产在编辑器中的表示和编辑提供支持。

### 头文件引入

```cpp
// 若需要操作USD资产缓存
#include "USDAssetCache3.h"
// 若需要自定义资产定义或编辑器工具
#include "AssetDefinition_USDAssetCache.h"
#include "USDAssetCacheAssetEditorToolkit.h"
```

### 基本用法

创建和编辑 `USDAssetCache3` 资产的编辑器工具由该模块提供。在编辑器中，双击一个 `UsdAssetCache3` 资产会打开其专用的编辑器窗口。

（来源：`USDAssetCacheAssetEditorToolkit.h`）

```cpp
// 打开一个 USD 资产缓存的编辑器窗口
UUsdAssetCache3* MyAssetCache = /* 获取或创建你的 USDAssetCache3 实例 */;
FUsdAssetCacheAssetEditorToolkit* Editor = new FUsdAssetCacheAssetEditorToolkit();
Editor->Initialize(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), MyAssetCache);
```

### 进阶用法

该模块还定义了 `UAssetDefinition_UsdAssetCache` 类，用于在虚幻编辑器的资产系统中注册 `UsdAssetCache3` 类型。这控制了资产在内容浏览器中的显示名称、颜色、图标以及导入能力。

（来源：`AssetDefinition_USDAssetCache.h`）

```cpp
// 资产定义决定了 UsdAssetCache3 在内容浏览器中的外观和行为。
// 开发者通常不需要直接操作它，但理解其存在有助于了解资产系统如何集成USD缓存。
```

## Demo 示例

一个可运行的示例需要设置完整的USD导入上下文，较为复杂。以下为使用 `USDClassesEditor` 模块功能的简化示例，展示如何关联资产缓存。

```cpp
// MyUSDActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyUSDActor.generated.h"

class UUsdAssetCache3;

UCLASS()
class AMyUSDActor : public AActor
{
    GENERATED_BODY()
public:
    AMyUSDActor();

    // 在编辑器中，你可以将一个 USDAssetCache3 资产拖拽到这个属性上
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "USD")
    TObjectPtr<UUsdAssetCache3> AssociatedAssetCache;

    // 其他Actor逻辑...
};
```

```cpp
// MyUSDActor.cpp
#include "MyUSDActor.h"
#include "USDAssetCache3.h" // 来自 USDStage 或相关Runtime模块

AMyUSDActor::AMyUSDActor()
{
    AssociatedAssetCache = nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDSchemas` | 提供USD核心数据类型和模式的运行时表示 |
| `USDStage` | 管理USD阶段（Stage）和prim（元素）的运行时表示 |
| `USDStageImporter` | 实现USD文件导入虚幻引擎的核心逻辑 |
| `USDExporter` | 实现将虚幻引擎资产/场景导出为USD的功能 |
| `GeometryCacheUSD` | 提供USD几何缓存的支持 |
| `PropertyEditor` | 用于在细节面板中自定义属性编辑界面 |
| `Slate`, `SlateCore` | 用于构建自定义编辑器UI（如资产缓存编辑器） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：新增支持分配独立于蓝图的控制绑定。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD：解决升级到26.03版本导致LOD切换时AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位格式说明符与64位参数不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

**活跃维护**。该插件创建于2018年，历史较长。但从最近的提交记录（截至2026年5月）来看，维护非常活跃，更新频繁。最近的改动不仅包含编译修复，更重要的是**持续添加新功能**（如新的控制绑定支持）和**解决复杂的技术问题**（如LOD切换时的引用失效、动画烘焙）。这表明该插件是Epic重点维护的核心工具链之一，处于持续开发和改进中。对于需要处理复杂USD资产的项目，**强烈推荐使用**，但需注意其 `IsBetaVersion: true` 和 `EnabledByDefault: false` 的状态，意味着需要手动启用且可能存在一些不稳定因素。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- 官方文档 (DocsURL字段为空，请参考引擎内置文档或搜索相关教程)
- 测试用例 (位于 `Source/USDTests/` 目录下)