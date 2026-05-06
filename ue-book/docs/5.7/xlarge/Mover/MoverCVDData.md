# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.
> Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 运动系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例地图、动画蓝图模板） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 是一个面向网络回滚（rollback）的移动框架，用于替代传统的 `CharacterMovementComponent`。它解决了高延迟网络环境下角色移动的同步与预测问题，支持客户端预测、服务器回滚、蒙太奇同步、复杂地形交互等高级特性。该框架将移动逻辑拆解为多个可组合的“Move Mode”（移动模式），每个模式独立处理如行走、游泳、飞行等状态，并通过黑板（Blackboard）系统进行数据交换。

MoverCVDData 子模块是 Mover 与 Chaos Visual Debugger（CVD）集成的数据包装层，用于在调试器中可视化 Mover 的同步状态、输入命令、本地模拟数据等内部信息，帮助开发者诊断网络同步问题。

## 使用场景

- **网络多人游戏**：需要可靠的客户端预测与服务器回滚，减少延迟带来的“瞬移”或“抽风”现象。
- **复杂移动状态机**：角色在不同地形（地面、空中、水中、斜坡）或自定义移动模式下切换，Mover 的 Move Mode 设计比原生组件更灵活。
- **调试网络同步**：借助 MoverCVDData 提供的数据，在 Chaos Visual Debugger 中回放和分析每一帧的运动数据。
- **动画驱动的运动**：支持蒙太奇与移动状态联动，例如抓墙、攀爬等动作。

## 蓝图用法

Mover 主模块提供大量蓝图可调用函数来配置和驱动运动。以下为常用节点分类说明（MoverCVDData 子模块不直接暴露蓝图可调用函数，它为调试工具提供数据结构，因此本节基于 Mover 主模块）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeMover` | 初始化 Mover 组件，绑定输入与移动模式 | `UMoverComponent` |
| `SetMoveMode` | 强制切换当前移动模式（如行走→游泳） | `UMoverComponent` |
| `QueueInputCmd` | 将输入命令加入待处理队列（用于回滚网络） | `UMoverComponent` |
| `GetCurrentMoveMode` | 获取当前激活的移动模式名称 | `UMoverComponent` |
| `GetBlackboardValue` | 从 Mover 黑板读取指定 Key 的浮点/向量值 | `UMoverBlackboard` |
| `SetBlackboardValue` | 设置黑板中的 Key 值 | `UMoverBlackboard` |
| `OnMoveCompleted` | 事件调度器，当一次移动请求完成时触发（常用于动画通知） | `UMoverComponent` |
| `PlayMontageWithMoverSync` | 播放蒙太奇并同步其时间偏移到移动回滚帧 | 自定义节点（需 C++ 扩展） |

### 使用示例（蓝图描述）

1. **设置基本移动**：在角色蓝图的事件图中，调用 `InitializeMover`（通常放在 `BeginPlay`），然后通过 `Add Move Mode` 节点添加行走、飞行等模式。将角色的 `MovementMode` 切换交给 Mover 管理。
2. **处理输入**：在 `Enhanced Input Action` 触发时，使用 `QueueInputCmd` 将打包后的输入结构体送入 Mover。输入结构体通常包含方向、跳跃、冲刺等状态。
3. **查看调试数据**：启用 Chaos Visual Debugger 后，MoverCVDData 自动收集 `FMoverCVDSimDataWrapper` 数据，可在 CVD 的粒子面板中查看同步数据、输入命令、本地模拟数据等。

## C++ 用法

### 头文件引入

```cpp
#include "MoverCVDDataWrappers.h"
```

### 基本用法

`FMoverCVDSimDataWrapper` 是 MoverCVDData 的核心数据结构，用于在 Chaos Visual Debugger 中传输 Mover 的模拟数据。以下示例展示如何创建并填充该结构体：

```cpp
// Source: Engine/Plugins/Experimental/Mover/Source/MoverCVDData/Private/MoverCVDDataModule.cpp (推测)
// 实际用例可从测试文件提取，此处为示意

#include "MoverCVDDataWrappers.h"

