# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图标、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于实现 **In-Camera VFX (ICVFX)** 和 **多机集群同步渲染** 的核心插件。它解决的核心问题是：**如何让多台 PC、多个显示输出（投影仪、LED 墙幕等）同步渲染同一个虚拟场景，实现大规模沉浸式显示或影视级虚拟制片**。

具体能力包括：

- **集群渲染（Cluster Rendering）**：将一个 UE 场景分发到多台 PC 上同步渲染，每台 PC 负责一个或多个视口（viewport），最终拼接成一个完整的大型显示画面
- **立体渲染（Stereo）**：支持左右眼立体渲染模式，用于 VR CAVE 等场景
- **投影映射（Projection / Warp & Blend）**：支持多种投影几何校正（MPCDI、Mesh warp、UV map），以及多投影仪之间的边缘融合（edge blending）
- **ICVFX 虚拟制片**：为 LED Volume（LED Volume）拍摄提供完整的虚拟制片管线，包括 nDisplay Root Actor、ICVFX Camera Component、Light Card、Inner Frustum 等
- **媒体采集与输出**：通过 SharedMemoryMedia 等模块实现高性能的帧捕获与输出
- **Movie Pipeline 集成**：支持在 Sequencer 和 Movie Render Queue 中使用 nDisplay 进行最终渲染输出
- **多用户编辑**：支持多人在编辑器中同时操作同一个 nDisplay 配置
- **远程控制**：通过 Remote Control 集成实现对 nDisplay 节点的远程参数调节

> ⚠️ 此插件**默认未启用**（`EnabledByDefault: false`），需要在项目设置中手动启用。它是 Epic 官方虚拟制片工具链的重要组成部分。

本文档重点描述 **DisplayClusterDetails** 子模块（ICVFX 详情面板），其余模块提供概览。

## 模块架构概览

nDisplay 包含 29 个模块，按功能可分为以下几组：

### 核心运行时
| 模块 | 职责 |
|---|---|
| `DisplayCluster` | 核心框架：集群同步、节点通信、渲染分发 |
| `DisplayClusterConfiguration` | nDisplay 配置资产（.ndisplay 文件）的数据模型 |
| `DisplayClusterProjection` | 投影映射与几何校正（MPCDI、mesh warp） |
| `DisplayClusterWarp` | Warp & Blend 变形和融合算法 |
| `DisplayClusterShaders` | nDisplay 专用 GPU 着色器 |
| `DisplayClusterReplication` | 集群节点间的网络数据同步 |
| `DisplayClusterMessageInterception` | 集群消息拦截与路由 |

### ICVFX 虚拟制片
| 模块 | 职责 |
|---|---|
| `DisplayClusterColorGrading` | 色彩分级面板与 LUT 管理 |
| `DisplayClusterDetails` | **ICVFX 详情面板**（本文档重点） |
| `DisplayClusterLightCardEditor` | Light Card（灯光卡片）编辑器 |
| `DisplayClusterLightCardEditorShaders` | Light Card 编辑器专用着色器 |
| `DisplayClusterStageMonitoring` | Stage（拍摄现场）状态监控 |

### 媒体与捕获
| 模块 | 职责 |
|---|---|
| `DisplayClusterMedia` | 媒体捕获与输出管线 |
| `DisplayClusterMediaEditor` | 媒体相关编辑器 UI |
| `SharedMemoryMedia` | 基于共享内存的高性能帧传输（支持 D3D12） |
| `SharedMemoryMediaEditor` | 共享内存媒体编辑器 UI |
| `DisplayClusterFillDerivedDataCache` | 衍生数据缓存预填充 |

### 编辑器工具
| 模块 | 职责 |
|---|---|
| `DisplayClusterEditor` | 主编辑器模块与资产类型注册 |
| `DisplayClusterConfigurator` | nDisplay 配置可视化编辑器 |
| `DisplayClusterOperator` | nDisplay Operator 操作面板 |
| `DisplayClusterMonitor` | 运行时状态监控器 |
| `DisplayClusterMonitorEditor` | 监控器编辑器 UI |
| `DisplayClusterScenePreview` | 场景预览渲染 |

### 影片管线与多用户
| 模块 | 职责 |
|---|---|
| `DisplayClusterMoviePipeline` | Movie Render Queue nDisplay 集成 |
| `DisplayClusterMoviePipelineEditor` | Movie Pipeline 编辑器 UI |
| `DisplayClusterMultiUser` | 多用户编辑同步 |
| `DisplayClusterRemoteControlInterceptor` | Remote Control API 拦截器 |

### 其他
| 模块 | 职责 |
|---|---|
| `DisplayClusterTests` | 自动化测试 |
| `ScalableMPCDI` | 第三方 MPCDI 格式解析库（External） |

---

## DisplayClusterDetails 子模块详解

> 将 ICVFX 详情抽屉面板添加到 nDisplay Operator 面板

### 架构设计

DisplayClusterDetails 采用 **数据模型 + 生成器模式**，将 UI 与数据解耦：

