# nDisplay Details Panel

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay详情面板 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DisplayClusterDetails` (Runtime), `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterDetails` 模块是 nDisplay 插件的一个专门组件，用于在 Unreal Editor 的 nDisplay Operator（操作员）面板中提供一个可停靠的详情抽屉。其核心功能是为选定的 `ADisplayClusterRootActor`（nDisplay 根 Actor）及其 `UDisplayClusterICVFXCameraComponent`（ICVFX 相机组件）显示一个经过筛选和组织的属性面板。

这个模块解决了在多显示器集群渲染环境下，艺术家或灯光师需要频繁调整大量相互关联的 Actor 和组件属性时的操作效率问题。它不是一个通用的细节面板，而是一个专门针对 nDisplay ICVFX（In-Camera Visual Effects）工作流优化的工具。它允许用户将相关的属性分组（Section）、自定义显示，并将面板状态（如选择的对象、展开的子节）持久化，从而提供比标准细节面板更高效、更专注的编辑体验。

## 使用场景

- **虚拟制片（LED Volume）**：在使用 nDisplay 驱动的大型 LED 墙进行虚拟拍摄时，灯光师或实时操作员需要快速调整主摄像机、各个 ICVFX 摄像机的曝光、颜色校正、遮罩形状等参数。本模块的抽屉面板提供了经过整理的、上下文相关的属性访问。
- **主题公园/大型装置**：在驾驶舱模拟器、穹顶投影或 CAVE（Cave Automatic Virtual Environment）等使用多台PC同步渲染的装置中，通过详情面板统一管理所有显示节点的投影校准和渲染设置。
- **需要扩展属性编辑**：当标准细节面板因包含过多无关属性而效率低下时，开发人员可以通过数据模型生成器（DataModelGenerator）机制，为特定的 nDisplay 相关 Actor 或组件类型注册自定义的、仅包含关键属性的详情视图。

## 蓝图用法

本模块主要面向编辑器扩展和 C++ 开发，直接暴露给蓝图的节点较少。其主要的公开接口是模块单例和抽屉单例的访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Details Module` | 获取 `IDisplayClusterDetails` 模块单例，用于访问详情面板功能。 | `IDisplayClusterDetails` |
| `Is Details Module Available` | 检查详情模块是否已加载并可用。 | `IDisplayClusterDetails` |
| `Dock Details Drawer` | 请求将详情抽屉停靠到 nDisplay Operator 面板的标签页中。 | `IDisplayClusterDetailsDrawerSingleton` |
| `Refresh Details Drawers` | 刷新所有已打开的详情抽屉实例的 UI。参数 `bPreserveDrawerState` 决定是否保持当前的选择状态。 | `IDisplayClusterDetailsDrawerSingleton` |

### 使用示例（蓝图描述）

虽然不能直接在事件图表中放置大量详情面板逻辑，但可以通过蓝图编辑器扩展（Editor Utility Widget）来间接使用。一个典型的流程是：
1.  在你的编辑器工具蓝图中，获取 `IDisplayClusterDetails` 模块。
2.  调用 `Get Details Drawer Singleton` 节点。
3.  使用该单例的 `Refresh Details Drawers` 节点，当你的工具检测到需要刷新显示时（例如，根 Actor 属性发生变化后），强制更新详情面板。

## C++ 用法

本模块的核心价值在于其**可扩展的数据模型生成器（DataModel Generator）机制**。开发者可以为自己的 Actor 或组件类型注册自定义的详情面板视图。

### 头文件引入

```cpp
// 模块接口
#include "IDisplayClusterDetails.h"

// 数据模型相关（用于扩展）
#include "DisplayClusterDetailsDataModel.h"
```

### 基本用法

**获取并使用详情抽屉单例（来自 `DisplayClusterDetailsModule.h`）**

```cpp
#include "IDisplayClusterDetails.h"

// 在需要操作详情面板的代码中
if (IDisplayClusterDetails::IsAvailable())
{
    IDisplayClusterDetails& DetailsModule = IDisplayClusterDetails::Get();
    IDisplayClusterDetailsDrawerSingleton& DrawerSingleton = DetailsModule.GetDetailsDrawerSingleton();
    
    // 刷新所有打开的详情抽屉，保持状态
    DrawerSingleton.RefreshDetailsDrawers(true);
    
    // 或者，将抽屉停靠到 Operator 面板
    // DrawerSingleton.DockDetailsDrawer();
}
```