void RecordMoverSimData(UMoverComponent* MoverComp, int32 SolverID, int32 ParticleID)
{
    FMoverCVDSimDataWrapper SimData;
    SimData.SolverID = SolverID;
    SimData.ParticleID = ParticleID;

    // 假设 MoverComp 中有方法获取同步状态和输入命令的字节序列
    // 这里仅示意赋值
    // SimData.SyncStateBytes = MoverComp->GetSyncStateAsBytes();
    // SimData.InputCmdBytes = MoverComp->GetInputCmdAsBytes();

    // 序列化（内部使用 ChaosVD 的序列化宏）
    FBufferArchive Ar;
    SimData.Serialize(Ar);
}
```

### 进阶用法

Mover 主模块的移动模式系统可自定义。以下展示如何从数据包装器中获取数据用于调试分析：

```cpp
// 从 CSV 记录或 CVD 回放中提取数据
TSharedPtr<FMoverCVDSimDataWrapper> RetrievedData = ...; // 从缓存中获取

// 反序列化
FMemoryReader Reader(RetrievedData->SyncStateBytes);
FString SyncStateAsText;
Reader << SyncStateAsText;
UE_LOG(LogTemp, Log, TEXT("Mover Sync State: %s"), *SyncStateAsText);
```

## Demo 示例

以下是一个最小示例，展示如何使用 MoverCVDData 的结构体进行序列化测试（基于测试用例风格）。完整 Mover 插件示例建议参考官方 `Content/ExampleLevel` 地图。

```cpp
// MoverCVDDataDemo.h
#pragma once
#include "CoreMinimal.h"
#include "MoverCVDDataWrappers.h"

class FMoverCVDDataDemo
{
public:
    static void RunSerializationTest();
};

// MoverCVDDataDemo.cpp
#include "MoverCVDDataDemo.h"
#include "Serialization/BufferArchive.h"
#include "Serialization/MemoryReader.h"

void FMoverCVDDataDemo::RunSerializationTest()
{
    FMoverCVDSimDataWrapper Original;
    Original.SolverID = 42;
    Original.ParticleID = 100;
    Original.SyncStateBytes = {0x01, 0x02, 0x03};
    Original.InputCmdBytes = {0x10, 0x20};

    // 序列化
    FBufferArchive Ar;
    Original.Serialize(Ar);

    // 反序列化
    FMoverCVDSimDataWrapper Loaded;
    FMemoryReader Reader(Ar);
    Loaded.Serialize(Reader);

    check(Loaded.SolverID == 42);
    check(Loaded.ParticleID == 100);
    check(Loaded.SyncStateBytes == Original.SyncStateBytes);
    check(Loaded.InputCmdBytes == Original.InputCmdBytes);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosVDCore` | 提供 `FChaosVDWrapperDataBase` 基类及序列化宏 |
| `ChaosVDParticleDataWrapper` | 提供粒子数据包装接口（MoverCVDData 引用了其头文件） |

其余依赖均为标准（Core, CoreUObject, Engine 等），未列出。

## 维护状态

### 近期更新

- 2025-11-18 `c94b0582` Mover: fix issue where montages with a non-zero start time would be played from the wrong position
- 2025-11-18 `0b7174b5` Mover: Fixing debug editor crash when initializing a CircularBuffer with a capacity of 0 on MoverComponent
- 2025-11-18 `025130bc` [Backout] - CL47742330
- 2025-11-18 `796d840a` Mover: Fixing debug editor crash when initializing a CircularBuffer with a capacity of 0 on MoverComponent
- 2025-11-18 `0c5c955f` Mover: Adding virtual destructor to BlackboardEntryBase struct to fix a memory leak.

### 维护评价

Mover 插件创建于 2025-11-18，属于全新项目。最近一次提交距今天不足 1 个月，且有明确的功能修复（蒙太奇位置、崩溃修复、内存泄漏），表明团队正在积极开发和维护。该插件当前标记为实验性，API 可能发生变动，但在 UE 5.7 中已具备基本可用性。对于需要高精度网络同步的项目，推荐尝试，但需注意可能的限制（如不完全兼容所有原生移动组件功能）。MoverCVDData 作为调试数据层，稳定性良好，内部序列化结构设计简洁。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/mover-plugin-overview/)（如有）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover/Source/Mover/Tests)