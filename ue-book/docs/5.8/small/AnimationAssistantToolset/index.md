# AnimationAssistantToolset

> Toolset for Animation Systems

| 属性 | 值 |
|---|---|
| 中文名 | 动画辅助工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationAssistantToolset` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AnimationAssistantToolset) | |

## 用途

AnimationAssistantToolset 是 Epic Games 开发的 AI Toolsets 框架的一部分，专门用于为动画系统提供 AI 辅助工具集。该插件通过 ToolsetRegistry 进行注册，作为 ControlRig 和 Sequencer 编辑器的扩展点，用于支持 AI 驱动的动画创建和编辑工作流。

从源码来看，该插件目前是一个极为精简的骨架实现——模块头文件仅包含标准的 `IModuleInterface` 启动/关闭方法，没有暴露任何公开的蓝图函数或 C++ API。这表明它仍处于早期开发阶段，主要作为工具集注册和容器存在，实际的动画工具功能可能由子工具（如 AnimationMixer 等）通过插件化方式提供。

## 使用场景

- 你正在使用 AI 辅助工作流编辑动画序列 → 通过 ToolsetRegistry 框架启用该工具集
- 你需要在 Sequencer 编辑器中进行 AI 驱动的动画混合和创建 → 该插件作为基础设施提供支持
- 你正在开发基于 ControlRig 的 AI 动画工具 → 该插件提供工具集注册框架

## 蓝图用法

该插件当前**不包含任何公开的蓝图节点**。模块头文件中未定义 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。

## C++ 用法

该插件当前**不包含任何公开的 C++ API**。模块仅实现了基础的 `IModuleInterface` 接口。

### 头文件引入

```cpp
#include "AnimationAssistantToolset.h"
```

### 模块引用（仅用于模块依赖检查）

```cpp
// 该模块目前仅提供生命周期管理，无额外 API
// 如需依赖此模块，仅需在 Build.cs 中添加模块依赖
FModuleManager::Get().LoadModule(TEXT("AnimationAssistantToolset"));
```

## Demo 示例

该插件目前无实质功能实现，不提供 Demo 示例。待插件功能完善后可补充。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 动画控制绑定系统，提供程序化动画能力 |
| `ToolsetRegistry` | AI Toolsets 框架的工具集注册系统 |
| `LevelSequenceEditor` | Sequencer 编辑器集成，用于动画序列编辑 |
| `SequencerScripting` | Sequencer 脚本 API，用于程序化序列操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 将动画混合器拆分为独立插件，新增 SequencerTools 工具集 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退了之前的某个变更 |
| 2026-04-10 | `e98edc29` | [EDA] Add SequencerTools toolset for AI-driven sequence creation and editing | 新增 SequencerTools 工具集，用于 AI 驱动的序列创建和编辑 |
| 2026-04-03 | `aed04419` | [AI Toolsets]: Ensure all toolset plugins are marked as editor only. | 确保所有工具集插件标记为仅编辑器使用 |
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 将所有工具集移至引擎初始化后加载，简化注册流程 |

### 维护评价

**⚠️ 早期实验性项目 — 谨慎使用**

- **创建时间**：2026-04-02，极为新生的插件（不到 1 个月）
- **更新频率**：创建后一周内有多次快速迭代，处于活跃开发初期
- **代码成熟度**：当前模块代码极为精简，仅包含标准的模块生命周期接口，无实质功能实现
- **实验性标记**：`IsExperimentalVersion=true`，且默认未启用（`Installed=false`）
- **依赖关系复杂**：依赖 ControlRig、Sequencer 等重量级模块，说明设计意图是构建大型动画工具集
- **已知限制**：当前版本无公开 API，无法直接使用；功能可能正在拆分到子插件中（见 Anim Mixer 拆分动向）

**建议**：该插件属于 Epic 内部 AI Toolsets 框架的一部分，目前处于非常早期的开发阶段。普通开发者暂不建议依赖此插件，建议关注后续版本的功能完善情况。可以作为参考 AI 工具集架构模式的学习资源。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AnimationAssistantToolset)
- 官方文档：暂无
- 测试用例：暂无