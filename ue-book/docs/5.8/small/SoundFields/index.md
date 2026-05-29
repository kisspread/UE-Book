# SoundFields

> Plugin featuring a variety of basic audio SoundFields solutions.

| 属性 | 值 |
|---|---|
| 中文名 | 声场插件 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SoundFields` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-02-09 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundFields) | |

## 用途

SoundFields 插件为 Unreal 音频引擎提供了基础的**声场（Soundfield）处理框架**，特别是实现了内置的 **Ambisonics（高阶立体声）** 格式支持。它并非一个独立的音频播放器，而是音频管线中的一个核心组件，负责处理具有空间信息的声音数据（如环绕声、全景声）的编码、解码和混合。

**为什么存在？** 现代音频需要支持复杂的空间音频格式（如 Ambisonics），以用于 VR/AR、游戏中的环境音效模拟、以及专业音频制作。该插件为 Unreal 提供了一套标准化的接口和默认实现，使开发者能够将空间音频无缝集成到引擎中，并方便地扩展支持更多声场格式。

## 使用场景

-   你在开发一个 **VR 或 AR 应用**，需要实现具有方向感的环境音效（如声音从特定方向传来）→ 使用 SoundFields 的 Ambisonics 编解码器。
-   你正在为一个 **3D 游戏**制作全景声环境音轨（如森林、城市氛围）→ 通过声场子混音（Soundfield Submix）进行编码和处理。
-   你需要在 Unreal 中集成 **专业音频工作流**（如 DAW 输出的 Ambisonics 音频）→ 利用该插件提供的转码功能，将 Ambisonics 音频适配到引擎音频管线。
-   你计划开发自己的 **自定义空间音频格式**→ 该插件的 `ISoundfieldFactory` 接口提供了完整的扩展框架。

## 蓝图用法

该插件主要通过数据资产（如 `USoundfieldEncodingSettingsBase` 的子类）进行配置，直接暴露给蓝图的可调用函数较少。核心的交互点是配置编码设置。

### 核心配置

| 属性/设置 | 说明 | 所在类 |
|---|---|---|
| `Ambisonics Order` | 设置 Ambisonics 的阶数（1-5阶）。阶数越高，空间分辨率越高，但计算成本也越高。 | `UAmbisonicsEncodingSettings` |

### 使用示例（蓝图描述）

1.  **创建编码设置资产**：在内容浏览器右键 -> 音频 -> Soundfield -> Ambisonics Encoding Settings，创建一个 `UAmbisonicsEncodingSettings` 资产。
2.  **配置资产**：打开该资产，在细节面板中找到 “Encoding Settings” 分类，调整 `Ambisonics Order`（如设为 3 阶）。
3.  **应用设置**：将此配置资产赋给需要使用 Ambisonics 的音频组件（如声场子混音）的相应属性。

## C++ 用法

### 头文件引入

```cpp
#include “SoundFields.h”
```

### 基本用法

主要涉及获取和配置默认的声场编码设置。

```cpp
// (来源：SoundFields.h)
// 创建一个 Ambisonics 编码设置对象并配置阶数
UAmbisonicsEncodingSettings* AmbiSettings = NewObject<UAmbisonicsEncodingSettings>();
AmbiSettings->AmbisonicsOrder = 3; // 设置为 3 阶 Ambisonics

// 通常，开发者不需要直接操作 FAmbisonicsSoundfieldFormat，它是内部工厂类。
// 核心工作流是：创建设置对象 -> 将其赋给音频系统中的相关属性。
```

### 进阶用法

对于高级用户，可以研究 `ISoundfieldFactory` 接口以实现自定义声场格式。以下展示了如何获取该工厂并查询其信息：

```cpp
// (来源：SoundFields.h)
// 注意：FAmbisonicsSoundfieldFormat 是内部实现类，直接使用需要访问引擎内部。
// 通常，引擎会通过其插件系统自动注册和管理这个工厂。
// 以下为概念性示例：
FAmbisonicsSoundfieldFormat AmbisonicsFactory;
FName FormatName = AmbisonicsFactory.GetSoundfieldFormatName(); // 应返回 “Ambisonics”
```

## Demo 示例

以下是一个在运行时动态创建并查询 Ambisonics 编码设置的最小示例。

**MySoundfieldActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SoundFields.h" // 引入 SoundFields 头文件
#include "MySoundfieldActor.generated.h"

UCLASS()
class MYPROJECT_API AMySoundfieldActor : public AActor
{
	GENERATED_BODY()

public:
	AMySoundfieldActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY()
	UAmbisonicsEncodingSettings* CurrentAmbisonicsSettings;
};
```

**MySoundfieldActor.cpp**
```cpp
#include "MySoundfieldActor.h"

AMySoundfieldActor::AMySoundfieldActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMySoundfieldActor::BeginPlay()
{
	Super::BeginPlay();

	// 创建一个默认的 Ambisonics 编码设置
	CurrentAmbisonicsSettings = NewObject<UAmbisonicsEncodingSettings>(this);

	// 可以在这里修改设置，例如：CurrentAmbisonicsSettings->AmbisonicsOrder = 2;

	// 打印当前设置，验证插件功能
	if (CurrentAmbisonicsSettings)
	{
		UE_LOG(LogTemp, Log, TEXT("SoundFields: Ambisonics Encoding Settings created. Default Order: %d"), CurrentAmbisonicsSettings->AmbisonicsOrder);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("SoundFields: Failed to create Ambisonics Encoding Settings."));
	}
}
```

## 模块依赖

根据声场处理的通用需求，该插件的核心模块 `SoundFields` 可能依赖以下音频相关模块。由于 `Build.cs` 文件未提供，以下是基于功能的合理推测。

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 提供数字信号处理（DSP）基础功能，用于 Ambisonics 的数学运算（如旋转、编码）。 |
| `AudioMixer` | 作为底层音频混音器，声场处理器需要与之交互以注入或提取声场音频包。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 将插件中的方法和静态变量标记为 `UE_API` (DLL导出)，是代码导出规范化的维护工作。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理了引擎版本迭代中遗留的、已废弃的头文件包含顺序相关的条件编译代码。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件的常规合并或大规模更新的一部分，无特定于 SoundFields 的新功能说明。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 同上，属于引擎插件集体更新。 |
| 2022-12-13 | `32b44518` | [Soundfields] changed check() for IsInGameThread to IsInAudioThread - Hitting check when initting so | 修复了一个线程检查错误：将断言 `IsInGameThread()` 改为 `IsInAudioThread()`，解决了在音频线程初始化时触发崩溃的 bug。 |

### 维护评价

-   **状态**：**维护中（但无活跃功能开发）**。插件创建于 2020 年，最近一次有意义的**功能性修复**是 2022 年的线程安全修复。此后的更新均为引擎级的代码规范化和维护性工作。
-   **实验性**：该插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，表明其接口和实现可能在未来版本中发生变化。
-   **推荐度**：**谨慎使用**。对于需要 Ambisonics 支持的**生产项目**，建议进行充分测试，并关注引擎更新日志，因为其 API 可能调整。它非常适合用于学习和原型开发，是理解 Unreal 声场系统基础的绝佳范例。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundFields)
-   [官方文档]() （未提供）