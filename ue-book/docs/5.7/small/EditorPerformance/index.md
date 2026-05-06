# Editor Performance

> Plugin that provides Editor Performance feedback to developers

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance) | |

## 总体用途

Editor Performance 插件为 Unreal Editor 开发者提供实时的性能反馈与诊断能力。它包含两个核心子系统：

- **EditorPerformance 模块**：负责收集编辑器运行时性能指标（帧率、卡顿次数、内存等），并在界面中展示状态栏通知和对话框。
- **StallLogSubsystem 模块**：记录编辑器主线程卡顿事件，生成结构化日志，帮助追踪定位性能瓶颈。

该插件是实验性工具，默认启用，旨在帮助开发者快速发现和解决编辑器自身或插件导致的性能问题。

## 模块一览

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `EditorPerformance` (Editor) | 提供编辑器性能状态监控、状态栏提示和诊断对话框。 | [EditorPerformance.md](EditorPerformance.md) |
| `StallLogSubsystem` (Editor) | 自动记录编辑器主线程卡顿堆栈与时长，支持 Log 输出与订阅回调。 | [StallLogSubsystem.md](StallLogSubsystem.md) |

## 使用场景

- **编辑器插件开发者**：需要监测自己的插件是否导致编辑器卡顿或帧率下降。
- **引擎工具团队**：希望快速定位编辑器启动或操作中的性能问题。
- **日常使用**：普通开发者可通过状态栏实时了解编辑器健康度，并在卡顿时获得自动诊断日志。
- **集成测试**：结合 StallLogSubsystem 的日志 API 编写自动化测试，确保编辑器性能基准。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance)
- 官方文档：无
- 测试用例：无独立测试目录（模块内测试分散于各自源文件）