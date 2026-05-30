# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.

| 属性 | 值 |
|---|---|
| 中文名 | 空间音频插件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Spatialization` (Runtime), `SpatializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-25 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization) | |

## 用途

此插件提供了基础的音频空间化功能，核心是实现了基于**ITD (Interaural Time Difference，双耳时间差)** 的双耳空间化算法。它解决的主要问题是：为 UE5 项目提供一个开箱即用的、基于头部相关传输函数 (HRTF) 的精确空间音频解决方案，使开发者能够快速实现声音随声源和听者相对位置变化而产生逼真空间感的效果，特别适用于 VR/AR 等需要高沉浸感音频的场景。

它不仅仅是一个简单的声像器 (Panner)，而是通过资产化的方式管理空间化参数，提供了可定制的滤波器和混合设置。

## 使用场景

- **开发 VR 游戏或应用**：你需要精确的头部相关空间音频，让玩家能通过声音准确判断物体位置。
- **制作第一人称沉浸式体验**：例如恐怖游戏，需要环境音效从不同方向和距离传来的立体感。
- **实现空间音频叙事**：在对话或旁白中，利用声音位置变化来引导玩家注意力或增强剧情表现力。

## 蓝图用法

经过分析，`SpatializationEditor` 模块主要提供编辑器端的资产创建和设置功能，并未暴露 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。空间化的核心配置通过资产（如 `UITDSpatializationSourceSettings`）和音频组件属性来完成，这些操作主要在编辑器界面或通过 C++ 代码进行。

**核心配置节点（编辑器操作）**：
1.  **创建空间化设置资产**：在内容浏览器中右键，选择 `Audio > Advanced > Binaural Spatialization > ITD Source Spatialization Settings` 来创建资产。
2.  **应用到音频源**：在 `Audio Volume` 或 `Sound Source` 组件的细节面板中，将创建的空间化设置资产指定给相应的空间化类。

## C++ 用法

### 头文件引入

```cpp
#include "Spatialization.h" // 包含核心空间化模块
#include "ITDSpatializationSourceSettings.h" // 包含ITD空间化设置类
```

### 基本用法

创建和使用一个基础的 ITD 空间化设置。

```cpp
// 1. 创建空间化设置对象（通常在编辑器工具或游戏逻辑中初始化）
UITDSpatializationSourceSettings* SpatialSettings = NewObject<UITDSpatializationSourceSettings>();

// 2. 配置参数（例如，根据需求调整ITD相关的滤波器强度）
// 假设 SpatialSettings 有可配置的属性，如滤波器类型、强度等
// SpatialSettings->SetFilterType(EITDFilterType::SomeType);

// 3. 将设置应用到音频组件
// 假设您有一个 UAudioComponent* AudioComp
// AudioComp->SetSpatializationSettings(SpatialSettings); // 伪代码，具体API需参考Audio模块

// 在源码中，UAssetDefinition_ITDSpatializationSettings 定义了资产在编辑器中的显示方式（如名称、颜色、分类）。
// 而 UITDSpatializationSettingsFactory 则负责在编辑器中通过菜单创建新的资产实例。
```

### 进阶用法

结合源码结构，进阶使用通常涉及对 `UITDSpatializationSourceSettings` 资产的深度定制，以及将其集成到更复杂的音频子系统中。

```cpp
// 1. 自定义空间化设置（通过继承或组合）
// 您可能需要子类化 UITDSpatializationSourceSettings 以实现自定义的滤波逻辑。

// 2. 在音频处理管线中使用
// 在引擎的音频渲染线程或音频处理回调中，读取空间化设置的数据，对音频信号进行实时滤波处理。
// 这通常涉及到对 FAuditionEffect 或类似音频处理节点的实现。

// 3. 动态切换空间化配置
// 根据游戏状态（如进入水下、室内/室外切换）动态更换不同的空间化设置资产。
```

## Demo 示例

以下是一个展示如何在 C++ 中定义一个简单的类来管理 ITD 空间化设置的最小示例。

**MySpatialAudioManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ITDSpatializationSourceSettings.h"
#include "MySpatialAudioManager.generated.h"

UCLASS()
class MYPROJECT_API AMySpatialAudioManager : public AActor
{
	GENERATED_BODY()

public:
	AMySpatialAudioManager();

protected:
	virtual void BeginPlay() override;

	// 引用或直接创建一个空间化设置资产
	UPROPERTY(EditAnywhere, Category = "Audio|Spatialization")
	UITDSpatializationSourceSettings* MySpatialSettings;

public:
	// 一个函数，演示如何获取并可能应用设置
	UFUNCTION(BlueprintCallable, Category = "Audio|Spatialization")
	UITDSpatializationSourceSettings* GetConfiguredSpatialSettings() const;
};
```

**MySpatialAudioManager.cpp**
```cpp
#include "MySpatialAudioManager.h"
#include "UObject/ConstructorHelpers.h"

AMySpatialAudioManager::AMySpatialAudioManager()
{
	PrimaryActorTick.bCanEverTick = false;

	// 在构造函数中尝试从内容资产路径加载默认设置
	static ConstructorHelpers::FObjectFinder<UITDSpatializationSourceSettings> SettingsAsset(TEXT("/Game/Audio/ITD_Spatialization_Default"));
	if (SettingsAsset.Succeeded())
	{
		MySpatialSettings = SettingsAsset.Object;
	}
	else
	{
		// 如果找不到资产，则创建一个临时对象
		MySpatialSettings = NewObject<UITDSpatializationSourceSettings>(this, TEXT("DynamicSpatialSettings"));
	}
}

void AMySpatialAudioManager::BeginPlay()
{
	Super::BeginPlay();

	if (MySpatialSettings)
	{
		// 在这里，可以将 MySpatialSettings 应用到需要空间化的音频源上
		// 例如，遍历场景中的音频组件并设置
		UE_LOG(LogTemp, Log, TEXT("Spatialization Settings Loaded: %s"), *MySpatialSettings->GetName());
	}
}

UITDSpatializationSourceSettings* AMySpatialAudioManager::GetConfiguredSpatialSettings() const
{
	return MySpatialSettings;
}
```

## 模块依赖

**Spatialization (Runtime) 模块**：
此模块是核心运行时逻辑。从其构建配置推断，它依赖于 UE 的核心音频处理模块，以实现空间化算法。作为插件的主模块，它为 `SpatializationEditor` 模块提供基础类。

**SpatializationEditor (Editor) 模块**：
此模块仅在编辑器中加载，提供了创建和编辑 `UITDSpatializationSourceSettings` 资产所需的工厂类 (`UITDSpatializationSettingsFactory`) 和资产定义 (`UAssetDefinition_ITDSpatializationSettings`)。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中，将“Audio”类别下的项目整合为新的子菜单。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，属于引擎代码风格现代化的批量更新。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 统一添加了 `dllexport/dllimport` 宏，是引擎构建系统（DLL导出）的通用性更新。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 对引擎插件目录结构的通用性维护提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了插件内可能存在的供应商链接为 HTTPS 安全协议。 |

### 维护评价

**综合评价**：
该插件创建于 2019 年初，距今已超过 6 年，属于**老古董**级别。从近期的 git 历史看，最近的实质性功能更新（非通用引擎适配）可追溯到很久以前。近两次更新主要是编辑器菜单调整和通用代码规范修改，**核心音频空间化算法本身已非常稳定，多年未有变动**。

这表明该插件的功能已基本定型，处于 **“维护中”** 状态：不再添加新特性，但会跟随引擎主分支进行必要的兼容性维护和代码规范更新。

**推荐使用**：如果你需要一个稳定的、基于ITD的基础双耳空间化方案，并且不需要最新的实验性音频特性，这个插件是一个可靠的选择。由于其长期存在和稳定性，遇到的问题和解决方案也比较容易找到。然而，对于更复杂或更新的空间音频需求（如基于物理的音频、新一代HRTF算法），可能需要查看其他更活跃的音频插件或引擎内置的新系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization)
- [官方文档]() （无）