### 进阶用法

**注册自定义数据模型生成器（来自 `DisplayClusterDetailsDataModel.h`）**

假设你有一个自定义的 Actor `AMyCustomStageLight`，你希望在 nDisplay 详情面板中为其显示精简的属性。

1.  **定义生成器类**（通常放在你的编辑器模块中）：
```cpp
// MyCustomStageLightDetailsGenerator.h
#pragma once

#include "DisplayClusterDetailsDataModel.h"

class AMyCustomStageLight;

class FMyCustomStageLightDetailsGenerator : public IDisplayClusterDetailsDataModelGenerator
{
public:
    static TSharedRef<IDisplayClusterDetailsDataModelGenerator> MakeInstance();

    // IDisplayClusterDetailsDataModelGenerator interface
    virtual void Initialize(const TSharedRef<FDisplayClusterDetailsDataModel>& DetailsDataModel, const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override;
    virtual void Destroy(const TSharedRef<FDisplayClusterDetailsDataModel>& DetailsDataModel, const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override;
    virtual void GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FDisplayClusterDetailsDataModel& OutDetailsDataModel) override;

private:
    TArray<TWeakObjectPtr<AMyCustomStageLight>> StageLights;
};
```

2.  **实现并注册**：
```cpp
// MyCustomStageLightDetailsGenerator.cpp
#include "MyCustomStageLightDetailsGenerator.h"
#include "MyCustomStageLight.h"

TSharedRef<IDisplayClusterDetailsDataModelGenerator> FMyCustomStageLightDetailsGenerator::MakeInstance()
{
    return MakeShared<FMyCustomStageLightDetailsGenerator>();
}

void FMyCustomStageLightDetailsGenerator::Initialize(...)
{
    // 在此处获取将要生成数据模型的 AMyCustomStageLight 实例指针
    // StageLights = ...
}

void FMyCustomStageLightDetailsGenerator::Destroy(...) { /* 清理工作 */ }

void FMyCustomStageLightDetailsGenerator::GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FDisplayClusterDetailsDataModel& OutDetailsDataModel)
{
    // 为 OutDetailsDataModel.DetailsSections 添加自定义的 Section
    // 例如，只添加“Intensity”和“Color”属性到一个新的 Section。
    FDisplayClusterDetailsDataModel::FDetailsSection CustomSection;
    CustomSection.DisplayName = NSLOCTEXT("MySection", "LightProperties", "Light Properties");
    // ... 配置 CustomSection 的 Subsections 和 Categories
    
    OutDetailsDataModel.DetailsSections.Add(CustomSection);
}
```

3.  **在模块启动时注册**：
```cpp
// 在你的编辑器模块的 StartupModule() 中
#include "DisplayClusterDetailsDataModel.h"

void FMyEditorModule::StartupModule()
{
    FDisplayClusterDetailsDataModel::RegisterDetailsDataModelGenerator<AMyCustomStageLight>(
        FGetDetailsDataModelGenerator::CreateStatic(&FMyCustomStageLightDetailsGenerator::MakeInstance)
    );
}
```

## Demo 示例

以下示例展示如何创建一个最小的数据模型生成器，为自定义 Actor 注册详情面板。

**MyDemoActorDetailsGenerator.h**
```cpp
#pragma once
#include "DisplayClusterDetailsDataModel.h"

class AMyDemoActor;

class FMyDemoActorDetailsGenerator : public IDisplayClusterDetailsDataModelGenerator
{
public:
    static TSharedRef<IDisplayClusterDetailsDataModelGenerator> MakeInstance();

    virtual void Initialize(const TSharedRef<FDisplayClusterDetailsDataModel>& InDataModel, const TSharedRef<IPropertyRowGenerator>& InPropertyRowGenerator) override;
    virtual void Destroy(const TSharedRef<FDisplayClusterDetailsDataModel>& InDataModel, const TSharedRef<IPropertyRowGenerator>& InPropertyRowGenerator) override;
    virtual void GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FDisplayClusterDetailsDataModel& OutDataModel) override;

private:
    TArray<TWeakObjectPtr<AMyDemoActor>> CachedActors;
};
```