```
┌─────────────────────────────────────────────────┐
│           FDisplayClusterDetailsDrawerSingleton   │
│  (管理抽屉生命周期、状态持久化、Operator 面板集成)   │
└───────────────┬─────────────────────────────────┘
                │ 创建
                ▼
┌─────────────────────────────────────────────────┐
│           SDisplayClusterDetailsDrawer            │
│  (顶层 Widget：对象列表 + 详情面板)                │
│  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ ObjectListView   │  │  DetailsPanel         │  │
│  │ (可选对象列表)     │  │  (属性详情面板)       │  │
│  └──────────────────┘  └──────────────────────┘  │
└───────────────┬─────────────────────────────────┘
                │ 数据驱动
                ▼
┌─────────────────────────────────────────────────┐
│           FDisplayClusterDetailsDataModel         │
│  (存储属性数据、分段/子段结构)                      │
└───────────────┬─────────────────────────────────┘
                │ 由生成器填充
                ▼
┌─────────────────────────────────────────────────┐
│  FDisplayClusterDetailsGenerator_RootActor        │
│  FDisplayClusterDetailsGenerator_ICVFXCamera      │
│  (为不同 UObject 类型生成结构化属性数据)             │
└─────────────────────────────────────────────────┘
```

### 核心类说明

| 类名 | 职责 |
|---|---|
| `FDisplayClusterDetailsModule` | 模块入口，实现 `IDisplayClusterDetails` 接口 |
| `FDisplayClusterDetailsDrawerSingleton` | 单例，管理抽屉/标签页的创建、状态保存与恢复 |
| `SDisplayClusterDetailsDrawer` | 顶层 Slate Widget，包含对象列表和详情面板 |
| `FDisplayClusterDetailsDataModel` | 数据模型，存储从 UObject 提取的属性结构 |
| `IDisplayClusterDetailsDataModelGenerator` | 数据模型生成器接口，用于为不同类型对象生成属性数据 |
| `FDisplayClusterDetailsGenerator_RootActor` | 为 `ADisplayClusterRootActor` 生成详情数据 |
| `FDisplayClusterDetailsGenerator_ICVFXCamera` | 为 `UDisplayClusterICVFXCameraComponent` 生成详情数据 |
| `SDisplayClusterDetailsObjectList` | 可选对象列表 Widget |
| `SDisplayClusterDetailsPanel` | 多段详情属性面板（最多 3 段同时显示） |
| `FDisplayClusterDetailsDrawerState` | 抽屉状态快照（选中对象 + 选中子段） |

## 使用场景

- **虚拟制片（Virtual Production）**：你在使用 LED Volume 进行影视拍摄，需要在 Operator 面板中快速查看和调整 nDisplay Root Actor 及 ICVFX Camera 的属性 → 使用 Details Drawer
- **主题公园/沉浸式体验**：你需要让多台 PC 驱动多个投影仪/显示器同步渲染一个连续画面 → 使用 nDisplay 集群渲染
- **CAVE VR 环境**：你需要在四面或六面投影的 CAVE 中进行立体 VR 渲染 → 使用 nDisplay 立体渲染 + 投影映射
- **现场活动/舞台 LED 墙**：你需要将 UE 场景实时输出到大型 LED 墙幕 → 使用 nDisplay + SharedMemoryMedia
- **影视后期渲染**：你需要通过 Movie Pipeline 对 nDisplay 集群进行离线高分辨率渲染 → 使用 DisplayClusterMoviePipeline

## 蓝图用法

DisplayClusterDetails 模块本身是纯编辑器 UI 模块，不直接暴露 Blueprint API。但 nDisplay 核心模块提供了大量蓝图接口。以下是 DisplayClusterDetails 中可通过蓝图/编辑器扩展的接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DockDetailsDrawer()` | 将详情抽屉固定到 Operator 面板标签页 | `IDisplayClusterDetailsDrawerSingleton` |
| `RefreshDetailsDrawers(bPreserveState)` | 刷新所有打开的详情抽屉 UI | `IDisplayClusterDetailsDrawerSingleton` |
| `GetDetailsDrawerSingleton()` | 获取详情抽屉单例实例 | `IDisplayClusterDetails` |
| `RegisterDetailsDataModelGenerator<T>(Delegate)` | 注册自定义 UObject 类型的数据模型生成器 | `FDisplayClusterDetailsDataModel` |

### 使用示例（编辑器操作）

1. 启用 nDisplay 插件后，在编辑器中打开 **nDisplay Operator** 面板
2. 在 Operator 面板底部状态栏中，点击 **Details Drawer** 图标打开详情抽屉
3. 抽屉左侧显示当前 nDisplay Root Actor 中的可编辑对象列表（Root Actor 本身、各 ICVFX Camera Component）
4. 点击列表中的对象，右侧详情面板显示该对象的分段属性视图
5. 点击 **Dock in Layout** 按钮可将抽屉固定为 Operator 面板的一个标签页
6. 详情面板支持 **撤销/重做**（实现了 `FEditorUndoClient`）

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterDetails.h"
#include "IDisplayClusterDetailsDrawerSingleton.h"
```

