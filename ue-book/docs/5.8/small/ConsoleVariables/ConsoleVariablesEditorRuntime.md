# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.

| 属性 | 值 |
|---|---|
| 中文名 | 控制台变量编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、运行时资产类） |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-08-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途

`ConsoleVariablesEditor` 是一个编辑器工具插件，它提供了一个专用的 Slate 面板（即“控制台变量编辑器”窗口）来管理和应用控制台变量（Cvars）。它的核心功能是将一组常用的控制台变量及其值保存为可复用的资产（`UConsoleVariablesAsset`）。这使得开发者和美术人员能够快速地在不同的调试配置、环境预设或虚拟制作场景之间切换，而无需每次手动输入一长串控制台命令。它解决了在复杂项目中（如虚拟制作管线）需要频繁、批量切换大量控制台变量状态效率低下的问题。

## 使用场景

- **虚拟制作/场景预设**：在虚拟制作中，你需要为不同的场景（如白天、夜晚、雨天）快速切换一整套环境、渲染和后处理相关的控制台变量。使用此插件，可以将每个预设保存为一个资产，并一键应用。
- **团队共享调试配置**：团队中的不同成员（程序、美术、技术美术）需要共享特定的调试或性能测试配置。通过将这些配置保存为插件的资产文件，可以方便地提交到版本控制系统中共享。
- **批量管理控制台变量**：当你需要同时调整数十个相互关联的控制台变量（如 LOD 设置、材质质量、物理模拟参数）时，手动输入非常繁琐。此插件允许你将它们作为一个集合进行管理、执行和导出。

## 蓝图用法

核心资产类 `UConsoleVariablesAsset` 提供了丰富的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Variable Collection Description` | 为此变量集合设置一个描述性文本 | `UConsoleVariablesAsset` |
| `Get Saved Commands` | 获取资产中保存的原始变量数据列表 | `UConsoleVariablesAsset` |
| `Get Saved Commands As String Array` | 将保存的命令转换为字符串数组。可选参数`bOnlyIncludeChecked`控制是否只包含UI中勾选的项。 | `UConsoleVariablesAsset` |
| `Get Saved Commands As Comma Separated String` | 将保存的命令转换为逗号分隔的字符串，便于传递给命令行参数。 | `UConsoleVariablesAsset` |
| `Execute Saved Commands` | 执行资产中保存的所有命令。这是应用预设的核心节点。 | `UConsoleVariablesAsset` |
| `Replace Saved Commands` | 用新的数据完全替换资产内已保存的数据。 | `UConsoleVariablesAsset` |
| `Find Saved Data By Command String` | 根据变量名查找对应的保存数据。 | `UConsoleVariablesAsset` |
| `Add Or Set Console Object Saved Data` | 添加一个新的变量记录，或更新已存在的同名变量记录。 | `UConsoleVariablesAsset` |
| `Remove Console Variable` | 根据变量名移除一条记录。 | `UConsoleVariablesAsset` |
| `Copy From` / `Add From` | 从另一个`UConsoleVariablesAsset`资产复制或合并变量列表。 | `UConsoleVariablesAsset` |

### 使用示例（蓝图描述）

1.  **创建并应用一个预设**：
    *   使用`Construct Object from Class`节点创建一个`UConsoleVariablesAsset`对象。
    *   调用`Add Or Set Console Object Saved Data`节点，构建一个`FConsoleVariablesEditorAssetSaveData`结构体（设置`CommandName`如`r.DefaultFeature.AntiAliasing`，`CommandValueAsString`如`2`），并添加到资产中。重复此过程添加所有需要的变量。
    *   调用`Execute Saved Commands`节点，将当前资产中的所有变量应用到游戏中。

2.  **保存和加载预设资产**：
    *   在编辑器中，右键内容浏览器 -> 虚拟制作 -> 控制台变量资产，可以创建资产文件。
    *   打开“控制台变量编辑器”窗口（菜单栏 -> 窗口 -> 控制台变量），在此UI中勾选、修改变量，并将当前状态保存到你创建的资产文件中。
    *   在蓝图中，可以通过`Load Asset`节点加载这个资产文件，然后获取其`UConsoleVariablesAsset`对象引用，再使用上述节点进行操作。

## C++ 用法

### 头文件引入

```cpp
#include "ConsoleVariablesAsset.h"
```

### 基本用法

```cpp
// 在游戏代码或工具中创建一个控制台变量集合资产
UConsoleVariablesAsset* MyCVarPreset = NewObject<UConsoleVariablesAsset>();

// 设置描述
MyCVarPreset->SetVariableCollectionDescription(TEXT("Performance Test Preset"));

// 添加一个控制台变量到资产中
FConsoleVariablesEditorAssetSaveData NewCVarData;
NewCVarData.CommandName = TEXT("r.Shadow.CSM.MaxCascades");
NewCVarData.CommandValueAsString = TEXT("1"); // 设置为低配
NewCVarData.CheckedState = ECheckBoxState::Checked; // 默认启用
MyCVarPreset->AddOrSetConsoleObjectSavedData(NewCVarData);

