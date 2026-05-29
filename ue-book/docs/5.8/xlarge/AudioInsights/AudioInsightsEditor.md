# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频洞察 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有插件模板 |
| 模块 | `AudioInsights` (EditorAndProgram), `AudioInsightsEditor` (EditorNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights) | |

## 用途
该插件是一套专门用于 Unreal Engine 音频性能分析、调试和监控的编辑器工具集。它并非直接在游戏运行时使用，而是扩展了 Unreal Insights 性能分析工具，为音频开发者提供了一个专门的音频分析仪表板。它通过集成的跟踪（Trace）功能收集音频数据，并在编辑器中进行可视化呈现，帮助开发者定位性能瓶颈、监听音频事件、可视化音频对象之间的信号流关系，以及调试虚拟化的音频循环等。

## 使用场景
- 你正在分析游戏音频系统的性能，需要查看特定 `USoundSubmix` 的实时频谱分析 → 使用“音频分析器”视图。
- 你需要监听和过滤引擎中触发的音频事件，以验证音频资产是否正确加载和播放 → 使用“事件日志”视图。
- 你想要可视化音频对象（如声源、衰减范围、声学表面）在场景中的空间关系和属性 → 使用“声音仪表板”或“细节”视图。
- 你在开发中需要调试音频对象的虚拟化状态（Virtual Loops）和衰减范围 → 使用“虚拟循环调试”和“衰减可视化”功能。

## 蓝图用法

该插件主要是一个编辑器扩展和性能分析工具，不提供游戏运行时（Runtime）的蓝图节点。其功能主要通过 Unreal Insights 窗口中的自定义面板和编辑器设置（Project Settings → Editor → Audio Insights）进行交互。

**可扩展接口（用于 C++ 插件开发）**:
该插件定义了 `IAudioInsightsEditorModule` 接口，允许其他插件注册自定义的仪表板视图。

## C++ 用法

### 头文件引入
```cpp
#include "IAudioInsightsEditorModule.h"
```

### 基本用法

**1. 获取模块实例与注册视图工厂**

这是扩展 Audio Insights 面板的核心方式。你需要实现 `IDashboardViewFactory` 接口，并在模块启动时注册它。
*(来源: `Public/IAudioInsightsEditorModule.h`, `Private/AudioInsightsEditorModule.h`)*

```cpp
#include "IAudioInsightsEditorModule.h"
#include "Modules/ModuleManager.h"

// 假设你已经定义了一个继承自 UE::Audio::Insights::IDashboardViewFactory 的类
class FMyAudioDashboardViewFactory : public UE::Audio::Insights::IDashboardViewFactory
{
public:
    virtual FName GetName() const override { return TEXT("MyCustomView"); }
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyPlugin", "MyView", "我的视图"); }
    virtual UE::Audio::Insights::EDefaultDashboardTabStack GetDefaultTabStack() const override { return UE::Audio::Insights::EDefaultDashboardTabStack::Custom; }
    virtual FSlateIcon GetIcon() const override { return FSlateIcon(); } // 或提供自定义图标
    virtual TSharedRef<SWidget> MakeWidget(TSharedRef<SDockTab> OwnerTab, const FSpawnTabArgs& SpawnTabArgs) override
    {
        // 返回你自定义的 Slate 控件
        return SNew(STextBlock).Text(FText::FromString(TEXT("这是自定义音频仪表板视图")));
    }
};

// 在你的模块启动函数中
void FMyModule::StartupModule()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& AudioInsightsModule = IAudioInsightsEditorModule::GetChecked();
        TSharedRef<FMyAudioDashboardViewFactory> MyFactory = MakeShared<FMyAudioDashboardViewFactory>();
        AudioInsightsModule.RegisterDashboardViewFactory(MyFactory);
    }
}

void FMyModule::ShutdownModule()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& AudioInsightsModule = IAudioInsightsEditorModule::GetChecked();
        AudioInsightsModule.UnregisterDashboardViewFactory(TEXT("MyCustomView"));
    }
}
```

**2. 访问模块内部管理器**

高级用户可以通过模块接口访问内部管理器，例如缓存管理器、时序视图扩展等。
*(来源: `Private/AudioInsightsEditorModule.h`)*

```cpp
if (IAudioInsightsEditorModule::IsModuleLoaded())
{
    // 注意：GetChecked() 返回的是 IAudioInsightsEditorModule&，但内部模块 FAudioInsightsEditorModule 提供更多细节方法。
    // 需要确保在正确的模块上下文中进行调用。
    FAudioInsightsEditorModule& InternalModule = FAudioInsightsEditorModule::GetChecked();
    FAudioInsightsCacheManager& CacheManager = InternalModule.GetCacheManager();
    FAudioInsightsTimingViewExtender& TimingViewExtender = InternalModule.GetTimingViewExtender();
    // ... 使用这些管理器进行更精细的控制或数据查询
}
```

**3. 注册事件日志类别和显示名称**

你可以扩展事件日志，让你的插件产生的音频事件也能被过滤和显示。
*(来源: `Private/AudioInsightsEditorModule.h`)*

```cpp
TMap<FString, TSet<FString>> CustomCategories;
CustomCategories.Add(TEXT("MyPlugin"), TSet<FString>{ TEXT("EventA"), TEXT("EventB") });

TMap<FString, FText> DisplayNames;
DisplayNames.Add(TEXT("MyPlugin"), FText::FromString(TEXT("我的插件")));
DisplayNames.Add(TEXT("EventA"), FText::FromString(TEXT("事件 A")));

// 在 StartupModule 中
FAudioInsightsEditorModule& InternalModule = FAudioInsightsEditorModule::GetChecked();
InternalModule.RegisterEventLogCategories(CustomCategories);
InternalModule.RegisterEventLogDisplayNames(DisplayNames);
```

