# Gameplay Tags Toolset

> Toolset for reading and managing gameplay tags via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayTagsToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameplayTagsToolset) | |

## 用途

这个插件为 Unreal Engine 的 AI 助手（AI Assistant）功能提供了一套专门用于操作 Gameplay Tags 系统的工具集。它通过 `UToolsetDefinition` 向 AI 工具注册表注册了一系列函数，使得 AI 助手能够查询、创建、修改和删除项目中的 Gameplay Tags。其核心目的是弥合 AI 助手与游戏标签管理系统之间的鸿沟，让 AI 能够理解并操作游戏逻辑中至关重要的标签数据。

## 使用场景

- **AI 辅助开发**：当你在使用 UE 的 AI 助手功能时，AI 需要查询、创建或修改 Gameplay Tags 来完成你的指令（例如：“帮我创建一个名为 `Enemy.Type.Boss` 的标签”）。
- **自动化标签管理**：通过 AI 助手批量处理标签的创建、重命名或清理工作，提高项目配置效率。

## 蓝图用法

此插件主要通过 `UFUNCTION(meta = (AICallable))` 暴露给 AI 系统，而非传统的蓝图节点。这些函数设计为由 AI 助手内部调用，但理论上也可以在蓝图中通过其静态函数形式调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListTags` | 列出项目中的所有标签，或指定父标签下的所有子标签。 | `UGameplayTagsToolset` |
| `GetTagInfo` | 获取指定标签的详细信息，包括注释、来源文件和直接子标签。 | `UGameplayTagsToolset` |
| `AddTag` | 向项目添加一个新的 Gameplay Tag。 | `UGameplayTagsToolset` |
| `RemoveTag` | 从项目中移除一个 Gameplay Tag。 | `UGameplayTagsToolset` |
| `RenameTag` | 重命名一个 Gameplay Tag，并更新项目中的所有引用。 | `UGameplayTagsToolset` |

### 使用示例（蓝图描述）

由于这些函数是静态的且主要为 AI 设计，在蓝图中直接使用的场景较少。一个理论上的用法是：在一个编辑器工具蓝图中，调用 `ListTags` 节点并传入空字符串，获取所有标签的字符串数组，然后遍历该数组，对每个标签调用 `GetTagInfo` 来获取其详细信息并进行处理。

## C++ 用法

### 头文件引入

```cpp
#include "GameplayTagsToolset/GameplayTagsToolset.h"
```

### 基本用法

从测试资产和函数签名推断的用法，用于在编辑器工具或自动化测试中操作标签。

```cpp
// 假设在某个编辑器工具或测试函数中
#include "GameplayTagsToolset/GameplayTagsToolset.h"

void ExampleUsage()
{
    // 1. 列出所有以 “Character.State” 开头的标签
    TArray<FString> StateTags = UGameplayTagsToolset::ListTags(TEXT("Character.State"));
    for (const FString& TagName : StateTags)
    {
        UE_LOG(LogTemp, Log, TEXT("Found State Tag: %s"), *TagName);
    }

    // 2. 获取特定标签的详细信息
    FGameplayTagInfo Info = UGameplayTagsToolset::GetTagInfo(TEXT("Character.State.Dead"));
    UE_LOG(LogTemp, Log, TEXT("Tag Comment: %s"), *Info.Comment);
    UE_LOG(LogTemp, Log, TEXT("Tag Source: %s"), *Info.Source);

    // 3. 添加一个新标签（需谨慎，通常由AI在获得用户确认后调用）
    UGameplayTagsToolset::AddTag(TEXT("Character.State.Invisible"), TEXT("Makes the character invisible."), TEXT(""));

    // 4. 重命名标签
    UGameplayTagsToolset::RenameTag(TEXT("Character.State.Invisible"), TEXT("Character.State.Stealth"));
}
```

### 进阶用法

结合 `FGameplayTagContainer` 和 `UGameplayTagTestAsset` 进行更复杂的标签查询和验证。

```cpp
#include "GameplayTagsToolset/Tests/GameplayTagToolsetTest.h"
#include "GameplayTagsToolset/GameplayTagsToolset.h"

