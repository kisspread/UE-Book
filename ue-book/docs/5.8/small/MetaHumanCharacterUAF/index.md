# MetaHuman Creator - UAF support

> UAF (Unreal Animation Framework) support for MetaHuman Creator

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman UAF 支持 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanCharacterUAFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF) | |

## 用途

此插件是 MetaHuman Creator 与 Unreal Animation Framework (UAF) 之间的集成桥梁。它的核心作用是为 MetaHuman 角色的构建流程提供 UAF 支持，允许开发者为不同质量等级的 MetaHuman 配置专门用于 UAF 动画系统的构建蓝图。

本质上，它解决了将基于 Skeletal Mesh 的 MetaHuman 与先进的 UAF 动画图表系统进行无缝对接的配置问题。通过此插件，可以确保在构建 MetaHuman 资产时，能够自动生成或应用与 UAF 兼容的动画蓝图和控制绑定。

## 使用场景

- 你正在开发一个使用 MetaHuman 角色的项目，并希望利用 UAF 动画框架来实现更复杂、更高性能的程序化动画或动画混合。
- 你需要为移动端和高端PC端的 MetaHuman 分别配置不同的动画蓝图和控制蓝图，以优化不同平台的性能和视觉效果。
- 你的 MetaHuman 工作流需要集成 RigLogic 和 UAF，此插件提供了必要的配置入口。

## 蓝图用法

此插件主要通过编辑器设置面板进行配置，未暴露直接的蓝图节点。其核心是一个项目设置 (`UDeveloperSettings`)，用于定义构建映射关系。

### 核心设置

| 设置项 | 说明 | 所在类 |
|---|---|---|
| `Build.Blueprints` | 一个映射表，将 MetaHuman 质量等级 (`EMetaHumanQualityLevel`) 与对应的构建 Actor 蓝图 (`TSoftClassPtr<AActor>`) 关联起来。 | `UMetaHumanCharacterUAFProjectSettings` |

### 使用示例（配置）
在编辑器中，通过 **项目设置 (Project Settings)** -> **插件 (Plugins)** -> **MetaHuman Character UAF** 可以找到配置界面。
在 `Build` 分类下，你可以为 `Low`, `Medium`, `High` 等不同的质量等级指定不同的 Actor 蓝图。这些蓝图定义了如何使用 UAF 来组装一个完整的 MetaHuman 角色。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacterUAFProjectSettings.h"
```

### 基本用法

获取项目设置实例并读取配置的蓝图映射。

```cpp
// 来源：实际使用场景推断，因测试用例未提供
// 获取默认设置对象
const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();

if (Settings)
{
    // 获取特定质量等级对应的构建蓝图类
    TSoftClassPtr<AActor>* FoundBlueprint = Settings->Blueprints.Find(EMetaHumanQualityLevel::High);
    if (FoundBlueprint && !FoundBlueprint->IsNull())
    {
        // 使用找到的蓝图类进行后续操作，例如异步加载
        UClass* BlueprintClass = FoundBlueprint->LoadSynchronous();
        // ... 使用 BlueprintClass
    }
}
```

### 进阶用法

在 MetaHuman 构建流程中，根据当前目标质量等级动态选择正确的构建蓝图。

```cpp
// 来源：结合插件用途推断
void BuildMetaHumanForUAF(EMetaHumanQualityLevel QualityLevel)
{
    const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
    if (!Settings) return;

    const TSoftClassPtr<AActor>* BlueprintPtr = Settings->Blueprints.Find(QualityLevel);
    if (BlueprintPtr && !BlueprintPtr->IsNull())
    {
        // 异步加载蓝图资产
        UAssetManager::GetStreamableManager().RequestAsyncLoad(
            BlueprintPtr->ToSoftObjectPath(),
            FStreamableDelegate::CreateLambda([BlueprintPtr, QualityLevel]()
            {
                UClass* ActorClass = BlueprintPtr->Get();
                if (ActorClass)
                {
                    // 在此处使用 ActorClass 实例化一个 UAF 版的 MetaHuman 组装器
                    // 例如：GetWorld()->SpawnActor<AActor>(ActorClass, ...);
                    UE_LOG(LogTemp, Log, TEXT("Loaded UAF blueprint for quality level: %d"), static_cast<int32>(QualityLevel));
                }
            })
        );
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No UAF blueprint configured for quality level: %d"), static_cast<int32>(QualityLevel));
    }
}
```

## Demo 示例

一个访问插件设置并获取特定质量级别构建蓝图类的最小示例。

**MetaHumanUAFDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanCharacterUAFProjectSettings.h" // 引入插件设置头文件
#include "MetaHumanUAFDemo.generated.h"

UCLASS()
class UMetaHumanUAFDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 根据质量等级获取对应的UAF构建蓝图类 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|UAF")
    static TSubclassOf<AActor> GetUAFBuildBlueprintClass(EMetaHumanQualityLevel QualityLevel);
};
```

