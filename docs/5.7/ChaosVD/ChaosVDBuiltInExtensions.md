# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、蓝图资产、扩展） |
| 模块 | `ChaosVD` (EditorAndProgram), `ChaosVDBlueprint` (RuntimeAndProgram), `ChaosVDBuiltInExtensions` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD) | |

## 用途

Chaos Visual Debugger (CVD) 是一个专为 Unreal Engine 5 的 Chaos 物理引擎设计的**可视化调试工具**。它解决的核心问题是：在复杂的物理模拟中，开发者难以直观地观察、分析和诊断物理对象的状态（如碰撞、约束、粒子、关节等）。

CVD 通过录制物理模拟过程中的关键数据（如物体轨迹、碰撞点、约束状态），并提供一个强大的编辑器工具来**回放、检查和可视化**这些数据。这使得开发者能够：
1.  **回溯问题**：重现并分析难以复现的物理 Bug。
2.  **理解模拟**：直观地查看物理世界内部的运行机制。
3.  **优化性能**：识别不必要的物理计算或复杂的碰撞查询。
4.  **调试蓝图**：可视化蓝图中物理相关节点的效果。

它本质上是一个物理模拟的“黑匣子”和“显微镜”。

## 使用场景

-   你在开发一个物理密集型游戏（如赛车、破坏模拟、布娃娃系统），需要调试复杂的碰撞和约束问题。
-   你需要分析物理性能瓶颈，想看看哪些对象在消耗大量物理计算资源。
-   你正在编写自定义的物理接口或 Chaos Modifiers，需要验证其行为是否符合预期。
-   你需要向团队成员或设计师展示物理模拟的内部工作原理。

## 蓝图用法

CVD 的主要交互界面是编辑器工具，但通过 `ChaosVDBlueprint` 模块暴露了一些运行时蓝图接口，用于控制录制和数据查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Recording` | 开始录制当前世界的物理模拟数据。 | `UChaosVDSubsystem` |
| `Stop Recording` | 停止当前的录制。 | `UChaosVDSubsystem` |
| `Save Recording To File` | 将录制的数据保存到 `.cvd` 文件。 | `UChaosVDSubsystem` |
| `Load Recording From File` | 从文件加载一个录制数据。 | `UChaosVDSubsystem` |
| `Get Recorded Frame Count` | 获取已录制的总帧数。 | `UChaosVDSubsystem` |
| `Set Playback Frame` | 跳转到录制数据的指定帧。 | `UChaosVDSubsystem` |

### 使用示例（蓝图描述）

1.  **录制物理模拟**：
    -   在游戏逻辑中（例如，当玩家开始一个物理挑战时），调用 `Start Recording` 节点。
    -   当挑战结束或需要保存数据时，调用 `Stop Recording`，然后立即调用 `Save Recording To File`，并提供一个文件路径。

2.  **回放与分析**：
    -   在编辑器工具或另一个测试关卡中，使用 `Load Recording From File` 加载之前保存的 `.cvd` 文件。
    -   使用 `Set Playback Frame` 节点配合时间轴滑块，逐帧查看物理状态。

## C++ 用法

CVD 的核心功能通过其子系统 `UChaosVDSubsystem` 暴露。更高级的定制和扩展则通过其扩展系统 (`ChaosVDExtensionsManager`) 实现。

### 头文件引入

```cpp
#include "ChaosVDSubsystem.h"
#include "ExtensionsSystem/ChaosVDExtensionsManager.h"
```

### 基本用法

控制物理模拟的录制过程。

```cpp
// 假设在某个 Actor 或 GameInstance 中
UChaosVDSubsystem* CVDSubsystem = GetWorld()->GetSubsystem<UChaosVDSubsystem>();
if (CVDSubsystem)
{
    // 开始录制
    CVDSubsystem->StartRecording();

    // ... 运行一些物理模拟 ...

    // 停止录制
    CVDSubsystem->StopRecording();

    // 保存到项目 Saved 目录
    FString SavePath = FPaths::ProjectSavedDir() / TEXT("MyPhysicsRecording.cvd");
    CVDSubsystem->SaveRecordingToFile(SavePath);
}
```

### 进阶用法

创建自定义的 CVD 扩展，以添加新的数据可视化类型或分析工具。这需要继承 `FChaosVDExtension` 并注册。

```cpp
// MyChaosVDExtension.h
#pragma once
#include "ExtensionsSystem/ChaosVDExtension.h"

