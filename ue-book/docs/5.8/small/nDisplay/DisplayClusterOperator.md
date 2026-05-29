# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMultiUser` (Runtime), `SharedMemoryMedia` (Runtime), `ScalableMPCDI` (External), 等共 30 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE 的**多机集群同步渲染**系统，解决的核心问题是：用多台 PC 协同渲染同一场景，然后将画面拼合投射到多个物理显示器上（如 LED 墙、穹顶投影、多屏 CAVE 等）。

它的存在原因包括：
- 单台 PC 的 GPU 性能不足以驱动超大分辨率（如 8K+ LED Volume）或多屏输出
- 需要精确的帧同步（genlock）和跨机器状态同步
- 需要复杂的投影校正（MPCDI、网格变形、边缘融合）以适配各种物理屏幕布局
- 虚拟制片（Virtual Production）中 ICVFX LED Volume 的标准基础设施

**注意**：此插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 使用场景

- 你在做**虚拟制片**（Virtual Production），需要用 LED Volume 实时渲染背景 → 用 nDisplay
- 你需要在 **CAVE 系统**（多面投影房间）中做沉浸式体验 → 用 nDisplay
- 你有一个**多屏显示器墙**（如主题公园、展览馆），需要多台 PC 协同渲染 → 用 nDisplay
- 你需要 **Movie Render Queue** 渲染 nDisplay 集群的多视角画面 → 用 `DisplayClusterMoviePipeline`
- 你需要将 nDisplay 集群状态通过**多用户编辑**同步给其他开发者 → 用 `DisplayClusterMultiUser`
- 你需要在编辑器中**可视化和管理**集群配置、预览各屏画面 → 用 `DisplayClusterOperator`

## 蓝图用法

nDisplay 的核心运行时逻辑主要通过配置驱动（`.ndisplay` 配置文件 + `ADisplayClusterRootActor`），蓝图层面的节点相对集中在 Root Actor 上。由于当前模块（DisplayClusterOperator）是编辑器工具面板，不暴露 BlueprintCallable 节点。以下列出其他子模块中常见的蓝图 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 获取/设置 Root Actor | 通过 Operator 模块获取当前场景中的 nDisplay 根 Actor | `ADisplayClusterRootActor` |
| `ToggleDrawer` | 切换操作面板抽屉的开/关状态 | `IDisplayClusterOperator` |
| `ForceDismissDrawers` | 强制关闭操作面板所有已打开的抽屉 | `IDisplayClusterOperator` |

### 使用示例（蓝图描述）

nDisplay 的使用以**配置文件**为核心：
1. 创建一个 `ADisplayClusterRootActor` 放入场景
2. 在 Root Actor 的 Details 面板中指定 `.ndisplay` 配置文件
3. 配置文件定义了：集群节点（Cluster Nodes）、视口（Viewports）、投影策略（Projection）、屏幕（Screens）
4. 启动时各台 PC 加载同一配置，根据自身 Cluster Node 名称自动分配渲染任务

在编辑器中，通过菜单 **Window > nDisplay > Operator** 打开操作面板，即可在面板中切换 Root Actor、查看各视口预览、编辑属性。

## C++ 用法

DisplayClusterOperator 模块提供了一个高度可扩展的编辑器操作面板框架，允许外部模块注册自定义 App、扩展工具栏和状态栏。

### 头文件引入

```cpp
#include "IDisplayClusterOperator.h"
```

### 基本用法

通过模块接口获取 Operator 模块实例，注册自定义 App 扩展：

```cpp
// 来源: Source/DisplayClusterOperator/Public/IDisplayClusterOperator.h
#include "IDisplayClusterOperator.h"

// 检查模块是否可用
if (IDisplayClusterOperator::IsAvailable())
{
    IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

    // 获取当前活跃的 Root Actor
    TSharedRef<IDisplayClusterOperatorViewModel> ViewModel = OperatorModule.GetOperatorViewModel();
    if (ViewModel->HasRootActor())
    {
        ADisplayClusterRootActor* RootActor = ViewModel->GetRootActor();
        // 对 Root Actor 进行操作...
    }
}
```

### 进阶用法

注册自定义 App 和扩展操作面板的工具栏/状态栏：

```cpp
// 来源: Source/DisplayClusterOperator/Public/IDisplayClusterOperator.h
// 来源: Source/DisplayClusterOperator/Public/DisplayClusterOperatorStatusBarExtender.h
#include "IDisplayClusterOperator.h"
#include "IDisplayClusterOperatorApp.h"
#include "DisplayClusterOperatorStatusBarExtender.h"

// 注册自定义 App
IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

FDelegateHandle AppHandle = OperatorModule.RegisterApp(
    IDisplayClusterOperator::FOnGetAppInstance::CreateLambda(
        [](TSharedRef<IDisplayClusterOperatorViewModel> InViewModel) -> TSharedRef<IDisplayClusterOperatorApp>
        {
            // 返回你的自定义 App 实例
            return MakeShared<FMyCustomOperatorApp>(InViewModel);
        }
    )
);

// 扩展工具栏（添加自定义按钮）
OperatorModule.GetOperatorToolBarExtensibilityManager()->AddExtender(MyToolbarExtender);

// 扩展状态栏（添加抽屉面板）
OperatorModule.OnRegisterStatusBarExtensions().AddLambda(
    [](FDisplayClusterOperatorStatusBarExtender& StatusBarExtender)
    {
        FWidgetDrawerConfig DrawerConfig;
        DrawerConfig.DrawerId = FName("MyCustomDrawer");
        DrawerConfig.Label = LOCTEXT("MyDrawer", "My Tool");
        DrawerConfig.Content = SNew(SMyDrawerWidget);
        StatusBarExtender.AddWidgetDrawer(DrawerConfig);
    }
);

// 监听 Root Actor 切换
ViewModel->OnActiveRootActorChanged().AddLambda(
    [](ADisplayClusterRootActor* NewRootActor)
    {
        UE_LOG(LogTemp, Log, TEXT("Root Actor changed to: %s"), *GetNameSafe(NewRootActor));
    }
);

// 监听详情面板对象变化
ViewModel->OnDetailObjectsChanged().AddLambda(
    [](const TArray<UObject*>& Objects)
    {
        // 详情面板显示了新的对象
    }
);

// 使用完后注销
OperatorModule.UnregisterApp(AppHandle);
```