**MetaHumanUAFDemo.cpp**
```cpp
#include "MetaHumanUAFDemo.h"

TSubclassOf<AActor> UMetaHumanUAFDemo::GetUAFBuildBlueprintClass(EMetaHumanQualityLevel QualityLevel)
{
    const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
    if (!Settings)
    {
        return nullptr;
    }

    const TSoftClassPtr<AActor>* BlueprintPtr = Settings->Blueprints.Find(QualityLevel);
    if (BlueprintPtr && !BlueprintPtr->IsNull())
    {
        // 加载软引用指向的类
        return BlueprintPtr->LoadSynchronous();
    }

    return nullptr;
}
```

## 模块依赖

此插件主要作为配置层，其模块 `MetaHumanCharacterUAFEditor` 依赖于其启用的上层插件所提供的功能模块。
使用者无需为自己的模块添加特殊的模块依赖，因为此插件的配置最终通过其依赖的 `UAF`， `MetaHumanCharacter` 等插件的核心模块生效。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-14 | `049dd5ce` | Rename UAnimNextRigVM* to UUAFRigVM* | 将 UAnimNextRigVM 相关类重命名为 UUAFRigVM，反映 UAF 命名空间更新。 |
| 2026-01-13 | `436f1414` | Rename UAnimNextComponent to UUAFComponent | 将 UAnimNextComponent 重命名为 UUAFComponent，跟进框架重命名。 |
| 2026-01-08 | `8e81a827` | Add UAF Asset Data structure to encapsulate an asset that can be used to generate a UAF graph or sys | 添加了 UAF Asset Data 结构，用于封装可生成 UAF 图表或系统的资产。 |
| 2026-01-07 | `7f65190a` | Rename UAnimNextModule to UUAFSystem | 将 UAnimNextModule 重命名为 UUAFSystem，统一命名前缀。 |
| 2025-09-29 | `e0a45858` | Fix for broken BP when Common folder is redirected when exporting a UAF MH | 修复了在导出 UAF MetaHuman 时，因 Common 文件夹重定向导致的蓝图损坏问题。 |

### 维护评价

**活跃维护**。此插件非常新（创建于 2025 年 9 月），并且在最近一个月内（2026 年 1 月）有多次提交，主要活动围绕其核心依赖 `UAF` 框架的重大重命名工作（从 AnimNext 到 UAF）。这表明它正处于快速开发和整合阶段，紧密跟随上游框架的演进。由于其 `IsExperimentalVersion` 为 `true`，API 和行为可能不稳定，但近期的更新证实其处于活跃开发中。

**推荐用于前沿开发或实验项目**，不推荐用于需要长期稳定支持的生产环境，除非你愿意跟随实验性 API 的变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF)
- [官方文档]() （无）
- [测试用例]() （无， 或位于上层 MetaHuman 插件测试目录中）