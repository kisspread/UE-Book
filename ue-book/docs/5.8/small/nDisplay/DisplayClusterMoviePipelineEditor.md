# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机集群渲染**插件，用于在多台 PC 之间实现同步的分屏/立体渲染。它解决的核心问题是：**当一台 PC 的算力不足以驱动多块高分辨率屏幕（如 CAVE、LED 墙、穹顶投影）时，如何让多台 PC 协同工作，将一个 UE5 场景同步渲染到多个物理显示器上。**

典型应用场景包括：
- **虚拟制片 LED Volume**（如《曼达洛人》那种大规模 LED 墙）
- **CAVE 沉浸式环境**（多面投影房间）
- **穹顶/球幕投影**
- **多屏赛车/飞行模拟器**
- **车展/博物馆大型显示装置**

插件内部处理了以下关键技术：
- **帧同步**：确保所有 PC 在同一帧渲染
- **视锥投影**：为每个显示节点计算正确的摄像机投影矩阵
- **Warp & Blend**：对投影画面进行几何校正和亮度混合
- **MPCDI 标准支持**：兼容行业标准的投影配置格式
- **共享内存传输**：通过 SharedMemoryMedia 模块实现低延迟帧传输
- **Movie Pipeline 集成**：支持 nDisplay 场景的离线渲染/录制

> ⚠️ 本插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你有一面由多块 LED 屏幕组成的虚拟制片墙 → 用 nDisplay 配置每块屏幕对应的视锥
- 你在搭建 CAVE 投影系统（多面墙投影）→ 用 nDisplay 配置多节点集群
- 你需要通过电影渲染管线离线输出 nDisplay 多视口画面 → 用 DisplayClusterMoviePipeline 模块
- 你需要在 Unreal Insights 或自定义监控中观察 nDisplay 集群状态 → 用 DisplayClusterStageMonitoring 模块
- 你需要通过蓝图或 Remote Control 动态调整 nDisplay 集群参数 → 用 DisplayClusterRemoteControlInterceptor 模块

## 蓝图用法

> 本章节聚焦 **DisplayClusterMoviePipelineEditor** 模块的功能。nDisplay 的核心蓝图 API（如 `ADisplayClusterRootActor`、`UDisplayClusterConfigurationData`）属于 DisplayCluster 主模块，不在本文档范围内。

DisplayClusterMoviePipelineEditor 主要提供**编辑器内属性面板的自定义 UI**，不直接暴露蓝图节点。其功能通过 Movie Pipeline 的设置面板间接影响工作流。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 本模块纯编辑器 UI 定制，不暴露 BlueprintCallable 函数 | — |

### 配置方式

在 Movie Pipeline 设置面板中，nDisplay 相关设置会以自定义 UI 呈现：

1. 在 `ULevelSequenceActor` 的 Movie Pipeline 配置中添加 nDisplay 输出
2. **Viewport 名称选择**：属性面板会显示一个**可搜索的下拉框**，列出当前集群配置中的所有 Viewport 名称
3. **Cluster Node 选择**：某些设置项会以集群节点列表下拉框呈现，方便选择目标节点

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterMoviePipelineEditor.h"
```

### 自定义属性面板（Property Type Customization）

DisplayClusterMoviePipelineEditor 的核心功能是为 nDisplay Movie Pipeline 设置提供自定义的 Details Panel 布局。以下是关键的基类用法：

```cpp
// 来源: Private/Details/DisplayClusterMoviePipelineEditorBaseTypeCustomization.h

// 自定义属性类型基类，提供以下元数据标记:
// - NoHeaderMetadataKey:       不显示类型标题（类似 ShowOnlyInnerProperties，但强制子属性归入父级分类）
// - HideChildrenMetadataKey:   不显示任何子属性
// - SubstitutionsMetadataKey:  为子属性显示文本指定替换规则
// - DefaultSubstitutionsMetadataKey: 默认替换规则

// 典型用法：派生自定义类型布局
class FMyCustomTypeCustomization : public FDisplayClusterMoviePipelineEditorBaseTypeCustomization
{
protected:
    virtual void Initialize(const TSharedRef<IPropertyHandle>& InPropertyHandle,
                            IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        // 在生成 UI 前初始化数据
    }

    virtual void SetHeader(const TSharedRef<IPropertyHandle>& InPropertyHandle,
                           FDetailWidgetRow& InHeaderRow,
                           IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        // 自定义标题行
    }

    virtual void SetChildren(const TSharedRef<IPropertyHandle>& InPropertyHandle,
                             IDetailChildrenBuilder& InChildBuilder,
                             IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        // 自定义子属性布局
    }
};
```

### 集群节点/视口选择控件

```cpp
// 来源: Private/Details/DisplayClusterMoviePipelineEditorNodeSelection.h

// 创建一个 Viewport 选择模式的下拉框数组控件
TSharedPtr<IPropertyHandle> DCRAPropertyHandle = /* 从 Details Panel 获取 */;
TSharedPtr<IPropertyHandle> SelectedOptionsHandle = /* 从 Details Panel 获取 */;

auto NodeSelection = MakeShared<FDisplayClusterMoviePipelineEditorNodeSelection>(
    FDisplayClusterMoviePipelineEditorNodeSelection::Viewports,
    DCRAPropertyHandle,
    SelectedOptionsHandle
);

// 获取集群配置数据
UDisplayClusterConfigurationData* ConfigData = NodeSelection->GetConfigData();