void AdvancedExample()
{
    // 创建一个测试资产来持有标签容器
    UGameplayTagTestAsset* TestAsset = NewObject<UGameplayTagTestAsset>();

    // 假设通过某种方式（如AI工具）添加了标签到容器
    // TestAsset->Tags.AddTag(FGameplayTag::RequestGameplayTag(FName("Enemy.Type.Boss")));

    // 使用工具集函数来验证标签是否存在
    TArray<FString> AllEnemyTags = UGameplayTagsToolset::ListTags(TEXT("Enemy"));
    bool bBossTagExists = AllEnemyTags.Contains(TEXT("Enemy.Type.Boss"));

    if (bBossTagExists)
    {
        FGameplayTagInfo BossInfo = UGameplayTagsToolset::GetTagInfo(TEXT("Enemy.Type.Boss"));
        // ... 进行后续操作
    }
}
```

## Demo 示例

一个最小的编辑器模块示例，展示如何包含并调用 GameplayTagsToolset 的功能。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterConsoleCommands();
    void UnregisterConsoleCommands();
    void OnListAllTagsCommand(const TArray<FString>& Args);
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "GameplayTagsToolset/GameplayTagsToolset.h"
#include "HAL/IConsoleManager.h"

#define LOCTEXT_NAMESPACE "FMyEditorToolModule"

void FMyEditorToolModule::StartupModule()
{
    RegisterConsoleCommands();
}

void FMyEditorToolModule::ShutdownModule()
{
    UnregisterConsoleCommands();
}

void FMyEditorToolModule::RegisterConsoleCommands()
{
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("MyTool.ListAllTags"),
        TEXT("Lists all gameplay tags in the project."),
        FConsoleCommandDelegate::CreateRaw(this, &FMyEditorToolModule::OnListAllTagsCommand),
        ECVF_Default
    );
}

void FMyEditorToolModule::UnregisterConsoleCommands()
{
    IConsoleManager::Get().UnregisterConsoleObject(TEXT("MyTool.ListAllTags"));
}

void FMyEditorToolModule::OnListAllTagsCommand(const TArray<FString>& Args)
{
    // 调用 GameplayTagsToolset 的函数
    TArray<FString> AllTags = UGameplayTagsToolset::ListTags(TEXT(""));
    UE_LOG(LogTemp, Display, TEXT("--- All Gameplay Tags ---"));
    for (const FString& Tag : AllTags)
    {
        UE_LOG(LogTemp, Display, TEXT("  %s"), *Tag);
    }
    UE_LOG(LogTemp, Display, TEXT("--- Total: %d ---"), AllTags.Num());
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorToolModule, MyEditorTool)
```

## 模块依赖

从 `.uplugin` 和 `Build.cs` 分析，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和 AI 工具注册框架。 |
| `GameplayTagsEditor` | 提供编辑器内操作 Gameplay Tags 的底层功能（如修改 INI 文件）。 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 `8c911af5` [Backout] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **创建时间**：非常新（2026年4月创建），是 UE5 AI 功能链的一部分。
- **更新频率**：创建后一周内有多次提交，主要围绕 AI 工具定义机制的调整和测试修复，表明处于**活跃开发初期**。
- **维护状态**：**活跃维护中**。作为实验性 AI 工具集的一部分，其开发与 UE 的 AI 助手功能紧密相关。
- **已知限制**：作为实验性插件 (`IsExperimentalVersion=true`)，API 和功能可能发生变化。默认未启用 (`EnabledByDefault=false`)，需要手动在插件管理器中启用。
- **推荐使用**：仅推荐给需要深度集成或扩展 UE AI 助手功能的开发者。对于普通 Gameplay Tags 操作，应使用标准的 `GameplayTags` 和 `GameplayTagsEditor` 模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameplayTagsToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameplayTagsToolset/Source/GameplayTagsToolset/Private/GameplayTagsToolset/Tests)