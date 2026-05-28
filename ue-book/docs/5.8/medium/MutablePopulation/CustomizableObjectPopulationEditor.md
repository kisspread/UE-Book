# MutablePopulation

> Extend the Mutable plugin to support Population assets.

| 属性 | 值 |
|---|---|
| 中文名 | 可变种群 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、资产定义） |
| 模块 | `CustomizableObjectPopulation` (Runtime), `CustomizableObjectPopulationEditor` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-09-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation) | |

## 用途

该插件是 [Mutable](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mutable) 可定制对象系统的一个扩展模块。它的核心目的是为大规模生成和管理角色实例（即“种群”）提供一个工作流和资产支持。

具体来说，Mutable 本身专注于通过“可定制对象”定义单个角色的可变外观（如衣服、发型、颜色）。而 MutablePopulation 插件在此基础上引入了“种群”（Population）和“种群类”（Population Class）的概念，允许开发者创建规则集来批量生成具有相似特征但又存在差异（如头发颜色在一定范围内随机变化）的大量角色实例。这解决了在开放世界、RPG 等需要大量 NPC（非玩家角色）且要求他们具有多样性和性能优化的场景下，手动创建和配置每一个实例不切实际的问题。

## 使用场景

- 你在制作一个需要生成大量具有相似基础外观、但细节（如皮肤颜色、服装纹理、体型参数）在特定规则范围内随机变化的 NPC 群体的游戏（例如中世纪城镇的居民、未来都市的市民）。
- 你需要为游戏中的角色定制系统（Character Customization）创建预设模板，并允许玩家基于这些模板快速生成或选择角色。
- 你希望管理一组角色实例的生成、预览和资产化过程，以提高内容生产管线的效率。

## C++ 用法

此插件的核心功能集中在编辑器工具和资产类型定义上，用于构建生产管线，而非直接在运行时通过 C++ API 调用生成实例。其主要用法体现在创建和使用其提供的编辑器工具。

### 头文件引入

要创建并打开“种群类”编辑器，需要引用编辑器模块的头文件：

```cpp
#include "MuCOPE/CustomizableObjectPopulationEditorModule.h"
#include "MuCOPE/ICustomizableObjectPopulationClassEditor.h"
```

### 基本用法

以下代码演示了如何通过编辑器模块接口来创建并打开一个 `UCustomizableObjectPopulationClass` 资产的编辑器：

```cpp
// 假设你已经持有一个有效的 UCustomizableObjectPopulationClass* 指针 PopulationClassAsset
UCustomizableObjectPopulationClass* PopulationClassAsset = /* ... */;

// 获取 Population 编辑器模块的接口
ICustomizableObjectPopulationEditorModule& PopulationEditorModule = ICustomizableObjectPopulationEditorModule::Get();

// 创建并打开编辑器
TSharedRef<ICustomizableObjectPopulationClassEditor> ClassEditor = 
    PopulationEditorModule.CreateCustomizableObjectPopulationClassEditor(
        EToolkitMode::Standalone, // 或者 Standalone, WorldCentric
        TSharedPtr<IToolkitHost>(), // 通常由编辑器框架提供
        PopulationClassAsset
    );

// 现在，编辑器窗口应该已经打开，你可以通过返回的 ClassEditor 引用进行进一步操作（如果需要）。
```

*(来源: Public/MuCOPE/CustomizableObjectPopulationEditorModule.h 中的 `CreateCustomizableObjectPopulationClassEditor` 函数声明)*

### 进阶用法

进阶用法主要涉及插件内部的复杂工作流，如通过 `FCustomizableObjectPopulationClassEditor` 类（见源码 `Private/MuCOPE/CustomizableObjectPopulationClassEditor.h`）来测试种群、生成实例资产等。这些通常是编辑器 UI 按钮触发的内部逻辑。例如，编辑器类提供了 `TestPopulationClass()` 和 `GeneratePopulationClassInstances()` 等方法。

## Demo 示例

以下是一个极简示例，展示如何在编辑器工具代码中触发“种群类”编辑器的打开。

**MyPopulationTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UCustomizableObjectPopulationClass;

class FMyPopulationTool
{
public:
    // 打开指定的种群类资产进行编辑
    void OpenPopulationClassForEditing(UCustomizableObjectPopulationClass* PopulationClassAsset);
};
```

**MyPopulationTool.cpp**
```cpp
#include "MyPopulationTool.h"
#include "MuCOPE/CustomizableObjectPopulationEditorModule.h"

void FMyPopulationTool::OpenPopulationClassForEditing(UCustomizableObjectPopulationClass* PopulationClassAsset)
{
    if (!PopulationClassAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to open Population Class editor: Asset is null."));
        return;
    }

    // 获取并调用编辑器模块来打开资产
    ICustomizableObjectPopulationEditorModule& EditorModule = ICustomizableObjectPopulationEditorModule::Get();
    EditorModule.CreateCustomizableObjectPopulationClassEditor(
        EToolkitMode::Standalone,
        TSharedPtr<IToolkitHost>(),
        PopulationClassAsset
    );
}
```

## 模块依赖

该插件的编辑器模块 `CustomizableObjectPopulationEditor` 依赖了一些 UnrealEd 的特定子系统，这使其本质上是一个**编辑器专用插件**。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器基础框架、资产编辑工具等 |
| `DerivedDataCache` | 访问派生数据缓存系统，可能用于加速实例资产的生成 |
| `MessageLog` | 输出编辑器日志和错误消息 |

*注：运行时模块 `CustomizableObjectPopulation` 的依赖未在提供信息中列出，通常它可能仅依赖 `Core` 和 `CoreUObject`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `f35985aa` | Fix Customizable Object Editor viewport orbit/pan broken with new gizmos | 修复了在新 Gizmo 系统下，可定制对象编辑器视口的轨道/平移功能失效的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏调用迁移到新的 `UE_LOGF` 宏，以适配引擎日志系统的更新。 |
| 2026-03-25 | `6dcf9bb4` | [Mutable] Fix CO Instances not updating. | 修复了可定制对象实例未正确更新（外观未变化）的 Bug。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的构建版本设置信息。 |
| 2026-01-13 | `5e60b0a5` | [Mutable] Allow components having the same name. | 允许可定制对象中的组件（Component）可以拥有相同的名称，放宽了之前的命名限制。 |

### 维护评价

该插件处于**活跃维护**状态。
- **创建时间**：2024年9月，是一个相对年轻的实验性插件。
- **最近更新**：最近一次实质性更新在2026年4月（修复视口交互），说明仍在积极维护以适配引擎新特性和修复问题。
- **已知限制**：作为实验性插件，其 API 和功能可能会发生变化。目前公开的蓝图/C++ 接口非常有限，主要功能集中于编辑器工具和资产类型，运行时生成逻辑可能封装在 `Mutable` 主插件中。
- **推荐使用**：**谨慎推荐**。如果你正在使用 Mutable 插件并需要大规模生成角色实例的管线，该插件是官方提供的解决方案，值得评估和使用。但需注意其实验性状态，并准备好应对可能的未来变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation)
- [官方文档](https://docs.unrealengine.com) (通常指向主 Mutable 插件文档，无独立文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation/Tests) (路径推断，需确认是否存在)