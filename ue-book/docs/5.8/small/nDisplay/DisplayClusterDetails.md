# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterMedia` (Runtime), `SharedMemoryMedia` (Runtime) 等 (共 29 个模块) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个高级的集群渲染解决方案，用于在多个物理显示器、投影仪或计算机节点上同步渲染同一场景。它不仅仅是将画面扩展到多个屏幕，而是实现了一套完整的分布式渲染框架。其核心目标是解决以下问题：
1.  **多屏同步**：确保所有参与渲染的PC（集群节点）在每一帧都渲染完全一致的视图，实现无缝拼接。
2.  **高级投影校正**：支持复杂的投影表面（如曲面屏、LED墙、穹顶），并通过内置的投影映射（Projection Mapping）和变形（Warping）功能进行几何校正。
3.  **摄影机内视效（ICVFX）**：专为虚拟制片优化，支持将虚拟场景实时渲染到LED墙上，并与物理摄影机完美同步，用于拍摄。
4.  **立体声（Stereo）渲染**：支持为VR或3D显示进行立体渲染。

它通过一个中心的“根Actor”来管理整个集群的拓扑结构、视口配置和同步逻辑。

## 使用场景

-   **虚拟制片（LED Volume）**：你在搭建一个用LED墙作为背景的拍摄现场，需要用实时渲染的虚拟场景替代绿幕 → 用 nDisplay 管理整个LED墙的渲染集群，并与摄影机跟踪系统同步。
-   **多屏显示装置**：你在创建一个沉浸式的飞行模拟器或科学可视化CAVE系统，需要多个投影仪无缝拼接 → 用 nDisplay 进行边缘融合和几何校正。
-   **大型活动或展览**：你在策划一个使用多台投影仪进行建筑投影映射的灯光秀 → 用 nDisplay 控制内容在异形表面上的精确映射。
-   **多机位同步录制/广播**：你需要从同一个虚拟场景中，同时渲染并输出多个不同机位的高清视频流 → 用 nDisplay 的多视口功能。

## 蓝图用法

由于 nDisplay 的核心逻辑（集群同步、帧同步）高度依赖C++和底层网络，其主要的用户交互接口是**编辑器工具**和**配置资产**。通过蓝图可控制的运行时节点相对有限，主要集中在状态查询和控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is nDisplay Cluster` | 检查当前运行环境是否为 nDisplay 集群的一部分 | `UDisplayClusterBlueprintAPI` |
| `Get Active Root Actor` | 获取当前场景中激活的 `ADisplayClusterRootActor` | `UDisplayClusterBlueprintAPI` |
| `Get nDisplay Node ID` | 获取当前节点的名称（如 “node0”） | `UDisplayClusterBlueprintAPI` |
| `Set Cluster Sync Settings` | 运行时调整集群同步相关的设置 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）
你无法直接通过蓝图构建一个完整的 nDisplay 集群，这需要通过编辑器中的 `ADisplayClusterRootActor` 和 nDisplay 配置编辑器来完成。蓝图主要用于在运行时读取状态或触发特定事件。
例如，在关卡蓝图中，你可以使用 `Get Active Root Actor` 节点获取当前的根Actor，然后通过它访问其配置的视口信息。

## C++ 用法

### 头文件引入
使用 nDisplay 的C++ API通常需要引入特定模块的头文件。
```cpp
#include "DisplayClusterModule.h" // 核心模块
#include "DisplayClusterRootActor.h" // 根Actor类
#include "DisplayClusterConfigurationTypes.h" // 配置数据类型
```

### 基本用法
与蓝图类似，C++ 中更多是用于访问运行时数据和扩展系统功能。
```cpp
// 获取 nDisplay 模块接口
IDisplayCluster& DisplayClusterModule = FModuleManager::GetModuleChecked<IDisplayCluster>(TEXT("DisplayCluster"));

// 检查模块是否已初始化
if (DisplayClusterModule.IsModuleInitialized())
{
    // 通常，nDisplay 的控制权在编辑器的配置资产和 ADisplayClusterRootActor 上。
    // 运行时，你可能会通过集群的同步机制来协调各节点。
    UE_LOG(LogTemp, Log, TEXT("nDisplay module is running."));
}
```

### 进阶用法：创建自定义投影策略
nDisplay 的投影系统是可扩展的。你可以实现自己的投影策略。
```cpp
// 1. 定义一个继承自 IDisplayClusterProjectionPolicyFactory 的工厂类
class FMyCustomProjectionFactory : public IDisplayClusterProjectionPolicyFactory
{
public:
    virtual TSharedPtr<IDisplayClusterProjectionPolicy> Create(const FString& ProjectionPolicyId, const FDisplayClusterConfigurationProjection* InConfigurationProjectionPolicy) override
    {
        // 根据配置创建并返回你的自定义投影策略实例
        return MakeShared<FMyCustomProjectionPolicy>(ProjectionPolicyId, InConfigurationProjectionPolicy);
    }
};

