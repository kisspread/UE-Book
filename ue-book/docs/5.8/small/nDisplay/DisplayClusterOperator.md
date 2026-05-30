# nDisplay

> 支持使用多台 PC 进行单视图或立体视图同步集群渲染。

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染操作面板 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterOperator` (Runtime) 等 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterOperator` 模块是 nDisplay 插件的核心编辑器界面。它提供了一个集中的操作面板，用于配置、管理和监控由多台 PC 组成的同步渲染集群。该模块解决的是复杂多视口项目（如虚拟制片、多投影仪映射、CAVE 系统等）中的设置和调试问题。它不仅仅是显示 nDisplay 的属性，还提供了一套完整的工具，用于选择要操作的根 Actor、查看组件结构、监控状态，并集成了灯光卡、媒体输出等其他 nDisplay 子系统的编辑器扩展。

## 使用场景

- **虚拟制片 (Virtual Production)**：使用多台计算机驱动 LED 墙或投影屏幕，需要精确同步和配置每台机器的渲染视口。操作面板用于集中管理整个 nDisplay 网络。
- **CAVE 系统或穹顶影院**：为多个物理投影仪设置几何校正、色彩校准和边缘融合。操作面板是配置投影几何体和校准参数的主要界面。
- **多机渲染性能调试**：当集群中某台机器的性能或同步出现问题时，可以通过操作面板快速定位和切换到特定节点的视角进行调试。
- **开发自定义编辑器扩展**：其他插件或工具可以通过 `IDisplayClusterOperator` 接口将自定义的选项卡、工具栏按钮或状态栏抽屉注册到操作面板中，实现工具集成。

## 蓝图用法

该模块主要提供编辑器时的可扩展接口，而非运行时蓝图节点。它通过委托模式允许其他模块扩展其UI。

### 核心事件（可用于蓝图绑定）

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnActiveRootActorChanged` | 当操作面板当前活动的 nDisplay 根 Actor 发生改变时广播。 | `IDisplayClusterOperatorViewModel` |
| `OnDetailObjectsChanged` | 当详情面板中显示的对象发生变化时广播。 | `IDisplayClusterOperatorViewModel` |
| `OnOutlinerSelectionChanged` | 当大纲视图中的选择发生变化时广播。 | `IDisplayClusterOperatorViewModel` |

### 使用示例（蓝图描述）

1.  **监听根 Actor 变化**：在某个编辑器工具蓝图的 `Event BeginPlay` 中，通过 `IDisplayClusterOperator::IsAvailable()` 检查模块是否可用，然后通过 `GetOperatorViewModel()` 获取视图模型对象，并绑定 `OnActiveRootActorChanged` 事件。当用户在操作面板的工具栏下拉列表中选择不同的根 Actor 时，此事件将触发。
2.  **操作详情面板**：调用 `IDisplayClusterOperatorViewModel::ShowDetailsForObject()`，传入一个 UObject（如一个 nDisplay 组件），即可将该对象的属性显示在操作面板的详情视图中。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterOperatorModule.h"
#include "IDisplayClusterOperator.h"
#include "IDisplayClusterOperatorViewModel.h"
```

### 基本用法

通过 `IDisplayClusterOperator` 单例访问操作面板模块，并监听根 Actor 的变化。

```cpp
// 来源: 从 IDisplayClusterOperator.h 和 IDisplayClusterOperatorViewModel.h 推断的用法

if (IDisplayClusterOperator::IsAvailable())
{
    // 获取操作面板模块
    IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

    // 获取操作面板的视图模型
    TSharedRef<IDisplayClusterOperatorViewModel> ViewModel = OperatorModule.GetOperatorViewModel();

    // 绑定当活动根 Actor 改变时的回调
    ViewModel->OnActiveRootActorChanged().AddLambda([](ADisplayClusterRootActor* NewRootActor)
    {
        if (NewRootActor)
        {
            UE_LOG(LogTemp, Log, TEXT("nDisplay Operator: Active Root Actor changed to %s"), *NewRootActor->GetName());
            // 在这里更新你的工具状态，例如刷新依赖于此根 Actor 的UI
        }
    });
}
```

### 进阶用法

将自定义的应用程序标签页注册到操作面板中。

