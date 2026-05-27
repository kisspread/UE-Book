# MetaHuman Creator - UAF support

> UAF (Unreal Animation Framework) support for MetaHuman Creator

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman UAF 集成 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（项目设置） |
| 模块 | `MetaHumanCharacterUAFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF) | |

## 用途

此插件是 **MetaHuman Creator** 与新一代动画框架 **UAF (Unreal Animation Framework)** 之间的桥梁。它并非独立工具，而是扩展了 MetaHuman Creator 的能力，使其能够为 UAF 驱动的 MetaHuman 生成和配置资产。
具体来说，它解决了在 MetaHuman Creator 中为 UAF 项目**组装和构建 MetaHuman 角色**的问题。例如，根据不同的品质级别（如高、中、低），指定使用哪个基础蓝图 Actor 作为 UAF 驱动的 MetaHuman 的载体。

## 使用场景

- 你的团队正在使用 **UAF 框架**来驱动动画，并希望将 **MetaHuman Creator** 作为角色资产的创建入口。
- 你需要在 MetaHuman Creator 内部**预览和配置** MetaHuman 在 UAF 工作流下的表现。
- 你希望为不同**性能或品质需求**的 MetaHuman（如电影级、游戏级）指定不同的 UAF Actor 蓝图。

## 蓝图用法

本插件主要提供编辑器项目设置功能，未暴露独立的运行时或蓝图可调用函数。

### 核心设置

| 设置项 | 说明 | 所在类 |
|---|---|---|
| `Blueprints` | 一个映射表，用于为不同品质级别 (`EMetaHumanQualityLevel`) 的 MetaHuman 指定默认的 UAF Actor 蓝图。 | `UMetaHumanCharacterUAFProjectSettings` |

### 使用示例（项目设置）

1.  在编辑器菜单中，打开 **Edit > Project Settings**。
2.  在左侧导航栏中，找到 **Plugins > MetaHuman Character UAF**。
3.  在 **Build** 分类下，你可以编辑 **Blueprints** 表格，为 `High`、`Medium`、`Low` 等品质级别设置对应的 `TSoftClassPtr<AActor>` 蓝图资产路径。

## C++ 用法

本插件的核心 C++ 接口是 `UMetaHumanCharacterUAFProjectSettings`，用于读取项目配置。

### 头文件引入

```cpp
#include "MetaHumanCharacterUAFProjectSettings.h"
```

### 基本用法：获取项目设置

你可以通过 `UDeveloperSettings` 的标准方法获取配置实例，并读取为特定品质级别指定的蓝图类。

```cpp
// 来源: MetaHumanCharacterUAFProjectSettings.h
// 假设我们想获取为“高品质”MetaHuman指定的蓝图
const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
if (Settings)
{
    // 获取高品质对应的蓝图软引用
    TSoftClassPtr<AActor> HighQualityBlueprintSoftPtr = Settings->Blueprints.FindRef(EMetaHumanQualityLevel::High);
    
    // 后续可以加载并使用该蓝图类
    if (!HighQualityBlueprintSoftPtr.IsNull())
    {
        UClass* HighQualityBlueprintClass = HighQualityBlueprintSoftPtr.LoadSynchronous();
        // ... 使用 HighQualityBlueprintClass 进行生成或配置
    }
}
```

## Demo 示例

以下代码演示了如何在编辑器模块或工具类中读取 `MetaHumanCharacterUAF` 项目设置，以获取特定品质级别的蓝图类。

```cpp
// MyMetaHumanUAFTool.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCharacterUAFProjectSettings.h"
#include "MetaHumanQualityLevel.h" // 假设此枚举在MetaHumanCharacter模块中定义

class FMyMetaHumanUAFTool
{
public:
    static UClass* GetBlueprintClassForQualityLevel(EMetaHumanQualityLevel QualityLevel)
    {
        const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
        if (!Settings)
        {
            return nullptr;
        }

        const TSoftClassPtr<AActor>* FoundPtr = Settings->Blueprints.Find(QualityLevel);
        if (FoundPtr && !FoundPtr->IsNull())
        {
            return FoundPtr->LoadSynchronous();
        }
        return nullptr;
    }
};
```

## 模块依赖

本插件依赖于多个核心 MetaHuman 和 UAF 相关插件，你的项目也需要启用这些插件。

| 模块/插件 | 用途 |
|---|---|
| `UAF` | UAF 动画框架核心运行时插件 |
| `UAFAnimGraph` | UAF 与动画蓝图图编辑器的集成 |
| `UAFControlRig` | UAF 与 Control Rig 的集成 |
| `RigLogicUAF` | RigLogic（MetaHuman 的面部解算核心）与 UAF 的集成 |
| `MetaHumanCharacter` | MetaHuman 角色的核心资产和逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-14 | `049dd5ce` | Rename UAnimNextRigVM* to UUAFRigVM* | 将 AnimNext 相关 RigVM 类重命名为 UAF 前缀，完成品牌统一。 |
| 2026-01-13 | `436f1414` | Rename UAnimNextComponent to UUAFComponent | 将动画核心组件类从 AnimNext 重命名为 UAF，与框架名一致。 |
| 2026-01-08 | `8e81a827` | Add UAF Asset Data structure to encapsulate an asset that can be used to generate a UAF graph or sys | 新增 UAF 资产数据结构，用于封装可生成 UAF 图或系统的资产。 |
| 2026-01-07 | `7f65190a` | Rename UAnimNextModule to UUAFSystem | 将模块级动画系统从 AnimNext 重命名为 UAFSystem。 |
| 2025-09-29 | `e0a45858` | Fix for broken BP when Common folder is redirected when exporting a UAF MH | 修复了当导出 UAF MetaHuman 时，若 Common 文件夹被重定向导致蓝图损坏的问题。 |

### 维护评价

- **活跃维护**：该插件近期（2026年1月）更新非常频繁，且为**功能性重构**（大规模类名从 `AnimNext` 更名为 `UAF`），表明它处于 **UAF 框架快速开发和集成的关键阶段**。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true` 且 `Installed: false`，明确标记为实验性。
- **结论**：这是一个**活跃开发中的实验性插件**，是 UAF 与 MetaHuman 工作流集成的最新进展。适合**早期采用者和框架贡献者**跟踪，但目前的 API 和功能可能还不稳定，不推荐用于面向最终用户的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF)
- 官方文档链接：暂无 (`DocsURL` 字段为空)