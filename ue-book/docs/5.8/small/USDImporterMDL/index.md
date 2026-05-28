# USD Importer MDL integration

> Allows importing USD files that reference MDL files, via the USD Stage Actor and USD import

| 属性 | 值 |
|---|---|
| 中文名 | USD MDL 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDImporterMDL` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 👴 老古董（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL) | |

## 用途

此插件为 `USDImporter` 插件提供了对 MDL (Material Definition Language) 材质标准的集成支持。当 USD（Universal Scene Description）资产中引用了基于 MDL 的材质定义时，此插件负责将这些材质正确地翻译并创建为 Unreal Engine 中的材质资产。它作为一个专门的翻译器存在，使得 USD 导入管线能够处理 MDL 材质。

## 使用场景

- 当您从支持 MDL 材质的 DCC 工具（如 Substance 3D Stager、Houdini Solaris 等）导出 USD 场景，并且希望在 Unreal Engine 中保留并正确渲染这些材质时。
- 在复杂的跨平台或跨引擎内容管线中，需要统一使用 MDL 作为材质标准，通过 USD 进行资产交换。

## 蓝图用法

该插件的核心功能是作为 USD 导入流程的内部翻译器，不直接向蓝图暴露特殊节点。它的作用发生在通过 **USD Stage Actor** 或标准的 **USD 导入** 操作加载 USD 文件时，如果文件内包含 MDL 材质引用，插件会自动介入处理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateAssets` | 重写了父类方法，专门处理 MDL 材质资产的创建 | `FMdlUsdShadeMaterialTranslator` |

### 使用示例（蓝图描述）

您无需在蓝图中直接调用此插件的节点。使用方式如下：
1.  将包含 MDL 材质引用的 `.usd`、`.usda` 或 `.usdc` 文件放入项目。
2.  在场景中放置一个 `USD Stage Actor`。
3.  在 USD Stage Actor 的细节面板中，选择您的 USD 文件。
4.  插件将自动工作，将 USD 中引用的 MDL 材质转换为 Unreal 材质资产，并应用到导入的网格体上。

## C++ 用法

该插件的设计使其成为 USD 导入管线的一部分，通常不直接由用户 C++ 代码调用。其核心类 `FMdlUsdShadeMaterialTranslator` 继承自 `FMaterialXUsdShadeMaterialTranslator`。

### 头文件引入

```cpp
#include "MDLUSDShadeMaterialTranslator.h"
#include "MDLUSDLog.h"
```

### 基本用法

主要用于理解插件内部逻辑，或在扩展 USD 导入器时参考。
```cpp
// 该插件注册了一个日志类别，可用于调试 MDL 相关问题
// 源自: Source/USDImporterMDL/Public/MDLUSDLog.h
DECLARE_LOG_CATEGORY_EXTERN(LogUsdMdl, Log, All);
// 使用示例:
UE_LOG(LogUsdMdl, Log, TEXT("MDL material translation started."));
```

### 进阶用法

该插件没有提供额外的公共 API 进阶用法。其主要价值在于启用后，增强了核心 `USDImporter` 的能力。

## Demo 示例

由于此插件是集成模块，没有独立的 Demo 项目。以下是一个检查 MDL 材质是否被正确导入的伪代码概念：
```cpp
// MyUSDAssetHelper.h
#pragma once
#include "CoreMinimal.h"

class FMyUSDAssetHelper
{
public:
    // 检查一个材质资产是否可能来自 MDL 翻译
    // 注意：这只是一个概念示例，具体实现需要依赖 USD 和材质知识
    static bool CheckIfMaterialPotentiallyFromMDL(UMaterialInterface* Material)
    {
        if (Material)
        {
            // 可以通过材质的元数据、名称约定或特定参数来辅助判断
            // 但最根本的判断逻辑在 USDImporterMDL 翻译器内部
            UE_LOG(LogTemp, Warning, TEXT("Checking material: %s. MDL origin detection requires plugin context."), *Material->GetName());
        }
        return false;
    }
};
```

## 模块依赖

从插件的依赖声明和 `.Build.cs` 推断，使用此插件需要确保以下插件/模块可用：

| 模块 | 用途 |
|---|---|
| `USDCore` | 提供 USD 资产处理的基础框架和类型 |
| `USDImporter` | 核心的 USD 导入功能，此插件作为其扩展 |
| `MDLImporter` | 提供 MDL 材质的底层解析和导入能力 |

（无其他特殊依赖，仅依赖上述专用插件及标准的 Core/Engine 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF 格式化日志宏。 |
| 2026-01-22 | `6bfebf62` | USD: Delete code that was deprecated up to and including in 5.5. | 清理 USD 模块中已在 5.5 及之前版本废弃的代码。 |
| 2026-01-09 | `49c11077` | [UObject] | UObject 相关的基础维护或重构。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrappe | 集中并公开了一个检查 USD SDK 是否启用的函数。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 撤销了某次提交 (CL47041219) 的更改。 |

### 维护评价

- **创建时间**：2025年初，插件历史较短。
- **最近更新**：最近一次提交在 2026 年 4 月，主要是代码现代化（日志迁移）和依赖清理，属于基础维护。功能性更新较少。
- **活跃度**：属于**维护中**，有定期的代码清洁和基础维护活动，但非核心功能频繁迭代。
- **状态**：插件在 `.uplugin` 中被标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它仍处于测试阶段，尚未稳定到默认启用。
- **推荐**：如果您有明确的 MDL 管线需求，并且愿意承担实验性功能的潜在风险，可以启用并使用。对于大多数标准 USD 导入工作流，如果不需要 MDL，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中找到相关测试文件路径)