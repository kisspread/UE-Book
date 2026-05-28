# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | Chaos物理调试器 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、UI组件、性能指标、调试可视化） |
| 模块 | `ChaosVD` (EditorAndProgram), `ChaosVDBlueprint` (RuntimeAndProgram), `ChaosVDBuiltInExtensions` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD) | |

## 用途

ChaosVD 并非一个简单的物理可视化工具，而是一套完整的、用于 **录制、回放和分析** Chaos 物理模拟数据的工具套件。它解决了在复杂物理场景中难以调试和理解系统行为的问题。开发者可以通过它：
1.  **记录完整的物理模拟过程**，包括每一帧的粒子状态、约束、加速度结构和自定义调试绘制信息。
2.  **在编辑器中离线回放和检查**这些记录的数据，无需实时运行游戏。
3.  **进行深入的性能和结构分析**，例如通过热力图查看物理计算的负载分布，或可视化碰撞检测使用的AABB树。
4.  **扩展其功能**，通过插件系统添加自定义的调试数据类型和可视化器。

## 使用场景

-   你需要**调试复杂的物理交互或碰撞问题**，需要查看每一步的模拟状态 → 使用 `ChaosVD` 主工具进行录制和回放。
-   你需要**分析物理模拟的性能瓶颈**，想知道哪些区域的物理计算最密集 → 使用 `ChaosVDBuiltInExtensions` 中的性能指标查看器。
-   你需要**可视化碰撞检测所使用的空间数据结构（如AABB树）**，以理解物体是如何被快速筛选的 → 使用加速度结构可视化器。
-   你需要**跟踪特定游戏摄像机的视角**，以在调试视图中重现玩家看到的场景 → 使用相机轨迹跟踪功能。
-   你需要为ChaosVD**添加自定义的调试数据类型**（如绘制自定义的调试形状） → 实现一个继承自 `FChaosVDExtension` 的扩展。

## 蓝图用法

ChaosVD 主要是一个**编辑器工具**，其核心功能通过编辑器UI和命令触发。但其 `ChaosVDBlueprint` 模块可能为运行时提供了一些蓝图接口（例如控制录制）。具体的蓝图节点需要查看该模块的API。

### 核心操作（编辑器内）

主要操作通过ChaosVD的主编辑器窗口菜单和工具栏完成。
-   **开始/停止录制**：控制物理模拟数据的记录。
-   **回放控制**：在时间轴上前进、后退、暂停。
-   **选择查看对象**：在列表中选择特定的Solver或粒子，以聚焦其在视口中的显示。
-   **打开分析窗口**：如性能指标查看器、加速度结构查看器等。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVDBuiltInExtensions.h"
```

### 基本用法 - 扩展ChaosVD

ChaosVD 具有高度可扩展性。你可以创建自己的扩展来添加新的数据类型和可视化。

```cpp
// 文件路径：Engine/Plugins/ChaosVD/Source/ChaosVDBuiltInExtensions/Private/CameraTraces/ChaosVDCameraTracesExtension.h
// 参考内置相机轨迹扩展的实现方式

class FMyCustomDataExtension final : public FChaosVDExtension
{
public:
    FMyCustomDataExtension();
    virtual ~FMyCustomDataExtension() override;

    // 注册用于处理原始追踪数据的处理器
    virtual void RegisterDataProcessorsInstancesForProvider(const TSharedRef<FChaosVDTraceProvider>& InTraceProvider) override;

    // 提供用于存储和显示自定义数据的组件类
    virtual TConstArrayView<TSubclassOf<UActorComponent>> GetSolverDataComponentsClasses() override;

    // 注册用于在编辑器中绘制自定义数据的可视化器
    virtual void RegisterComponentVisualizers(const TSharedRef<SChaosVDMainTab>& InCVDToolKit) override;

private:
    TArray<TSubclassOf<UActorComponent>> DataComponentsClasses;
};
```

### 进阶用法 - 性能指标分析

性能指标系统允许你查看物理模拟的详细负载信息。

```cpp
// 文件路径：Engine/Plugins/ChaosVD/Source/ChaosVDBuiltInExtensions/Private/PerformanceMetrics/ChaosVDMetrics.h
// 参考性能指标计算逻辑

// 定义一种新的粒子指标类型
UENUM()
enum class EMyChaosMetricType : uint8
{
    CustomCalculation,
    AnotherMetric,
};

