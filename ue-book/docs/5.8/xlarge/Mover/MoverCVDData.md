# Mover CVD Data

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.
Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 移动器调试数据 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例资源、测试资源） |
| 模块 | `MoverCVDData` (Runtime), `Mover` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover) | |

## 用途

MoverCVDData 是 Mover 插件的子模块，专门负责将 Mover 运动模拟过程中的**调试数据序列化**为 Chaos Visual Debugger (CVD) 可识别的格式。它解决的核心问题是：在回滚网络（Rollback Networking）架构下，运动状态的调试和可视化极其复杂，因为模拟可能在客户端和服务器之间回滚、重放。

该模块将 Mover 的各种状态（同步状态、输入命令、本地模拟数据等）打包成统一的 CVD Wrapper 结构体，使得开发者可以在 Chaos Visual Debugger 中直观地查看每个 Solver/Particle 在每一帧的完整运动状态，包括：
- **同步状态（SyncState）**：网络同步的核心状态数据
- **输入命令（InputCmd）**：驱动运动的输入数据
- **本地模拟数据（LocalSimData）**：分为多个命名 Section（如 LocalSimInput、InternalSimData、DebugSimData），每个 Section 独立序列化以保留结构体来源信息

## 使用场景

- 你在使用 Mover 插件实现角色运动，需要**调试网络同步问题** → 使用 CVD 查看每帧的 SyncState 和 InputCmd
- 你需要排查运动模拟中的**状态回滚/预测不一致**问题 → 用 CVD 比较客户端和服务端的模拟数据
- 你在开发自定义运动模式，需要**可视化内部模拟数据** → 将自定义数据注册到 LocalSimDataSections

## 蓝图用法

MoverCVDData 模块是纯数据序列化层，不直接暴露蓝图节点。调试数据的可视化通过 Chaos Visual Debugger 编辑器工具完成。

### 核心结构体

| 结构体 | 说明 |
|---|---|
| `FMoverCVDSimDataWrapper` | 单个 Mover 模拟对象的调试数据快照，包含 SyncState、InputCmd、LocalSimData 等 |
| `FMoverCVDSimDataContainer` | 按 SolverID 组织的调试数据容器，用于批量管理多个模拟对象的数据 |

### FMoverCVDSimDataWrapper 字段说明

| 属性 | 类型 | 说明 |
|---|---|---|
| `SolverID` | `int32` | 物理求解器 ID |
| `ParticleID` | `int32` | 粒子 ID，标识具体的模拟对象 |
| `SyncStateBytes` | `TArray<uint8>` | 网络同步状态的序列化字节 |
| `SyncStateDataCollectionBytes` | `TArray<uint8>` | 同步状态数据集合的序列化字节 |
| `InputCmdBytes` | `TArray<uint8>` | 输入命令的序列化字节 |
| `InputMoverDataCollectionBytes` | `TArray<uint8>` | 输入数据集合的序列化字节 |
| `LocalSimDataSections` | `TArray<TPair<FName, TArray<uint8>>>` | 本地模拟数据分区，每个分区独立序列化以保留来源结构信息 |

## C++ 用法

### 头文件引入

```cpp
#include "MoverCVDDataWrappers.h"
```

### 基本用法：创建和序列化调试数据

```cpp
// 创建一个 Mover CVD 调试数据快照
FMoverCVDSimDataWrapper SimData;
SimData.SolverID = 0;
SimData.ParticleID = 42;

// 序列化同步状态
FMemoryWriter Writer(SimData.SyncStateBytes);
FSyncState SyncState;
// ... 填充同步状态数据
SyncState.Serialize(Writer);

// 序列化输入命令
FMemoryWriter InputWriter(SimData.InputCmdBytes);
FMoverDefaultInputs InputCmd;
// ... 填充输入数据
InputCmd.Serialize(InputWriter);

// 添加本地模拟数据分区（保留结构体来源信息）
TArray<uint8> LocalSimBytes;
FMemoryWriter LocalWriter(LocalSimBytes);
// ... 序列化本地模拟数据
SimData.LocalSimDataSections.Add(MakeTuple(FName("LocalSimInput"), MoveTemp(LocalSimBytes)));

// 序列化整个 Wrapper 用于 CVD 存储
FMemoryArchive Archive;
SimData.Serialize(Archive);
```

### 进阶用法：使用容器管理多个模拟对象

```cpp
// 按 SolverID 组织多个模拟对象的调试数据
FMoverCVDSimDataContainer DataContainer;

// 为 Solver 0 添加数据
TArray<TSharedPtr<FMoverCVDSimDataWrapper>>& SolverData =
    DataContainer.SimDataBySolverID.FindOrAdd(0);

TSharedPtr<FMoverCVDSimDataWrapper> Data = MakeShared<FMoverCVDSimDataWrapper>();
Data->SolverID = 0;
Data->ParticleID = 1;
// ... 填充状态数据
SolverData.Add(Data);

// 为同一个 Solver 添加多帧数据（用于时间线回放）
TSharedPtr<FMoverCVDSimDataWrapper> NextFrameData = MakeShared<FMoverCVDSimDataWrapper>();
NextFrameData->SolverID = 0;
NextFrameData->ParticleID = 1;
// ... 填充下一帧数据
SolverData.Add(NextFrameData);
```

