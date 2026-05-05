# Motion Design Scene State

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、状态机图表、事件图表等） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是一个面向虚拟制作（Virtual Production）和 Motion Design 的场景状态管理系统。它提供了一套基于状态机（State Machine）的框架，允许设计师和开发者以可视化的方式定义场景中各种元素（如灯光、材质、动画、Actor 属性等）的状态、状态之间的转换逻辑以及触发这些转换的事件。其核心目标是将复杂的场景交互逻辑从硬编码中解放出来，通过蓝图和图表进行直观的编辑和管理，特别适用于需要精确控制场景元素随时间或用户交互而变化的虚拟制作、实时图形和交互式演示场景。

## 使用场景

- **虚拟制作（Virtual Production）**：在 LED 墙或绿幕拍摄中，需要根据剧本或导演指令，实时切换场景的灯光氛围、背景环境、道具状态等。使用 SceneState 可以预先编排这些状态序列，并通过事件（如时间轴信号、用户输入）触发切换。
- **Motion Design 动态设计**：创建复杂的动态图形、产品展示或品牌动画，其中多个元素的动画、材质变化需要精确同步和编排。SceneState 的状态机和任务系统可以很好地管理这种时序逻辑。
- **交互式场景演示**：构建产品配置器、建筑可视化或互动艺术装置，用户的操作（如点击、滑动）会触发场景进入不同的展示状态。
- **游戏中的复杂过场或机制**：虽然主要面向虚拟制作，但其状态机逻辑也可用于管理游戏中的复杂环境事件序列或非玩家角色（NPC）的行为状态。

## 蓝图用法

基于提供的 `SceneStateBlueprintEditor` 模块头文件，该插件主要通过编辑器扩展点提供蓝图支持。运行时蓝图 API 主要分布在 `SceneState`、`SceneStateTasks` 等模块中（未在提供的头文件中展示）。以下是编辑器侧的扩展接口：

### 核心节点（编辑器扩展）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterContextEditor` | 注册一个上下文编辑器，用于为特定类型的对象（如 `USceneStateObject`）提供自定义的编辑器视图和逻辑。 | `UE::SceneState::Editor::IBlueprintEditorModule` |
| `UnregisterContextEditor` | 注销一个已注册的上下文编辑器。 | `UE::SceneState::Editor::IBlueprintEditorModule` |
| `RegisterCompiler` | 注册一个蓝图编译器，用于处理特定类型的 `USceneStateBlueprint`。 | `UE::SceneState::Editor::IBlueprintEditorModule` |
| `CreateViewWidget` | 为给定的上下文对象创建用于调试查看的 Slate 控件。 | `UE::SceneState::Editor::IContextEditor` |

### 使用示例（蓝图描述）

在编辑器扩展蓝图（如编辑器工具蓝图）中，你可以通过获取 `SceneStateBlueprintEditor` 模块来注册自定义的上下文编辑器。例如，创建一个 `IContextEditor` 的实现，为你的自定义场景状态对象提供一个专属的属性面板或可视化调试视图。

## C++ 用法

### 头文件引入

```cpp
#include "ISceneStateBlueprintEditorModule.h"
#include "ISceneStateContextEditor.h"
```

### 基本用法

以下示例展示了如何实现一个简单的 `IContextEditor`，并将其注册到 SceneState 蓝图编辑器模块中。这允许你为特定的场景状态对象类扩展编辑器功能。

**来源文件**: `Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateBlueprintEditor/Public/ISceneStateContextEditor.h`, `Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateBlueprintEditor/Public/ISceneStateBlueprintEditorModule.h`

