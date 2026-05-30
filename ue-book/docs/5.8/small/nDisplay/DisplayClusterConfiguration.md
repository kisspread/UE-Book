# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、编辑器工具、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的专业级多机集群渲染解决方案。它解决的核心问题是：**如何让多台 PC 同步渲染并组成一个统一的大型显示系统**。

典型应用场景包括：

- **LED 虚拟摄影棚（ICVFX / In-Camera VFX）**：在 LED 墙上实时渲染虚拟场景，让真实摄像机拍摄前景演员与 LED 屏幕上的虚拟背景完美融合，这是 nDisplay 最核心的用途。支持内视锥（Inner Frustum）渲染、色键（Chromakey）、灯卡（Light Cards）、分块渲染（Tile Rendering）等高级功能。
- **CAVE / 环幕投影**：多台 PC 驱动多个投影仪，组成环形或弧形沉浸式显示环境。
- **多屏同步输出**：任何需要多个 GPU 或多台机器同步渲染到不同显示器/投影仪的场景。
- **立体（Stereo）渲染**：支持 Side-by-Side 和 Top-Bottom 立体渲染模式。
- **电影管线输出**：通过 DisplayClusterMoviePipeline 模块支持多机同步的离线渲染。

该插件 `EnabledByDefault=false`，需要在项目设置中手动启用。

## 使用场景

- 你在搭建一个 LED 虚拟摄影棚用于影视拍摄 → 使用 nDisplay 配置 ICVFX 摄像机、色键、灯卡
- 你需要多台 PC 组成 CAVE 环境进行 VR 体验 → 使用 nDisplay 配置多节点集群和投影策略
- 你想让多个显示器显示同一个 3D 场景的不同视角 → 使用 nDisplay 配置多个视口（Viewport）
- 你需要从多个摄像机视角同步录制虚拟场景 → 使用 nDisplay + MoviePipeline 模块
- 你需要在 LED 墙上实现实时色键抠像 → 使用 nDisplay 的 Chromakey 和 Light Card 功能

## 蓝图用法

nDisplay 的蓝图 API 主要集中在配置数据访问和运行时控制。以下是 DisplayClusterConfiguration 模块中暴露的关键蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewportIds` | 获取集群节点的所有视口 ID 列表 | `UDisplayClusterConfigurationClusterNode` |
| `GetViewport` | 根据 ID 获取指定视口的配置对象 | `UDisplayClusterConfigurationClusterNode` |
| `GetReferencedMeshNames` | 获取策略中引用的所有网格名称 | `UDisplayClusterConfigurationClusterNode` |
| `GetNodeIds` | 获取集群中所有节点 ID | `UDisplayClusterConfigurationCluster` |
| `GetNode` | 根据 ID 获取指定节点的配置对象 | `UDisplayClusterConfigurationCluster` |
| `GetViewportIds` (根) | 获取整个集群所有视口 ID | `UDisplayClusterConfigurationData` |
| `GetNodeIds` (根) | 获取整个集群所有节点 ID | `UDisplayClusterConfigurationData` |
| `AssignPostprocess` | 为指定节点分配后处理效果 | `UDisplayClusterConfigurationData` |
| `RemovePostprocess` | 移除指定节点的后处理效果 | `UDisplayClusterConfigurationData` |
| `GetPostprocess` | 获取指定节点的后处理配置 | `UDisplayClusterConfigurationData` |
| `GetProjectionPolicy` | 获取指定视口的投影策略 | `UDisplayClusterConfigurationData` |

### 配置数据结构

nDisplay 使用 `.ndisplay` 文件（JSON 格式）描述整个集群配置。核心数据结构层次如下：

```
UDisplayClusterConfigurationData（根容器）
├── Info                  - 配置元信息（描述、版本、资产路径）
├── Scene                 - 场景层级（摄像机、屏幕、变换）
│   ├── Cameras           - 摄像机定义（IPD、立体偏移等）
│   ├── Screens           - 屏幕定义（位置、大小）
│   └── Xforms            - 变换节点
├── Cluster               - 集群配置
│   ├── PrimaryNode       - 主节点定义（ID、端口）
│   ├── Sync              - 同步策略（渲染同步、输入同步）
│   ├── Network           - 网络设置（重试、超时）
│   ├── Failover          - 故障转移设置
│   └── Nodes             - 所有集群节点
│       └── Viewports     - 每个节点的视口列表
├── StageSettings         - ICVFX 舞台设置
│   ├── DefaultFrameSize  - 默认帧分辨率
│   ├── Lightcard         - 灯卡设置
│   ├── HideList          - 隐藏列表
│   └── GlobalChromakey   - 全局色键设置
├── RenderFrameSettings   - 渲染帧设置（RTT 缩放、缓冲比率）
└── CustomParameters      - 自定义参数
```

### 使用示例（蓝图描述）

**获取集群中所有视口并遍历：**
1. 从 nDisplay 根 Actor 获取配置数据
2. 调用 `GetNodeIds` 获取所有节点 ID
3. 对每个节点调用 `GetNode` 获取节点对象
4. 对每个节点调用 `GetViewportIds` 获取视口 ID
5. 对每个视口调用 `GetViewport` 获取视口配置

**动态分配后处理：**
1. 获取配置数据引用
2. 调用 `AssignPostprocess`，传入节点 ID、后处理 ID、类型字符串和参数 Map
3. 后处理会在下一帧生效

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterConfigurationTypes_ICVFX.h"
#include "DisplayClusterConfigurationTypes_Viewport.h"
#include "DisplayClusterConfigurationTypes_Media.h"
#include "DisplayClusterConfigurationTypes_Postprocess.h"
#include "IDisplayClusterConfiguration.h"
```