// 添加另一个变量
FConsoleVariablesEditorAssetSaveData AnotherCVar;
AnotherCVar.CommandName = TEXT("foliage.LODDistanceScale");
AnotherCVar.CommandValueAsString = TEXT("0.5");
MyCVarPreset->AddOrSetConsoleObjectSavedData(AnotherCVar);

// 执行这个预设中的所有命令
MyCVarPreset->ExecuteSavedCommands(GetWorld());

// 获取命令列表，用于日志输出或其他处理
TArray<FString> CommandList = MyCVarPreset->GetSavedCommandsAsStringArray(true);
for (const FString& Cmd : CommandList)
{
    UE_LOG(LogTemp, Log, TEXT("CVar Preset Command: %s"), *Cmd);
}
```

### 进阶用法

`UConsoleVariablesAsset` 实现了 `IMovieSceneConsoleVariableTrackInterface`，这意味着它可以无缝集成到 Sequencer 中。你可以在 Sequencer 轨道上添加一个控制台变量轨道，并将你的 `UConsoleVariablesAsset` 资产指定给它，从而在过场动画播放过程中自动应用和恢复控制台变量设置。这是虚拟制作中动态调整渲染设置的关键功能。

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在游戏模块中创建一个简单的控制台变量预设管理器。

```cpp
// MyCVarPresetManager.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ConsoleVariablesAsset.h"
#include "MyCVarPresetManager.generated.h"

UCLASS()
class UMyCVarPresetManager : public UObject
{
	GENERATED_BODY()

public:
	// 初始化一个默认的性能预设
	void InitDefaultPerformancePreset();

	// 执行预设
	void ApplyPreset();

private:
	UPROPERTY()
	TObjectPtr<UConsoleVariablesAsset> PerformancePreset;
};
```

```cpp
// MyCVarPresetManager.cpp
#include "MyCVarPresetManager.h"

void UMyCVarPresetManager::InitDefaultPerformancePreset()
{
	PerformancePreset = NewObject<UConsoleVariablesAsset>(this);
	PerformancePreset->SetVariableCollectionDescription(TEXT("Default Performance Preset"));

	// 添加阴影相关设置
	FConsoleVariablesEditorAssetSaveData ShadowQuality;
	ShadowQuality.CommandName = TEXT("sg.ShadowQuality");
	ShadowQuality.CommandValueAsString = TEXT("1"); // Low
	ShadowQuality.CheckedState = ECheckBoxState::Checked;
	PerformancePreset->AddOrSetConsoleObjectSavedData(ShadowQuality);

	// 添加抗锯齿设置
	FConsoleVariablesEditorAssetSaveData AntiAliasing;
	AntiAliasing.CommandName = TEXT("r.DefaultFeature.AntiAliasing");
	AntiAliasing.CommandValueAsString = TEXT("0"); // None
	AntiAliasing.CheckedState = ECheckBoxState::Checked;
	PerformancePreset->AddOrSetConsoleObjectSavedData(AntiAliasing);

	UE_LOG(LogTemp, Log, TEXT("Initialized default performance CVar preset."));
}

void UMyCVarPresetManager::ApplyPreset()
{
	if (PerformancePreset)
	{
		PerformancePreset->ExecuteSavedCommands(GetWorld());
		UE_LOG(LogTemp, Log, TEXT("Applied performance CVar preset: %s"), *PerformancePreset->GetVariableCollectionDescription());
	}
}
```

## 模块依赖

此插件的运行时模块依赖较为标准，但其编辑器部分依赖于多用户编辑（Concert）框架，这是其支持团队协作特性的基础。

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | 用于支持多用户编辑会话中的客户端同步 |
| `ConcertSyncCore` | 提供多用户编辑的核心同步功能 |
| `ConcertMain` | 多用户编辑的主要模块 |
| `ConcertSharedSlate` | 提供用于多用户编辑的共享 Slate UI 组件 |
| `MovieScene` | 用于与 Sequencer 集成，实现控制台变量轨道 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将此插件相关的虚拟制作资产迁移至新的资产类别，优化组织结构。 |
| 2026-05-12 | `de91208d` | CVAR Editor - Copy/Paste Cosmetic Fixes | 修复了控制台变量编辑器中复制/粘贴功能的显示问题。 |
| 2026-04-22 | `0f1a8af2` | Copy / Paste support for Console Variable Editor | 为控制台变量编辑器新增了复制和粘贴变量的功能。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 调整了内容浏览器中创建此资产类型的菜单入口。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将模块内的日志宏更新为新的 `UE_LOGF` 格式。 |

### 维护评价

该插件创建于 2020 年，已存在约 6 年，属于一个成熟工具。从近期的提交记录来看（截至 2026 年 5 月），它仍在被**积极维护和改进**。最新的更新不仅修复了 UI 问题（`de91208d`），还增加了重要的新功能（复制粘贴 `0f1a8af2`），并随着引擎的整体演进进行适配（资产分类迁移 `b046e53d`，日志宏更新 `35e60df1`）。

**综合评价**：这是一个稳定且仍在活跃开发的官方插件。它功能明确，是虚拟制作和高级调试工作流中的**推荐工具**。其与 Sequencer 的集成和多用户编辑支持进一步增强了它的实用价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor)
- [官方文档]() （未在 .uplugin 中提供）