# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置文件、蓝图资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterScenePreview` (Runtime), `SharedMemoryMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现多PC同步集群渲染的高级框架。它解决的核心问题是：如何将一个大型的、可能跨越多个物理显示器或投影仪的复杂视图（如大型LED虚拟制作舞台、穹顶投影、多屏模拟器），在多台联网的PC上进行实时、精确的同步渲染和输出。它不仅仅是多屏显示，更是一个完整的集群渲染管理系统，包含了视图投射、几何变形校正、色彩管理、同步帧控制等关键功能，确保从任何角度看，所有屏幕上的画面都能无缝拼合成一个完整的场景。

## 使用场景

- 你在搭建一个电影或广告拍摄用的大型LED虚拟制作舞台（Virtual Production Volume）→ 用 nDisplay 来同步驱动每台渲染节点PC，管理每一块LED屏幕的视图投射和变形。
- 你为一个博物馆或展览设计一个360度穹顶投影或环绕式沉浸式体验 → 用 nDisplay 来精确控制每台投影仪的画面，并进行边缘融合。
- 你在开发一个专业的飞行/驾驶模拟器，需要多个屏幕组成一个大的视景系统 → 用 nDisplay 来同步生成不同方向的视图（如前视、侧视、后视镜）。
- 你需要一个稳定的、可管理的多PC渲染集群，用于大型项目的后期渲染或可视化预览。

## 蓝图用法

nDisplay 的大部分核心配置和逻辑通过编辑器工具和配置资产完成，但也暴露了一些用于运行时控制的蓝图接口。

### 核心设置节点

通过 `UDisplayClusterEditorSettings` 对象，可以在蓝图中动态查询或修改插件的编辑器行为设置。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get bEnabled` | 读取“自动覆盖引擎类和设置”选项的状态。 | `UDisplayClusterEditorSettings` |
| `Set bEnabled` | 设置“自动覆盖引擎类和设置”选项（需重启引擎生效）。 | `UDisplayClusterEditorSettings` |
| `Get bClusterReplicationEnabled` | 读取是否启用集群复制（替换NetDriver）的状态。 | `UDisplayClusterEditorSettings` |

### PIE 会话控制

`UDisplayClusterEditorEngine` 提供了与编辑器播放（PIE）相关的代理和控制功能，可在蓝图中监听。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnBeginPIE` (事件) | 当 PIE 会话开始时触发，可用于初始化 nDisplay 集群会话。 | `UDisplayClusterEditorEngine` |
| `OnEndPIE` (事件) | 当 PIE 会话结束时触发，可用于清理 nDisplay 集群会话。 | `UDisplayClusterEditorEngine` |

### 使用示例

1.  **在蓝图中监听PIE开始以启动集群**：在某个 Actor 或 Game Instance 的蓝图中，绑定到 `UDisplayClusterEditorEngine` 的 `OnBeginPIE` 事件。在事件触发时，执行 `nDisplay` 的启动集群节点（通常通过其他管理类暴露，如 `DisplayCluster` 子系统），传入集群配置资产。
2.  **动态调整编辑器设置**：创建一个编辑器工具蓝图，通过 `Get Default Display Cluster Editor Settings` 节点获取 `UDisplayClusterEditorSettings` 的单例。然后通过 `Set bClusterReplicationEnabled` 节点，在需要时动态启用或禁用集群复制功能。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterEditorModule.h"
#include "DisplayClusterEditorEngine.h"
#include "DisplayClusterEditorSettings.h"
```

### 基本用法

从提供的头文件中可以看出，`UDisplayClusterEditorEngine` 是核心的引擎扩展类。

```cpp
// 在 C++ 中访问 nDisplay 编辑器设置
// 来源: DisplayClusterEditorSettings.h
UDisplayClusterEditorSettings* Settings = GetMutableDefault<UDisplayClusterEditorSettings>();
if (Settings)
{
    // 检查 nDisplay 是否激活了引擎覆盖
    bool bIsEnabled = Settings->bEnabled;
    UE_LOG(LogDisplayClusterEditor, Log, TEXT("nDisplay engine override enabled: %s"), bIsEnabled ? TEXT("Yes") : TEXT("No"));
}
```

### 进阶用法

监听 PIE 会话并管理 nDisplay 会话生命周期是核心用法。`UDisplayClusterEditorEngine` 通过委托暴露了这些事件。

```cpp
// 在某个编辑器插件或工具类中，监听 PIE 开始/结束事件
// 来源: DisplayClusterEditorEngine.h (基于其成员变量结构推断)
UDisplayClusterEditorEngine* EditorEngine = Cast<UDisplayClusterEditorEngine>(GEditor);
if (EditorEngine)
{
    // 绑定 BeginPIE 委托 (假设存在相应的 delegate getter)
    EditorEngine->OnBeginPIEDelegate.AddLambda([](bool bSimulate)
    {
        UE_LOG(LogDisplayClusterEditor, Log, TEXT("PIE session started (Simulate: %d). Initializing nDisplay cluster..."), bSimulate);
        // 在此处调用启动 nDisplay 集群的逻辑
    });

    // 绑定 EndPIE 委托
    EditorEngine->OnEndPIEDelegate.AddLambda([](bool bSimulate)
    {
        UE_LOG(LogDisplayClusterEditor, Log, TEXT("PIE session ended. Shutting down nDisplay cluster..."));
        // 在此处调用关闭 nDisplay 集群的逻辑
    });
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在编辑器中获取和使用 nDisplay 编辑器设置。

**NDisplayDemoHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "DisplayClusterEditorSettings.h"
#include "NDisplayDemoHelper.generated.h"

UCLASS()
class UNDisplayDemoHelper : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 检查并打印 nDisplay 的当前编辑器配置状态。 */
    UFUNCTION(BlueprintCallable, Category = "nDisplayDemo")
    void CheckEditorSettings() const;
};
```

**NDisplayDemoHelper.cpp**
```cpp
#include "NDisplayDemoHelper.h"
#include "DisplayClusterEditorLog.h"

