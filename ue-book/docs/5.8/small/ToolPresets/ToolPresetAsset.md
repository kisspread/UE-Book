# Tool Presets

> Adds support for saving and loading tool settings as presets.

| 属性 | 值 |
|---|---|
| 中文名 | 工具预设 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ToolPresetAsset` (Editor), `ToolPresetEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets) | |

## 用途

ToolPresets 插件提供了一套框架，用于将交互式工具（如建模工具）的当前配置保存为可重用的预设资产，并在需要时加载这些预设，从而恢复工具的状态。这解决了在重复性工作流中反复配置相同工具参数的效率问题。预设以资产的形式存在，可以跨会话、跨项目共享。

## 使用场景

- 你是一位3D艺术家，经常使用带有特定参数（如笔刷大小、强度、材质设置）的建模工具进行雕刻。你可以将这些参数保存为一个名为“皮肤毛孔”的预设，下次工作时快速加载，无需手动调整。
- 你在设计一个系统，需要测试多种不同的工具参数组合（如不同的曲线生成设置）。可以将每种组合保存为不同的预设，方便快速切换和对比。
- 你的团队需要统一某些工具的配置标准。可以将标准配置保存为预设资产并共享给团队成员。

## 蓝图用法

预设操作主要通过 `UToolPresetAssetSubsystem` 子系统进行管理，预设数据本身存储在 `UInteractiveToolsPresetCollectionAsset` 资产中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Default Collection` | 获取编辑器的默认预设集合资产。如果不存在，子系统会初始化一个。 | `UToolPresetAssetSubsystem` |
| `Save Default Collection` | 将默认的预设集合资产保存到磁盘。返回是否成功。 | `UToolPresetAssetSubsystem` |

### 数据结构说明（蓝图类型）

- **`FInteractiveToolPresetDefinition`**: 代表一个具体的预设。包含序列化的属性字符串(`StoredProperties`)、显示名称(`Label`)和工具提示(`Tooltip`)。
- **`FInteractiveToolPresetStore`**: 代表一个工具的预设存储，内含一个命名的预设数组(`NamedPresets`)、工具的显示名称(`ToolLabel`)和图标(`ToolIcon`)。
- **`UInteractiveToolsPresetCollectionAsset`**: 顶层资产类，使用一个 `TMap<FString, FInteractiveToolPresetStore>` (`PerToolPresets`) 来按工具名存储其所有预设。

### 使用示例（蓝图描述）

1.  **获取子系统**: 使用 `Get Editor Subsystem` 节点，类选择 `UToolPresetAssetSubsystem`，获取其实例。
2.  **获取预设集合**: 从子系统实例调用 `Get Default Collection` 节点，得到一个 `UInteractiveToolsPresetCollectionAsset` 对象。
3.  **读取/写入预设**: 通过返回的资产对象，访问其 `PerToolPresets` 映射。可以使用工具名（`FString`）作为键来访问对应的 `FInteractiveToolPresetStore`，进而操作其 `NamedPresets` 数组。
4.  **保存**: 对预设集合进行修改后，通过子系统实例调用 `Save Default Collection` 节点来持久化更改。

## C++ 用法

### 头文件引入

```cpp
#include "ToolPresetAssetSubsystem.h"
#include "ToolPresetAsset.h"
```

### 基本用法

从子系统和资产类的结构可以推断出以下用法模式。

```cpp
// 1. 获取工具预设子系统
UToolPresetAssetSubsystem* PresetSubsystem = GEditor->GetEditorSubsystem<UToolPresetAssetSubsystem>();
if (!PresetSubsystem) return;

// 2. 获取默认的预设集合资产
UInteractiveToolsPresetCollectionAsset* PresetCollection = PresetSubsystem->GetDefaultCollection();
if (!PresetCollection) return;

// 3. 根据工具名查找或创建其预设存储
const FString ToolName = TEXT("MySpecialTool");
FInteractiveToolPresetStore* ToolStore = PresetCollection->PerToolPresets.Find(ToolName);
if (!ToolStore)
{
    // 如果不存在，可能需要先初始化（具体实现依赖于插件内部逻辑）
    ToolStore = &PresetCollection->PerToolPresets.Add(ToolName);
    ToolStore->ToolLabel = FText::FromString(ToolName);
    // ... 设置ToolIcon等
}