### 基本用法

从源码中提取的配置数据加载和访问示例：

```cpp
// 从 IDisplayClusterConfiguration 模块接口加载配置
// 来源: DisplayClusterConfigurationModule.h

#include "IDisplayClusterConfiguration.h"

// 获取配置模块
IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();

// 检查配置文件版本
EDisplayClusterConfigurationVersion Version = ConfigModule.GetConfigVersion(TEXT("path/to/config.ndisplay"));

// 加载配置数据
UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(TEXT("path/to/config.ndisplay"), GetTransientPackage());
if (ConfigData)
{
    // 访问集群配置
    UDisplayClusterConfigurationCluster* Cluster = ConfigData->Cluster;
    
    // 获取所有节点 ID
    TArray<FString> NodeIds;
    Cluster->GetNodeIds(NodeIds);
    
    // 遍历每个节点
    for (const FString& NodeId : NodeIds)
    {
        UDisplayClusterConfigurationClusterNode* Node = Cluster->GetNode(NodeId);
        if (Node)
        {
            // 获取节点的视口列表
            TArray<FString> ViewportIds;
            Node->GetViewportIds(ViewportIds);
            
            UE_LOG(LogTemp, Log, TEXT("Node %s has %d viewports"), *NodeId, ViewportIds.Num());
        }
    }
}
```

### 进阶用法

访问 ICVFX 配置和动态修改后处理：

```cpp
// 访问 ICVFX 舞台设置
// 来源: DisplayClusterConfigurationTypes_ICVFX.h, DisplayClusterConfigurationTypes.h

UDisplayClusterConfigurationData* ConfigData = /* 获取配置数据 */;

// 访问舞台设置
FDisplayClusterConfigurationICVFX_StageSettings& StageSettings = ConfigData->StageSettings;

// 检查内视锥是否启用
bool bInnerFrustumEnabled = StageSettings.bEnableInnerFrustums;

// 获取默认帧分辨率
int32 DefaultWidth = StageSettings.DefaultFrameSize.Width;   // 默认 2560
int32 DefaultHeight = StageSettings.DefaultFrameSize.Height; // 默认 1440
bool bAdaptSize = StageSettings.DefaultFrameSize.bAdaptSize; // 自适应分辨率

// 访问灯卡设置
const FDisplayClusterConfigurationICVFX_LightcardSettings& LightcardSettings = StageSettings.Lightcard;

// 访问全局色键设置
const FDisplayClusterConfigurationICVFX_GlobalChromakeySettings& Chromakey = StageSettings.GlobalChromakey;

// 动态分配后处理到指定节点
TMap<FString, FString> PostprocessParams;
PostprocessParams.Add(TEXT("SomeParam"), TEXT("SomeValue"));

bool bSuccess = ConfigData->AssignPostprocess(
    TEXT("node_1"),            // 节点 ID
    TEXT("my_postprocess"),    // 后处理 ID
    TEXT("some_type"),         // 类型
    PostprocessParams,         // 参数
    0                          // 渲染顺序
);

// 获取视口的投影策略
FDisplayClusterConfigurationProjection Projection;
if (ConfigData->GetProjectionPolicy(TEXT("node_1"), TEXT("viewport_1"), Projection))
{
    UE_LOG(LogTemp, Log, TEXT("Projection type: %s"), *Projection.Type);
    // Parameters 包含投影策略的具体参数
    for (const auto& ParamPair : Projection.Parameters)
    {
        UE_LOG(LogTemp, Log, TEXT("  %s = %s"), *ParamPair.Key, *ParamPair.Value);
    }
}
```

