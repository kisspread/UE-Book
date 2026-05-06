# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSounds 实验性扩展 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalEditor` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 总体用途

Metasounds Experimental 是 MetaSound 系统的开发中特性预览插件。它包含尚未完全稳定或准备正式发布的新节点、优化及实验性功能，允许音频程序员和声音设计师提前使用并反馈。当前主要亮点包括 **Fade Node**（淡入淡出节点）及相关的性能优化。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `AudioExperimentalRuntime` | Runtime | 提供音频实验运行时基础设施，用于加载和处理实验性音频资源。 |
| `MetasoundExperimentalRuntime` | Runtime | 包含实验性 MetaSound 节点逻辑（如 Fade Node）及核心算法实现。 |
| `MetasoundExperimentalEngineRuntime` | Runtime | 负责将实验性 MetaSound 功能集成到引擎管线中，如节点注册与优化反馈。 |
| `MetasoundExperimentalEditor` | Runtime | 在编辑器中提供实验性节点的 UI 支持、测试工具及资产管理。 |

> 各模块的详细 API 和用法请参考对应模块文档：
> - [AudioExperimentalRuntime](./AudioExperimentalRuntime.md)
> - [MetasoundExperimentalRuntime](./MetasoundExperimentalRuntime.md)
> - [MetasoundExperimentalEngineRuntime](./MetasoundExperimentalEngineRuntime.md)
> - [MetasoundExperimentalEditor](./MetasoundExperimentalEditor.md)

## 使用场景

- **开发自定义 MetaSound 节点**：利用实验性框架提前开发并测试尚未标准化的节点。
- **测试音频信号处理新特性**：如 Fade Node 等，评估其在项目中的表现和稳定性。
- **参与 MetaSound 功能演进**：为 Epic 提供早期反馈，影响后续正式版本的 API 设计。
- **性能优化验证**：利用插件中的优化反馈机制，对比与官方 MetaSound 的性能差异。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metasound/)（MetaSound 主文档）
- 测试用例路径：`Engine/Plugins/Experimental/MetasoundExperimental/Tests/`