## Demo 示例

### MoverCVDDataSerializer.h

```cpp
// 自定义 Mover 调试数据收集器
#pragma once

#include "CoreMinimal.h"
#include "MoverCVDDataWrappers.h"

UCLASS()
class UMyMoverDebugDataCollector : public UObject
{
	GENERATED_BODY()

public:
	// 收集当前帧所有 Mover 模拟对象的调试数据
	void CollectSimData(int32 CurrentFrame);

	// 获取序列化后的数据，用于 CVD 录制
	const FMoverCVDSimDataContainer& GetCollectedData() const { return DataContainer; }

	// 清除历史数据
	void Reset();

private:
	FMoverCVDSimDataContainer DataContainer;

	void SerializeSyncState(FMoverCVDSimDataWrapper& OutWrapper, const void* SyncStateData);
	void SerializeInputCmd(FMoverCVDSimDataWrapper& OutWrapper, const void* InputCmdData);
	void AddLocalSimSection(FMoverCVDSimDataWrapper& OutWrapper,
		FName SectionName, const TArray<uint8>& SectionData);
};
```

### MoverCVDDataSerializer.cpp

```cpp
#include "MyMoverDebugDataCollector.h"
#include "Serialization/MemoryWriter.h"

void UMyMoverDebugDataCollector::CollectSimData(int32 CurrentFrame)
{
	// 遍历场景中的 Mover 组件，收集调试数据
	// 实际使用中需要根据 Mover 组件的 API 获取当前状态
}

void UMyMoverDebugDataCollector::SerializeSyncState(
	FMoverCVDSimDataWrapper& OutWrapper, const void* SyncStateData)
{
	// 将同步状态序列化为字节数组
	FMemoryWriter Writer(OutWrapper.SyncStateBytes);
	// 根据具体的 FSolverSyncState 类型进行序列化
}

void UMyMoverDebugDataCollector::SerializeInputCmd(
	FMoverCVDSimDataWrapper& OutWrapper, const void* InputCmdData)
{
	// 将输入命令序列化为字节数组
	FMemoryWriter Writer(OutWrapper.InputCmdBytes);
	// 根据具体的 FMoverDataCollectionBase 类型进行序列化
}

void UMyMoverDebugDataCollector::AddLocalSimSection(
	FMoverCVDSimDataWrapper& OutWrapper,
	FName SectionName,
	const TArray<uint8>& SectionData)
{
	// 添加命名的本地模拟数据分区
	// 每个分区独立保留结构体类型信息，CVD 查看器可据此正确解析
	OutWrapper.LocalSimDataSections.Add(
		MakeTuple(SectionName, SectionData));
}

void UMyMoverDebugDataCollector::Reset()
{
	DataContainer.SimDataBySolverID.Empty();
}
```

## 模块依赖

MoverCVDData 模块是独立的轻量级数据层，其 Build.cs 中的依赖项较少。以下是使用者需要注意的依赖：

| 模块 | 用途 |
|---|---|
| `ChaosVDData` | Chaos Visual Debugger 数据层，提供 `FChaosVDWrapperDataBase` 基类和 CVD 序列化宏 |
| `Mover` | Mover 主模块，提供同步状态、输入命令等核心类型定义 |

> 注意：该模块被 Mover 主模块依赖（`Mover.Build.cs` → `MoverCVDData`），因此使用 Mover 插件时会自动引入。如果只需 CVD 数据结构而不需要完整 Mover 运行时，可单独依赖 MoverCVDData。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6ef46a3c` | Mover: update README for next release | 更新 README 文档以适配下一个版本 |
| 2026-05-22 | `4ea45e21` | Mover: fix bug where skipping vertical anim root motion was not being respected in all montage cases | 修复垂直动画根运动跳过逻辑在部分蒙太奇场景下未生效的 bug |
| 2026-05-20 | `dd78e781` | Mover: fix for inconsistent behavior of mode-changed events (kinematic / NPP cases) resulting in que | 修复运动模式切换事件（运动学/NPP）行为不一致导致排队问题 |
| 2026-05-14 | `801be5dc` | Mover/ChaosMover: Just like moves, move instances are now using a pull mechanism so they can work in | 移动实例改用 pull 机制以兼容回滚网络架构 |
| 2026-05-14 | `d040bc9f` | Mover: adding simulation that's specific to kinematically-moved Actors | 新增运动学驱动 Actor 的专用模拟支持 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2024-02-02，插件年龄约 2 年
- **更新频率**：近期（2026 年 5 月）有密集的功能更新和 bug 修复，几乎每周都有提交
- **维护状态**：非常活跃，Epic Games 持续投入开发，功能仍在快速迭代
- **实验性标记**：仍标记为 Experimental，说明 API 尚未稳定，未来可能有 Breaking Changes
- **已知限制**：作为实验性插件，可能在边缘场景下存在未发现的同步问题
- **推荐程度**：适合用于**原型开发和内部测试**，生产环境使用需谨慎并密切关注更新。如果你需要支持回滚网络的运动系统，Mover 是目前 UE5 中唯一的官方方案，值得投入学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
- [官方文档]()（暂无独立文档页面，请参考插件内 README）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover/Source/MoverTests)