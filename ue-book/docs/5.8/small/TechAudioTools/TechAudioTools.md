# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具箱 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、视图模型） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

该插件的核心功能是为音频参数在内部系统（如 MetaSound 节点）和用户界面（如自定义 Widget 或 Preset 控件）之间提供一套健壮、可配置的转换和映射框架。它主要解决以下问题：
1.  **单位转换与范围映射**：内部系统可能使用线性增益（`0.0 - 1.0`），而 UI 需要显示为分贝（`-60 dB - 6 dB`）；内部使用频率乘数（`0.5`），而 UI 可能显示为半音（`-12`）。`UTechAudioToolsFloatMapping` 类自动化了这种双向转换。
2.  **ViewModel 绑定**：通过 `UAudioComponentViewModel`，将 `UAudioComponent` 的实时播放状态（如播放、停止、淡入淡出）以一种响应式的方式（`FieldNotify`）暴露给 UI Widget，简化了基于 MVVM 架构的音频 UI 开发。
3.  **MetaSound 集成**：提供与 MetaSound 编辑器深度集成的工具，用于改善节点（如 Literal）的交互体验。

简而言之，该插件是构建高级音频工具、自定义音频控件或封装 MetaSound 预设的底层基础设施。

## 使用场景

-   你正在开发一个**音频混音工具或自定义音效控件**，需要在 UI 中使用分贝、半音等专业单位，而 MetaSound 内部使用线性值。
-   你正在为音频组件（`UAudioComponent`）创建一个**自定义的播放状态 UI**，希望使用数据绑定（MVVM）模式来实时更新播放、暂停、虚拟化等状态。
-   你正在扩展 **MetaSound 编辑器**，希望改善 Literal 节点或其它节点的参数输入/显示逻辑。
-   你需要一个统一的方案来管理游戏中所有音频参数（音量、音调、滤波器带宽等）的**内部值与显示值之间的映射规则**。

## 蓝图用法

### 核心节点

#### 映射操作 (`UTechAudioToolsFloatMapping`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SourceToDisplay` | 将内部系统使用的源值转换为适合在 UI 上显示的值。 | `UTechAudioToolsFloatMapping` |
| `DisplayToSource` | 将 UI 上编辑的显示值转换回内部系统可用的源值。 | `UTechAudioToolsFloatMapping` |
| `NormalizedToSource` | 将归一化（0-1）值转换为源范围内的实际值。 | `UTechAudioToolsFloatMapping` |
| `SourceToNormalized` | 将源范围内的实际值转换为归一化（0-1）值。 | `UTechAudioToolsFloatMapping` |
| `NormalizedToDisplay` | 将归一化（0-1）值转换为显示范围内的实际值。 | `UTechAudioToolsFloatMapping` |
| `DisplayToNormalized` | 将显示范围内的实际值转换为归一化（0-1）值。 | `UTechAudioToolsFloatMapping` |
| `GetUnits` | 获取指定端点（Source 或 Display）所使用的单位。 | `UTechAudioToolsFloatMapping` |

#### 视图模型操作 (`UAudioComponentViewModel`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAudioComponent` | 绑定一个音频组件实例到此视图模型，开始监听其状态变化。 | `UAudioComponentViewModel` |

### 使用示例（蓝图描述）

**示例 1：创建一个音量映射对象**
1.  创建一个 `UTechAudioToolsFloatMapping` 类的对象实例（例如，在 Actor 或 Widget 的变量中）。
2.  在对象的详细面板中，将 `Mapping Type` 设置为 `Volume`。
3.  设置 `Source Volume Units` 为 `Linear Gain`，`Display Volume Units` 为 `Decibels`。
4.  调整 `Display Decibel Range` 为你希望的 UI 范围（如 `-60` 到 `0`）。
5.  在蓝图图表中，将 MetaSound 输入的线性增益值（如 `0.5`）连接到 `SourceToDisplay` 节点，输出结果（如 `-6.02`）即可绑定到滑动条的值上。
6.  当用户拖动滑动条（显示分贝值）时，调用 `DisplayToSource` 将新值转换回线性增益，并传递给 MetaSound。

**示例 2：绑定音频组件状态到 UI**
1.  在你的 UI Widget 中，创建一个 `UAudioComponentViewModel` 类型的变量。
2.  当拥有音频组件的 Actor 准备好时，调用 `SetAudioComponent` 并传入该 Actor 的音频组件引用。
3.  在 Widget 的 `Construct` 或绑定逻辑中，将 `ViewModel` 的 `IsPlaying`、`PlayState` 等属性（带 `FieldNotify`）绑定到对应的 UI 元素（如按钮的文本、图片的可见性）上。
4.  当音频组件的播放状态改变时，UI 将自动更新。

## C++ 用法

### 头文件引入

```cpp
#include “TechAudioToolsFloatMapping.h”
#include “Viewmodels/AudioComponentViewModel.h”
```

### 基本用法

以下示例展示如何使用浮点映射进行单位转换。

