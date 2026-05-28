# MVVM Toolset

> Toolset for creating and managing MVVM data via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | MVVM工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MVVMToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MVVMToolset) | |

## 用途

MVVMToolset 是一个实验性编辑器插件，它作为一个自动化工具集，旨在简化和加速 Unreal Engine 中基于 MVVM（Model-View-ViewModel）架构的用户界面开发工作流。其核心功能是通过提供一系列工具函数，允许开发者（或 AI 代理）以编程方式或通过蓝图来创建、修改和配置 MVVM 数据资产，特别是 `ViewModel` 蓝图，以及管理 `WidgetBlueprint` 中的视图绑定（View Binding）。它解决了手动在编辑器中进行 MVVM 配置可能较为繁琐的问题，为脚本化或自动化 UI 开发流程提供了支持。

## 使用场景

- 你需要为一个大型 UI 系统批量创建多个具有相似结构的 `ViewModel` 蓝图资产。
- 你希望通过脚本或蓝图自动化地为 `UserWidget` 添加 `ViewModel` 并配置属性绑定，而不是在编辑器界面中逐个操作。
- 你在开发一个工具或 AI 系统，该系统需要能够动态生成和修改 MVVM 架构的 UI 资产。

## 蓝图用法

该插件的核心是一个名为 `UMVVMToolset` 的隐藏工具集类，其中所有公开函数均标记为 `BlueprintCallable` 并带有 `Experimental` 和 `AICallable` 元数据，表明它们主要设计供工具链或 AI 调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateViewModel` | 在指定路径创建一个新的 ViewModel 蓝图资产 | `UMVVMToolset` |
| `AddViewModelProperty` | 向一个现有的 ViewModel 蓝图添加一个新属性 | `UMVVMToolset` |
| `ListViewModels` | 列出指定路径下的所有 ViewModel 资产 | `UMVVMToolset` |
| `ListWidgetViewModels` | 列出一个 WidgetBlueprint 中已使用的所有 ViewModel 类 | `UMVVMToolset` |
| `AddViewModelToWidget` | 将一个 ViewModel 类添加到一个 WidgetBlueprint 中 | `UMVVMToolset` |
| `ListWidgetViewBindings` | 列出一个 WidgetBlueprint 中的所有视图绑定 | `UMVVMToolset` |
| `CreateViewBinding` | 创建一个从源属性到目标属性的视图绑定 | `UMVVMToolset` |
| `RemoveWidgetViewBinding` | 根据 ID 移除一个视图绑定 | `UMVVMToolset` |
| `ListConversionFunctions` | 列出可用于绑定的类型转换函数 | `UMVVMToolset` |

### 使用示例（蓝图描述）

1.  **创建一个新的 ViewModel**：
    - 使用 `CreateViewModel` 节点，输入你想要的 ViewModel 名称（例如 `WBP_MainMenu_ViewModel`）、一个资产路径（例如 `/Game/UI/ViewModels/`）以及父类（例如 `UMVVMViewModelBase`）。执行后，一个新的 ViewModel 蓝图将被创建。
2.  **为 ViewModel 添加属性**：
    - 先获取一个 `UBlueprint` 对象（例如通过 `LoadAsset` 加载刚才创建的 ViewModel）。然后使用 `AddViewModelProperty` 节点，传入该蓝图、属性名（例如 `PlayerName`）、属性类型字符串（例如 `FString`）和可选的默认值。
3.  **将 ViewModel 绑定到 Widget 并创建绑定**：
    - 使用 `AddViewModelToWidget` 节点，传入你的 `UWidgetBlueprint` 和想要使用的 ViewModel 类（例如上一步创建的）。
    - 使用 `CreateViewBinding` 节点，设置源上下文（`SourceContext` 为 `null` 表示来自 WidgetBlueprint 本身）、源属性路径（例如 `ViewModel.PlayerName`）、目标上下文（`DestinationContext` 为一个文本框 Widget 对象）和目标属性路径（例如 `Text`）。如果类型不匹配，系统会尝试自动查找并应用转换函数。

## C++ 用法

虽然插件主要为蓝图和自动化设计，但所有函数都是静态的 C++ 函数，也可以在 C++ 中调用。

### 头文件引入

```cpp
#include "MVVMToolset/MVVMToolset.h"
```

### 基本用法

```cpp
// 创建一个新的 ViewModel 蓝图资产
// (来源: Source/MVVMToolset/Private/MVVMToolset/MVVMToolset.h)
UBlueprint* NewViewModel = UMVVMToolset::CreateViewModel(
    TEXT("MyPlayerViewModel"),
    TEXT("/Game/UI/ViewModels/"),
    UMVVMViewModelBase::StaticClass()
);

