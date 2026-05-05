# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、图标等编辑器资源） |
| 模块 | `ChaosVD` (Editor), `ChaosVDBlueprint` (Runtime), `ChaosVDBuiltInExtensions` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD) | |

## 用途

Chaos Visual Debugger (CVD) 是一个**基于 Trace 系统的 Chaos 物理模拟可视化调试工具**。它解决的核心问题是：物理模拟运行速度极快，开发者难以在运行时观察和诊断物理行为（碰撞、约束、场景查询等）。

CVD 的工作原理是：
1. **录制**：通过 UE Trace 系统将 Chaos 物理模拟的每一帧数据（粒子状态、碰撞约束、关节约束、场景查询等）序列化为二进制流
2. **回放**：在专用编辑器工具中加载录制文件，逐帧/逐阶段回放物理模拟
3. **可视化**：在 3D 视口中重建物理世界的几何体、碰撞形状、约束连线、场景查询射线等
4. **检查**：通过 Details Panel、World Outliner、Scene Query Browser 等面板深入检查任意物理对象的属性

CVD 还支持**实时会话连接**（Live Session），可以直接连接到正在运行的游戏进程，实时查看物理模拟数据，无需先录制文件。

## 使用场景

- 你在调试角色穿模问题 → 用 CVD 回放碰撞约束数据，查看碰撞检测的完整过程
- 你在排查物理关节抖动 → 用 CVD 逐帧检查关节约束的力和角度
- 你在优化物理性能 → 用 CVD 查看每个 Solver 的帧阶段耗时分布
- 你在调试网络物理同步 → 用 CVD 的 NetworkTick 同步模式对比服务器/客户端的物理状态
- 你需要在 Dedicated Server 上调试物理 → CVD 支持独立程序模式（ChaosVisualDebugger Program）
- 你需要扩展物理调试功能 → 通过 CVD Extension 系统注册自定义数据处理器、可视化器和标签页

## 架构概览

CVD 采用模块化架构，核心组件关系如下：

```
FChaosVDModule (模块入口)
  ├── FChaosVDTraceManager (Trace 会话管理)
  │     └── FChaosVDTraceProvider (数据提供者)
  │           └── FChaosVDDataProcessorBase (数据处理器)
  ├── FChaosVDEngine (核心引擎，每个 CVD 实例一个)
  │     ├── FChaosVDPlaybackController (回放控制)
  │     └── FChaosVDScene (场景重建)
  │           ├── AChaosVDDataContainerBaseActor (数据容器 Actor)
  │           ├── FChaosVDSceneParticle (粒子场景对象)
  │           ├── FChaosVDGeometryBuilder (几何体构建)
  │           └── FChaosVDSceneStreaming (场景流式加载)
  ├── SChaosVDMainTab (主 UI 面板)
  │     ├── FChaosVDPlaybackViewportTab (回放视口)
  │     ├── FChaosVDWorldOutlinerTab (场景大纲)
  │     ├── FChaosVDObjectDetailsTab (详情面板)
  │     ├── FChaosVDSolversTracksTab (Solver 时间线)
  │     └── FChaosVDSceneQueryBrowser (场景查询浏览器)
  └── FChaosVDExtensionsManager (扩展系统)
        └── FChaosVDExtension (扩展基类)
```

## 核心概念

### 录制与回放

CVD 使用 UE 的 **Trace** 基础设施进行数据录制。物理模拟数据被序列化为二进制格式，包含：
- **Game Frame Data**：游戏线程帧数据
- **Solver Frame Data**：每个物理 Solver 的帧数据
- **Frame Stage Data**：帧内的各个阶段（BroadPhase、NarrowPhase、Constraint 等）

回放由 `FChaosVDPlaybackController` 控制，支持：
- 逐帧/逐阶段播放
- 多 Solver 时间线同步（RecordedTimestamp / NetworkTick / Independent 模式）
- 多录制文件合并加载

### 场景流式加载

`FChaosVDSceneStreaming` 实现了伪 Level Streaming 系统，用于处理大型物理场景。它基于 AABB 空间加速结构，根据摄像机位置决定哪些物理对象需要完整加载/卸载，避免一次性加载所有数据导致内存溢出。

### 扩展系统

