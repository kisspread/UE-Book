# ConfigSettingsToolset

> Toolset for listing, inspecting, and editing Config Settings sections via the AI Toolset Registry.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 配置设置工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConfigSettingsToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset) | |

## 用途

`ConfigSettingsToolset` 是一个面向 AI 工具链（AI Toolset Registry）的编辑器插件，它提供了一组静态函数，允许程序化地枚举和修改引擎与项目级别的配置设置（即 `Editor Preferences` 和 `Project Settings` 中的条目）。其核心目标是为自动化工具（如 AI 代理）提供一个结构化的接口，使其能够理解、查询和修改编辑器的配置，而无需通过 UI。

## 使用场景

- **自动化配置管理**：在 CI/CD 流水线或自动化测试脚本中，需要程序化地读取或修改项目设置（例如，设置默认地图、调整渲染参数）。
- **AI 辅助配置**：开发 AI 驱动的工具或助手，使其能够理解当前项目的配置状态，并根据上下文提出或应用配置更改。
- **配置检查与诊断**：快速列出和检查特定类别下的所有设置项及其当前值，用于调试或生成配置报告。

## 蓝图用法

此插件的核心功能通过 `UFUNCTION(meta = (AICallable))` 暴露，主要设计给 AI 工具注册表（Toolset Registry）调用，**未标记为 `BlueprintCallable`，因此不能直接在蓝图中作为节点调用**。其使用主要通过 C++ 代码或与 Toolset Registry 的集成来实现。

## C++ 用法

### 头文件引入

```cpp
#include "ConfigSettingsToolset.h"
```

### 基本用法

该插件提供了一系列静态函数，用于发现和操作配置设置。以下示例展示了如何使用它来查询项目设置中的内容。

*来源文件: `Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset/Source/ConfigSettingsToolset/Private/ConfigSettingsToolset.h`*

```cpp
// 1. 列出所有可用的设置容器（如 “Editor”, “Project”）
TArray<FString> Containers = UConfigSettingsToolset::ListContainers();
UE_LOG(LogTemp, Log, TEXT("Available containers: %s"), *FString::Join(Containers, TEXT(", ")));

// 2. 列出 “Project” 容器下的所有类别（如 “Engine”, “Input”）
TArray<FString> Categories = UConfigSettingsToolset::ListCategories(TEXT("Project"));
UE_LOG(LogTemp, Log, TEXT("Categories in Project: %s"), *FString::Join(Categories, TEXT(", ")));

// 3. 获取特定设置部分的属性模式（Schema）
FString SchemaJson = UConfigSettingsToolset::GetSectionSchema(TEXT("Project"), TEXT("Engine"), TEXT("General"));
if (!SchemaJson.IsEmpty())
{
    UE_LOG(LogTemp, Log, TEXT("Schema for Project->Engine->General: %s"), *SchemaJson);
}

// 4. 读取特定属性的当前值
TArray<FString> PropertiesToRead = {TEXT("bUseFixedFrameRate"), TEXT("FixedFrameRate")};
FString ValuesJson = UConfigSettingsToolset::GetSectionPropertyValues(
    TEXT("Project"), TEXT("Engine"), TEXT("General"), PropertiesToRead);
UE_LOG(LogTemp, Log, TEXT("Current values: %s"), *ValuesJson);

// 5. 设置属性值
TMap<FString, FString> PropertiesToSet;
PropertiesToSet.Add(TEXT("bUseFixedFrameRate"), TEXT("true"));
PropertiesToSet.Add(TEXT("FixedFrameRate"), TEXT("30.0"));
bool bSuccess = UConfigSettingsToolset::SetSectionPropertyValues(
    TEXT("Project"), TEXT("Engine"), TEXT("General"), PropertiesToSet);
UE_LOG(LogTemp, Log, TEXT("Setting properties: %s"), bSuccess ? TEXT("Success") : TEXT("Failed"));
```

### 进阶用法

结合测试用例中的设置对象，可以创建自定义的可配置项，并通过本工具集进行管理。这需要先将自定义设置对象注册到设置系统中。

