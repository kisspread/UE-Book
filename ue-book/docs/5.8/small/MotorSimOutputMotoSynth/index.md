# MotorSimOutputMotoSynth

> A MotorSim Output component using MotoSynth.

| 属性 | 值 |
|---|---|
| 中文名 | 摩托合成输出组件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MotorSimOutputMotoSynth` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotorSimOutputMotoSynth) | |

## 用途

本插件是 **AudioMotorSim（音频电机模拟）系统** 的输出组件之一，将 `AudioMotorSim` 框架计算出的电机状态（转速、负载等）通过 **MotoSynth（摩托合成器）** 实际渲染为音频。

核心角色：它是 AudioMotorSim 系统与 MotoSynth 音频引擎之间的 **桥梁组件**。AudioMotorSim 系统负责计算物理参数，MotoSynth 负责根据参数生成引擎声音，而本插件负责将两者连接起来。

**解决的问题**：如果你使用 AudioMotorSim 系统模拟车辆/摩托车的电机状态，需要将模拟结果转换为实际的引擎音效，就需要本组件将数据喂给 MotoSynth 来发声。

## 使用场景

- 你在做赛车/摩托车游戏，使用 AudioMotorSim 系统进行电机参数模拟，同时需要 MotoSynth 生成真实的引擎音效
- 你需要一个现成的 MotorSim 输出实现，不想手动桥接 AudioMotorSim 和 MotoSynth
- 你使用 MotoSynth 作为引擎音效方案，并希望与 AudioMotorSim 的状态机系统集成

## 蓝图用法

该插件没有暴露额外的 `BlueprintCallable` 函数。它的核心逻辑通过实现 `IAudioMotorSimOutput` 接口的虚函数（`Update`、`StartOutput`、`StopOutput`）完成，这些调用由 AudioMotorSim 系统内部驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （组件自身作为 MotorSim 输出） | 将该组件添加到 Actor 上，并注册为 AudioMotorSim 的输出，系统会自动调用其 Update/Start/Stop | `UMotorSimOutputMotoSynth` |

### 使用示例（蓝图描述）

1. 在你的 Actor（如摩托车 Pawn）上添加 `MotorSimOutputMotoSynth` 组件（类名：`MotorSimOutputMotoSynth`，位于 Synth 分组下）
2. 在 AudioMotorSim 系统的配置中，将该组件注册为输出接口（通过 `IAudioMotorSimOutput` 接口引用）
3. AudioMotorSim 系统在模拟循环中会自动调用 `Update()` 传递当前输入/运行时状态，MotoSynth 会根据这些参数生成对应的引擎音效
4. 当需要开始/停止引擎音效时，系统调用 `StartOutput()` / `StopOutput()`

## C++ 用法

### 头文件引入

```cpp
#include "MotorSimOutputMotoSynth.h"
```

### 基本用法

该组件的核心功能通过 `IAudioMotorSimOutput` 接口实现，由 AudioMotorSim 系统自动驱动。以下是接口方法的说明：

```cpp
// 来源: Source/MotorSimOutputMotoSynth/Public/MotorSimOutputMotoSynth.h

// UMotorSimOutputMotoSynth 继承自 USynthComponentMoto 和 IAudioMotorSimOutput
// 系统会在每帧调用 Update，将电机模拟数据传入 MotoSynth
UE_API virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override;

// 启动引擎音效输出
UE_API virtual void StartOutput() override;

// 停止引擎音效输出
UE_API virtual void StopOutput() override;
```

### 进阶用法

如果你需要自定义 MotorSim 输出行为，可以继承 `UMotorSimOutputMotoSynth` 并重写这三个虚函数，在调用父类实现的基础上添加自定义逻辑（例如叠加额外音效层、调整参数映射等）。

## Demo 示例

```cpp
// MyMotorcycle.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MotorSimOutputMotoSynth.h"
#include "MyMotorcycle.generated.h"

UCLASS()
class AMyMotorcycle : public APawn
{
    GENERATED_BODY()

public:
    AMyMotorcycle();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UMotorSimOutputMotoSynth* MotoSynthOutput;
};

// MyMotorcycle.cpp
#include "MyMotorcycle.h"

AMyMotorcycle::AMyMotorcycle()
{
    MotoSynthOutput = CreateDefaultSubobject<UMotorSimOutputMotoSynth>(TEXT("MotoSynthOutput"));
    RootComponent = MotoSynthOutput;
}
```

## 模块依赖

该插件依赖以下插件（在 .uplugin 中声明），你的项目需要同时启用它们：

| 插件/模块 | 用途 |
|---|---|
| `AudioMotorSim` | 提供电机模拟框架和 `IAudioMotorSimOutput` 接口定义 |
| `MotoSynth` | 提供 `USynthComponentMoto` 基类和摩托引擎音效合成能力 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量将析构函数改写为 `= default` 格式，纯代码风格修复 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 批量添加 DLL 导出宏，构建系统调整 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 移除 5.2 版本废弃的头文件包含顺序宏 |
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化私有模块依赖关系 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件目录批量提交 |

### 维护评价

**⚠️ 维护不活跃 — 实验性插件，无实质性功能更新**

- 创建于 2022 年 6 月，至今约 3 年
- 自创建以来 **从未有过功能性更新**，所有 commit 均为全局代码风格修复、构建系统调整等机械性改动
- 标记为 `IsExperimentalVersion = true`，且 `Installed = false`（默认未启用）
- 代码量极小（仅 4 个文件），结构稳定但功能有限
- 作为实验性插件，可能在未来版本中被移除或重构

**建议**：如果你需要在 AudioMotorSim 系统中使用 MotoSynth 作为输出，该插件提供了最直接的实现。但由于其实验性质和长期无更新的状态，建议准备好自定义实现作为备选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotorSimOutputMotoSynth)
- [AudioMotorSim 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim)（依赖插件）
- [MotoSynth 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MotoSynth)（依赖插件）