// 2. 在你的模块启动时注册这个工厂
void FMyModule::StartupModule()
{
    IDisplayCluster& DCModule = IDisplayCluster::Get();
    if (DCModule.IsModuleInitialized())
    {
        // 注册工厂，使得配置中可以使用 “MyCustom” 作为投影策略类型
        DCModule.GetProjectionFactory().RegisterProjectionPolicyFactory(TEXT("MyCustom"), MakeShared<FMyCustomProjectionFactory>());
    }
}
```

## Demo 示例

以下是一个最小化的C++示例，展示如何在模块中注册一个自定义的投影策略工厂。
**MyProjectionModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyProjectionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    static inline FMyProjectionModule& Get()
    {
        return FModuleManager::GetModuleChecked<FMyProjectionModule>(TEXT("MyProjectionModule"));
    }
};
```

**MyProjectionModule.cpp**
```cpp
#include "MyProjectionModule.h"
#include "DisplayClusterModule.h"
#include "Render/Projection/IDisplayClusterProjectionPolicyFactory.h"
#include "Render/Projection/IDisplayClusterProjectionPolicy.h"

// 假设你已实现了 FMyCustomProjectionPolicy 和 FMyCustomProjectionFactory
// #include "MyCustomProjectionPolicy.h"

void FMyProjectionModule::StartupModule()
{
    // 等待 nDisplay 模块初始化完成
    FCoreDelegates::OnAllModuleLoadingComplete.AddLambda([]()
    {
        if (IDisplayCluster::IsAvailable())
        {
            IDisplayCluster& DCModule = IDisplayCluster::Get();
            // 注册自定义的投影策略工厂
            // DCModule.GetProjectionFactory().RegisterProjectionPolicyFactory(TEXT("MyCustom"), MakeShared<FMyCustomProjectionFactory>());
            UE_LOG(LogTemp, Log, TEXT("Custom projection policy factory registered (example)."));
        }
    });
}

void FMyProjectionModule::ShutdownModule()
{
    // 清理工作，如果需要的话
}

IMPLEMENT_MODULE(FMyProjectionModule, MyProjectionModule)
```

## 模块依赖

nDisplay 包含多个子模块。要使用其核心功能（如创建根Actor、进行投影），你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，包含集群同步、视口管理等基础功能 |
| `DisplayClusterConfiguration` | 处理 nDisplay 的配置数据（.ndisplay资产） |
| `DisplayClusterProjection` | 投影策略和映射算法 |
| `SharedMemoryMedia` | 用于节点间基于共享内存的高性能媒体（纹理）传输 |
| `DisplayClusterMedia` | 整合媒体框架，处理纹理在集群中的分发 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 MovieGraph 管线添加 EXR 多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并MoviePipeline中的WarpBlendAlpha模式到WarpBlend，简化接口。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复MRG中拓扑感知相机命名；修复MPCDI/ICVFX着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，正确处理非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当GUI纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价
nDisplay 虽然创建于2018年（约7年前），是一个“老古董”级别的插件，但它一直是 Epic Games 虚拟制片战略的核心组成部分。**从近期的提交记录（2025年）来看，它仍在被非常活跃地维护和开发**，更新内容聚焦于功能增强（如EXR多层支持）、与新系统（MovieGraph）的集成以及重要的Bug修复。这表明它是一个成熟、稳定且持续投入的关键技术。

**推荐使用**：如果你需要开发涉及多屏同步渲染、投影校正、尤其是虚拟制片（ICVFX）的项目，nDisplay 是UE5中官方的、功能完备的解决方案。尽管入门门槛较高，但其稳定性和功能深度值得投入学习。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档（请参考 Epic Games 官方文档站点，路径通常为“引擎功能 > 虚拟制片 > nDisplay”）
- 测试用例：插件内部包含 `DisplayClusterTests` 模块，路径为 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/`。