访问视口级 ICVFX 配置：

```cpp
// 访问视口的 ICVFX 自定义设置
// 来源: DisplayClusterConfigurationTypes_Viewport.h

UDisplayClusterConfigurationViewport* Viewport = /* 获取视口 */;

// 检查 ICVFX 相关设置
const FDisplayClusterConfigurationViewport_ICVFX& ICVFX = Viewport->ICVFX;

bool bAllowICVFX = ICVFX.bAllowICVFX;              // 是否允许 ICVFX
bool bAllowInnerFrustum = ICVFX.bAllowInnerFrustum; // 是否允许内视锥

// 获取渲染设置
const FDisplayClusterConfigurationViewport_RenderSettings& RenderSettings = Viewport->RenderSettings;
float BufferRatio = RenderSettings.BufferRatio;     // 缓冲比率（分辨率缩放）
int GPUIndex = Viewport->GPUIndex;                  // GPU 索引（-1 表示默认）

// 获取 ICVFX 标志
EDisplayClusterViewportICVFXFlags Flags = Viewport->GetViewportICVFXFlags(ConfigData->StageSettings);
```

### 配置序列化

```cpp
// 保存和序列化配置
// 来源: IDisplayClusterConfiguration.h, DisplayClusterConfigurationModule.h

IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();

// 保存到文件
ConfigModule.SaveConfig(ConfigData, TEXT("path/to/output.ndisplay"));

// 转换为字符串
FString ConfigString;
if (ConfigModule.ConfigAsString(ConfigData, ConfigString))
{
    UE_LOG(LogTemp, Log, TEXT("Config JSON:\n%s"), *ConfigString);
}

// 创建空白配置
UDisplayClusterConfigurationData* NewConfig = UDisplayClusterConfigurationData::CreateNewConfigData();
```

### 配置版本兼容

```cpp
// nDisplay 支持多个配置文件版本
// 来源: DisplayClusterConfigurationVersion.h

// 版本枚举
enum class EDisplayClusterConfigurationVersion : uint8
{
    Unknown,     // 未知版本
    Version_426, // 4.26 JSON 配置格式
    Version_427, // 4.27 JSON 配置格式
    Version_500, // 5.00 JSON 配置格式（当前版本）
};

// 当前版本标记为 "5.00"
```

## 模块依赖

DisplayClusterConfiguration 模块依赖关系非常简洁，几乎全部是标准模块：

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> 其他 nDisplay 子模块有一些特殊依赖：
> 
> | 模块 | 用途 |
> |---|---|
> | `D3D12RHI` | DisplayClusterMedia / SharedMemoryMedia 模块使用 D3D12 进行跨 GPU 纹理传输 |
> | `ScalableMPCDI` (External) | MPCDI 投影格式的第三方库支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 中新增 nDisplay EXR 多层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 渲染模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机命名和 MPCDI/ICVFX 着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时尊重非默认的 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

nDisplay 是 Epic Games **重点维护**的活跃插件，属于虚幻引擎企业级/虚拟制作核心功能之一。

**优势：**
- 持续活跃更新，近几个月每周都有功能改进和 bug 修复
- 模块数量达 28 个，功能覆盖面极广（配置、投影、媒体、色彩、着色器、监控、多用户协作等）
- 配置格式从 4.26 起持续演进（4.26 → 4.27 → 5.00），保持向后兼容
- 支持 Win64 和 Linux 平台

**注意事项：**
- `EnabledByDefault=false`，需要手动在项目设置中启用
- 插件总源码文件数超过 1300 个，属于超大型插件，学习曲线较陡
- 主要面向虚拟制作（Virtual Production）和主题公园等专业领域，普通游戏项目通常不需要
- 部分功能（如 RenderFamilyMode、RenderTargetAtlasing）标记为实验性但尚未实现

**推荐使用：** 如果你的项目涉及 LED 虚拟摄影棚、CAVE 环境、多机集群渲染或任何多显示器同步渲染需求，nDisplay 是唯一的官方解决方案，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)