```cpp
// 假设在某个类中有一个 UTechAudioToolsFloatMapping* 变量 VolumeMapping
// 并且它已经被正确配置（例如，Source为LinearGain, Display为Decibels）

// 1. 将内部线性增益转换为UI分贝值
float LinearGain = 0.5f;
float DisplayDecibels = VolumeMapping->SourceToDisplay(LinearGain);
// DisplayDecibels 可能约为 -6.02

// 2. 将用户在UI上设置的分贝值转换回内部线性增益
float NewDisplayDecibels = -12.0f;
float NewLinearGain = VolumeMapping->DisplayToSource(NewDisplayDecibels);
// NewLinearGain 可能约为 0.25
```

### 进阶用法

结合视图模型，构建一个响应式的音频组件监控器。

```cpp
// 在 Actor 的头文件 (.h) 中
UPROPERTY(BlueprintReadOnly, Category = “UI”)
TObjectPtr<UAudioComponentViewModel> AudioViewModel;

// 在 Actor 的初始化函数中 (.cpp)
AudioViewModel = NewObject<UAudioComponentViewModel>(this);
AudioViewModel->SetAudioComponent(MyAudioComponent); // MyAudioComponent 是 UAudioComponent*

// 现在可以在绑定的 Widget 中通过 AudioViewModel->IsPlaying() 等安全地访问状态。
// 当 AudioComponent 状态变化时，ViewModel 会通过 FieldNotify 通知绑定的 UI。
```

## Demo 示例

这是一个最小可编译示例，展示了如何自定义映射并使用视图模型。

**MyAudioTool.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “TechAudioToolsFloatMapping.h”
#include “Viewmodels/AudioComponentViewModel.h”
#include “MyAudioTool.generated.h”

UCLASS(BlueprintType)
class MYPROJECT_API UMyAudioTool : public UObject
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Instanced, Category = “Mapping”)
	TObjectPtr<UTechAudioToolsFloatMapping> VolumeMapping;

	UPROPERTY(BlueprintReadOnly, Category = “ViewModel”)
	TObjectPtr<UAudioComponentViewModel> ViewModel;

	UFUNCTION(BlueprintCallable, Category = “Tool”)
	void Initialize(UAudioComponent* InComponent)
	{
		VolumeMapping = NewObject<UTechAudioToolsFloatMapping>(this);
		VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
		VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
		VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;

		ViewModel = NewObject<UAudioComponentViewModel>(this);
		ViewModel->SetAudioComponent(InComponent);
	}

	UFUNCTION(BlueprintCallable, Category = “Tool”)
	float GetDisplayVolume(float InLinearGain) const
	{
		return VolumeMapping ? VolumeMapping->SourceToDisplay(InLinearGain) : InLinearGain;
	}

	UFUNCTION(BlueprintCallable, Category = “Tool”)
	float SetSourceVolumeFromDisplay(float InDecibels) const
	{
		return VolumeMapping ? VolumeMapping->DisplayToSource(InDecibels) : InDecibels;
	}
};
```

**MyAudioTool.cpp**
```cpp
#include “MyAudioTool.h”
// 无复杂逻辑，所有实现均在头文件中内联或委托给插件API。
```

## 模块依赖

该插件对 UE 核心模块的依赖较少，主要依赖其声明的插件依赖。

| 模块 | 用途 |
|---|---|
| `MetaSound` | 为 TechAudioToolsMetaSound 和 Editor 模块提供核心 MetaSound 功能和节点基类。 |
| `ModelViewViewModel` | 为 `UAudioComponentViewModel` 提供 MVVM 框架基类 `UMVVMViewModelBase`。 |
| `MetasoundEditor` | （TechAudioToolsMetaSoundEditor 模块依赖）提供 MetaSound 编辑器的集成接口和工具。 |

**说明**：你的项目或模块若需使用此插件（特别是 `TechAudioToolsMetaSound` 和 `TechAudioToolsMetaSoundEditor`），需在 `.Build.cs` 中添加对相应插件模块（`Metasound`, `ModelViewViewModel`, `MetasoundEditor`）的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | MetaSound：整合了引脚类型注册及相关编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了一个导致编译错误的提交。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | MetaSound：整合了引脚类型注册及相关编辑器行为。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为MetaSound的Literal视图模型添加了事务支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将“文档配置”重命名为“MetaSound(文档)模板”。 |

### 维护评价

-   **创建时间**：2025年4月，插件相对年轻。
-   **更新频率**：最近一个月内有多次提交，更新活跃。
-   **更新内容**：主要围绕 MetaSound 节点（尤其是 Literal）的交互改进和编辑器行为整合，表明正在积极开发和完善。
-   **实验性**：插件被标记为 `IsBetaVersion` 和 `IsExperimentalVersion`，且默认未安装（`Installed: false`），说明 API 和功能可能尚未稳定。
-   **推荐度**：**推荐尝试使用，但需谨慎**。该插件为解决特定的音频参数映射和 UI 绑定问题提供了专业的方案。由于其实验性状态，不建议在生产环境的核心功能中深度依赖，应做好未来 API 变更的准备。非常适合用于原型开发、内部工具或可控的实验性功能。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
-   [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/)（暂无专门文档）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools/Tests)（路径假设，需确认）