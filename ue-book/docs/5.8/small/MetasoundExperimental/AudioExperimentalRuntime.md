# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | Metasound 实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频实验性资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

这是 MetaSound 插件的实验性扩展，用于在正式发布前测试 MetaSound 的新功能。当前的核心开发方向是 **CAT（Channel Agnostic Types，通道无关类型）**系统，旨在让 MetaSound 节点能够处理与通道布局无关的音频数据。

该插件解决的核心问题是：MetaSound 默认的节点和类型系统是与特定音频通道布局（如立体声、5.1）紧密耦合的，CAT 系统提供了一套通道无关的抽象类型和节点，使 MetaSound 图可以在不同通道布局间无缝工作。

插件默认不启用（`EnabledByDefault: false`），标记为实验性（`IsExperimentalVersion: true`），需要手动在插件管理器中启用。

## 使用场景

- 你正在使用 MetaSound 构建音频图，需要节点在单声道、立体声、环绕声等不同通道布局下都能正确工作 → 启用此插件并使用 CAT 节点
- 你想尝试 MetaSound 即将推出的新功能（如新节点、新类型）→ 此插件是 Epic 内部功能的公开预览
- 你需要使用实验性的 MetaSound 节点，如通道无关的乘法节点、梯形滤波器等

## 蓝图用法

此插件主要面向 MetaSound 图编辑器，不暴露传统的蓝图节点。其功能通过 MetaSound 图中的节点体现。

### 核心节点（MetaSound 图）

| 节点 | 说明 | 所在类/类型 |
|---|---|---|
| `[CAT] Multiply` | 通道无关的乘法节点，对 CAT 类型执行乘法运算 | MetaSound 节点 |
| `[CAT] Ladder Filter` | 通道无关的梯形滤波器节点 | MetaSound 节点 |
| `[CAT] Wave` | 通道无关的波形类型支持 | MetaSound 数据类型 |

### 使用示例

在 MetaSound 编辑器中：

1. 启用插件后，MetaSound 节点面板中会出现带 `[CAT]` 前缀的新节点
2. 将 `[CAT] Multiply` 节点拖入图中，连接 CAT 类型的输入/输出引脚
3. CAT 节点可以接收和输出通道无关的音频数据，无需关心底层通道布局
4. `[CAT] Ladder Filter` 可用于对 CAT 类型的音频信号进行滤波处理

## C++ 用法

### 模块结构

插件包含 4 个模块：

| 模块 | 类型 | 职责 |
|---|---|---|
| `AudioExperimentalRuntime` | Runtime | 音频实验性运行时基础功能 |
| `MetasoundExperimentalRuntime` | Runtime | MetaSound 实验性运行时，包含 CAT 类型和节点实现 |
| `MetasoundExperimentalEngineRuntime` | Runtime | MetaSound 实验性引擎运行时集成 |
| `MetasoundExperimentalEditor` | Editor | MetaSound 实验性编辑器扩展 |

### 头文件引入

```cpp
// MetaSound 实验性运行时
#include "MetasoundExperimentalRuntimeModule.h"

// 音频实验性运行时
#include "AudioExperimentalRuntimeModule.h"

// MetaSound 引擎运行时（依赖 Metasound 插件）
#include "MetasoundExperimentalEngineRuntimeModule.h"
```

### 基本用法

此插件的核心功能通过 MetaSound 节点注册系统提供。自定义 CAT 节点时，参考插件内部的节点实现模式：

```cpp
// 引入 MetaSound 核心头文件
#include "MetasoundVertex.h"
#include "MetasoundNodeInterface.h"

// CAT 类型的节点通常继承自 MetaSound 的标准节点基类
// 具体的 CAT 数据类型定义在 MetasoundExperimentalRuntime 模块中
```

### Build.cs 模块依赖

```cpp
// 如果你的模块需要使用 CAT 类型
PublicDependencyModuleNames.Add("MetasoundExperimentalRuntime");

// 如果需要引擎级别的集成
PublicDependencyModuleNames.Add("MetasoundExperimentalEngineRuntime");

// 基础音频实验性功能
PublicDependencyModuleNames.Add("AudioExperimentalRuntime");
```

## Demo 示例

由于此插件主要提供 MetaSound 编辑器中的实验性节点，演示方式是通过 MetaSound 图而非 C++ 代码：

```cpp
// MyMetaSoundActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMetaSoundActor.generated.h"

UCLASS()
class AMyMetaSoundActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaSoundActor();

    // 引用一个使用了 CAT 节点的 MetaSound 资产
    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<USoundBase> ExperimentalMetaSound;

    UPROPERTY(VisibleAnywhere, Category = "Audio")
    TObjectPtr<UAudioComponent> AudioComponent;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void PlayExperimentalMetaSound();
};
```

```cpp
// MyMetaSoundActor.cpp
#include "MyMetaSoundActor.h"
#include "Components/AudioComponent.h"

AMyMetaSoundActor::AMyMetaSoundActor()
{
    AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComponent"));
    RootComponent = AudioComponent;
}

void AMyMetaSoundActor::PlayExperimentalMetaSound()
{
    if (ExperimentalMetaSound && AudioComponent)
    {
        AudioComponent->SetSound(ExperimentalMetaSound);
        AudioComponent->Play();
    }
}
```

> **提示**：CAT 节点的使用主要在 MetaSound 图编辑器中完成。创建 MetaSound 资产后，在节点面板中搜索 `[CAT]` 即可找到实验性节点。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心插件（.uplugin 声明的插件依赖） |

无其他特殊依赖（仅标准 Core/Engine/CoreUObject 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增 CAT 通道无关类型的 Wave（波形）数据类型支持 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 新增 CAT 乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 新增 CAT 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261' | 从待提交列表中提取并提交（之前的搁置改动） |

### 维护评价

- **活跃维护** ✅：最近更新集中在 2026 年 4-5 月，CAT 功能正在密集开发中
- **创建时间**：2025 年 4 月从 NotForLicensees 迁出公开，约 1 年历史
- **开发方向明确**：当前聚焦于 CAT（Channel Agnostic Types）通道无关类型系统，包括新的数据类型（Wave）和节点（Multiply、Ladder Filter）
- **实验性标记**：`IsExperimentalVersion: true`，`EnabledByDefault: false`，API 可能随版本变化
- **推荐使用**：如果你需要 MetaSound 的通道无关功能，此插件是唯一途径。但注意实验性 API 可能不稳定，不建议用于生产环境的最终版本。适合早期开发和原型验证阶段使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- 官方文档：无
- [MetaSound 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)