# Audio Motor Sim

> Compositional method for simulating audio for vehicles.

| 属性 | 值 |
|---|---|
| 中文名 | 音频马达模拟 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioMotorSim` (Runtime), `AudioMotorSimStandardComponents` (Runtime), `AudioMotorSimDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim) | |

## 用途

此插件提供了一种**组合式**的架构，用于模拟车辆（特别是赛车、跑车）的引擎声音。它并非直接播放静态音频样本，而是通过一系列可组合的组件（Component），将车辆运行数据（如 RPM、油门位置、负载等）实时转换为动态变化的音频输出。这种方法能生成高度响应和真实的引擎声音反馈，比传统采样方法更灵活、更节省内存。

## 使用场景

- **开发赛车或驾驶模拟游戏**：你需要让引擎声音随着玩家的操作（如踩油门、换挡）实时、平滑地变化。
- **创建高度自定义的车辆音效**：希望摆脱预录音频样本的限制，通过调整参数来塑造独特的引擎音色。
- **优化音频内存和性能**：使用基于组件的生成式音频，而非加载大量高保真采样。

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `AudioMotorSim` | Runtime | 核心模块，定义了模拟的基础接口和数据类型。 |
| `AudioMotorSimStandardComponents` | Runtime | 标准组件库，提供如“音高”、“负载”等常见的马达模拟组件。 |
| `AudioMotorSimDebug` | Runtime | 调试模块（非 Shipping 构建），提供可视化调试工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，统一代码风格。 |
| 2026-01-17 | `302d1b88` | [Backout] - CL49913998 | 回退了之前的某次提交。 |
| 2026-01-17 | `622fab9f` | SlateIM: You can now create always on top windows. | 依赖的SlateIM插件功能更新。 |

### 维护评价

该插件创建于约 4 年前，仍处于**实验性**阶段（`IsExperimentalVersion=true`）。最近一年内的提交主要是依赖项更新和内部维护，未见核心音频模拟功能的实质性迭代。由于标记为实验性且默认未启用，其状态可能仍为**探索或内部使用**。对于外部开发者，可将其视为一个**有潜力但尚不成熟**的参考架构，不建议直接用于需要高度稳定性的商业项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim)
- [子模块文档：核心接口](AudioMotorSim.md)
- [子模块文档：标准组件](AudioMotorSimStandardComponents.md)
- [子模块文档：调试工具](AudioMotorSimDebug.md)