### 基本用法

获取详情抽屉单例并操作它：

```cpp
// Source: Public/IDisplayClusterDetails.h, Public/IDisplayClusterDetailsDrawerSingleton.h

#include "IDisplayClusterDetails.h"

// 检查模块是否可用
if (IDisplayClusterDetails::IsAvailable())
{
    // 获取模块接口
    IDisplayClusterDetails& DetailsModule = IDisplayClusterDetails::Get();
    
    // 获取详情抽屉单例
    IDisplayClusterDetailsDrawerSingleton& DrawerSingleton = DetailsModule.GetDetailsDrawerSingleton();
    
    // 将详情抽屉固定到 Operator 面板标签页
    DrawerSingleton.DockDetailsDrawer();
    
    // 刷新所有打开的详情抽屉（保留 UI 状态）
    DrawerSingleton.RefreshDetailsDrawers(true /*bPreserveDrawerState*/);
}
```

### 注册自定义数据模型生成器

为自定义 UObject 类型生成详情面板数据：

```cpp
// Source: Private/DisplayClusterDetailsDataModel.h

#include "DisplayClusterDetailsDataModel.h"

// 1. 实现 IDisplayClusterDetailsDataModelGenerator 接口
class FMyCustomDetailsGenerator : public IDisplayClusterDetailsDataModelGenerator
{
public:
    static TSharedRef<IDisplayClusterDetailsDataModelGenerator> MakeInstance()
    {
        return MakeShared<FMyCustomDetailsGenerator>();
    }

    virtual void Initialize(
        const TSharedRef<FDisplayClusterDetailsDataModel>& DetailsDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override
    {
        // 初始化时的逻辑
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
        // 生成分段和子段数据
        FDisplayClusterDetailsDataModel::FDetailsSection MySection;
        MySection.DisplayName = FText::FromString(TEXT("My Custom Section"));
        
        // 添加子段
        FDisplayClusterDetailsDataModel::FDetailsSubsection Subsection;
        Subsection.DisplayName = FText::FromString(TEXT("Main"));
        Subsection.Categories.Add(FName("MyCategory"));
        MySection.Subsections.Add(Subsection);
        
        OutDetailsDataModel.DetailsSections.Add(MySection);
    }
};

// 2. 注册生成器（在模块启动时）
FDisplayClusterDetailsDataModel::RegisterDetailsDataModelGenerator<UMyCustomClass>(
    FGetDetailsDataModelGenerator::CreateStatic(&FMyCustomDetailsGenerator::MakeInstance)
);
```

### 进阶用法：操作数据模型

```cpp
// Source: Private/DisplayClusterDetailsDataModel.h

// 创建数据模型并设置目标对象
TSharedRef<FDisplayClusterDetailsDataModel> DataModel = MakeShared<FDisplayClusterDetailsDataModel>();

// 设置要显示详情的对象
TArray<UObject*> Objects;
Objects.Add(MyRootActor);
DataModel->SetObjects(Objects);

// 检查数据模型是否包含指定类型的对象
if (DataModel->HasObjectOfType(ADisplayClusterRootActor::StaticClass()))
{
    // 该对象已加载对应的详情生成器
}

// 获取 PropertyRowGenerator
TSharedRef<IPropertyRowGenerator> PropRowGen = DataModel->GetPropertyRowGenerator();

// 保存/恢复抽屉状态
FDisplayClusterDetailsDrawerState SavedState;
DataModel->GetDrawerState(SavedState);

// ... 稍后恢复
DataModel->SetDrawerState(SavedState);

// 监听数据模型生成完成事件
DataModel->OnDataModelGenerated().AddLambda([]()
{
    // 数据模型已更新，刷新 UI
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 属性编辑器（IPropertyRowGenerator）、编辑器撤销/重做 |
| `D3D12RHI` | DisplayClusterMedia、SharedMemoryMedia 的 D3D12 帧捕获 |
| `LevelEditor` | DisplayCluster 主模块的关卡编辑器集成 |
| `EditorWidgets` | DisplayCluster 主模块的编辑器 Widget |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 增加 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名及 MPCDI/ICVFX 着色器的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** — nDisplay 作为 Epic 虚拟制片工具链的核心组件，维护非常活跃。近一周内有 5 次提交，涵盖功能增强（EXR 多图层）、API 整合（WarpBlend 模式合并）、着色器修复和边缘情况 bug 修复。

- ✅ **活跃维护**：持续有功能性更新
- ✅ **核心地位**：Epic 官方虚拟制片管线的重要组成部分
- ⚠️ **复杂度高**：29 个模块，1351 个源文件，学习曲线陡峭
- ⚠️ **默认未启用**：需要手动在项目设置中启用
- ✅ **推荐使用**：如果需要 ICVFX 虚拟制片或多机集群渲染，这是唯一的官方解决方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/in-camera-vfx-in-unreal-engine/)