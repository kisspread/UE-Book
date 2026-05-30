# nDisplay Operator

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 操作面板 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`nDisplay` 插件的核心功能是支持使用多台 PC 进行同步的集群渲染，适用于单眼或立体显示。其中的 `DisplayClusterOperator` 模块专门提供了一个**编辑器操作面板**，用于在编辑器中可视化地管理和配置 nDisplay 集群渲染系统中的根 Actor（`ADisplayClusterRootActor`）。它不是一个运行时功能，而是一个强大的编辑器工具，解决了在复杂集群渲染场景中，难以直观地检查、编辑和调试各个显示节点、视口及参数配置的痛点。

## 使用场景

- 你正在为大型 LED 虚拟影棚（如 VP 舞台）搭建 nDisplay 集群渲染系统，需要在编辑器中集中查看和调整所有参与渲染的 PC 配置。
- 你需要在一个统一的界面中快速切换和编辑场景中不同的 `ADisplayClusterRootActor` 实例，而无需在场景大纲中反复查找。
- 你希望为 nDisplay 操作面板扩展自定义的工具栏按钮、状态栏窗口或命令，以集成自己的工具或调试视图。

## 蓝图用法

**注意**：`DisplayClusterOperator` 模块主要提供的是编辑器 UI 和 C++ 接口，其公开的 API 主要面向其他编辑器模块扩展，**没有公开的蓝图可调用函数**。其功能主要在编辑器面板中操作。

### 核心节点（编辑器内部使用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterApp` | 向操作面板注册一个自定义应用视图 | `IDisplayClusterOperator` |
| `UnregisterApp` | 从操作面板注销一个自定义应用视图 | `IDisplayClusterOperator` |
| `GetOperatorViewModel` | 获取操作面板的视图模型，用于与面板状态交互 | `IDisplayClusterOperator` |
| `GetRootActorLevelInstances` | 获取当前关卡中所有的 nDisplay 根 Actor 实例 | `IDisplayClusterOperator` |
| `ToggleDrawer` | 切换状态栏上指定ID的抽屉窗口的打开/关闭状态 | `IDisplayClusterOperator` |

### 使用示例（编辑器面板操作）

1.  **打开操作面板**：在编辑器菜单中，通过 `Window` -> `nDisplay` -> `Operator` 打开操作面板标签页。
2.  **选择根 Actor**：在面板顶部的工具栏下拉框中，选择你想要编辑的 `ADisplayClusterRootActor`。
3.  **编辑属性**：在下方的“Details”面板中查看并修改该根 Actor 的属性。
4.  **查看组件**：在“Root Actor”面板中，可以展开查看该 Actor 的所有组件结构。
5.  **扩展面板**：其他插件可以通过 `IDisplayClusterOperator` 接口注册自定义的标签页到主区域（`PrimaryTabExtensionId`）或辅助区域（`AuxilliaryTabExtensionId`），或向工具栏和状态栏添加元素。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterOperator.h"
```

### 基本用法

主要通过模块单例 `IDisplayClusterOperator::Get()` 访问功能。
来源: `Source/DisplayClusterOperator/Public/IDisplayClusterOperator.h`

```cpp
// 检查模块是否加载
if (IDisplayClusterOperator::IsAvailable())
{
    // 获取模块实例
    IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

    // 获取当前场景中所有的 nDisplay 根 Actor
    TArray<ADisplayClusterRootActor*> RootActors;
    OperatorModule.GetRootActorLevelInstances(RootActors);

    // 获取操作面板的视图模型，以便监听或改变面板状态
    TSharedRef<IDisplayClusterOperatorViewModel> ViewModel = OperatorModule.GetOperatorViewModel();

    // 监听当前编辑的根 Actor 变化
    ViewModel->OnActiveRootActorChanged().AddLambda([](ADisplayClusterRootActor* NewRootActor)
    {
        // 当用户在操作面板切换根 Actor 时触发
    });

    // 在操作面板的详细视图中显示指定对象
    UObject* ObjectToInspect = ...;
    ViewModel->ShowDetailsForObject(ObjectToInspect);

    // 切换操作面板状态栏上的“日志”抽屉窗口
    const FName LogDrawerId = TEXT("LogDrawer");
    OperatorModule.ToggleDrawer(LogDrawerId);
}
```

### 进阶用法：扩展操作面板

你可以通过操作面板提供的委托，向其 UI 中添加自定义内容。
来源: `Source/DisplayClusterOperator/Public/IDisplayClusterOperator.h`, `DisplayClusterOperatorStatusBarExtender.h`

```cpp
// 1. 向工具栏添加一个自定义按钮
IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();
TSharedPtr<FExtensibilityManager> ToolbarManager = OperatorModule.GetOperatorToolBarExtensibilityManager();
if (ToolbarManager.IsValid())
{
    // 创建并注册一个自定义的工具栏扩展器（需要自己实现 FExtender 逻辑）
    TSharedPtr<FExtender> MyToolbarExtender = MakeShared<FExtender>();
    MyToolbarExtender->AddToolBarExtension("YourExtensionPoint", EExtensionHook::After, OperatorModule.GetOperatorViewModel().ToSharedRef()->GetTabManager(), FToolBarExtensionDelegate::CreateLambda([](FToolBarBuilder& Builder){ /* 添加按钮 */ }));
    ToolbarManager->AddExtender(MyToolbarExtender);
}