// 4. 创建一个新的预设定义
FInteractiveToolPresetDefinition NewPreset;
NewPreset.Label = TEXT("MyPreset");
NewPreset.Tooltip = TEXT("A preset for my tool.");

// 假设有一个当前工具属性对象数组需要序列化
TArray<UObject*> CurrentToolProperties = ... ; // 从活动工具中获取
NewPreset.SetStoredPropertyData(CurrentToolProperties); // 序列化属性到字符串

// 5. 将预设添加到存储中
ToolStore->NamedPresets.Add(NewPreset);

// 6. 保存整个预设集合
PresetSubsystem->SaveDefaultCollection();
```
*(此示例基于公开的API结构推断，展示了典型的工作流程)*

## Demo 示例

以下是一个最小化的C++类，演示如何获取预设子系统并访问默认集合。

```cpp
// MyPresetDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPresetDemoActor.generated.h"

UCLASS()
class AMyPresetDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyPresetDemoActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

	UFUNCTION(BlueprintCallable, Category="ToolPresets")
	void PrintDefaultPresetCollectionInfo();
};

// MyPresetDemoActor.cpp
#include "MyPresetDemoActor.h"
#include "ToolPresetAssetSubsystem.h"
#include "ToolPresetAsset.h"

AMyPresetDemoActor::AMyPresetDemoActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMyPresetDemoActor::BeginPlay()
{
	Super::BeginPlay();
}

void AMyPresetDemoActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AMyPresetDemoActor::PrintDefaultPresetCollectionInfo()
{
	// 此功能只能在编辑器中运行，因为子系统是编辑器子系统。
#if WITH_EDITOR
	UToolPresetAssetSubsystem* PresetSubsystem = GEditor->GetEditorSubsystem<UToolPresetAssetSubsystem>();
	if (PresetSubsystem)
	{
		UInteractiveToolsPresetCollectionAsset* Collection = PresetSubsystem->GetDefaultCollection();
		if (Collection)
		{
			UE_LOG(LogTemp, Log, TEXT("Default Preset Collection Label: %s"), *Collection->CollectionLabel.ToString());
			UE_LOG(LogTemp, Log, TEXT("Number of tools with presets: %d"), Collection->PerToolPresets.Num());
			for (const auto& Pair : Collection->PerToolPresets)
			{
				UE_LOG(LogTemp, Log, TEXT("  Tool: %s, Number of presets: %d"), *Pair.Key, Pair.Value.NamedPresets.Num());
			}
		}
	}
#endif
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 提供交互工具和属性序列化的基础框架（`UInteractiveToolsPresetCollectionAsset` 基于 `UEditorConfigBase`）。 |
| `ModelingToolsEditorMode` | 插件的核心依赖者，该模式使用此预设功能来管理其工具设置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以支持新的字符串类型，可能为性能优化做准备。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 在内容浏览器的“添加”菜单中调整了分类，可能影响预设资产的创建入口。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 修复内存问题，移除了JSON对象中的重复字符串，属于稳定性改进。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 对上一次的提交进行修正，修复了错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了某个更改（CL51314860），说明之前的一次提交引入了问题。 |

### 维护评价

ToolPresets 插件自创建以来约2年，仍处于 **实验性** 阶段。从近期提交记录看，它仍然 **活跃维护**，但主要活动集中在 **底层基础设施的重构和bug修复**（如字符串内存管理、JSON处理），而非功能添加。最后的实质性功能提交可追溯至首次提交。

- **优点**: 核心框架存在，有明确的用途，仍在更新维护。
- **风险与限制**: 实验性状态意味着API和功能设计可能不稳定。目前的代码注释中提到，当前数据结构是临时的，未来可能会添加更多辅助方法（添加、删除、重命名、保存、检索预设）。`ENABLE_PRESETS` CVAR 表明其UX可能需要手动开启。
- **推荐使用**: 对于 **探索性项目** 或需要自定义扩展UE建模工具工作流的开发者，值得一试。对于生产项目，需谨慎评估其实验性标签带来的潜在不稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/tool-presets-overview)（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets/Tests)（暂未在路径中发现）