void UNDisplayDemoHelper::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogDisplayClusterEditor, Log, TEXT("nDisplay Demo Helper Initialized."));
}

void UNDisplayDemoHelper::Deinitialize()
{
    UE_LOG(LogDisplayClusterEditor, Log, TEXT("nDisplay Demo Helper Deinitialized."));
    Super::Deinitialize();
}

void UNDisplayDemoHelper::CheckEditorSettings() const
{
    const UDisplayClusterEditorSettings* Settings = GetDefault<UDisplayClusterEditorSettings>();
    if (Settings)
    {
        UE_LOG(LogDisplayClusterEditor, Display, TEXT("=== nDisplay Editor Settings ==="));
        UE_LOG(LogDisplayClusterEditor, Display, TEXT("Engine Override Enabled: %s"), Settings->bEnabled ? TEXT("TRUE") : TEXT("FALSE"));
        UE_LOG(LogDisplayClusterEditor, Display, TEXT("Cluster Replication Enabled: %s"), Settings->bClusterReplicationEnabled ? TEXT("TRUE") : TEXT("FALSE"));
        UE_LOG(LogDisplayClusterEditor, Display, TEXT("================================"));
    }
    else
    {
        UE_LOG(LogDisplayClusterEditor, Warning, TEXT("Could not access UDisplayClusterEditorSettings."));
    }
}
```

## 模块依赖

nDisplay 插件包含多个模块，使用者在自己的 `Build.cs` 中需要根据实际功能引入对应的依赖。核心的 `DisplayCluster` 模块提供了最基础的运行时接口。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供根 Actor、集群同步、输入处理等基础功能。 |
| `DisplayClusterConfiguration` | 处理 nDisplay 集群的配置文件（.ndisplay 资产）的解析和管理。 |
| `DisplayClusterProjection` | 负责多屏幕、多投影仪的视图投射和几何变形（MPCDI, Simple）。 |
| `DisplayClusterWarp` | 实现更高级的几何变形（Warping）和色彩校正功能。 |
| `DisplayClusterMedia` | 处理与 Media 框架的集成，用于外部视频输入输出。 |
| `SharedMemoryMedia` | 提供基于共享内存的高性能媒体纹理传输机制。 |
| `DisplayClusterMultiUser` | 支持多用户编辑和协作时的 nDisplay 会话同步。 |
| `ScalableMPCDI` | 第三方库，用于解析和加载 `.mpcdi` 变形配置文件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影图中的 nDisplay 添加 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了 MoviePipeline 中的扭曲混合模式，简化配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知的相机命名和着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在回退编码时未尊重自定义 DisplayGamma 设置的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了 GUI 纹理尺寸小于视口尺寸时导致的闪烁问题。 |

### 维护评价

**活跃维护**。nDisplay 是一个处于持续活跃开发状态的成熟插件。
- **创建时间**：8年前（2018年），是 UE 中较早的集群渲染解决方案之一。
- **最近更新频率**：非常频繁，在 2026 年 5 月的最后一周内有多次功能增强和问题修复提交。
- **维护内容**：近期的更新主要集中在电影渲染管线（MoviePipeline）的集成改进、着色器修复以及与新版渲染功能的兼容性，表明 Epic 对此插件在虚拟制作（Virtual Production）领域的发展非常重视。
- **已知限制**：配置复杂，学习曲线较陡峭。依赖特定的网络和硬件环境。
- **推荐使用**：**强烈推荐**用于任何需要多PC同步渲染的专业场景，特别是虚拟制作项目。尽管配置复杂，但其功能强大、稳定且得到官方积极支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) (通常位于插件自身的 `Tests` 目录)