## Demo 示例

一个自定义 Operator App 扩展的最小示例：

```cpp
// MyOperatorApp.h
#pragma once

#include "IDisplayClusterOperatorApp.h"
#include "IDisplayClusterOperatorViewModel.h"

class FMyOperatorApp : public IDisplayClusterOperatorApp
{
public:
    FMyOperatorApp(TSharedRef<IDisplayClusterOperatorViewModel> InViewModel)
        : ViewModel(InViewModel)
    {
        // 监听 Root Actor 变化
        RootActorChangedHandle = ViewModel->OnActiveRootActorChanged().AddRaw(
            this, &FMyOperatorApp::OnRootActorChanged);
    }

    virtual ~FMyOperatorApp() override
    {
        if (ViewModel.IsValid())
        {
            ViewModel->OnActiveRootActorChanged().Remove(RootActorChangedHandle);
        }
    }

private:
    void OnRootActorChanged(ADisplayClusterRootActor* NewRootActor)
    {
        UE_LOG(LogTemp, Log, TEXT("MyOperatorApp: Active root actor is now %s"),
            NewRootActor ? *NewRootActor->GetName() : TEXT("None"));
    }

    TSharedPtr<IDisplayClusterOperatorViewModel> ViewModel;
    FDelegateHandle RootActorChangedHandle;
};
```

```cpp
// MyOperatorExtension.h
#pragma once

#include "IDisplayClusterOperator.h"

class FMyOperatorExtension
{
public:
    void Register()
    {
        if (!IDisplayClusterOperator::IsAvailable())
        {
            return;
        }

        IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

        // 注册 App
        AppHandle = OperatorModule.RegisterApp(
            IDisplayClusterOperator::FOnGetAppInstance::CreateRaw(
                this, &FMyOperatorExtension::CreateApp));

        // 注册状态栏扩展
        OperatorModule.OnRegisterStatusBarExtensions().AddRaw(
            this, &FMyOperatorExtension::ExtendStatusBar);
    }

    void Unregister()
    {
        if (IDisplayClusterOperator::IsAvailable())
        {
            IDisplayClusterOperator::Get().UnregisterApp(AppHandle);
        }
    }

private:
    TSharedRef<IDisplayClusterOperatorApp> CreateApp(
        TSharedRef<IDisplayClusterOperatorViewModel> InViewModel)
    {
        return MakeShared<FMyOperatorApp>(InViewModel);
    }

    void ExtendStatusBar(FDisplayClusterOperatorStatusBarExtender& Extender)
    {
        FWidgetDrawerConfig Config;
        Config.DrawerId = FName("MyStatusDrawer");
        Config.Label = FText::FromString(TEXT("My Info"));
        // Config.Content = SNew(SMyStatusWidget); // 需要实际的 Widget
        Extender.AddWidgetDrawer(Config);
    }

    FDelegateHandle AppHandle;
};
```

## 模块依赖

nDisplay 是一个庞大的插件，不同子模块依赖差异较大。以下是该插件**独特**的、不常见的依赖项：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 共享内存媒体传输（SharedMemoryMedia）的 D3D12 资源访问 |
| `LevelEditor` | Operator 面板集成到关卡编辑器 |
| `EditorWidgets` | Operator 面板的编辑器 UI 组件 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 投影校正库 |

> 注：由于插件包含 30 个模块，各模块还可能依赖 Slate、RenderCore、RHI、MediaFramework 等标准渲染/媒体模块。具体依赖请参考各子模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 nDisplay EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名及 MPCDI 着色器不透明 alpha |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码时未使用非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

- **创建时间**：2018 年（UE 4.20 时代），随虚拟制片需求发展至今
- **近期活跃度**：非常活跃，最近一次更新距今不到 1 周，持续修复 bug 和添加功能
- **维护状态**：**活跃维护中** — 由 Epic 核心团队维护，是虚拟制片的关键基础设施
- **模块规模**：30 个模块、1351 个源文件，属于 UE 中最大的 Runtime 插件之一
- **推荐程度**：如果你的项目涉及多机渲染、LED Volume、CAVE 投影等场景，这是**唯一**的官方解决方案，必须使用。普通单机项目无需启用。
- **注意**：插件默认未启用，需手动在项目设置中开启；文档相对匮乏，主要依赖源码和官方虚拟制片指南学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)（虚拟制片 / nDisplay 章节）