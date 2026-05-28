# MetaHuman Creator - UAF support

> UAF (Unreal Animation Framework) support for MetaHuman Creator

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman UAF支持 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、项目设置） |
| 模块 | `MetaHumanCharacterUAFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF) | |

## 用途

该插件的核心作用是将 Unreal Animation Framework (UAF) 动画框架集成到 MetaHuman Creator 工作流中。它不是一个通用的动画框架，而是专门为 MetaHuman 角色定制的**构建支持插件**。

它解决的具体问题是：当使用 UAF 动画系统时，如何根据不同的质量级别（例如：高保真、简化版）为 MetaHuman 角色自动装配（Assemble）不同的、预配置好的蓝图 Actor。插件通过一个项目设置，将 `EMetaHumanQualityLevel` 枚举映射到对应的蓝图类，从而让 UAF 构建流程知道应该使用哪个蓝图来创建最终的 MetaHuman 角色实例。

## 使用场景

- 你正在使用 MetaHuman Creator 并计划使用 UAF 动画框架驱动你的 MetaHuman 角色。
- 你需要为不同硬件平台或性能要求准备不同质量（如顶点数、材质复杂度）的 MetaHuman 角色蓝图。
- 你希望构建流程能自动根据预设的质量级别选择正确的蓝图进行组装。

## 蓝图用法

该插件主要提供编辑器内的项目设置功能，没有额外的公开蓝图函数。

### 核心配置

配置通过 **项目设置 (Project Settings) -> 插件 -> MetaHuman Character UAF** 进行。

| 配置项 | 说明 |
|---|---|
| `Blueprints` (Build 分类) | 一个 `TMap`，键是 `EMetaHumanQualityLevel`（质量级别），值是对应的 `AActor` 蓝图类。在此处为每个质量级别指定你希望 UAF 使用的 MetaHuman 角色蓝图。 |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacterUAFProjectSettings.h"
```

### 基本用法

访问和修改项目设置中的蓝图映射。
*来源文件: `Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF/Source/MetaHumanCharacterUAFEditor/Private/MetaHumanCharacterUAFProjectSettings.h`*

```cpp
// 获取项目设置实例（单例）
UMetaHumanCharacterUAFProjectSettings* Settings = GetMutableDefault<UMetaHumanCharacterUAFProjectSettings>();
if (Settings)
{
    // 假设我们想为“高”质量级别指定一个蓝图
    static const FName HighQualityLevelName = TEXT("High");
    EMetaHumanQualityLevel HighQualityLevel = ... // 将枚举字符串转换为枚举值

    // 设置蓝图映射
    Settings->Blueprints.Add(HighQualityLevel, YourHighQualityBlueprintClass);

    // 保存设置到配置文件
    Settings->SaveConfig();
}
```

### 进阶用法

在 UAF 构建流程中，根据质量级别查询应使用的蓝图。
*此逻辑可能存在于其他 UAF 或 MetaHuman 插件中，但展示了本插件提供的配置如何被使用。*

```cpp
const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
TSoftClassPtr<AActor>* FoundBlueprint = Settings->Blueprints.Find(CurrentQualityLevel);

if (FoundBlueprint && !FoundBlueprint->IsNull())
{
    // 加载并使用找到的蓝图类进行 MetaHuman 角色装配
    UClass* BlueprintClass = FoundBlueprint->LoadSynchronous();
    if (BlueprintClass)
    {
        // ... 使用 BlueprintClass 生成 Actor
    }
}
```

## Demo 示例

```cpp
// MetaHumanUAFDemoSettings.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanCharacterUAFDemoSettings.generated.h"

UCLASS()
class UMetaHumanUAFDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 打印当前项目设置中所有质量级别与蓝图的映射关系。 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|UAF")
    void PrintUAFBlueprintMappings();
};

// MetaHumanUAFDemoSettings.cpp
#include "MetaHumanUAFDemoSettings.h"
#include "MetaHumanCharacterUAFProjectSettings.h"
#include "MetaHumanQualityLevel.h" // 假设枚举定义在此头文件

void UMetaHumanUAFDemoSubsystem::PrintUAFBlueprintMappings()
{
    const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
    if (!Settings) return;

    UE_LOG(LogTemp, Log, TEXT("--- MetaHuman UAF Blueprint Mappings ---"));
    for (const auto& Pair : Settings->Blueprints)
    {
        const EMetaHumanQualityLevel& QualityLevel = Pair.Key;
        const TSoftClassPtr<AActor>& BlueprintPtr = Pair.Value;

        // 假设EMetaHumanQualityLevel可以通过UEnum::GetValueAsString转换
        FString QualityLevelStr = UEnum::GetValueAsString(QualityLevel);
        FString BlueprintName = BlueprintPtr.IsNull() ? TEXT("None") : BlueprintPtr.GetAssetName();

        UE_LOG(LogTemp, Log, TEXT("Quality Level: %s -> Blueprint: %s"), *QualityLevelStr, *BlueprintName);
    }
}
```

## 模块依赖

从插件的依赖声明 (`“Plugins”: [...]`) 和模块类型推断，使用此插件时，你的模块需要链接以下模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | MetaHuman 角色核心系统 |
| `UAF` | Unreal Animation Framework 核心 |
| `UAFAnimGraph` | UAF 动画图支持 |
| `UAFControlRig` | UAF 控制绑定支持 |
| `RigLogicUAF` | RigLogic 与 UAF 的集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-14 | `049dd5ce` | Rename UAnimNextRigVM* to UUAFRigVM* | 将动画相关RigVM类重命名为UAF前缀，统一命名规范 |
| 2026-01-13 | `436f1414` | Rename UAnimNextComponent to UUAFComponent | 将动画组件重命名为UAF组件，完成UAF品牌替换 |
| 2026-01-08 | `8e81a827` | Add UAF Asset Data structure to encapsulate an asset that can be used to generate a UAF graph or sys | 添加UAF资产数据结构，用于封装可生成UAF图的资产 |
| 2026-01-07 | `7f65190a` | Rename UAnimNextModule to UUAFSystem | 将动画模块重命名为UAF系统，是UAF品牌整合的一部分 |
| 2025-09-29 | `e0a45858` | Fix for broken BP when Common folder is redirected when exporting a UAF MH | 修复导出UAF MetaHuman时，Common文件夹重定向导致蓝图损坏的问题 |

### 维护评价

该插件创建于 **2025 年 9 月**，属于较新的插件，目前仍在 **活跃开发** 中。从 Git 历史看，最近的更新集中在 2026 年 1 月，主要工作是将插件从早期的 "AnimNext" 命名全面迁移到 "UAF"（Unreal Animation Framework）命名，这表明 UAF 框架正在经历重要的品牌和架构整合阶段。

该插件被明确标记为 **实验性 (IsExperimentalVersion=true)**，并且 **默认未启用 (Installed: false)**。这意味着它尚未稳定，API 可能发生变化，不建议在正式生产项目中直接使用，更适合用于原型验证和技术探索。

**综合评价**：作为 MetaHuman 与 UAF 集成的桥梁插件，它功能明确但当前处于实验阶段。开发者如果正在探索 UAF 动画框架并希望驱动 MetaHuman 角色，可以关注并试用此插件，但需注意其不稳定性和平台限制（目前仅支持 Win64）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF)
- [官方文档]() （暂无）
- [测试用例]() （该插件目录下未发现公开的测试用例文件）