CVD 提供了 `FChaosVDExtension` 扩展基类，允许第三方插件：
- 注册自定义数据处理器（`RegisterDataProcessorsInstancesForProvider`）
- 注册自定义组件可视化器（`RegisterComponentVisualizers`）
- 注册自定义标签页（`RegisterCustomTabSpawners`）
- 自定义 Details Panel 属性布局（`SetCustomPropertyLayouts`）
- 响应回放状态变化（`HandlePlaybackControllerDataUpdated`、`HandleControllerTrackFrameUpdated`）

### TEDS 集成

CVD 深度集成了 UE 的 **Typed Element Data Storage (TEDS)** 系统，通过 `FStructTypedElementData` 将 UStruct 类型的物理数据（粒子、约束等）注册为 Typed Element，使其能够参与 UE 的统一选择系统和 Scene Outliner。

## 蓝图用法

CVD 主要是编辑器工具，大部分 API 为 C++ 专用。`ChaosVDBlueprint` 模块（RuntimeAndProgram 类型）提供运行时可访问的接口，但核心可视化调试功能不暴露给蓝图。

### 可用的 UObject 类

| 类 | 说明 |
|---|---|
| `UChaosVDCoreSettings` | CVD 核心设置（材质引用、天空球等） |
| `UChaosVDSettingsObjectBase` | 所有 CVD 设置的基类，支持配置持久化 |
| `UChaosVDVisualizationSettingsObjectBase` | 可视化设置基类，修改时自动刷新视口 |
| `UChaosVDSelectionInterface` | TEDS 选择接口实现 |
| `UChaosVDSolverDataComponent` | Solver 数据组件基类 |
| `UChaosVDParticleDataComponent` | 粒子数据组件，管理单个 Solver 的所有粒子 |

### 可用的 USTRUCT 类型

| 结构体 | 说明 |
|---|---|
| `FChaosVDSceneParticle` | 场景中的粒子对象，包含几何体、碰撞数据、可见性状态 |
| `FChaosVDBaseSceneObject` | 所有 CVD 场景对象的基类，支持 TEDS 集成 |
| `FChaosVDTrackInfo` | 回放轨道信息（ID、类型、当前帧、同步状态等） |
| `FChaosVDSceneCompositionTestData` | 场景组合测试数据，用于功能测试 |
| `FChaosVDExtractedGeometryDataHandle` | 从隐式对象提取的几何体数据句柄 |
| `FChaosVDMeshDataInstanceState` | 网格实例状态，用于 Details Panel 显示 |
| `FChaosVDImplicitObjectBasicView` | 隐式对象基本信息视图 |

## C++ 用法

### 头文件引入

```cpp
// 核心引擎
#include "ChaosVDEngine.h"
#include "ChaosVDModule.h"

// 场景管理
#include "ChaosVDScene.h"
#include "ChaosVDSceneParticle.h"

// 回放控制
#include "ChaosVDPlaybackController.h"

// Trace 系统
#include "Trace/ChaosVDTraceManager.h"
#include "Trace/ChaosVDTraceProvider.h"

// 扩展系统
#include "ExtensionsSystem/ChaosVDExtension.h"
#include "ExtensionsSystem/ChaosVDExtensionsManager.h"

// 可视化
#include "Visualizers/ChaosVDComponentVisualizerBase.h"
#include "Visualizers/ChaosVDDebugDrawUtils.h"

// 设置
#include "Settings/ChaosVDCoreSettings.h"
#include "ChaosVDSettingsManager.h"
```

### 基本用法：获取 CVD 模块实例

```cpp
// 获取 CVD 模块实例
FChaosVDModule& CVDModule = FChaosVDModule::Get();

// 获取 Trace 管理器
TSharedPtr<FChaosVDTraceManager> TraceManager = CVDModule.GetTraceManager();

// 生成一个新的 CVD 标签页实例
CVDModule.SpawnCVDTab();

// 检查是否以独立 ChaosVisualDebugger 程序运行
bool bIsStandalone = FChaosVDModule::IsStandaloneChaosVisualDebugger();
```

### 基本用法：加载录制文件