### 进阶用法

**使用插件模板创建自定义扩展插件**

插件提供了一个模板，用于快速生成包含自定义视图工厂的插件骨架。这可以通过编辑器中的“新建插件”向导完成。
*(来源: `Private/AudioInsightsPluginTemplate.h`)*
该模板会预生成一个包含 `FAudioInsightsPluginTemplateDescription` 的插件项目，自动配置好模块依赖和基本的仪表板视图工厂代码，帮助你快速开始开发自定义的 Audio Insights 扩展。

## Demo 示例

下面是一个最小化的编辑器模块示例，演示如何创建一个简单的自定义 Audio Insights 仪表板视图。

**MyAudioInsightsExtension.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"
#include "IAudioInsightsEditorModule.h"

class FMyAudioInsightsExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FName FactoryName = TEXT("SimpleTestView");
};
```

**MyAudioInsightsExtension.cpp**
```cpp
#include "MyAudioInsightsExtension.h"

#define LOCTEXT_NAMESPACE "FMyAudioInsightsExtensionModule"

// 简单的自定义视图工厂
class FSimpleTestViewFactory : public UE::Audio::Insights::IDashboardViewFactory, public TSharedFromThis<FSimpleTestViewFactory>
{
public:
    virtual FName GetName() const override { return TEXT("SimpleTestView"); }
    virtual FText GetDisplayName() const override { return LOCTEXT("ViewName", "测试视图"); }
    virtual UE::Audio::Insights::EDefaultDashboardTabStack GetDefaultTabStack() const override { return UE::Audio::Insights::EDefaultDashboardTabStack::Custom; }
    virtual FSlateIcon GetIcon() const override { return FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports"); }
    virtual TSharedRef<SWidget> MakeWidget(TSharedRef<SDockTab> OwnerTab, const FSpawnTabArgs& SpawnTabArgs) override
    {
        return SNew(SBorder)
            .Padding(10.0f)
            [
                SNew(STextBlock)
                .Text(LOCTEXT("TestViewContent", "这是 Audio Insights 的一个简单测试视图。\n它可以用来展示任何自定义的音频分析内容。"))
                .AutoWrapText(true)
            ];
    }
};

void FMyAudioInsightsExtensionModule::StartupModule()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& AudioInsightsModule = IAudioInsightsEditorModule::GetChecked();
        TSharedRef<FSimpleTestViewFactory> Factory = MakeShared<FSimpleTestViewFactory>();
        AudioInsightsModule.RegisterDashboardViewFactory(Factory);
    }
}

void FMyAudioInsightsExtensionModule::ShutdownModule()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& AudioInsightsModule = IAudioInsightsEditorModule::GetChecked();
        AudioInsightsModule.UnregisterDashboardViewFactory(FactoryName);
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyAudioInsightsExtensionModule, MyAudioInsightsExtension)
```

## 模块依赖

从 `Build.cs` 文件分析，要使用或扩展此插件，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AudioInsightsRuntime` | 核心运行时跟踪和提供器逻辑，是数据的基础来源 |
| `AudioWidgets` | 提供音频分析器控件（如频谱分析仪、响度表）的 Slate 控件库 |
| `TraceServices` | 用于读取和分析 Unreal Insights 的跟踪数据 |
| `Insights` | Unreal Insights 前端框架，用于构建自定义的时序视图和调试器 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `28c5c884` | [Audio Insights] Plugin template readme file to assist users when expanding Audio Insights with cust | 添加了插件模板的自述文件，帮助用户创建自定义扩展。 |
| 2026-05-19 | `a9b19eba` | [Audio Insights] Stop Event Log from automatically setting new items in the details panel when scrub | 修复了事件日志在时间轴拖动时自动选择新项目的问题。 |
| 2026-05-14 | `d492400a` | [Audio Insights] Fix localization for event log filter menu strings | 修复了事件日志过滤器菜单字符串的本地化问题。 |
| 2026-05-14 | `64ecb7b0` | [Audio Insights] Setting Audio Insights and Audio Insights Runtime plugins to be Production | 将 Audio Insights 及其运行时插件标记为 Production（生产就绪）版本。 |
| 2026-05-14 | `62b99116` | [Audio Insights] Add user-adjustable node padding multipliers to signal flow graph settings menu. Tw | 为信号流图设置菜单添加了用户可调节的节点内边距乘数。 |

### 维护评价
**活跃维护**。该插件创建于 2023 年底，处于活跃开发阶段。从近期提交记录可以看出，Epic Games 团队正在持续对其进行优化、功能增强和 Bug 修复。在最近的更新中，官方已将其标记为“Production”版本，表明其稳定性和功能完备性已达到生产环境要求。插件设计模块化，通过接口支持扩展，是 Unreal Engine 音频工具链中一个成熟且重要的组成部分。

**推荐使用**：对于需要进行深度音频性能分析、调试和监控的 UE5 项目，强烈推荐启用和使用此插件。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights)
- [Unreal Insights 文档](https://docs.unrealengine.com/5.8/en-US/unreal-insights-in-unreal-engine/)（官方性能分析工具文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights/Tests)（如果存在）