```cpp
// MyContextEditor.h
#pragma once
#include "ISceneStateContextEditor.h"

class FMyContextEditor : public UE::SceneState::Editor::IContextEditor
{
public:
    // 声明此编辑器支持的上下文对象类
    virtual void GetContextClasses(TArray<TSubclassOf<UObject>>& OutContextClasses) const override
    {
        // 假设我们有一个自定义的场景状态对象类 UMySceneStateObject
        OutContextClasses.Add(UMySceneStateObject::StaticClass());
    }

    // 为上下文对象创建调试视图控件
    virtual TSharedPtr<SWidget> CreateViewWidget(const FContextParams& InContextParams) const override
    {
        // 这里可以创建并返回一个自定义的 Slate 控件，用于显示 UMySceneStateObject 的特定信息
        // 例如，一个显示当前状态和参数的面板
        return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Scene State View")));
    }
};
```

```cpp
// 在某个编辑器模块（如你的游戏编辑器模块）的 StartupModule 中注册
void FMyGameEditorModule::StartupModule()
{
    if (UE::SceneState::Editor::IBlueprintEditorModule::IsLoaded())
    {
        auto& BlueprintEditorModule = UE::SceneState::Editor::IBlueprintEditorModule::Get();
        MyContextEditor = MakeShared<FMyContextEditor>();
        BlueprintEditorModule.RegisterContextEditor(MyContextEditor);
    }
}

void FMyGameEditorModule::ShutdownModule()
{
    if (MyContextEditor.IsValid() && UE::SceneState::Editor::IBlueprintEditorModule::IsLoaded())
    {
        UE::SceneState::Editor::IBlueprintEditorModule::Get().UnregisterContextEditor(MyContextEditor);
        MyContextEditor.Reset();
    }
}
```

### 进阶用法

`SceneStateBlueprintEditorUtils` 头文件提供了一系列编辑器工具函数，用于处理属性句柄、GUID、属性包比较等，这些在开发自定义的细节面板（Detail Customization）或蓝图节点时非常有用。

**来源文件**: `Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateBlueprintEditor/Public/SceneStateBlueprintEditorUtils.h`

```cpp
#include "SceneStateBlueprintEditorUtils.h"

// 示例：在自定义的细节面板中，检查一个属性是否为特定类的对象属性
void FMyDetailsCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    TSharedRef<IPropertyHandle> SomePropertyHandle = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyClass, SomeProperty));
    
    UClass* TargetClass = UMySpecificObject::StaticClass();
    if (UE::SceneState::Editor::IsObjectPropertyOfClass(SomePropertyHandle->GetProperty(), TargetClass))
    {
        // 如果属性是 UMySpecificObject 类型的对象属性，则进行特殊处理
        // 例如，添加一个自定义的“浏览”按钮
    }
}

// 示例：比较两个属性包的布局是否兼容
FInstancedPropertyBag BagA, BagB;
// ... 填充 BagA 和 BagB ...
bool bLayoutCompatible = UE::SceneState::Editor::CompareParametersLayout(BagA, BagB);
if (bLayoutCompatible)
{
    // 布局兼容，可以进行参数迁移或同步
}
```

## Demo 示例

以下是一个最小化的编辑器模块示例，演示了如何集成 SceneState 的上下文编辑器扩展。

**MySceneStateEditorExtension.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMySceneStateEditorExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<UE::SceneState::Editor::IContextEditor> ContextEditor;
};
```

**MySceneStateEditorExtension.cpp**
```cpp
#include "MySceneStateEditorExtension.h"
#include "ISceneStateBlueprintEditorModule.h"
#include "ISceneStateContextEditor.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "FMySceneStateEditorExtensionModule"

// 简单的上下文编辑器实现
class FSimpleContextEditor : public UE::SceneState::Editor::IContextEditor
{
public:
    virtual void GetContextClasses(TArray<TSubclassOf<UObject>>& OutContextClasses) const override
    {
        // 支持 UObject 作为示例，实际应替换为你的场景状态对象类
        OutContextClasses.Add(UObject::StaticClass());
    }

    virtual TSharedPtr<SWidget> CreateViewWidget(const FContextParams& InContextParams) const override
    {
        return SNew(STextBlock)
            .Text(LOCTEXT("SimpleView", "Simple Scene State Context View"))
            .Font(FCoreStyle::GetDefaultFontStyle("Bold", 14));
    }
};

