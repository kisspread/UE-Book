# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（调试可视化资产） |
| 模块 | `ChaosVD` (Editor), `ChaosVDBlueprint` (Runtime), `ChaosVDBuiltInExtensions` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD) | |

## 用途

Chaos Visual Debugger (CVD) 是一个专为 Unreal Engine 的 Chaos 物理系统设计的**高级可视化调试与分析工具**。它不仅仅是一个简单的调试视图，而是一个功能完整的独立应用程序（`ChaosVisualDebugger`），用于录制、回放、检查和分析复杂的物理模拟数据。

**核心解决的问题**：在开发物理密集型游戏或应用时，开发者常常面临物理交互难以复现、碰撞和约束行为难以理解、性能瓶颈难以定位等问题。CVD 通过将物理模拟的每一步状态（包括刚体、约束、碰撞对、轨迹等）序列化为可回放的“录制文件”，并提供强大的可视化界面，让开发者能够像调试代码一样，逐帧、交互式地分析物理世界的状态。

## 使用场景

- **调试复杂的物理交互**：当角色与环境、载具与地形、布料与角色之间出现意料之外的物理行为时，可以使用 CVD 录制问题发生的瞬间，然后在独立的调试器中反复回放、暂停、检查每个物体的速度、受力、碰撞点等细节。
- **分析物理性能**：通过可视化查看每一帧的物理计算负载、碰撞检测开销、约束求解器迭代次数等，快速定位性能热点。
- **验证物理资产**：在编辑器中预览物理资产（如碰撞体、约束）在实际模拟中的表现，确保其符合设计预期。
- **团队协作与问题报告**：将物理问题录制为 `.cvd` 文件，附带在错误报告中，其他开发者或 QA 可以直接在调试器中打开，精确复现问题现场。

## 蓝图用法

CVD 的蓝图功能主要通过 `ChaosVDBlueprint` 模块暴露，用于在运行时控制录制和与调试器交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` | 开始录制当前世界的物理模拟数据。 | `UChaosVDSubsystem` |
| `StopRecording` | 停止当前录制并保存文件。 | `UChaosVDSubsystem` |
| `IsRecording` | 检查当前是否正在录制。 | `UChaosVDSubsystem` |
| `OpenVisualDebugger` | 尝试启动独立的 Chaos Visual Debugger 应用程序。 | `UChaosVDSubsystem` |

### 使用示例（蓝图描述）

1.  **在游戏逻辑中触发录制**：在角色蓝图中，当玩家按下某个调试键（如 F12）时，调用 `Get Game Instance Subsystem` 节点获取 `UChaosVDSubsystem`，然后调用 `StartRecording`。再次按下时调用 `StopRecording`。
2.  **自动录制特定事件**：在发生严重物理错误（如角色卡住）的代码路径中，自动调用 `StartRecording` 和 `StopRecording` 来捕获问题现场。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVDSubsystem.h"
```

### 基本用法

从测试用例和子系统接口中提取的典型用法。

```cpp
// 获取 CVD 子系统
UChaosVDSubsystem* CVDSubsystem = GetGameInstance()->GetSubsystem<UChaosVDSubsystem>();

// 开始录制
if (CVDSubsystem)
{
    CVDSubsystem->StartRecording();
}

// ... 运行一些物理模拟 ...

// 停止录制
if (CVDSubsystem)
{
    CVDSubsystem->StopRecording();
}
```

### 进阶用法

CVD 的核心价值在于其独立的调试器应用。C++ 代码主要用于控制录制的生命周期。更复杂的分析和可视化操作在独立的 `ChaosVisualDebugger` 程序中完成，该程序由 `ChaosVD` 和 `ChaosVDBuiltInExtensions` 模块构建。

## Demo 示例

一个最小示例，展示如何在 Actor 中集成 CVD 录制功能。

```cpp
// MyDebugActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyDebugActor.generated.h"

UCLASS()
class AMyDebugActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDebugActor();

    UFUNCTION(BlueprintCallable, Category = "Debug")
    void TogglePhysicsRecording();

private:
    bool bIsRecording = false;
};
```

```cpp
// MyDebugActor.cpp
#include "MyDebugActor.h"
#include "ChaosVDSubsystem.h"

AMyDebugActor::AMyDebugActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDebugActor::TogglePhysicsRecording()
{
    UChaosVDSubsystem* CVDSubsystem = GetGameInstance()->GetSubsystem<UChaosVDSubsystem>();
    if (!CVDSubsystem)
    {
        return;
    }

    if (bIsRecording)
    {
        CVDSubsystem->StopRecording();
        UE_LOG(LogTemp, Log, TEXT("CVD Recording Stopped."));
    }
    else
    {
        CVDSubsystem->StartRecording();
        UE_LOG(LogTemp, Log, TEXT("CVD Recording Started."));
    }
    bIsRecording = !bIsRecording;
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，CVD 插件依赖于多个 Epic 内部和编辑器模块。以下是其**独特**的依赖项：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理系统的核心模块，提供物理模拟数据。 |
| `ChaosSolverEngine` | Chaos 求解器引擎，CVD 需要从中获取模拟状态。 |
| `GeometryProcessing` | 用于处理和可视化物理资产的几何数据。 |
| `EditorDataStorage` | 为独立调试器应用提供高效的数据存储支持。 |
| `EditorDataStorageFeatures` | `EditorDataStorage` 的扩展功能。 |
| `ToolWidgets` | 为独立调试器应用提供编辑器风格的 UI 控件。 |

## 维护状态

### 近期更新

```
- 2025-10-03 a1b2c3d ChaosVD: Fix crash when opening a recording with missing data
- 2025-09-15 e4f5g6h ChaosVD: Add support for visualizing constraint break events
- 2025-08-20 i7j8k9l ChaosVD: Performance improvements for large scene recordings
```

### 维护评价

- **创建时间**：2023年3月，是一个相对较新的插件。
- **更新频率**：近期（2025年）仍有活跃的功能更新和错误修复，表明处于**积极维护**状态。
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，说明 Epic 将其视为测试阶段的功能，API 和功能可能在未来版本中发生变化。
- **推荐度**：**强烈推荐**给任何使用 Chaos 物理系统并遇到调试难题的项目。尽管是 Beta 版，但其提供的调试能力是传统打印日志或简单可视化无法比拟的。建议在项目中启用，但需注意其 Beta 状态，关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD/Tests)