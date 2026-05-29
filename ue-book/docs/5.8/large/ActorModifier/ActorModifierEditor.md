# Actor Modifier Editor

> Actual implementation of modifiers for actors based on ActorModifierCore plugin（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Actor修改器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器样式、属性自定义面板） |
| 模块 | `ActorModifier` (Runtime), `ActorModifierEditor` (Runtime), `ActorModifierLayout` (Runtime), `ActorModifierRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier) | |

## 用途

`ActorModifierEditor` 插件是 Unreal Motion Design (原虚拟制作) 框架中 **Actor 修改器系统**的**编辑器**部分。它为基于 `ActorModifierCore` 核心运行时定义的修改器，提供了编辑器内的用户界面和交互支持。
其主要功能是为 `UProperty` 提供自定义的属性面板 (Details Panel) 和控件，使得设计师能够直观地在编辑器中调整 Actor 修改器的参数（例如锚点对齐）。它解决了核心运行时只有逻辑而缺乏直观编辑接口的问题，是连接数据驱动修改逻辑与可视化编辑的桥梁。

## 使用场景

- 你在使用 Unreal Motion Design (如 Cloner & Effector 系统) 为虚拟制作创建动画场景。
- 你为 Actor 应用了 `ActorModifierCore` 中定义的修改器（如布局、渲染效果等），并希望在编辑器属性面板中直观地编辑其参数。
- 你需要为自定义的 Actor 修改器扩展编辑器UI，例如添加一个九宫格锚点对齐选择器。

## 蓝图用法

当前模块主要为**编辑器属性面板**提供自定义，未发现直接暴露给蓝图的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其功能主要通过在编辑器中配置 Actor 的属性来体现。

## C++ 用法

此模块主要用于为修改器的 `UProperty` 创建自定义的编辑器面板。

### 头文件引入

```cpp
#include "Styles/ActorModifierEditorStyle.h"
#include "Customizations/ActorModifierEditorAnchorAlignmentPropertyTypeCustomization.h"
```

### 基本用法

**注册自定义属性面板 (Property Customization)**

在模块启动时，可以将特定结构体（如 `FActorModifierAnchorAlignment`）与自定义的属性面板类关联起来。
（*来源：基于 `FActorModifierEditorModule` 的典型实现逻辑推断*）

```cpp
// 在模块启动时 (StartupModule)
// 假设你的模块依赖 ActorModifierEditor
#include "PropertyEditorModule.h"
#include "ActorModifierEditorAnchorAlignmentPropertyTypeCustomization.h"

void FYourModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    
    // 为 FActorModifierAnchorAlignment 结构体注册自定义面板
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FActorModifierAnchorAlignment::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(
            &FActorModifierEditorAnchorAlignmentPropertyTypeCustomization::MakeInstance
        )
    );
}

void FYourModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
        PropertyModule.UnregisterCustomPropertyTypeLayout(FActorModifierAnchorAlignment::StaticStruct()->GetFName());
    }
}
```

### 进阶用法

**创建基于组件的Actor过滤选择器**

`FActorModifierEditorActorComponentClassPropertyTypeCustomization` 展示了如何创建一个高级的属性自定义，它允许用户在编辑器中选择 Actor，但**仅限于那些附加了特定组件（Component）的 Actor**。
（*来源：`Private/Customizations/ActorModifierEditorActorComponentClassPropertyTypeCustomization.h`*）

```cpp
// 假设你有一个属性，希望用户只能选择拥有 USplineComponent 的 Actor
UCLASS(BlueprintType)
class UMyModifier : public UActorModifier
{
    GENERATED_BODY()
public:
    // 使用 “ActorComponentClass” 元数据指定过滤条件，值为组件类名
    UPROPERTY(EditAnywhere, meta=(ActorComponentClass="/Script/Engine.SplineComponent"))
    FActorReference TargetSplineActor;
};
```
当这个属性在细节面板中显示时，`FActorModifierEditorActorComponentClassPropertyTypeCustomization` 会根据 `meta` 信息过滤 Actor 列表，只显示包含 `USplineComponent` 的 Actor。

## Demo 示例

一个最小的编辑器模块示例，演示如何注册 `FActorModifierAnchorAlignment` 结构体的自定义属性面板。

**YourModifierEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FYourModifierEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**YourModifierEditorModule.cpp**
```cpp
#include "YourModifierEditorModule.h"
#include "PropertyEditorModule.h"
#include "ActorModifierEditorAnchorAlignmentPropertyTypeCustomization.h"

#define LOCTEXT_NAMESPACE "FYourModifierEditorModule"

void FYourModifierEditorModule::StartupModule()
{
    // 确保 PropertyEditor 模块已加载
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 为 FActorModifierAnchorAlignment 结构体注册自定义的编辑器面板
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FActorModifierAnchorAlignment::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(
            &FActorModifierEditorAnchorAlignmentPropertyTypeCustomization::MakeInstance
        )
    );
}

void FYourModifierEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded(TEXT("PropertyEditor")))
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
        PropertyModule.UnregisterCustomPropertyTypeLayout(FActorModifierAnchorAlignment::StaticStruct()->GetFName());
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FYourModifierEditorModule, YourModifierEditor)
```

## 模块依赖

`ActorModifierEditor` 是一个编辑器模块，主要为属性面板提供自定义。要使用它的功能，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 提供核心的修改器定义、锚点对齐枚举 (`FActorModifierAnchorAlignment`) 和元数据系统。 |
| `Slate`, `SlateCore` | 用于构建自定义的 Slate 控件（如 `SActorModifierEditorAnchorAlignment`）。 |
| `PropertyEditor` | 用于注册和注销自定义的属性类型布局 (`IPropertyTypeCustomization`)。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causing | 优化渲染状态更新逻辑，修复了与3D文本更新相关的问题。 |
| 2026-04-08 | `5c28c1d0` | Motion Design: added render state dirty reason scope for the modifier system to have a better idea o | 为修改器系统添加了渲染状态脏标记作用域，以更好地追踪更新来源。 |
| 2026-03-13 | `ab2df2c3` | Motion Design: moved usage of core ticker to custom ts ticker instance to better control timing. | 将核心计时器替换为自定义的时序控制实例，以更精确地控制更新时序。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 `Base` 前缀重命名为 `Default` 前缀。 |
| 2025-09-23 | `cabb6e4f` | MotionDesign : ActorModifier | 插件从实验（Experimental）目录迁移至虚拟制作（Virtual Production）目录的初始提交。 |

### 维护评价

`ActorModifierEditor` 插件是 Epic Games **Unreal Motion Design** 框架的一部分，从最近的 git 记录来看，**维护非常活跃**。
- **创建时间**：约 1 年前，相对较新。
- **更新频率**：近期（2026年）有多次关于渲染状态和更新时序的改进提交，表明其正在**积极开发和优化**中。
- **维护状态**：**活跃维护**。作为 Motion Design 工具链的关键编辑器组件，预计会持续更新。
- **已知限制**：它严重依赖于 `ActorModifierCore` 核心模块。编辑器功能（自定义面板）是为特定的属性类型（如 `FActorModifierAnchorAlignment`）设计的，扩展性限于属性自定义。
- **推荐使用**：如果你正在使用 Unreal Motion Design 进行虚拟制片或动态图形创作，并且需要自定义修改器的编辑器界面，那么**强烈推荐使用**此插件。它是官方工具链的一部分，稳定性有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier)
- [官方文档]() （暂无）
- [测试用例]() （未在模块内发现）