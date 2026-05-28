# Chaos Cloth Asset Editor (Deprecated)

> Deprecated plugin, please use the Chaos Cloth Asset Editor Core and Chaos Cloth Asset Usd Dataflow Nodes plugins instead.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器（已弃用） |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

该插件是一个**已弃用的过渡性包装插件**。它的核心功能并非提供独立的编辑器工具，而是通过依赖 (`ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes`) 来维持向后兼容性，并引导用户使用新的、功能更专注的插件。它的存在解决了在插件架构重组（拆分）过程中，避免现有项目因插件名称变更而立即崩溃的问题。

## 使用场景

- **项目升级过渡**：如果你的项目是从 UE 5.3 或更早版本升级而来，并且原已启用 `ChaosClothAssetEditor` 插件，启用此插件可以确保项目能顺利启动，无需立即修改配置。
- **系统学习**：如果你想了解 Unreal Engine 中布料资产系统的历史架构演变，这个插件是一个很好的切入点，它揭示了从单一编辑器插件到功能模块化拆分的过程。

## 蓝图用法

由于 `ChaosClothAssetEditor` 本身**没有模块和源码**，因此它不直接提供任何新的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *无直接节点* | 此插件仅作为依赖加载器 | - |

*蓝图用户应参考 [`ChaosClothAssetEditorCore`](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) 和 [`ChaosClothAssetUsdDataflowNodes`](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes) 插件文档以获取可用的编辑器工具和数据流节点。*

### 使用示例（蓝图描述）

在“插件”窗口中启用“Chaos Cloth Asset Editor (Deprecated)”后，您便可以在内容浏览器中正常创建、编辑 `ClothAsset`。所有实际功能（如布料模拟工具、USD数据导入节点）均由其依赖的子插件提供。

## C++ 用法

在 C++ 中，您通常不需要直接引用此插件。您应直接依赖其功能子模块。

### 头文件引入

由于此插件无自身模块，C++ 代码应直接包含替代插件的头文件。
```cpp
// 引用 ChaosClothAssetEditorCore 插件的功能（如果可用）
#include "ChaosClothAssetEditorCore/...YourSpecificHeader.h"

// 引用 ChaosClothAsset（核心运行时资产）的功能
#include "ChaosClothAsset/...YourSpecificHeader.h"
```

### 基本用法

如果您正在迁移代码，请将旧的模块依赖（如 `ChaosClothAssetEditor`）替换为新的模块。
```cpp
// 旧的 Build.cs 写法（已弃用）
PublicDependencyModuleNames.Add(“ChaosClothAssetEditor”);

// 新的推荐写法（根据您实际使用的功能选择模块）
// 1. 如果使用核心编辑器功能：
PublicDependencyModuleNames.Add(“ChaosClothAssetEditorCore”);
// 2. 如果使用布料资产运行时：
PublicDependencyModuleNames.Add(“ChaosClothAsset”);
```

### 进阶用法

在代码中，您可以通过 `FModuleManager` 检查新插件是否已正确加载，实现更健壮的迁移。
```cpp
// 检查核心编辑器插件是否加载成功
if (FModuleManager::Get().IsModuleLoaded(“ChaosClothAssetEditorCore”))
{
    // 安全地使用 ChaosClothAssetEditorCore 提供的类和函数
}
else
{
    UE_LOG(LogTemp, Warning, TEXT(“ChaosClothAssetEditorCore module is not loaded. Please enable the ChaosClothAssetEditorCore plugin.”));
}
```

## Demo 示例

一个体现从旧插件迁移到新插件的最小 .Build.cs 配置示例。

```cpp
// MyProject.Build.cs
using UnrealBuildTool;

public class MyProject : ModuleRules
{
    public MyProject(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            // “ChaosClothAssetEditor”, // ← 旧写法，已弃用
            "ChaosClothAsset",        // ← 新写法：引入布料资产运行时
            "ChaosClothAssetEditorCore" // ← 新写法：引入编辑器核心功能（如果需要）
        });
    }
}
```

## 模块依赖

本插件无自身模块，但通过 `.uplugin` 的 `Plugins` 部分声明了对以下插件的运行时依赖：

| 模块 | 用途 |
|---|---|
| `ChaosClothAssetEditorCore` | 提供实际的布料资产编辑器核心功能。 |
| `ChaosClothAssetUsdDataflowNodes` | 提供与 USD 格式和数据流相关的节点。 |

*使用者无需在 `Build.cs` 中声明对这些子插件模块的依赖，因为它们会随着本插件一起自动加载。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 布料资产相关模块正式移除测试版标记，标志着核心系统已稳定。 |
| 2026-01-27 | `4c7d09a3` | Chaos Cloth Asset - Split the ChaosClothEditor plugin into three plugins in order to move USD code o... | 将原编辑器插件拆分为三个独立插件，完成了模块化重构，本插件作为过渡包装被创建。 |
| 2026-01-26 | `ae188081` | Guard against crash and unexpected results in cloth remesh node | 修复了布料重网格化节点中的潜在崩溃和异常结果问题。 |
| 2026-01-26 | `306c3592` | Chaos Cloth Asset - Replaced lambda by existing LinearToSRGB function in the static mesh color space | 代码优化，用现有函数替代了Lambda表达式。 |
| 2026-01-26 | `d217d1d3` | Chaos Cloth Asset: (commit message truncated) | 布料资产相关的其他改进。 |

### 维护评价

- **插件状态**：**明确已弃用 (Deprecated)**。
- **创建与活跃期**：创建于 2024-03-22，作为 2026 年初插件架构拆分后的兼容性包而存在。
- **维护情况**：其依赖的子插件（`ChaosClothAssetEditorCore` 等）仍在活跃维护（2026 年有实质性更新）。本插件自身无代码更新。
- **推荐行动**：**强烈建议迁移**。不应在新项目中使用此插件。现有项目应在适当时机，将 `.uplugin` 和 `.Build.cs` 中的依赖项切换为 `ChaosClothAssetEditorCore` 和 `ChaosClothAsset`，然后禁用或移除此弃用插件。
- **警告**：此插件仅为向后兼容而存在，未来版本可能被完全移除。依赖于此插件名称属于技术债务。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor)
- [替代插件：ChaosClothAssetEditorCore](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- [替代插件：ChaosClothAssetUsdDataflowNodes](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)