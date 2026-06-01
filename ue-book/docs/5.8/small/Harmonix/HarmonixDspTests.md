# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、MetaSound 节点） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMidi` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidiTests` (Runtime), `HarmonixEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

---

## 📦 模块结构

| 模块 | 类型 | 说明 |
|---|---|---|
| `Harmonix` | Runtime | 核心模块，统一管理音乐相关功能 |
| `HarmonixDsp` | Runtime | 数字信号处理，音频合成与采样 |
| `HarmonixMetasound` | Runtime | MetaSound 集成，提供音乐相关音频节点 |
| `HarmonixMidi` | Runtime | MIDI 解析与处理 |
| `HarmonixDspEditor` | Runtime | DSP 模块的编辑器支持 |
| `HarmonixMetasoundEditor` | Runtime | MetaSound 模块的编辑器支持 |
| `HarmonixMidiEditor` | Runtime | MIDI 模块的编辑器支持 |
| `HarmonixDspTests` | Runtime | DSP 模块自动化测试 |
| `HarmonixMetasoundTests` | Runtime | MetaSound 模块自动化测试 |
| `HarmonixMidiTests` | Runtime | MIDI 模块自动化测试 |
| `HarmonixEditor` | Runtime | 编辑器通用功能 |

> **注意**：所有模块的 `Type` 均标记为 Runtime，但包含 Editor/Tests 后缀的模块主要用于编辑器和测试场景。

---

## 用途

Harmonix 是由 Epic Games 旗下 Harmonix GenTech 团队开发的**专业音乐音频引擎插件**，提供完整的音乐制作与交互音频解决方案。

该插件解决以下核心问题：

1. **音乐与节奏游戏开发**：为 Fortnite Festival 等节奏游戏提供底层音频支持
2. **MIDI 数据处理**：完整的 MIDI 文件解析、事件处理与实时控制
3. **音频 DSP 处理**：高级数字信号处理，支持音频合成、采样播放（Fusion 系统）
4. **MetaSound 扩展**：为 UE5 的 MetaSound 系统添加音乐相关的专业节点

该插件从 `ue5-main` 分支迁移至 `Engine/Plugins/Runtime/`，使所有 UE5 授权用户可以使用。

---

## 使用场景

- 你在开发**节奏游戏**（如《吉他英雄》类）→ 使用 HarmonixMidi + HarmonixDsp 处理音符同步与音频回放
- 你需要在 MetaSound 中使用**专业音乐节点**（BPM 同步、音高变换、音符触发）→ 使用 HarmonixMetasound
- 你要处理 **MIDI 文件**用于动态配乐或交互式音乐 → 使用 HarmonixMidi
- 你需要高质量的**音频采样合成**与 Fusion 乐器系统 → 使用 HarmonixDsp
- 你正在开发 **Fortnite Festival** 等需要精确音符判定的游戏 → 完整使用 Harmonix 插件栈

---

## 蓝图用法

> ⚠️ 该插件为实验性功能，蓝图 API 可能随版本变化。以下为核心功能节点。

### 核心节点

| 节点 | 说明 | 所在模块 |
|---|---|---|
| MIDI 文件加载/解析 | 加载 MIDI 文件并解析为可用数据结构 | `HarmonixMidi` |
| 音频 Fusion 乐器 | 基于采样的乐器合成系统 | `HarmonixDsp` |
| MetaSound 音乐节点 | BPM 同步、音符触发等音乐专用节点 | `HarmonixMetasound` |

### 使用示例（蓝图描述）

**MIDI 驱动的交互音乐**：
1. 通过 `HarmonixMidi` 加载 MIDI 文件
2. 将 MIDI 事件流连接到 `HarmonixMetasound` 的音符触发节点
3. 在 MetaSound 图表中实现动态音乐过渡

**Fusion 乐器系统**：
1. 创建 FusionPatch 资产（定义音区映射和采样）
2. 通过 `HarmonixDsp` 的 Fusion 播放器节点进行音频回放
3. 实时控制音高、音量和包络

---

## C++ 用法

### 头文件引入

```cpp
// MIDI 模块
#include "HarmonixMidi/MidiFile.h"

// DSP 模块
#include "HarmonixDsp/FusionPatch.h"

// MetaSound 模块
#include "HarmonixMetasound/..."
```

### 基本用法 - 测试工具

来自 `HarmonixDspTests/Private/TestUtility.h`：

```cpp
#include "HarmonixDspTests/Private/TestUtility.h"

// 比较两个浮点数组是否相等（带容差）
TArray<float> Expected = { 1.0f, 2.0f, 3.0f };
TArray<float> Actual = { 1.0f, 2.00001f, 3.0f };
bool bMatch = Harmonix::Testing::Utility::CheckAll(Expected, Actual, 0.001f);

// 将数组转换为可读字符串（调试用）
FString Description = Harmonix::Testing::Utility::ArrayToString(Actual, 3);
// 输出: "{1.000, 2.000, 3.000}"
```

### 进阶用法 - Fusion 乐器系统

```cpp
// FusionPatch 代理用于追踪乐器活动
// 从 commit 0ae74ea8 可知支持用户对象绑定
UFusionPatchProxy* PatchProxy = /* ... */;
PatchProxy->SetUserObject(MyTrackerObject);  // 用于追踪活动状态
```

---

## Demo 示例

> 该插件为大型框架，完整示例请参考 Epic 的 Festival 示例项目。以下是最小化使用示例。

### MIDI 文件加载

```cpp
// MyMidiPlayer.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMidiPlayer.generated.h"

UCLASS()
class AMyMidiPlayer : public AActor
{
    GENERATED_BODY()

public:
    AMyMidiPlayer();

    UPROPERTY(EditAnywhere, Category = "Music")
    FString MidiFilePath;

    void LoadAndPlayMidi();
};
```

```cpp
// MyMidiPlayer.cpp
#include "MyMidiPlayer.h"
#include "HarmonixMidi/MidiFile.h"

AMyMidiPlayer::AMyMidiPlayer()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMidiPlayer::LoadAndPlayMidi()
{
    // MIDI 加载与播放逻辑
    // 实际 API 请参考 HarmonixMidi 模块文档
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HarmonixMidi` | MIDI 文件解析与事件处理 |
| `HarmonixDsp` | 音频 DSP 与 Fusion 乐器系统 |
| `HarmonixMetasound` | MetaSound 音乐节点扩展 |
| `AssetRegistry` | 资产注册与管理 |
| `MetasoundEngine` | MetaSound 核心引擎 |

> `UnrealEd` 依赖仅用于 Editor 类模块，运行时不需要。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音频系统 KeyZone 排序问题并增加空值防护 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 的截断警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 为 FusionPatch 代理添加用户对象，用于追踪乐器活动状态 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

- **状态**：🟢 **活跃维护中**
- **创建时间**：2024-01-17，约 2 年历史
- **更新频率**：近期（2026年5月）持续有实质性更新
- **团队背景**：由 Epic Games 旗下 Harmonix GenTech 专业团队维护
- **已知限制**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **推荐度**：⭐⭐⭐⭐ 适合需要专业音乐功能的项目，但需注意实验性状态

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 官方文档：暂无公开文档
- 相关项目：Fortnite Festival（该插件的主要使用场景）

---

## 启用方式

在项目的 `.uproject` 文件或编辑器插件设置中：

```json
{
    "Plugins": [
        {
            "Name": "Harmonix",
            "Enabled": true
        }
    ]
}
```

或在编辑器中：**Edit → Plugins → 搜索 "Harmonix" → 启用**