// 使用内置的指标计算命名空间
namespace ChaosVDMetrics
{
    // 计算你自定义的指标
    void CalculateMyCustomMetric(const TSharedRef<FChaosVDSceneParticle>& InParticle, TWeakPtr<FChaosVDScene> WeakScene, FParticleMetricEntry& OutMetrics)
    {
        // ... 进行你的自定义计算 ...
        OutMetrics.SimplePrimitives = ...; // 假设计算基元数量
    }
}
```

## Demo 示例

下面的示例展示了如何创建一个最基础的 ChaosVD 扩展，用于注册一个新的数据处理器。

```cpp
// MyCustomDataProcessor.h
#pragma once

#include "Trace/DataProcessors/ChaosVDDataProcessorBase.h"

class FMyCustomDataProcessor final : public FChaosVDDataProcessorBase
{
public:
    explicit FMyCustomDataProcessor();
    
    // 处理从ChaosVD录制中获取的原始数据块
    virtual bool ProcessRawData(const TArray<uint8>& InData) override;
};

// MyCustomDataProcessor.cpp
#include "MyCustomDataProcessor.h"
#include "ChaosVDTraceProvider.h"

FMyCustomDataProcessor::FMyCustomDataProcessor()
{
    // 设置此处理器负责的数据类型标识符
    DataTypeIdentifier = TEXT("MyCustomDebugData");
}

bool FMyCustomDataProcessor::ProcessRawData(const TArray<uint8>& InData)
{
    // 在这里解析 InData 字节数组，将其转换为结构化的调试数据
    // FMemoryReader Reader(InData);
    // FMyCustomDataWrapper MyData;
    // MyData.Serialize(Reader);
    
    // 将处理后的数据存储到当前帧的上下文中
    if (TSharedPtr<FChaosVDTraceProvider> ProviderPtr = Provider.Pin())
    {
        if (FChaosVDSolverFrameData* CurrentSolverFrame = ProviderPtr->GetCurrentSolverFrame(MyData.SolverID))
        {
            // 存储到扩展数据容器中
            // CurrentSolverFrame->GetCustomDataHandler().SetData<FMyCustomDataWrapper>(MyData);
        }
    }
    
    return true;
}
```

## 模块依赖

从插件的 `.uplugin` 配置中提取的依赖。要使用此插件或开发其扩展，你的模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | 为编辑器内数据存储提供支持 |
| `EditorDataStorageFeatures` | `EditorDataStorage` 的特性模块 |
| `GeometryProcessing` | 提供几何处理工具，用于调试绘制等 |
| `ChaosVD` | ChaosVD 的核心编辑器和程序模块 |
| `ChaosVDBlueprint` | ChaosVD 的运行时和蓝图模块 |
| `ChaosVDBuiltInExtensions` | ChaosVD 的内置扩展模块（如性能指标、相机跟踪） |

**注意**：`ChaosVDBlueprint` 是 `RuntimeAndProgram` 类型，意味着它可能可以被游戏模块在运行时引用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联逻辑，提升代码清晰度 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚一个有问题的变更 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同 `cfb610df` 的变更提交 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `b4158d4d` | Make CVD Perf Analysis Async | 将性能分析计算异步化，防止阻塞编辑器线程 |

### 维护评价

ChaosVD 是一个**处于积极开发中**的**实验性/测试版**插件。
-   **创建时间**：2024年3月，相对年轻。
-   **维护活跃度**：非常活跃。从2026年5月的提交记录可见，Epic开发团队正在持续优化其性能（异步化）、代码质量（重构）和稳定性（修复警告和回滚问题）。
-   **状态**：虽然 `.uplugin` 中 `IsBetaVersion=true`，且从实验目录移出的时间不长（2024年3月），但其高频更新表明它正在为正式发布做准备。
-   **推荐**：**强烈推荐**给所有需要对Chaos物理进行深度调试和分析的项目。尽管是Beta版，但它提供的功能对于解决复杂物理问题至关重要，并且正在快速成熟。注意其API和功能可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD)
- 官方文档（暂无）
- 测试用例（通常位于 `Engine/Plugins/ChaosVD/Source/` 下的 `Tests` 目录或 `Engine/Tests/` 目录中，具体路径需在仓库中搜索）