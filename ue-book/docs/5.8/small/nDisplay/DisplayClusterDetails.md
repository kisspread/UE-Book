# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、图标、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多台 PC 同步集群渲染**的核心系统，主要服务于以下专业场景：

- **LED 虚拟摄影棚（In-Camera VFX / ICVFX）**：通过多台渲染 PC 驱动 LED 墙，实现虚实结合的影视拍摄
- **CAVE 系统**：多投影仪组成的沉浸式显示环境
- **多屏同步输出**：需要跨多台机器同步画面的大型显示装置

该插件解决了单台 PC 无法满足超大分辨率或多视口同步渲染的问题。它通过网络协议协调多台 PC 的渲染管线，确保所有屏幕的帧同步和透视校正。其中包含 29 个子模块，覆盖从投影变形（Projection/Warp）、媒体输入输出（Media）、色彩分级（ColorGrading）、到电影管线集成（MoviePipeline）的完整功能栈。

> **注意**：该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

---

本文档聚焦于 **DisplayClusterDetails** 子模块。

# DisplayClusterDetails

> Module which adds the In-Camera VFX details drawer to the ICVFX panel

| 属性 | 值 |
|---|---|
| 中文名 | 详情面板模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterDetails` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterDetails) | |

## 用途

DisplayClusterDetails 模块为 nDisplay Operator 面板提供了一个**In-Camera VFX 属性详情抽屉（Details Drawer）**。它解决的核心问题是：在 ICVFX 工作流中，用户需要方便地查看和编辑 nDisplay 根 Actor 及其 ICVFX 相机组件的属性，而标准的细节面板不足以满足 ICVFX 专用的属性展示需求。

该模块通过**数据模型-生成器模式**（Data Model / Generator Pattern），为不同类型的 UObject（如 `ADisplayClusterRootActor`、`UDisplayClusterICVFXCameraComponent`）注册专用的数据模型生成器，从这些对象中提取并组织属性信息，然后在自定义的详情面板中以分段（Section）和子段（Subsection）的形式展示。

## 使用场景

- 你正在构建 LED 虚拟摄影棚（ICVFX）→ 使用 nDisplay Operator 面板的 Details Drawer 查看和编辑根 Actor、相机组件的属性
- 你需要快速切换和对比多个 nDisplay 对象的属性 → 通过 Details Drawer 的对象列表进行选择
- 你希望将 Details Drawer 固定到 Operator 面板的标签页中 → 使用 `DockDetailsDrawer()` 功能
- 你需要扩展自定义的属性展示 → 实现 `IDisplayClusterDetailsDataModelGenerator` 接口注册自定义生成器

## 蓝图用法

该模块主要面向 C++ 扩展，不直接暴露蓝图 API。通过 `IDisplayClusterDetails` 模块接口在 C++ 层面访问。

### 核心节点

该模块无 `UFUNCTION(BlueprintCallable)` 接口，所有交互通过模块接口和 Slate UI 进行。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterDetails.h"
#include "IDisplayClusterDetailsDrawerSingleton.h"
```

### 基本用法：访问模块单例

```cpp
// 检查模块是否可用并获取 Details Drawer 单例
if (IDisplayClusterDetails::IsAvailable())
{
    IDisplayClusterDetails& DetailsModule = IDisplayClusterDetails::Get();
    IDisplayClusterDetailsDrawerSingleton& DrawerSingleton = DetailsModule.GetDetailsDrawerSingleton();

    // 将 Details Drawer 停靠到 Operator 面板标签页中
    DrawerSingleton.DockDetailsDrawer();

    // 刷新所有已打开的 Details Drawer 的 UI（保留抽屉状态）
    DrawerSingleton.RefreshDetailsDrawers(true);
}
```

### 注册自定义数据模型生成器