class FMyChaosVDExtension : public FChaosVDExtension
{
public:
    virtual void RegisterVisualizers() override;
    // ... 其他重写方法
};

// MyChaosVDExtension.cpp
#include "MyChaosVDExtension.h"
#include "ChaosVDExtensionsManager.h"

void FMyChaosVDExtension::RegisterVisualizers()
{
    // 在这里注册自定义的可视化器
    // FChaosVDExtensionsManager::Get().RegisterVisualizer(...);
}

// 在模块启动时注册此扩展（例如在 FMyGameModule::StartupModule 中）
void FMyGameModule::StartupModule()
{
    TSharedRef<FMyChaosVDExtension> MyExtension = MakeShared<FMyChaosVDExtension>();
    FChaosVDExtensionsManager::Get().RegisterExtension(MyExtension);
}
```

## Demo 示例

一个最小的自定义 CVD 扩展示例，用于在 CVD 面板中添加一个简单的自定义可视化。

**MyCustomCVDExtension.h**
```cpp
#pragma once
#include "ExtensionsSystem/ChaosVDExtension.h"

class FMyCustomCVDExtension : public FChaosVDExtension
{
public:
    FMyCustomCVDExtension();
    virtual ~FMyCustomCVDExtension() override;

    // FChaosVDExtension interface
    virtual void RegisterVisualizers() override;
    virtual void UnregisterVisualizers() override;
};
```

**MyCustomCVDExtension.cpp**
```cpp
#include "MyCustomCVDExtension.h"
#include "ChaosVDExtensionsManager.h"
#include "Visualizers/ChaosVDParticleDataVisualizer.h" // 假设的基类

// 一个简单的可视化器，用于显示所有粒子的速度矢量
class FMyVelocityVisualizer : public FChaosVDParticleDataVisualizer
{
public:
    virtual void DrawVisualization(const FChaosVDParticleData& ParticleData, FChaosVDScene& Scene) const override
    {
        // 使用 Scene 的绘制工具绘制速度箭头
        // Scene.DrawArrow(ParticleData.Position, ParticleData.Position + ParticleData.Velocity * 0.1f, FColor::Green);
    }
};

FMyCustomCVDExtension::FMyCustomCVDExtension()
{
}

FMyCustomCVDExtension::~FMyCustomCVDExtension()
{
}

void FMyCustomCVDExtension::RegisterVisualizers()
{
    // 创建并注册我们的自定义可视化器
    TSharedRef<FMyVelocityVisualizer> VelocityVis = MakeShared<FMyVelocityVisualizer>();
    FChaosVDExtensionsManager::Get().RegisterVisualizer(VelocityVis);
}

void FMyCustomCVDExtension::UnregisterVisualizers()
{
    // 清理工作
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供物理模拟数据和接口。 |
| `ChaosSolverEngine` | Chaos 求解器引擎，管理物理世界的模拟。 |
| `GeometryProcessing` | 用于处理和可视化物理碰撞几何体。 |
| `EditorDataStorage` | 为 CVD 编辑器工具提供高效的数据存储和查询。 |
| `EditorDataStorageFeatures` | EditorDataStorage 的扩展功能。 |

## 维护状态

### 近期更新

```
- a2e75189887d 为包含对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME。
- 80aae88f6303 [ChaosVD] 添加了在数据可视化设置中禁用枚举条目的方法，并更新了所有现有的可视化标志选项以使用它。
- fcc24c2d6336 [ChaosVD] 修复了重置设置按钮对某些设置类别不起作用的问题。
```

### 维护评价

**活跃维护**。Chaos Visual Debugger 是 Epic Games 为 Chaos 物理引擎提供的官方调试工具，创建于 2023 年初，相对较新。从最近的提交记录看，团队仍在积极开发和修复问题（如改进设置系统、修复 UI Bug）。作为 Chaos 生态系统的关键调试组件，它预计会随着 Chaos 引擎的演进而持续更新。

**推荐使用**：对于任何使用 Chaos 物理引擎并需要进行深度调试的项目，强烈推荐启用和使用此插件。它是目前最强大、最集成的 Chaos 可视化调试方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD)
- [官方文档]() (暂无)
- [测试用例]() (暂无)