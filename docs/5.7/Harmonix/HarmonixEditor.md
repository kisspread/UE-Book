# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、MIDI 资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 旗下 Harmonix GenTech 团队开发的**音乐与音频处理工具集**。Harmonix 是著名的音乐游戏（如《Rock Band》、《Guitar Hero》）背后的开发团队，该插件将他们在音乐技术领域的专业知识带入 Unreal Engine。

该插件解决的核心问题是：**在游戏运行时提供专业级的音乐同步、MIDI 处理和音频 DSP 能力**。它不是一个简单的音频播放器，而是一套完整的音乐技术栈，包含：

- **MIDI 解析与处理**（HarmonixMidi）：读取、解析和操作 MIDI 文件，支持音符事件、控制器变化、时间签名等
- **音频 DSP 处理**（HarmonixDsp）：提供音频信号处理算法，如滤波器、延迟、混响等效果器
- **MetaSound 集成**（HarmonixMetasound）：将 Harmonix 的音乐处理能力与 UE5 的 MetaSound 音频图系统深度集成
- **核心框架**（Harmonix）：提供音乐时间、节拍同步、BPM 跟踪等基础音乐理论功能

**为什么存在**：UE5 内置的音频系统主要面向通用音效播放，缺乏专业音乐游戏和交互式音乐体验所需的精确节拍同步、MIDI 处理和音乐理论支持。Harmonix 填补了这一空白。

## 使用场景

- 你在开发**节奏游戏**（如音游、舞蹈游戏）→ 用 HarmonixMidi 解析谱面，用 Harmonix 核心模块做节拍同步
- 你需要**交互式音乐系统**（音乐随游戏状态动态变化）→ 用 HarmonixMetasound 与 MetaSound 图结合
- 你在做**音乐可视化**（音频频谱分析驱动视觉效果）→ 用 HarmonixDsp 进行音频分析
- 你需要**精确的 BPM 同步**（动画、特效与音乐节拍对齐）→ 用 Harmonix 核心模块的节拍时钟
- 你在开发**DJ/混音应用**→ 用 HarmonixDsp 的音频处理和 Harmonix 的时间控制

## 模块架构

```
Harmonix (插件根)
├── Harmonix              ← 核心框架：音乐时间、节拍同步、BPM
├── HarmonixDsp           ← 音频 DSP：滤波器、延迟、效果器
├── HarmonixMidi          ← MIDI 处理：解析、事件、序列
├── HarmonixMetasound     ← MetaSound 集成：节点、图表
├── HarmonixEditor        ← 核心编辑器支持
├── HarmonixDspEditor     ← DSP 编辑器支持
├── HarmonixMidiEditor    ← MIDI 编辑器支持
├── HarmonixMetasoundEditor ← MetaSound 编辑器支持
├── HarmonixDspTests      ← DSP 测试
├── HarmonixMidiTests     ← MIDI 测试
└── HarmonixMetasoundTests ← MetaSound 测试
```

## 蓝图用法

> ⚠️ 由于本插件为实验性且源码规模极大（722 文件），以下为基于模块结构推断的核心功能。具体蓝图节点需在启用插件后查看。

### 核心功能模块

| 功能域 | 说明 | 所在模块 |
|---|---|---|
| MIDI 文件解析 | 加载和解析 MIDI 文件，获取音符、节拍、控制器事件 | `HarmonixMidi` |
| 节拍时钟 | 基于 BPM 的精确节拍跟踪，支持变速和时间签名变化 | `Harmonix` |
| 音频效果器 | DSP 效果处理链（滤波、延迟、失真等） | `HarmonixDsp` |
| MetaSound 节点 | 在 MetaSound 图中使用 Harmonix 音乐处理节点 | `HarmonixMetasound` |

### 典型工作流

1. **导入 MIDI 文件** → 通过 HarmonixMidi 创建 MIDI 资产
2. **创建节拍时钟** → 通过 Harmonix 核心模块建立 BPM 同步时钟
3. **连接 MetaSound** → 在 MetaSound 图中使用 Harmonix 节点处理音频
4. **响应音乐事件** → 通过蓝图事件绑定音符/节拍回调

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "HarmonixModule.h"

// MIDI 处理
#include "HarmonixMidiModule.h"

// DSP 处理
#include "HarmonixDspModule.h"

// MetaSound 集成
#include "HarmonixMetasoundModule.h"
```

### 模块依赖配置

在你的模块 `Build.cs` 中添加依赖：

```csharp
// 基础 MIDI 功能
PublicDependencyModuleNames.Add("HarmonixMidi");

// 音频 DSP 处理
PublicDependencyModuleNames.Add("HarmonixDsp");

// MetaSound 集成
PublicDependencyModuleNames.Add("HarmonixMetasound");

// 核心框架（通常被其他模块自动依赖）
PublicDependencyModuleNames.Add("Harmonix");
```

## 子模块文档

由于 Harmonix 是 xlarge 级插件（722 个源文件），各子模块独立文档：

| 子模块 | 说明 | 文档 |
|---|---|---|
| Harmonix | 核心框架：音乐时间、节拍同步 | [Harmonix 核心](Harmonix.md) |
| HarmonixDsp | 音频 DSP 处理引擎 | [HarmonixDsp](HarmonixDsp.md) |
| HarmonixMidi | MIDI 文件解析与处理 | [HarmonixMidi](HarmonixMidi.md) |
| HarmonixMetasound | MetaSound 集成节点 | [HarmonixMetasound](HarmonixMetasound.md) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册与发现（HarmonixDsp, HarmonixMetasound, HarmonixMidi 使用） |
| `UnrealEd` | 编辑器功能支持（资产导入、自定义编辑器等） |
| `MetasoundEngine` | MetaSound 音频图引擎集成 |
| `MetasoundFrontend` | MetaSound 前端节点定义 |

## 维护状态

### 近期更新

```
- 2024-01-17 797f4521b125 [Harmonix] Move Harmonix plugin into Engine/Plugins/Runtime to make it available to licensees in UE 5.4
```

### 维护评价

- **创建时间**：2024 年 1 月，非常新的插件
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **维护活跃度**：仅有一次初始提交（将插件移入 Runtime 目录），尚无后续功能更新
- **团队背景**：由 Epic Games Harmonix GenTech 团队开发，有专业音乐游戏开发背景
- **已知限制**：
  - 实验性 API，可能在后续版本中发生重大变更
  - 默认未启用，需要手动在插件管理器中激活
  - 文档和示例可能不完善

**推荐程度**：⭐⭐⭐（3/5）

适合对音乐同步和交互式音频有专业需求的项目。由于是实验性插件，建议在生产环境中谨慎使用，密切关注版本更新。对于节奏游戏和音乐可视化项目，这是目前 UE5 中最专业的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)