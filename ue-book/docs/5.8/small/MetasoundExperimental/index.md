# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound 实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性功能节点） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

此插件是 MetaSound 系统的实验性功能扩展库，用于在新功能正式发布到主插件 `Metasound` 前进行开发和测试。它包含了正在积极开发的前沿音频节点和功能，如通道无关类型 (Channel Agnostic Types, CAT) 相关操作，旨在为 MetaSound 图表提供更强大、更灵活的底层音频处理能力。

## 使用场景

- 你是音频程序员或技术音效设计师，需要提前体验并测试 MetaSound 即将推出的新节点和功能。
- 你的项目需要使用实验性的通道无关音频处理功能（如 CAT 波形、滤波器、运算节点）来构建复杂的音频逻辑。
- 你在为 MetaSound 引擎本身开发新特性，需要在此沙盒环境中进行原型设计和迭代。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `AudioExperimentalRuntime` | Runtime | 提供底层的、与 MetaSound 引擎解耦的实验性音频运行时功能和数据类型。 |
| `MetasoundExperimentalRuntime` | Runtime | 包含核心的、实验性的 MetaSound 节点、图表元素和运行时逻辑。 |
| `MetasoundExperimentalEngineRuntime` | Runtime | 负责将实验性 MetaSound 功能与引擎更深层次的系统（如声音波形数据）进行集成。 |
| `MetasoundExperimentalEditor` | Editor | 提供在编辑器中使用实验性 MetaSound 功能所需的工具和界面扩展。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档]() (暂无)
- [测试用例]() (暂无)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加实验性MetaSound通道无关类型(CAT)波形节点 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与FSoundWaveData API废弃相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 添加了CAT乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 添加了CAT阶梯滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从挂起的更改列表中恢复提交 |

### 维护评价

此插件处于**活跃开发**状态。创建时间虽短（约1年），但从近期提交记录看，更新非常频繁，内容集中在添加全新的实验性功能（CAT系列节点）。作为实验性插件，其功能和API可能随时变动，不推荐用于需要稳定性的生产项目。适用于希望提前探索 MetaSound 新功能的开发者和贡献者。