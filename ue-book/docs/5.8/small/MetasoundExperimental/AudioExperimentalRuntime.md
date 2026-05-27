# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound 实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频实验性资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

MetaSound 实验性功能插件，专门用于在正式发布前测试 MetaSound 系统的新特性。该插件目前聚焦于 **Channel Agnostic Types (CAT，通道无关类型)** 系统的开发，这是一种让音频处理不依赖特定通道配置（如单声道、立体声、5.1 等）的架构设计。

该插件的存在意义：
- 为 MetaSound 的新功能提供一个安全的实验环境
- CAT Wave 系统使得音频节点可以在不同通道配置下保持一致的行为逻辑
- 新的音频处理节点（如 Ladder Filter）在集成到主 MetaSound 系统前先在此验证

## 使用场景

- 你需要在 MetaSound 中创建通道无关的音频处理逻辑 → 用 CAT Wave
- 你想提前体验 MetaSound 即将推出的新节点和功能 → 启用此插件
- 你在开发跨平台音频系统，需要统一不同通道配置下的音频行为 → 使用 CAT 类型

## 蓝图用法

本插件为实验性运行时功能，主要面向 MetaSound 节点编辑器，而非蓝图。CAT 节点在 MetaSound 编辑器中以图形化节点形式使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| CAT Wave | 通道无关的音频波形输入节点 | MetaSound 节点 |
| CAT Multiply | 通道无关的信号乘法节点 | MetaSound 节点 |
| CAT Ladder Filter | 通道无关的阶梯滤波器节点 | MetaSound 节点 |

### 使用示例（MetaSound 编辑器）

1. 启用插件后，在 MetaSound 编辑器中搜索 "CAT" 前缀的节点
2. 将 CAT Wave 节点连接到 CAT Multiply 或 CAT Ladder Filter 节点
3. CAT 类型会自动适配当前音频输出的通道配置，无需手动处理通道映射

## C++ 用法

本插件的主要功能通过 MetaSound 节点图使用，C++ 接口主要用于节点扩展开发。

### 头文件引入

```cpp
#include "AudioExperimentalRuntime/AudioExperimentalRuntime.h"
#include "MetasoundExperimentalRuntime/MetasoundExperimentalRuntime.h"
```

### 基本用法

作为运行时模块，该插件主要扩展 MetaSound 的节点注册系统，开发者可以通过继承扩展新的 CAT 节点。

## Demo 示例

本插件为实验性 MetaSound 扩展，主要使用方式是通过 MetaSound 编辑器中的节点图。C++ 集成主要面向节点开发者，而非直接的应用层代码。

## 模块依赖

本插件依赖 MetaSound 插件：

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心系统（必要依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增通道无关类型（CAT）Wave 功能 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 新增 CAT Multiply 节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 新增 CAT Ladder Filter 节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261' | 从待处理变更集中恢复 |

### 维护评价

**状态：活跃开发中 🟢**

- **创建时间**：约 1 年前（2025-04-22），从 NotForLicensees 目录移出
- **最近更新**：最近数天内有密集的功能性更新，CAT 系统正在快速迭代
- **开发趋势**：Channel Agnostic Types (CAT) 是当前开发重心，新增了 Wave、Multiply、Ladder Filter 等节点
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **推荐使用**：适合提前体验 MetaSound 新特性，但不建议在生产环境使用。CAT 系统处于活跃开发中，API 可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [MetaSound 文档](https://docs.unrealengine.com/5.8/en-US/metasounds-in-unreal-engine/)（基础 MetaSound 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)（待确认）