```cpp
#include "DisplayClusterDetailsDataModel.h"

// 定义一个数据模型生成器，用于你的自定义 UObject 类型
class FMyCustomDataModelGenerator : public IDisplayClusterDetailsDataModelGenerator
{
public:
    static TSharedRef<IDisplayClusterDetailsDataModelGenerator> MakeInstance()
    {
        return MakeShared<FMyCustomDataModelGenerator>();
    }

    virtual void Initialize(
        const TSharedRef<FDisplayClusterDetailsDataModel>& DetailsDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override
    {
        // 初始化时的逻辑，例如绑定委托
    }

    virtual void Destroy(
        const TSharedRef<FDisplayClusterDetailsDataModel>& DetailsDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override
    {
        // 清理资源
    }

    virtual void GenerateDataModel(
        IPropertyRowGenerator& PropertyRowGenerator,
        FDisplayClusterDetailsDataModel& OutDetailsDataModel) override
    {
        // 定义详情面板的 Section 和 Subsection
        FDisplayClusterDetailsDataModel::FDetailsSection MySection;
        MySection.DisplayName = FText::FromString(TEXT("My Custom Section"));
        
        FDisplayClusterDetailsDataModel::FDetailsSubsection MySubsection;
        MySubsection.DisplayName = FText::FromString(TEXT("General"));
        MySection.Subsections.Add(MySubsection);

        OutDetailsDataModel.DetailsSections.Add(MySection);
    }
};

// 在模块启动时注册生成器
FDisplayClusterDetailsDataModel::RegisterDetailsDataModelGenerator<UMyCustomClass>(
    FGetDetailsDataModelGenerator::CreateStatic(&FMyCustomDataModelGenerator::MakeInstance));
```

### 操作数据模型

```cpp
#include "DisplayClusterDetailsDataModel.h"

// 创建并配置数据模型
TSharedRef<FDisplayClusterDetailsDataModel> DataModel = MakeShared<FDisplayClusterDetailsDataModel>();

// 设置要显示属性的对象列表
TArray<UObject*> Objects;
Objects.Add(MyRootActor);
DataModel->SetObjects(Objects);

// 检查数据模型是否包含指定类型的对象
if (DataModel->HasObjectOfType(ADisplayClusterRootActor::StaticClass()))
{
    // 处理根 Actor 的属性...
}

// 保存和恢复抽屉状态
FDisplayClusterDetailsDrawerState SavedState;
DataModel->GetDrawerState(SavedState);

// 稍后恢复
DataModel->SetDrawerState(SavedState);
```

## Demo 示例

以下示例展示如何在自己的编辑器模块中集成 DisplayClusterDetails 功能：

```cpp
// MyICVFXHelper.h
#pragma once

#include "IDisplayClusterDetails.h"
#include "IDisplayClusterDetailsDrawerSingleton.h"

class FMyICVFXHelper
{
public:
    /** 打开 nDisplay Details 并刷新以反映当前场景状态 */
    static void OpenAndRefreshDetailsDrawer()
    {
        if (!IDisplayClusterDetails::IsAvailable())
        {
            UE_LOG(LogTemp, Warning, TEXT("DisplayClusterDetails module is not available"));
            return;
        }

        IDisplayClusterDetailsDrawerSingleton& Drawer =
            IDisplayClusterDetails::Get().GetDetailsDrawerSingleton();

        // 停靠到 Operator 面板
        Drawer.DockDetailsDrawer();

        // 刷新 UI，保留之前的抽屉状态（选中对象、子段选择等）
        Drawer.RefreshDetailsDrawers(true);
    }
};
```

```cpp
// MyICVFXHelper.cpp
#include "MyICVFXHelper.h"

// 该文件中不需要额外实现，所有逻辑已在头文件中内联
// 实际使用时可在其他编辑器工具模块中调用：
//   FMyICVFXHelper::OpenAndRefreshDetailsDrawer();
```

## 模块依赖

DisplayClusterDetails 模块的 Build.cs 未列出特殊依赖项，其依赖通过 nDisplay 插件的整体模块结构隐式关联。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

> 该模块依赖 nDisplay Operator 面板（`DisplayClusterOperator`）提供宿主环境。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 集成新增 EXR 多图层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名和着色器不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

nDisplay 是 **活跃维护中** 的大型专业插件：

- **持续更新**：最近一周内有多次功能性提交（MoviePipeline、着色器修复、Gamma 支持等），表明 Epic 对该插件投入持续开发资源
- **核心产品线**：nDisplay 是 Unreal Engine 虚拟制作（Virtual Production）工作流的关键组件，不太可能被废弃
- **社区活跃**：ICVFX/LED Volume 市场持续增长，该插件有明确的商业驱动
- **模块庞大**：29 个子模块、1351 个源文件，使用时建议按需加载，避免不必要的编译开销
- **DisplayClusterDetails 模块**作为 Operator 面板的属性展示层，随 nDisplay 主体一同维护，功能稳定

**推荐使用**：如果你的项目涉及 LED 墙、多屏投影或虚拟制作，nDisplay 是官方推荐的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/ndisplay-in-unreal-engine)（nDisplay 整体文档）