// 2. 向状态栏添加一个抽屉窗口（例如自定义监控窗口）
OperatorModule.OnRegisterStatusBarExtensions().AddLambda([](FDisplayClusterOperatorStatusBarExtender& StatusBarExtender)
{
    FWidgetDrawerConfig DrawerConfig;
    DrawerConfig.Name = TEXT("MyCustomMonitor");
    DrawerConfig.Icon = FAppStyle::Get().GetBrush("Icons.Analytics");
    DrawerConfig.Label = LOCTEXT("MyMonitorLabel", "My Monitor");
    DrawerConfig.CreateDrawerContentWidget = SNew(SMyCustomMonitorWidget); // 你的自定义Slate控件
    StatusBarExtender.AddWidgetDrawer(DrawerConfig, 0); // 插入到状态栏第一个位置
});
```

## Demo 示例

一个最小的示例，展示如何从另一个编辑器模块访问 `DisplayClusterOperator` 并监听根 Actor 变化。

**MyNDisplayMonitorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyNDisplayMonitorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle ActiveRootActorChangedHandle;
};
```

**MyNDisplayMonitorModule.cpp**
```cpp
#include "MyNDisplayMonitorModule.h"
#include "IDisplayClusterOperator.h"
#include "IDisplayClusterOperatorViewModel.h"

void FMyNDisplayMonitorModule::StartupModule()
{
    if (IDisplayClusterOperator::IsAvailable())
    {
        IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();
        TSharedRef<IDisplayClusterOperatorViewModel> ViewModel = OperatorModule.GetOperatorViewModel();

        // 绑定到根 Actor 变化事件
        ActiveRootActorChangedHandle = ViewModel->OnActiveRootActorChanged().AddLambda(
            [](ADisplayClusterRootActor* NewRootActor)
            {
                if (NewRootActor)
                {
                    UE_LOG(LogTemp, Log, TEXT("Operator panel switched to root actor: %s"), *NewRootActor->GetName());
                }
            }
        );
    }
}

void FMyNDisplayMonitorModule::ShutdownModule()
{
    if (IDisplayClusterOperator::IsAvailable() && ActiveRootActorChangedHandle.IsValid())
    {
        IDisplayClusterOperator::Get().GetOperatorViewModel()->OnActiveRootActorChanged().Remove(ActiveRootActorChangedHandle);
    }
}

IMPLEMENT_MODULE(FMyNDisplayMonitorModule, MyNDisplayMonitor);
```

## 模块依赖

要使用或集成 `DisplayClusterOperator` 模块，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DisplayClusterOperator` | 操作面板模块本身 |
| `DisplayClusterConfiguration` | nDisplay 配置系统 |
| `UnrealEd` | 编辑器基础功能 |
| `EditorWidgets` | 提供编辑器控件（如 `SSubobjectEditor`） |
| `LevelEditor` | 与关卡编辑器交互 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的影片渲染管线添加了 EXR 多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 影片渲染管线：合并了 WarpBlendAlpha 模式到 WarpBlend 中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了在影片渲染队列中拓扑感知相机的命名问题；修复了 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退时支持非默认的 DisplayGamma。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时的闪烁问题。 |

### 维护评价

`nDisplay` 是一个为特定高端应用（虚拟制片、专业可视化）设计的大型、成熟插件。尽管创建于约 8 年前，但**维护非常活跃**。从近期提交记录可以看出，团队在持续修复 Bug、优化性能并添加新功能（如与 MovieRenderGraph 集成）。该插件不属于“实验性”，但因其复杂性（`EnabledByDefault: false`）和专业性，建议在需要时手动启用。鉴于其持续活跃的维护和广泛的实际应用，**推荐在符合条件的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)