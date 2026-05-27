# MetaHuman Character UAF

> UAF (Unreal Animation Framework) support for MetaHuman Creator（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画框架支持 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `MetaHumanCharacterUAFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF) | |

## 用途

此插件是 MetaHuman 角色系统与 Unreal Animation Framework (UAF) 动画框架之间的集成层。它为 MetaHuman Creator 工具链提供了必要的配置和构建支持，使得创建的 MetaHuman 角色能够利用 UAF 动画系统，而非传统的基于动画蓝图的资产。

其主要解决的问题是：当开发者选择使用 UAF 这种更新的、可能更高效或功能更强大的动画框架时，需要为其 MetaHuman 角色生成适配 UAF 工作流的资产和配置。此插件提供了这种桥接和构建规则。

## 使用场景

- 你正在使用 **MetaHuman Creator** 工具创建逼真的人类角色。
- 你决定或需要在你的项目中采用 **Unreal Animation Framework (UAF)** 动画系统来驱动角色动画。
- 你需要配置项目，以便导出和组装的 MetaHuman 能够与 UAF 组件和系统兼容并高效工作。

*注意：此插件标记为实验性，且默认不启用。主要用于前沿功能评估和特定工作流开发。*

## 蓝图用法

此插件当前提供的蓝图功能非常有限，主要通过编辑器设置面板进行配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MetaHuman Character UAF Project Settings` | 在插件设置中配置用于组装 MetaHuman 的默认 Actor 蓝图。 | `UMetaHumanCharacterUAFProjectSettings` |

### 使用示例（蓝图描述）

由于插件本身不提供运行时蓝图节点，其“蓝图用法”体现在 **项目设置** 中：
1.  打开编辑器设置（Editor -> Project Settings）。
2.  导航至 **Plugins -> MetaHuman Character UAF** 分类。
3.  在 “Build” 类别下，你可以编辑 `Blueprints` 属性。这是一个 `TMap`，将不同的 `EMetaHumanQualityLevel`（质量级别）映射到对应的 `AActor` 蓝图类（`TSoftClassPtr<AActor>`）。这定义了在使用 UAF 组装不同质量级别的 MetaHuman 时，应该使用哪个基础蓝图作为模板。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacterUAFProjectSettings.h"
```

### 基本用法

从插件唯一的头文件 `MetaHumanCharacterUAFProjectSettings.h` 中提取，用于在 C++ 中访问项目设置。

```cpp
// 获取 MetaHuman UAF 项目的设置单例
const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();

if (Settings)
{
    // 读取指定质量级别对应的蓝图资产路径（软引用）
    // 假设我们想查看 EMetaHumanQualityLevel::High 对应的蓝图
    const TSoftClassPtr<AActor>* HighQualityBlueprintPtr = Settings->Blueprints.Find(EMetaHumanQualityLevel::High);

    if (HighQualityBlueprintPtr && !HighQualityBlueprintPtr->IsNull())
    {
        // 在此处可以异步加载该蓝图类
        UE_LOG(LogTemp, Log, TEXT("Found Blueprint for High quality: %s"), *HighQualityBlueprintPtr->ToString());
    }
}
```
*代码来源：基于 `Source/MetaHumanCharacterUAFEditor/Private/MetaHumanCharacterUAFProjectSettings.h` 解析。*

## Demo 示例

以下是一个最小的示例，演示如何在模块中获取并查询 `MetaHumanCharacterUAFProjectSettings`。

**MyModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyModule.cpp**
```cpp
#include "MyModule.h"
#include "MetaHumanCharacterUAFProjectSettings.h"

void FMyModule::StartupModule()
{
    // 示例：在模块启动时检查设置
    const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
    if (Settings)
    {
        // 假设存在一个名为 “AMH_UAF_Standard” 的资产，我们想查询它的配置
        for (const auto& Pair : Settings->Blueprints)
        {
            UE_LOG(LogTemp, Warning, TEXT("Quality Level %d uses Blueprint: %s"),
                static_cast<int32>(Pair.Key), *Pair.Value.GetAssetName());
        }
    }
}

void FMyModule::ShutdownModule()
{
    // 清理
}

IMPLEMENT_MODULE(FMyModule, MyModule)
```

## 模块依赖

从插件的 `.uplugin` 元数据中的 `Plugins` 列表推断，使用此插件需要以下插件处于启用状态：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心的 Unreal Animation Framework 插件。 |
| `UAFAnimGraph` | 用于 UAF 的动画图表编辑功能。 |
| `UAFControlRig` | UAF 与 Control Rig 的集成。 |
| `RigLogicUAF` | 为 MetaHuman 面部 Rig 提供 UAF 支持。 |
| `MetaHumanCharacter` | MetaHuman 角色系统的基础插件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-14 | `049dd5ce` | Rename UAnimNextRigVM* to UUAFRigVM* | 将 `UAnimNextRigVM` 类重命名为 `UUAFRigVM`，跟进 UAF 框架的命名更新。 |
| 2026-01-13 | `436f1414` | Rename UAnimNextComponent to UUAFComponent | 将 `UAnimNextComponent` 重命名为 `UUAFComponent`，是 UAF 框架重构的一部分。 |
| 2026-01-08 | `8e81a827` | Add UAF Asset Data structure to encapsulate an asset that can be used to generate a UAF graph or system | 添加 `UAF Asset Data` 数据结构，用于封装可生成 UAF 图或系统的资产。 |
| 2026-01-07 | `7f65190a` | Rename UAnimNextModule to UUAFSystem | 将 `UAnimNextModule` 重命名为 `UUAFSystem`，是框架命名统一。 |
| 2025-09-29 | `e0a45858` | Fix for broken BP when Common folder is redirected when exporting a UAF MH | 修复在导出 UAF MetaHuman 时，若 “Common” 文件夹被重定向会导致蓝图损坏的问题。 |

### 维护评价

- **状态**：**活跃开发中**。尽管创建于约1年前，但最近的提交（2026年1月）显示插件正在持续更新，主要工作是跟进 UAF 框架的类名重构，并添加新功能。
- **实验性**：插件明确标记为 `IsExperimentalVersion: true`，且默认不启用。这表明它仍处于早期验证阶段，API 和功能可能不稳定，不建议用于生产环境。
- **推荐度**：仅推荐给**提前评估 UAF 与 MetaHuman 集成**的技术美术或动画程序员。对于常规 MetaHuman 开发，建议使用成熟的默认动画蓝图工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF/Tests) (预期路径，可能存在)