```cpp
// 假设已获取 FChaosVDEngine 实例
TSharedPtr<FChaosVDEngine> Engine = /* ... */;

// 加载单个录制文件（替换当前加载的数据）
Engine->LoadRecording(TEXT("path/to/recording.cvd"), EChaosVDLoadRecordedDataMode::SingleSource);

// 加载并合并到当前数据
Engine->LoadRecording(TEXT("path/to/another.cvd"), EChaosVDLoadRecordedDataMode::MultiSource);

// 连接到实时会话
Engine->ConnectToLiveSession(SessionID, TEXT("192.168.1.100"));

// 保存当前打开的会话为合并文件
Engine->SaveOpenSessionToCombinedFile(TEXT("path/to/combined.cvd"));
```

### 基本用法：设置管理

```cpp
#include "ChaosVDSettingsManager.h"

// 获取设置管理器
FChaosVDSettingsManager& SettingsManager = FChaosVDSettingsManager::Get();

// 获取核心设置对象（如果不存在会自动创建）
UChaosVDCoreSettings* CoreSettings = SettingsManager.GetSettingsObject<UChaosVDCoreSettings>();

// 重置设置到 CDO 默认值
SettingsManager.ResetSettings<UChaosVDCoreSettings>();
```

### 进阶用法：创建自定义扩展

```cpp
#include "ExtensionsSystem/ChaosVDExtension.h"
#include "ExtensionsSystem/ChaosVDExtensionsManager.h"

class FMyCustomCVDExtension : public FChaosVDExtension
{
public:
    FMyCustomCVDExtension()
    {
        ExtensionName = FName("MyCustomExtension");
    }

    // 注册自定义数据处理器
    virtual void RegisterDataProcessorsInstancesForProvider(
        const TSharedRef<FChaosVDTraceProvider>& InTraceProvider) override
    {
        auto MyProcessor = MakeShared<FMyCustomDataProcessor>(TEXT("MyCustomDataType"));
        InTraceProvider->RegisterDataProcessor(MyProcessor);
    }

    // 注册自定义组件可视化器
    virtual void RegisterComponentVisualizers(
        const TSharedRef<SChaosVDMainTab>& InCVDToolKit) override
    {
        // 注册自定义可视化器...
    }

    // 注册自定义标签页
    virtual void RegisterCustomTabSpawners(
        const TSharedRef<SChaosVDMainTab>& InParentTabWidget) override
    {
        // 注册自定义标签页...
    }

    // 响应回放数据更新
    virtual void HandlePlaybackControllerDataUpdated(
        TWeakPtr<FChaosVDPlaybackController> InController) override
    {
        if (TSharedPtr<FChaosVDPlaybackController> Controller = InController.Pin())
        {
            // 处理新数据...
        }
    }
};

// 注册扩展
TSharedRef<FMyCustomCVDExtension> MyExtension = MakeShared<FMyCustomCVDExtension>();
FChaosVDExtensionsManager::Get().RegisterExtension(MyExtension);
```

### 进阶用法：自定义数据处理器

```cpp
#include "Trace/DataProcessors/ChaosVDDataProcessorBase.h"

class FMyCustomDataProcessor : public FChaosVDDataProcessorBase
{
public:
    explicit FMyCustomDataProcessor(FStringView InCompatibleType)
        : FChaosVDDataProcessorBase(InCompatibleType)
    {
    }

    virtual bool ProcessRawData(const TArray<uint8>& InData) override
    {
        // 使用 Chaos::VisualDebugger::ReadDataFromBuffer 反序列化数据
        FMyCustomDataStruct MyData;
        TSharedPtr<FChaosVDTraceProvider> Provider = TraceProvider.Pin();

        if (Chaos::VisualDebugger::ReadDataFromBuffer(InData, MyData, Provider.ToSharedRef()))
        {
            // 处理解析后的数据...
            ProcessedBytes += InData.Num();
            return true;
        }
        return false;
    }
};
```

### 进阶用法：场景选择观察者

```cpp
#include "ChaosVDSceneSelectionObserver.h"

class FMySelectionObserver : public FChaosVDSceneSelectionObserver
{
protected:
    virtual void HandlePreSelectionChange(
        const UTypedElementSelectionSet* SelectionSetPreChange) override
    {
        // 选择即将改变前的处理
    }

    virtual void HandlePostSelectionChange(
        const UTypedElementSelectionSet* ChangedSelectionSet) override
    {
        // 选择已改变后的处理
        // 可以查询 ChangedSelectionSet 获取当前选中的对象
    }
};
```

### 进阶用法：Debug Draw 工具

