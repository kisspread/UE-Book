# nDisplay Operator

> Display Cluster Operator module interface

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 操作面板模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器操作面板UI和扩展接口） |
| 模块 | `DisplayClusterOperator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterOperator) | |

## 用途

`DisplayClusterOperator` 是 `nDisplay` 插件的核心编辑器扩展模块。它**不是**渲染或网络运行时组件，而是提供了一个**集中式的、可扩展的操作面板（Operator Panel）**，用于在编辑器中配置、管理和监控 nDisplay 多机渲染集群。

nDisplay 系统涉及复杂的分布式渲染配置（节点、视口、投影、同步等），传统的属性面板难以高效管理。此模块解决的核心问题是：为复杂的 nDisplay 根Actor（`ADisplayClusterRootActor`）及其庞大的组件树，提供一个定制化的、上下文感知的编辑界面。它允许将多个相关的编辑工具（如视口预览、色彩校准、监控器视图）整合到一个专属面板中，并通过可扩展的接口让其他子系统（如 `DisplayClusterColorGrading`, `DisplayClusterMonitor`）注入自己的UI和功能。

## 使用场景

- **搭建和配置 nDisplay 集群环境**：当你在编辑器中放置一个 `ADisplayClusterRootActor` 并需要为其数十个子组件（节点、屏幕、投影设置）进行参数调整时。
- **多屏/沉浸式CAVE环境开发**：在需要协调多个物理屏幕或投影仪输出的项目中，使用此面板进行统一的预览、调试和配置。
- **虚拟拍摄 (Virtual Production) 或 VR/XR 项目**：需要实时调整ICVFX（视觉特效摄像机内拍摄）环境的渲染设置、色彩和几何扭曲时。
- **开发 nDisplay 扩展插件**：如果你需要为 nDisplay 工作流添加自定义工具（如自定义监控、特定设备控制），可以通过此模块提供的接口将你的工具注册到操作面板中。

## 蓝图用法

此模块主要为 C++ 编辑器扩展设计，不直接暴露大量游戏逻辑蓝图节点。其核心价值在于提供可扩展的编辑器UI框架。在蓝图层面，主要通过 `IDisplayClusterOperatorViewModel` 接口与操作面板的状态进行交互（需要通过 C++ 获取该接口的引用）。

### 核心接口 (通过IDisplayClusterOperatorViewModel)

| 接口/函数 | 说明 | 访问方式 |
|---|---|---|
| `GetRootActor()` | 获取当前操作面板正在编辑的 nDisplay 根 Actor | 通过 C++ 获取 `IDisplayClusterOperatorViewModel` 接口后调用 |
| `SetRootActor(ADisplayClusterRootActor*)` | 设置操作面板当前编辑的根 Actor | 通过 C++ 获取 `IDisplayClusterOperatorViewModel` 接口后调用 |
| `ShowDetailsForObjects(const TArray<UObject*>&)` | 在操作面板的“细节”窗口中显示指定对象的属性 | 通过 C++ 获取 `IDisplayClusterOperatorViewModel` 接口后调用 |
| `OnActiveRootActorChanged()` | 当活动根 Actor 改变时广播的多播委托 | 通过 C++ 获取 `IDisplayClusterOperatorViewModel` 接口后绑定 |
| `OnDetailObjectsChanged()` | 当“细节”窗口显示的对象改变时广播的多播委托 | 通过 C++ 获取 `IDisplayClusterOperatorViewModel` 接口后绑定 |

## C++ 用法

此模块的核心用法是通过其公开接口 `IDisplayClusterOperator` 来注册自定义应用、扩展布局和工具栏。

### 头文件引入

```cpp
#include "IDisplayClusterOperator.h"
#include "IDisplayClusterOperatorApp.h"
#include "IDisplayClusterOperatorViewModel.h"
```

### 基本用法：获取操作面板实例并查询状态

```cpp
// 检查模块是否可用
if (IDisplayClusterOperator::IsAvailable())
{
    // 获取操作面板模块接口
    IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();
    
    // 获取操作面板的视图模型（ViewModel），用于访问当前状态
    TSharedRef<IDisplayClusterOperatorViewModel> ViewModel = OperatorModule.GetOperatorViewModel();
    
    // 检查当前是否有正在编辑的根Actor
    if (ViewModel->HasRootActor())
    {
        // 获取当前根Actor
        ADisplayClusterRootActor* CurrentRootActor = ViewModel->GetRootActor();
        UE_LOG(LogTemp, Log, TEXT("当前操作面板正在编辑的根Actor: %s"), *CurrentRootActor->GetName());
        
        // 将某个对象显示在操作面板的细节窗口中
        UObject* SomeObjectToInspect = ...; // 某个需要检查的对象
        ViewModel->ShowDetailsForObject(SomeObjectToInspect);
    }
    
    // 监听根Actor变更事件
    ViewModel->OnActiveRootActorChanged().AddLambda([](ADisplayClusterRootActor* NewRootActor)
    {
        UE_LOG(LogTemp, Log, TEXT("操作面板的活动根Actor已变更为: %s"), 
            NewRootActor ? *NewRootActor->GetName() : TEXT("None"));
    });
}
```

### 进阶用法：向操作面板注册自定义应用（App）

这是扩展操作面板功能的主要方式。你需要实现 `IDisplayClusterOperatorApp` 接口，并将其注册。

```cpp
// MyOperatorApp.h
#include "IDisplayClusterOperatorApp.h"