```cpp
// 来源: 基于 FDisplayClusterOperatorModule 和 IDisplayClusterOperatorApp 的接口设计

// 1. 定义你的自定义应用类
class FMyCustomOperatorApp : public IDisplayClusterOperatorApp
{
public:
    // 应用特定的状态和逻辑
    // ...
};

// 2. 注册应用到操作面板
if (IDisplayClusterOperator::IsAvailable())
{
    IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

    // 注册一个委托，当操作面板需要创建你的应用实例时调用
    auto GetAppDelegate = IDisplayClusterOperator::FOnGetAppInstance::CreateLambda(
        [](TSharedRef<IDisplayClusterOperatorViewModel> ViewModel) -> TSharedRef<IDisplayClusterOperatorApp>
        {
            // 创建并返回你的应用实例
            return MakeShared<FMyCustomOperatorApp>();
        });

    FDelegateHandle AppHandle = OperatorModule.RegisterApp(GetAppDelegate);

    // 当不再需要时，确保取消注册
    // OperatorModule.UnregisterApp(AppHandle);
}
```

## Demo 示例

一个最小的自定义操作面板应用示例，它会在操作面板的主区域添加一个简单的文本标签页。

```cpp
// MyOperatorApp.h
#pragma once

#include "IDisplayClusterOperatorApp.h"

class FMyOperatorApp : public IDisplayClusterOperatorApp
{
public:
    virtual ~FMyOperatorApp() = default;

    // 应用启动时由系统调用
    void OnStartup();

    // 应用关闭时由系统调用
    void OnShutdown();
};
```

```cpp
// MyOperatorApp.cpp
#include "MyOperatorApp.h"
#include "IDisplayClusterOperator.h"
#include "Framework/Docking/TabManager.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Text/STextBlock.h"

void FMyOperatorApp::OnStartup()
{
    if (IDisplayClusterOperator::IsAvailable())
    {
        IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();

        // 获取操作面板的主扩展区域 ID
        const FName PrimaryExtensionId = OperatorModule.GetPrimaryOperatorExtensionId();

        // 注册一个标签页
        FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MyCustomTab", FOnSpawnTab::CreateLambda(
            [](const FSpawnTabArgs& Args) -> TSharedRef<SDockTab>
            {
                return SNew(SDockTab)
                    .TabRole(NomadTab)
                    [
                        SNew(STextBlock)
                        .Text(FText::FromString(TEXT("这是我的自定义 nDisplay 操作面板应用!")))
                    ];
            }))
            .SetDisplayName(FText::FromString(TEXT("我的工具")))
            .SetTooltipText(FText::FromString(TEXT("一个示例自定义标签页")))
            .SetGroup(OperatorModule.GetOperatorViewModel()->GetWorkspaceMenuGroup().ToSharedRef());
    }
}

void FMyOperatorApp::OnShutdown()
{
    // 注销标签页
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner("MyCustomTab");
}
```

## 模块依赖

要使用 `DisplayClusterOperator` 模块，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | 访问 nDisplay 配置数据结构和资产。 |
| `DisplayClusterEditor` | 编辑器核心工具和公共函数。 |
| `Slate`, `SlateCore` | 构建自定义UI界面。 |
| `PropertyEditor` | 创建和管理属性编辑器视图（用于详情面板）。 |
| `UnrealEd` | 编辑器框架，用于标签页注册、工具栏扩展等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加 EXR 多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 MoviePipeline 中的 WarpBlendAlpha 模式到 WarpBlend 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机命名和 MPCDI/ICVFX 着色器的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，尊重非默认的显示 Gamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

`DisplayClusterOperator` 模块作为 nDisplay 这一企业级功能的核心 UI 组件，其维护状态非常活跃。从最近的 Git 提交记录看，更新频率高（几乎每周），且改动内容主要集中在**功能增强**（如 EXR 多层支持）、**流程优化**（合并着色器模式）和**问题修复**（着色器、同步、显示问题）上，表明该模块在积极开发和完善中。鉴于其在虚拟制片等前沿领域的重要性，以及 Epic Games 的持续投入，该模块稳定可靠，**推荐在生产环境中使用**。它默认关闭（`EnabledByDefault: false`），需要在项目设置中手动启用，这符合其面向特定专业用户的定位。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)