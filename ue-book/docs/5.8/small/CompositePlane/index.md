# Composite Plane

> Provides a cine camera actor for projecting textures and videos

| 属性 | 值 |
|---|---|
| 中文名 | 合成平面 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CompositePlane` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-02-21 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CompositePlane) | |

## 用途

该插件在虚拟制片工作流中提供一个特殊的电影摄像机角色，其核心功能是将纹理或视频内容投射到一个平面（Plane）上。这主要用于实时合成，允许艺术家将一个预先渲染的或实时的图像（如虚拟背景、LED墙内容）投射到场景中的一个特定平面上，以便在拍摄时实现精确的视觉匹配和合成效果。

## 使用场景

- **虚拟制片（Virtual Production）**：当你需要在现实场景的镜头中，通过一个平面精准地融入一个虚拟环境（如LED墙上的内容）时，使用此插件来创建和配置这个投射平面。
- **实时合成**：在需要动态地将视频素材或实时渲染的画面投射到场景中的特定表面时。

## 蓝图用法

根据提供的源码分析，该插件的功能主要通过编辑器模块和放置逻辑实现，未直接暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 函数。其使用主要通过在编辑器中放置相应的演员（Actor）并配置其属性来完成。

### 核心功能

该插件在编辑器中注册了放置行为（Placement），这意味着你可以在“放置演员”（Place Actors）面板中找到它提供的可放置对象。

### 使用示例（编辑器操作）

1.  在 Unreal Editor 的“放置演员”面板中，查找“Composite Plane”或相关类别。
2.  将对应的演员拖拽到场景中。
3.  在该演员的“细节”（Details）面板中，配置用于投射的纹理或视频源。
4.  调整平面的位置、旋转和缩放，使其与你的合成场景需求相匹配。

## C++ 用法

### 头文件引入

```cpp
// 该插件的API较为基础，主要涉及模块启动与放置注册。
// 通常情况下，用户通过编辑器界面操作，无需直接引入头文件。
// 如需扩展或修改放置逻辑，可能需要研究其私有实现。
```

### 基本用法

该插件的核心是 `FCompositePlanePlacement` 类，它负责在引擎中注册和取消注册“合成平面”类型的可放置对象。这是编辑器操作的基础。

```cpp
// 源文件: Source/CompositePlane/Private/CompositePlanePlacement.h
// 该类为插件提供了核心的放置（Placement）注册功能。
// 在插件的模块启动时调用 RegisterPlacement()，在关闭时调用 UnregisterPlacement()。

#include "CompositePlanePlacement.h"

// 在插件模块启动时
void FCompositePlaneModule::StartupModule()
{
    FCompositePlanePlacement::RegisterPlacement();
}

// 在插件模块关闭时
void FCompositePlaneModule::ShutdownModule()
{
    FCompositePlanePlacement::UnregisterPlacement();
}
```

## Demo 示例

一个最简单的、展示如何从代码层面与此插件交互（例如，在另一个插件中查询其状态）的示例。注意，该插件本身没有提供公开的业务API。

**CompositePlaneDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FCompositePlaneDemo
{
public:
    // 示例：检查CompositePlane插件模块是否已加载
    static bool IsCompositePlaneModuleLoaded();
};
```

**CompositePlaneDemo.cpp**
```cpp
#include "CompositePlaneDemo.h"
#include "Modules/ModuleManager.h"

bool FCompositePlaneDemo::IsCompositePlaneModuleLoaded()
{
    return FModuleManager::Get().IsModuleLoaded("CompositePlane");
}
```

## 模块依赖

无特殊依赖（仅标准 Core/CoreUObject/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-11-06 | `7debe66b` | [Backout] CompositePlane: Remove deprecation again due to remaining internal project use. | **回退操作**：由于内部项目仍在使用，再次撤销了此前对插件的废弃标记。 |
| 2025-11-04 | `65e9ea7d` | [Resubmit] | **重新提交**：通常用于代码合并或变更的重新提交。 |
| 2025-09-19 | `3aee1b78` | [Backout] - CL45991071 | **回退操作**：撤销了某个特定的变更列表。 |
| 2025-09-19 | `1087290e` | CompositePlane: Start deprecation process. | **开始废弃流程**：官方启动了对CompositePlane插件的废弃程序。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | **引擎插件更新**：一次范围较广的引擎插件更新。 |

### 维护评价

**状态：不稳定，可能废弃**

该插件的维护状态令人担忧。从近期提交记录可以清晰地看到，官方在 2025 年 9 月已正式启动了该插件的废弃（Deprecation）流程。尽管由于“内部项目仍在使用”，废弃流程在 11 月被临时回退，但这强烈表明该插件已不再被积极维护和推荐，其未来可能会从引擎中移除。

**结论：**
- **不推荐用于新项目**：鉴于其明确的废弃流程，不应在新项目中采用此插件。
- **遗留项目风险**：已在使用该插件的项目应密切关注官方更新，并制定迁移计划，因为它随时可能因官方移除而导致编译失败。
- **实验性且仅限编辑器**：插件标记为 `IsBetaVersion=true` 且模块类型为 `Editor`，进一步限制了其适用范围。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CompositePlane)