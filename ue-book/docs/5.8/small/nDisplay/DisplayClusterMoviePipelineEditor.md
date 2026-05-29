# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMediaEditor` (Runtime), `SharedMemoryMediaEditor` (Runtime), `DisplayClusterTests` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多机集群同步渲染**的核心系统。它解决的核心问题是：当你需要将一个 UE 场景同时渲染到多台 PC 驱动的多个显示器上时（例如 LED 墙、CAVE 洞穴投影、多屏环幕），如何保持各机之间的帧同步、视锥体校准和颜色一致性。

该插件不是简单的多窗口方案，而是一套完整的虚拟制片基础设施，包含：

- **集群配置与同步**：定义多台 PC 的拓扑结构（Cluster Node），确保所有机器同步渲染同一帧
- **投影与变形（Warp/Blend）**：支持 MPCDI、MESH 等格式的投影校正和边缘融合
- **ICVFX 集成**：专为 LED 墙虚拟制片（In-Camera VFX）设计，支持多视口、Light Card、颜色分级
- **媒体管线**：通过共享内存（SharedMemoryMedia）和硬件加速实现低延迟帧传输
- **Movie Pipeline 集成**：支持将 nDisplay 集群渲染用于离线渲染输出（EXR 多层等）

## 使用场景

- **LED 墙虚拟制片**：你在搭建一个 LED Volume 摄影棚 → 用 nDisplay 驱动 LED 墙显示场景背景，并同步相机视角
- **CAVE / 环幕投影**：你需要在多面投影墙上显示沉浸式 VR 环境 → 用 nDisplay 配置每面墙的投影矩阵和边缘融合
- **多屏驾驶模拟器**：你有 3-6 台显示器环绕驾驶员 → 用 nDisplay 定义每台显示器的视锥角和集群节点
- **超大分辨率输出**：需要 8K+ 分辨率输出到单块大屏 → 用多台 PC 分片渲染再拼合
- **离线渲染输出**：你需要为 nDisplay LED 墙渲染高质量 EXR 序列帧 → 用 Movie Pipeline + nDisplay 集成

## 当前子模块：DisplayClusterMoviePipelineEditor

本文档重点介绍 **DisplayClusterMoviePipelineEditor** 模块，该模块为 nDisplay 的 Movie Pipeline 集成提供编辑器端属性自定义 UI。

### 模块定位

该模块负责自定义 nDisplay Movie Pipeline 设置在 Details 面板中的显示方式，提供：

1. **节点/视口选择下拉框**：在配置电影渲染时，让用户从下拉列表中选择要渲染的 Cluster Node 或 Viewport
2. **属性面板自定义**：控制哪些属性可见、如何显示、文本替换等
3. **可搜索下拉框控件**：提供带搜索功能的自定义 ComboBox 控件

## 蓝图用法

本模块为纯编辑器定制模块，不暴露 BlueprintCallable API。nDisplay 的蓝图 API 主要位于 `DisplayCluster` 和 `DisplayClusterConfiguration` 核心模块中。

### 核心节点（来自其他子模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node Names` | 获取集群中所有节点名称 | `ADisplayClusterRootActor` |
| `Get Viewport IDs` | 获取所有视口 ID 列表 | `ADisplayClusterRootActor` |

### 配置说明

使用 Movie Pipeline 渲染 nDisplay 内容时，在 **Movie Pipeline Config** 中添加 **nDisplay 渲染设置**，Details 面板会显示自定义的节点/视口选择界面：

1. 打开 Movie Render Queue → 添加 Job → 配置 nDisplay 设置
2. 在设置中选择目标 Cluster Node（哪些 PC 参与渲染）
3. 选择目标 Viewport（渲染哪些视口）
4. 配置 WarpBlend 模式和输出格式

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMoviePipelineEditorModule.h"
```

### 基本用法：自定义属性面板布局

该模块通过 `IPropertyTypeCustomization` 接口实现属性面板自定义。以下是其核心基类的使用模式（来源：`DisplayClusterMoviePipelineEditorBaseTypeCustomization.h`）：

```cpp
// 自定义属性类型 - 控制 Details 面板的显示
class FMyTypeCustomization : public FDisplayClusterMoviePipelineEditorBaseTypeCustomization
{
public:
    static TSharedRef<IPropertyTypeCustomization> MakeInstance()
    {
        return MakeShared<FMyTypeCustomization>();
    }

protected:
    // 自定义头部显示
    virtual void SetHeader(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        FDetailWidgetRow& InHeaderRow,
        IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        InHeaderRow
        .NameContent()
        [
            InPropertyHandle->CreatePropertyNameWidget()
        ]
        .ValueContent()
        [
            InPropertyHandle->CreatePropertyValueWidget()
        ];
    }