class FMyCustomOperatorApp : public IDisplayClusterOperatorApp
{
public:
    virtual ~FMyCustomOperatorApp() = default;
    
    // 你的应用逻辑和UI可以放在这里
    void DoSomething();
};

// MyOperatorApp.cpp
void RegisterMyApp()
{
    if (IDisplayClusterOperator::IsAvailable())
    {
        IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();
        
        // 注册一个App工厂委托。当操作面板需要创建你的App实例时，它会调用此委托。
        FDelegateHandle Handle = OperatorModule.RegisterApp(
            IDisplayClusterOperator::FOnGetAppInstance::CreateLambda([](TSharedRef<IDisplayClusterOperatorViewModel> InViewModel) -> TSharedRef<IDisplayClusterOperatorApp>
            {
                // 在这里创建并返回你的应用实例
                auto MyApp = MakeShared<FMyCustomOperatorApp>();
                // 你可以使用 InViewModel 来与操作面板主状态进行交互
                return MyApp.ToSharedRef();
            })
        );
        
        // 保存Handle以便后续卸载
        // MyDelegateHandle = Handle;
    }
}
```

## Demo 示例

一个最小的示例，展示如何在你的编辑器模块中注册一个简单的操作面板扩展。

```cpp
// MyEditorExtensions.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorExtensionsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle OperatorAppHandle;
};

// MyEditorExtensions.cpp
#include "MyEditorExtensions.h"
#include "IDisplayClusterOperator.h"
#include "IDisplayClusterOperatorApp.h"

void FMyEditorExtensionsModule::StartupModule()
{
    if (IDisplayClusterOperator::IsAvailable())
    {
        IDisplayClusterOperator& OperatorModule = IDisplayClusterOperator::Get();
        
        // 1. 注册一个应用
        OperatorAppHandle = OperatorModule.RegisterApp(
            IDisplayClusterOperator::FOnGetAppInstance::CreateLambda(
                [](TSharedRef<IDisplayClusterOperatorViewModel> ViewModel) -> TSharedRef<IDisplayClusterOperatorApp>
                {
                    // 创建一个最简单的App实例
                    class FSimpleApp : public IDisplayClusterOperatorApp
                    {
                    public:
                        virtual ~FSimpleApp() = default;
                    };
                    return MakeShared<FSimpleApp>().ToSharedRef();
                }
            )
        );
        
        // 2. 监听状态栏扩展事件，添加一个简单的抽屉（Drawer）
        OperatorModule.OnRegisterStatusBarExtensions().AddLambda(
            [](FDisplayClusterOperatorStatusBarExtender& Extender)
            {
                FWidgetDrawerConfig MyDrawerConfig;
                MyDrawerConfig.DrawerId = FName("MyCustomDrawer");
                MyDrawerConfig.WidgetContent = SNew(STextBlock).Text(FText::FromString(TEXT("Hello from My Extension!")));
                MyDrawerConfig.ButtonLabel = FText::FromString(TEXT("My Tool"));
                Extender.AddWidgetDrawer(MyDrawerConfig);
            }
        );
    }
}

void FMyEditorExtensionsModule::ShutdownModule()
{
    if (IDisplayClusterOperator::IsAvailable())
    {
        IDisplayClusterOperator::Get().UnregisterApp(OperatorAppHandle);
    }
}

IMPLEMENT_MODULE(FMyEditorExtensionsModule, MyEditorExtensions)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供 `ADisplayClusterRootActor` 等核心类 |
| `DisplayClusterConfiguration` | nDisplay 配置资产和数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影管线添加EXR多图层渲染支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并电影管线中的扭曲混合Alpha模式到扭曲混合模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知摄像机命名和MPCDI/ICVFX着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在帧输出编码回退时尊重非默认的显示伽马值 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当GUI纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护**。`nDisplay` 作为 Unreal Engine 中用于沉浸式环境和虚拟制作的关键技术，其操作面板模块（`DisplayClusterOperator`）得到持续的功能增强和缺陷修复。从最近的提交记录可以看出，更新集中在与电影渲染管线、着色器、伽马处理以及UI稳定性的改进上，表明 Epic Games 仍在积极开发和维护此功能。

创建于 2018 年（UE4 4.20 时期），已运行超过 8 年，是一个成熟且仍在演进的模块。尽管标记为 `EnabledByDefault: false`（需要用户在项目设置中手动启用），但这主要是因为其面向的是专业和特定领域（如虚拟制片、大型视觉仿真）的用户，而非所有项目都需要。

**推荐使用**：如果你正在进行需要 nDisplay 技术的项目（如 CAVE 系统、LED 虚拟影棚、多屏同步渲染），此模块是编辑器端不可或缺的管理工具。对于普通游戏项目，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterOperator)
- [官方文档]() (暂无官方文档链接)
- [测试用例]() (测试代码位于 `Source/DisplayClusterTests/`)