*来源文件: `Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset/Source/ConfigSettingsToolset/Private/Tests/ConfigSettingsToolsetTestObjects.h`*

```cpp
// 定义自定义配置类 (通常在模块的 .h 文件中)
UCLASS(config=MyGameConfig, defaultconfig)
class UMyGameSettings : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(config, EditAnywhere, Category = "Gameplay")
    float DifficultyScale = 1.0f;
    UPROPERTY(config, EditAnywhere, Category = "Gameplay")
    bool bShowTutorials = true;
};
```
在编辑器启动时（例如，在模块的 `StartupModule` 中），需要将此设置类注册到 `ISettingsModule` 中。之后，它便可以通过 `UConfigSettingsToolset` 的接口进行查询和修改。

## Demo 示例

一个展示如何定义可配置类并使用工具集查询其信息的最小示例。

**MyConfigurableSettings.h**
```cpp
#pragma once
#include "UObject/Object.h"
#include "MyConfigurableSettings.generated.h"

UCLASS(config=MyGameSettings, defaultconfig)
class UMyConfigurableSettings : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(config, EditAnywhere, Category = "Graphics")
    int32 TextureQuality = 2;
    UPROPERTY(config, EditAnywhere, Category = "Graphics")
    bool bEnableVSync = true;
};
```

**ConfigDemo.cpp (示例代码片段)**
```cpp
#include "MyConfigurableSettings.h"
#include "ConfigSettingsToolset.h"
#include "ISettingsModule.h"

void RegisterMySettings()
{
    // 假设 ISettingsModule* SettingsModule 已获取
    SettingsModule->RegisterSettings("Project", "MyGame", "Graphics",
        FText::FromString("Graphics Settings"),
        FText::FromString("My custom graphics settings"),
        GetMutableDefault<UMyConfigurableSettings>()
    );
}

void QueryMySettings()
{
    // 使用 ConfigSettingsToolset 查询我们刚注册的设置
    TArray<FString> Sections = UConfigSettingsToolset::ListSections(TEXT("Project"), TEXT("MyGame"));
    UE_LOG(LogTemp, Log, TEXT("Found sections: %s"), *FString::Join(Sections, TEXT(", ")));

    if (Sections.Contains(TEXT("Graphics")))
    {
        FString Values = UConfigSettingsToolset::GetSectionPropertyValues(
            TEXT("Project"), TEXT("MyGame"), TEXT("Graphics"),
            {TEXT("TextureQuality"), TEXT("bEnableVSync")}
        );
        UE_LOG(LogTemp, Log, TEXT("Graphics Settings Values: %s"), *Values);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 插件功能的基础，`UToolsetDefinition` 的父类定义于此。 |
| `Settings` | (隐含) 用于访问 `ISettingsModule` 和 `ISettingsSection`，是操作配置系统的核心。 |

## 维护状态

### 近期更新

```
- 2026-05-14 02299b89 [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties
- 2026-05-13 978a5c16 [Backout] - CL53875137
- 2026-05-13 e58befb6 [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties
- 2026-05-12 4c45fb27 [ConfigSettingsToolset] Fix round-trip test for read-only config on Horde
- 2026-05-12 b0a44cc5 Add ConfigSettingsToolset plugin
```

### 维护评价

- **创建时间**: 2026-05-12，距今非常近。
- **最近更新**: 最近一次更新在2天前(2026-05-14)，且是修复核心功能（容器变更通知）的提交，表明该插件处于**积极开发和调试阶段**。
- **状态**: 标记为 `IsExperimentalVersion=true`，说明这是一个实验性功能，API 和行为可能发生变化。
- **建议**: 虽然功能明确且更新活跃，但由于其“实验性”状态，**不建议在需要高度稳定性的生产项目中使用**。它非常适合用于工具链开发、内部测试或技术预研。需密切关注其 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset)
- [官方文档](https://docs.unrealengine.com)（该插件无专属文档，可参考通用设置系统文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset/Source/ConfigSettingsToolset/Private/Tests)