if (NewViewModel)
{
    // 向 ViewModel 添加一个 bool 类型的属性
    bool bSuccess = UMVVMToolset::AddViewModelProperty(
        NewViewModel,
        TEXT("IsAlive"),
        TEXT("bool"),
        TEXT("true")
    );
}
```

### 进阶用法

```cpp
// 获取一个已存在的 WidgetBlueprint 引用 (通常通过 FAssetRegistryModule 或 LoadObject 获取)
UWidgetBlueprint* MyWidgetBP = ...; // 假设已获得

// 为 Widget 添加一个 ViewModel
UClass* ViewModelClass = UMVVMViewModelBase::StaticClass(); // 或其他自定义 ViewModel 类
UMVVMToolset::AddViewModelToWidget(MyWidgetBP, ViewModelClass);

// 创建一个从 WidgetBlueprint 上的 ViewModel 属性到某个 Widget 属性的绑定
// 假设 ViewModel 中有一个 FText 属性 "DisplayText"， 我们想绑定到一个 TextBlock 的 Text 属性上
FGuid BindingID = UMVVMToolset::CreateViewBinding(
    MyWidgetBP,
    nullptr, // SourceContext 为 null，表示源属性路径相对于 WidgetBlueprint
    TEXT("ViewModel.DisplayText"), // 源属性路径
    MyTextBlockWidget, // DestinationContext 是具体的 Widget 对象
    TEXT("Text"), // 目标属性路径
    NAME_None // 使用自动推断的转换函数
);

if (BindingID.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("Created binding with ID: %s"), *BindingID.ToString());
}

// 列出该 WidgetBlueprint 上的所有绑定
TArray<FMVVMBlueprintViewBinding> AllBindings = UMVVMToolset::ListWidgetViewBindings(MyWidgetBP);
```

## Demo 示例

一个最小化的 C++ 类，用于演示如何使用 `UMVVMToolset` 创建一个简单的 ViewModel。

**MVVMToolsetDemo.h**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MVVMToolsetDemo.generated.h"

UCLASS()
class UMVVMToolsetDemoSubsystem : public UEngineSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	// 创建一个演示用的 ViewModel
	void CreateDemoViewModel();
};
```

**MVVMToolsetDemo.cpp**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#include "MVVMToolsetDemo.h"

// 关键：引入 MVVM 工具集的头文件
#include "MVVMToolset/MVVMToolset.h"
#include "Engine/Blueprint.h"

void UMVVMToolsetDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	// 在引擎初始化完成后创建演示 ViewModel
	FTimerHandle TimerHandle;
	GEngine->GetTimerManager().SetTimerForNextTick([this]() { CreateDemoViewModel(); });
}

void UMVVMToolsetDemoSubsystem::CreateDemoViewModel()
{
	// 使用工具集创建 ViewModel
	UBlueprint* DemoViewModel = UMVVMToolset::CreateViewModel(
		TEXT("DemoViewModel"),
		TEXT("/Game/Automation/MVVMDemo/"),
		UMVVMViewModelBase::StaticClass()
	);

	if (DemoViewModel)
	{
		UE_LOG(LogTemp, Log, TEXT("Successfully created demo ViewModel at: %s"), *DemoViewModel->GetPathName());

		// 向 ViewModel 添加属性
		UMVVMToolset::AddViewModelProperty(DemoViewModel, TEXT("DemoName"), TEXT("FString"), TEXT("Hello MVVM"));
		UMVVMToolset::AddViewModelProperty(DemoViewModel, TEXT("DemoValue"), TEXT("float"), TEXT("42.0f"));
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to create demo ViewModel."));
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `ToolsetRegistry` | 此插件作为“工具集”被注册和发现的底层框架 |
| `ModelViewViewModel` | 提供 `UMVVMViewModelBase`、`FMVVMBlueprintViewBinding` 等 MVVM 核心类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprint assets | 插件初始化提交，实现了通过蓝图资产创建和修改ViewModel的核心功能。 |

### 维护评价

这是一个**全新**的实验性插件，于 2026 年 5 月首次提交。目前仅有一次初始提交，表明其功能处于早期实现阶段，后续可能会有更多更新和完善。由于标记为 `IsExperimentalVersion` 且 `EnabledByDefault` 为 false，它尚未被视为稳定功能，主要面向实验和高级自动化工作流。鉴于其依赖于实验性的 `ToolsetRegistry`，建议在正式项目中谨慎评估使用，并做好它可能随引擎版本迭代而发生 API 变化的准备。目前可以尝试用于原型开发或自动化脚本编写。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MVVMToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MVVMToolset/Source/MVVMToolset/Private/MVVMToolset/Tests)