    // 自定义子属性显示
    virtual void SetChildren(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        IDetailChildrenBuilder& InChildBuilder,
        IPropertyTypeCustomizationUtils& CustomizationUtils) override
    {
        // 只显示特定子属性
        TSharedPtr<IPropertyHandle> ChildHandle =
            GetChildHandleChecked(InPropertyHandle, TEXT("MyChildProperty"));
        if (ChildHandle.IsValid())
        {
            InChildBuilder.AddProperty(ChildHandle.ToSharedRef());
        }
    }
};
```

### 进阶用法：节点选择控件

来源：`DisplayClusterMoviePipelineEditorNodeSelection.h`

```cpp
// 创建集群节点选择数组控件
// 用于在 Details 面板中展示可选的 Cluster Node 列表
void SetupNodeSelection(IDetailChildrenBuilder& ChildBuilder)
{
    // 获取 DisplayClusterRootActor 的配置数据
    UDisplayClusterConfigurationData* ConfigData = NodeSelection->GetConfigData();
    if (!ConfigData)
    {
        return;
    }

    // 创建视口选择模式（也可以用 ClusterNodes 模式）
    auto ViewportSelection = MakeShared<FDisplayClusterMoviePipelineEditorNodeSelection>(
        FDisplayClusterMoviePipelineEditorNodeSelection::Viewports,
        DCRAPropertyHandle,
        SelectedOptionsHandle
    );

    // 可选：设置启用状态
    ViewportSelection->IsEnabled(bIsEnabled);

    // 构建下拉选择数组
    ViewportSelection->CreateArrayBuilder(PropertyHandle, ChildBuilder);
}
```

### 控件重置与刷新

```cpp
// 当集群配置发生变化时，刷新下拉列表选项
NodeSelection->ResetOptionsList();

// 获取当前配置数据
UDisplayClusterConfigurationData* ConfigData = NodeSelection->GetConfigData();
```

## Demo 示例

### 属性自定义注册示例

```cpp
// MyCustomPropertyCustomization.h
#pragma once

#include "DisplayClusterMoviePipelineEditorBaseTypeCustomization.h"

class FMyCustomPropertyCustomization
    : public FDisplayClusterMoviePipelineEditorBaseTypeCustomization
{
public:
    static TSharedRef<IPropertyTypeCustomization> MakeInstance()
    {
        return MakeShared<FMyCustomPropertyCustomization>();
    }

protected:
    virtual void Initialize(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        IPropertyTypeCustomizationUtils& CustomizationUtils) override;

    virtual void SetHeader(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        FDetailWidgetRow& InHeaderRow,
        IPropertyTypeCustomizationUtils& CustomizationUtils) override;

    virtual void SetChildren(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        IDetailChildrenBuilder& InChildBuilder,
        IPropertyTypeCustomizationUtils& CustomizationUtils) override;

private:
    TSharedPtr<FDisplayClusterMoviePipelineEditorNodeSelection> NodeSelection;
};
```

```cpp
// MyCustomPropertyCustomization.cpp
#include "MyCustomPropertyCustomization.h"
#include "DisplayClusterMoviePipelineEditorNodeSelection.h"

void FMyCustomPropertyCustomization::Initialize(
    const TSharedRef<IPropertyHandle>& InPropertyHandle,
    IPropertyTypeCustomizationUtils& CustomizationUtils)
{
    // 调用基类初始化
    FDisplayClusterMoviePipelineEditorBaseTypeCustomization::Initialize(
        InPropertyHandle, CustomizationUtils);

    // 初始化节点选择器（显示视口模式）
    NodeSelection = MakeShared<FDisplayClusterMoviePipelineEditorNodeSelection>(
        FDisplayClusterMoviePipelineEditorNodeSelection::Viewports,
        InPropertyHandle,
        InPropertyHandle->GetChildHandle(TEXT("ViewportNames"))
    );
}

void FMyCustomPropertyCustomization::SetHeader(
    const TSharedRef<IPropertyHandle>& InPropertyHandle,
    FDetailWidgetRow& InHeaderRow,
    IPropertyTypeCustomizationUtils& CustomizationUtils)
{
    InHeaderRow
    .NameContent()
    [
        InPropertyHandle->CreatePropertyNameWidget()
    ]
    .ValueContent()
    [
        SNew(STextBlock)
        .Text(FText::FromString(TEXT("nDisplay Movie Pipeline Settings")))
        .Font(IDetailLayoutBuilder::GetDetailFont())
    ];
}

void FMyCustomPropertyCustomization::SetChildren(
    const TSharedRef<IPropertyHandle>& InPropertyHandle,
    IDetailChildrenBuilder& InChildBuilder,
    IPropertyTypeCustomizationUtils& CustomizationUtils)
{
    if (NodeSelection.IsValid())
    {
        // 使用自定义的节点选择数组构建器
        NodeSelection->CreateArrayBuilder(InPropertyHandle, InChildBuilder);
    }
    else
    {
        // 回退：显示所有子属性
        AddAllChildren(InPropertyHandle, InChildBuilder);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayClusterMoviePipeline` | nDisplay Movie Pipeline 核心逻辑，提供要自定义的配置类型 |
| `DisplayClusterConfiguration` | nDisplay 集群配置数据模型 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：完整使用 nDisplay 插件还需要依赖其核心模块（DisplayCluster、DisplayClusterProjection 等），详见各子模块的 Build.cs。部分模块额外依赖 `D3D12RHI`（媒体模块）、`LevelEditor` 和 `EditorWidgets`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 添加 MovieGraph EXR 多层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 拓扑感知相机命名及 MPCDI 着色器 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

- **活跃维护** ✅：最近一次更新距今仅数天（2026-05-26），且持续有功能性更新
- **更新频率**：近一周内有 5 次提交，涵盖新功能（EXR 多层）和 Bug 修复
- **成熟度**：自 2018 年创建至今已 8 年，经过多个 UE 版本迭代，属于成熟的生产级插件
- **虚拟制片核心组件**：nDisplay 是 Epic 虚拟制片战略的核心技术栈之一，有持续的官方投入
- **模块规模**：29 个模块、1351+ 源文件，是 UE5 中最大型的插件之一
- **已知限制**：`EnabledByDefault=false`，需手动启用；部分模块标记为 Runtime 但实际依赖编辑器模块

**强烈推荐**用于虚拟制片、LED 墙、CAVE 和多屏渲染场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)