// 在 Details Panel 中创建自定义数组 UI
NodeSelection->CreateArrayBuilder(PropertyHandle, ChildBuilder);
```

### 可搜索下拉框控件

```cpp
// 来源: Private/Widgets/SDisplayClusterMoviePipelineEditorSearchableComboBox.h

// SDisplayClusterMoviePipelineEditorSearchableComboBox 是 SSearchableComboBox 的扩展版本
// 支持动态重置选项列表，适合频繁更新的集群配置场景

TArray<TSharedPtr<FString>> Options = { MakeShared<FString>(TEXT("node_1")), MakeShared<FString>(TEXT("node_2")) };

SNew(SDisplayClusterMoviePipelineEditorSearchableComboBox)
    .OptionsSource(&Options)
    .OnSelectionChanged_Lambda([](TSharedPtr<FString> InValue, ESelectInfo::Type) {
        // 处理选择变更
    })
    .SearchVisibility(EVisibility::Visible);
```

### 进阶用法

```cpp
// 注册自定义属性布局（在模块 StartupModule 中执行）
// 来源: Private/DisplayClusterMoviePipelineEditorModule.h

// 模块启动时注册自定义 Details Panel 布局
void FDisplayClusterMoviePipelineEditorModule::StartupModule()
{
    RegisterCustomLayouts();
}

void FDisplayClusterMoviePipelineEditorModule::ShutdownModule()
{
    UnregisterCustomLayouts();
}
```

## Demo 示例

> 本模块是纯编辑器 UI 定制模块，不提供独立的运行时功能。以下展示如何在你的项目中注册类似的自定义属性布局。

### 自定义 Movie Pipeline 属性布局

```cpp
// MyMoviePipelineTypeCustomization.h
#pragma once

#include "DisplayClusterMoviePipelineEditorBaseTypeCustomization.h"

class FMyMoviePipelineTypeCustomization
    : public FDisplayClusterMoviePipelineEditorBaseTypeCustomization
{
public:
    static TSharedRef<IPropertyTypeCustomization> MakeInstance()
    {
        return MakeShared<FMyMoviePipelineTypeCustomization>();
    }

protected:
    virtual void SetHeader(const TSharedRef<IPropertyHandle>& InPropertyHandle,
                           FDetailWidgetRow& InHeaderRow,
                           IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        // 不显示标题，子属性直接嵌入父级分类
        // 可通过在 UPROPERTY 中添加 meta=(NoHeader) 实现
    }

    virtual void SetChildren(const TSharedRef<IPropertyHandle>& InPropertyHandle,
                             IDetailChildrenBuilder& InChildBuilder,
                             IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        // 只显示特定子属性，隐藏其余
        AddAllChildren(InPropertyHandle, InChildBuilder);
    }

    virtual bool ShouldShowHeader(const TSharedRef<IPropertyHandle>& InPropertyHandle) const override
    {
        return false; // 隐藏类型标题
    }
};
```

```cpp
// MyMoviePipelineTypeCustomization.cpp
#include "MyMoviePipelineTypeCustomization.h"

// 在你的编辑器模块 StartupModule() 中注册：
// FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
// PropertyModule.RegisterCustomPropertyTypeLayout(
//     "MyStructType",
//     FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMyMoviePipelineTypeCustomization::MakeInstance)
// );
```

## 模块依赖

> 以下仅列出该插件独特且不常见的依赖。`DisplayCluster` 核心模块依赖 UnrealEd/EditorWidgets/LevelEditor 是因为包含大量编辑器集成代码。

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | DisplayClusterMedia 和 SharedMemoryMedia 使用，用于 Direct3D 12 共享纹理传输 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 标准库，用于投影配置文件的读写 |
| `DisplayClusterConfiguration` | 集群配置数据模型（运行时共享） |
| `DisplayClusterProjection` | 投影矩阵计算和视锥管理 |
| `DisplayClusterWarp` | 几何校正（Warp）和亮度混合（Blend） |
| `DisplayClusterShaders` | nDisplay 专用着色器（ICVFX、MPCDI 渲染） |
| `DisplayClusterMoviePipeline` | nDisplay Movie Pipeline 离线渲染核心逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 MovieGraph 管线添加 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 MoviePipeline 的 WarpBlendAlpha 模式合并到 WarpBlend 模式中 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机命名及 MPCDI/ICVFX 着色器的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码回退路径未遵循非默认 DisplayGamma 的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** 🟢

- **创建时间**：2018 年 6 月（UE4.20 时代），是 Epic 面向虚拟制片和主题娱乐行业的核心企业级插件
- **更新频率**：极为活跃，最近一次提交距今不到 1 天（2026-05-26），近一周内有 5 次提交
- **更新内容**：涵盖功能新增（EXR 多图层）、API 重构（合并 WarpBlendAlpha）、Bug 修复（着色器、闪烁、Gamma）等，说明项目处于快速迭代期
- **模块规模**：28+ 模块、1351 个源文件，属于 UE5 中最大的插件之一
- **限制**：默认未启用，需要手动在项目设置中开启；仅支持 Win64 和 Linux 平台；主要用于专业级显示系统，不适合一般游戏开发场景
- **推荐使用**：如果你正在做虚拟制片、CAVE、LED 墙或多屏模拟器项目，这是唯一的选择且持续得到 Epic 官方支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/getting-started-with-ndisplay-in-unreal-engine)