```cpp
#include "Visualizers/ChaosVDDebugDrawUtils.h"

// 在组件可视化器中绘制调试信息
void DrawMyDebugData(FPrimitiveDrawInterface* PDI, const FTransform& WorldTransform)
{
    // 绘制箭头
    FChaosVDDebugDrawUtils::DrawArrowVector(
        PDI,
        WorldTransform.GetLocation(),
        WorldTransform.GetLocation() + WorldTransform.GetRotation().GetForwardVector() * 100.0f,
        NSLOCTEXT("MyDebug", "Force", "Force Vector"),
        FColor::Red
    );

    // 绘制球体
    FChaosVDDebugDrawUtils::DrawSphere(
        PDI,
        WorldTransform.GetLocation(),
        50.0f,
        16,
        FColor::Green,
        NSLOCTEXT("MyDebug", "Bounds", "Bounding Sphere")
    );

    // 绘制隐式对象
    FChaosVDDebugDrawUtils::DrawImplicitObject(
        PDI,
        GeometryBuilder,
        MyImplicitObject,
        WorldTransform,
        FColor::Blue,
        NSLOCTEXT("MyDebug", "Shape", "Physics Shape")
    );

    // 绘制屏幕文字
    FChaosVDDebugDrawUtils::DrawText(
        NSLOCTEXT("MyDebug", "Info", "Debug Info"),
        WorldTransform.GetLocation(),
        FColor::White,
        EChaosVDDebugDrawTextLocationMode::Screen
    );
}
```

## Demo 示例

### 自定义 CVD 扩展插件

以下示例展示如何创建一个最小的 CVD 扩展，在 CVD 中注册自定义数据处理器。

**MyCVDExtension.h**

```cpp
#pragma once

#include "ExtensionsSystem/ChaosVDExtension.h"
#include "Trace/DataProcessors/ChaosVDDataProcessorBase.h"

// 自定义数据处理器
class FMyPhysicsDataProcessor : public FChaosVDDataProcessorBase
{
public:
    FMyPhysicsDataProcessor()
        : FChaosVDDataProcessorBase(TEXT("MyPhysicsData"))
    {
    }

    virtual bool ProcessRawData(const TArray<uint8>& InData) override
    {
        // 反序列化并处理自定义物理数据
        TSharedPtr<FChaosVDTraceProvider> Provider = TraceProvider.Pin();
        if (!Provider.IsValid())
        {
            return false;
        }

        // 在此处处理数据...
        ProcessedBytes += InData.Num();
        return true;
    }
};

// 自定义 CVD 扩展
class FMyCVDExtension : public FChaosVDExtension
{
public:
    FMyCVDExtension();
    virtual ~FMyCVDExtension() = default;

    virtual void RegisterDataProcessorsInstancesForProvider(
        const TSharedRef<FChaosVDTraceProvider>& InTraceProvider) override;

    virtual void HandlePlaybackControllerDataUpdated(
        TWeakPtr<FChaosVDPlaybackController> InController) override;
};
```

**MyCVDExtension.cpp**

```cpp
#include "MyCVDExtension.h"
#include "ExtensionsSystem/ChaosVDExtensionsManager.h"
#include "Trace/ChaosVDTraceProvider.h"

FMyCVDExtension::FMyCVDExtension()
{
    ExtensionName = FName("MyPhysicsExtension");
}

void FMyCVDExtension::RegisterDataProcessorsInstancesForProvider(
    const TSharedRef<FChaosVDTraceProvider>& InTraceProvider)
{
    // 注册自定义数据处理器
    auto Processor = MakeShared<FMyPhysicsDataProcessor>();
    InTraceProvider->RegisterDataProcessor(Processor);
}

void FMyCVDExtension::HandlePlaybackControllerDataUpdated(
    TWeakPtr<FChaosVDPlaybackController> InController)
{
    if (TSharedPtr<FChaosVDPlaybackController> Controller = InController.Pin())
    {
        // 当新数据加载时，执行自定义逻辑
    }
}

// 在模块启动时注册扩展
class FMyCVDExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        Extension = MakeShared<FMyCVDExtension>();
        FChaosVDExtensionsManager::Get().RegisterExtension(Extension.ToSharedRef());
    }

    virtual void ShutdownModule() override
    {
        if (Extension.IsValid())
        {
            FChaosVDExtensionsManager::Get().UnRegisterExtension(Extension.ToSharedRef());
        }
    }

private:
    TSharedPtr<FMyCVDExtension> Extension;
};
```