**MyDemoActorDetailsGenerator.cpp**
```cpp
#include "MyDemoActorDetailsGenerator.h"
#include "MyDemoActor.h" // 假设这是你的自定义 Actor 类

TSharedRef<IDisplayClusterDetailsDataModelGenerator> FMyDemoActorDetailsGenerator::MakeInstance()
{
    return MakeShared<FMyDemoActorDetailsGenerator>();
}

void FMyDemoActorDetailsGenerator::Initialize(const TSharedRef<FDisplayClusterDetailsDataModel>& InDataModel, const TSharedRef<IPropertyRowGenerator>& InPropertyRowGenerator)
{
    // InDataModel->GetObjects() 可能包含多个 UObjects，你需要筛选出 AMyDemoActor
    // 这里简化为：假设列表已被正确过滤。
    // 通常，Generator 的创建是通过静态注册的委托，由系统在需要时调用。
}

void FMyDemoActorDetailsGenerator::Destroy(...) {}

void FMyDemoActorDetailsGenerator::GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FDisplayClusterDetailsDataModel& OutDataModel)
{
    // 为你的 Actor 创建一个自定义的详情节 (Section)
    FDisplayClusterDetailsDataModel::FDetailsSection DemoSection;
    DemoSection.DisplayName = FText::FromString(TEXT("Demo Actor Properties"));
    
    // 你可以创建子节 (Subsections) 以进一步组织属性
    FDisplayClusterDetailsDataModel::FDetailsSubsection MainSub;
    MainSub.DisplayName = FText::FromString(TEXT("Main"));
    DemoSection.Subsections.Add(MainSub);

    // 这里只创建结构，实际的属性过滤和定制通过 DetailCustomizationDelegate 或 Categories 完成
    // 更高级的用法可以重写 IDetailCustomization 来精确控制哪些属性显示。

    OutDataModel.DetailsSections.Add(DemoSection);
}
```

**注册（在你的编辑器模块 StartupModule 中）**：
```cpp
#include "DisplayClusterDetailsDataModel.h"

FDisplayClusterDetailsDataModel::RegisterDetailsDataModelGenerator<AMyDemoActor>(
    FGetDetailsDataModelGenerator::CreateStatic(&FMyDemoActorDetailsGenerator::MakeInstance)
);
```

## 模块依赖

本模块 (`DisplayClusterDetails`) 的功能依赖于 nDisplay 的核心和 Operator 模块。对于希望**扩展**详情面板内容的开发者，需要关注以下模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供 `ADisplayClusterRootActor` 等基础类型。 |
| `DisplayClusterOperator` | nDisplay Operator 面板模块，详情抽屉需要集成到其中。 |

*注：上表仅列出该模块独特且关键的依赖。其 `Build.cs` 还隐含依赖了常见的 `Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等标准模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 Movie Graph 输出添加 EXR 多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 MoviePipeline 中的 WarpBlendAlpha 模式合并到 WarpBlend 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机命名问题以及 MPCDI/ICVFX 着色器中的不透明度 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复在输出帧编码回退路径中未正确使用非默认 DisplayGamma 设置的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能导致的闪烁问题。 |

### 维护评价

- **维护状态**：**活跃维护**。
- **分析**：
    1.  **创建时间早**：该插件/模块创建于 2018 年，是 Epic 官方为支持企业级和虚拟制片需求而开发的核心组件。
    2.  **更新非常频繁**：仅从提供的最后几次提交记录（均在 2026 年 5 月）来看，其维护非常活跃，持续有功能增强（如 EXR 多层、模式合并）和关键 bug 修复。
    3.  **核心组件**：作为 Unreal Engine 虚拟制片和大型显示解决方案的核心部分，它会被长期支持和维护。
    4.  **已知问题/限制**：由于其复杂性和与特定硬件/软件的集成（如多 PC 同步、特定 GPU），在不同配置下可能会遇到特定问题，但 Epic 通过持续的更新来应对。
- **结论**：**强烈推荐使用**。这是用于专业虚拟制片、主题娱乐和大型沉浸式体验的标准工具，拥有来自 Epic 的官方和持续支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/in-camera-vfx-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)