void FMySceneStateEditorExtensionModule::StartupModule()
{
    // 检查并加载 SceneStateBlueprintEditor 模块
    if (FModuleManager::Get().IsModuleLoaded(TEXT("SceneStateBlueprintEditor")))
    {
        auto& Module = UE::SceneState::Editor::IBlueprintEditorModule::Get();
        ContextEditor = MakeShared<FSimpleContextEditor>();
        Module.RegisterContextEditor(ContextEditor);
    }
}

void FMySceneStateEditorExtensionModule::ShutdownModule()
{
    if (ContextEditor.IsValid())
    {
        if (FModuleManager::Get().IsModuleLoaded(TEXT("SceneStateBlueprintEditor")))
        {
            UE::SceneState::Editor::IBlueprintEditorModule::Get().UnregisterContextEditor(ContextEditor);
        }
        ContextEditor.Reset();
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMySceneStateEditorExtensionModule, MySceneStateEditorExtension)
```

## 模块依赖

从模块结构推断，使用此插件的核心功能（如状态机运行时）需要依赖其内部模块。开发编辑器扩展则需要额外的编辑器模块依赖。

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心运行时模块，包含状态机、场景状态对象等基础类。 |
| `SceneStateBinding` | 处理场景状态与外部对象（如 Actor、组件）属性之间的绑定逻辑。 |
| `SceneStateBlueprint` | 提供场景状态蓝图（`USceneStateBlueprint`）的运行时支持。 |
| `SceneStateEvent` | 定义和管理触发状态转换的事件系统。 |
| `SceneStateTasks` | 提供在状态中执行的具体任务（Task）实现，如修改材质、播放动画等。 |
| `SceneStateGameplay` | 可能包含与游戏玩法逻辑集成的特定功能。 |
| `SceneStateBlueprintEditor` | 蓝图编辑器扩展，提供上下文编辑器、编译器注册等接口。 |
| `SceneStateEditor` | 通用的场景状态编辑器工具和UI。 |
| `SceneStateEventEditor` | 事件图表的编辑器支持。 |
| `SceneStateMachineEditor` | 状态机图表的编辑器支持。 |
| `SceneStateMachineGraph` | 状态机图表的运行时图结构。 |
| `SceneStateEventGraph` | 事件图表的运行时图结构。 |
| `SceneStateTransitionGraph` | 状态转换条件图表的运行时图结构。 |
| `Slate`, `PropertyEditor` | 用于构建自定义编辑器UI和属性面板。 |

## 维护状态

### 近期更新

- 2025-10-03 26c5be73ff3d Motion Design Scene State: 修复了实例化到生成类并保存在共享结构体中的 UObject 被标记为不可达并被垃圾回收的问题。通过将模板数据从结构体（曾用作共享结构体）更改为 UObject 来解决。UObject 方法的好处是任务 UObject 现在可以直接以外部对象（Outer）的形式关联到模板数据 UObject，而不是关联到拥有类。
- 2025-09-15 35e014880fab Motion Design Scene State: 修复了转换参数枚举在图表中无法使用的问题。
- 2025-08-20 9d2e4cc30738 Motion Design Scene State: 修复了复制任务等对象时不会复制函数值（仅复制类型）的问题。

### 维护评价

SceneState 是一个非常新的插件（创建于 2025 年 4 月），目前处于 **Beta 实验性** 阶段。从近期的 git 提交记录来看，开发团队正在积极修复核心功能中的 Bug（如垃圾回收、参数复制、枚举支持），表明插件处于 **活跃开发** 状态。然而，由于其“实验性”标签和较短的生命周期，API 和功能可能会发生较大变化，稳定性无法保证。它适合用于原型开发和探索虚拟制作中的状态管理方案，但不建议在需要高度稳定性的生产项目中作为核心依赖使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无
- 测试用例：未在提供的路径中明确标识，通常位于 `Engine/Plugins/VirtualProduction/SceneState/Tests/` 或 `Engine/Tests/` 目录下。