## 内置标签页

CVD 内置了以下标签页（通过 `FChaosVDTabID` 定义）：

| 标签页 ID | 说明 |
|---|---|
| `ChaosVisualDebuggerTab` | 主 CVD 标签页 |
| `PlaybackViewport` | 3D 回放视口 |
| `WorldOutliner` | 场景大纲（显示粒子、约束等层级） |
| `DetailsPanel` | 选中对象的详情面板 |
| `IndependentDetailsPanel1-4` | 4 个独立详情面板（可同时查看多个对象） |
| `OutputLog` | 输出日志 |
| `SolversTrack` | Solver 时间线（帧/阶段导航） |
| `StatusBar` | 状态栏 |
| `CollisionDataDetails` | 碰撞数据详情 |
| `SceneQueryDataDetails` | 场景查询数据详情 |
| `ConstraintsInspector` | 约束检查器 |
| `SceneQueryBrowser` | 场景查询浏览器 |
| `RecordedOutputLog` | 录制的输出日志 |

## 可视化标志系统

CVD 使用位标志系统控制可视化内容的显示/隐藏：

### 粒子隐藏标志 (`EChaosVDHideParticleFlags`)

| 标志 | 说明 |
|---|---|
| `HiddenByVisualizationFlags` | 被可视化标志设置隐藏 |
| `HiddenBySceneOutliner` | 被场景大纲手动隐藏 |
| `HiddenByActiveState` | 因非活跃状态隐藏（已销毁的粒子） |
| `HiddenBySolverVisibility` | 因所属 Solver 不可见而隐藏 |

### 粒子脏标志 (`EChaosVDSceneParticleDirtyFlags`)

| 标志 | 说明 |
|---|---|
| `Visibility` | 可见性已改变 |
| `Coloring` | 颜色已改变 |
| `Active` | 活跃状态已改变 |
| `Transform` | 变换已改变 |
| `Parent` | 父对象已改变 |
| `Geometry` | 几何体已改变 |
| `CollisionData` | 碰撞数据已改变 |
| `TEDS` | TEDS 数据需要同步 |
| `StreamingBounds` | 流式加载边界已改变 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心（隐式对象、Solver 数据等） |
| `TraceServices` | UE Trace 分析服务（录制数据解析） |
| `TypedElementFramework` | Typed Element 框架（统一选择系统） |
| `EditorDataStorage` | TEDS 编辑器数据存储 |
| `EditorDataStorageFeatures` | TEDS 功能特性 |
| `GeometryProcessing` | 几何体处理（隐式对象转网格） |
| `ToolWidgets` | 编辑器工具控件 |
| `ToolMenus` | 编辑器菜单系统 |

## 维护状态

### 近期更新

```
- 0967fc00b808 [ChaosVD] Fix for a random crash caused by an array being accessed from multiple thread without a read lock in some places.
- a4bb1dcc9156 [ChaosVD] Removing visibility of the Transport mode override from the settings menu.
- d306792863f9 [ChaosVD] Fixed an issue where FChaosVDTraceManager::GetTraceFileNameFromStoreForSession returned an invalid file path.
```

### 维护评价

Chaos Visual Debugger 是一个**活跃维护中**的编辑器工具插件，由 Epic Games 官方团队开发和维护。

**优势**：
- 创建于 2023 年 3 月，至今约 2 年，仍在持续更新
- 近期提交均为 bug 修复（线程安全、路径修复、UI 调整），说明基础功能已稳定
- 架构设计良好，支持扩展系统，便于第三方插件集成
- 深度集成 UE 的 Trace、TEDS 等现代基础设施
- 支持实时会话和录制回放两种调试模式

**注意事项**：
- `.uplugin` 标记为 `IsBetaVersion: true`，API 可能在未来版本中发生变化
- 作为编辑器工具，不适用于运行时场景
- 大型物理场景的录制文件可能非常大，需要注意磁盘空间
- 多线程访问需要特别注意锁的使用（从近期 bug fix 可见）

**推荐使用**：✅ 强烈推荐。这是 UE5 中调试 Chaos 物理模拟的**官方标准工具**，对于任何涉及 Chaos 物理的项目都是必备的调试工具。即使标记为 Beta，其核心功能已经相当成熟和稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD)
- 官方文档（暂无）