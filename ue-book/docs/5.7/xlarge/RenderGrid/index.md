# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid) | |

## 总体用途

Render Grid 是一个面向电影级渲染管道的高级编排工具。它允许用户创建、管理并批量渲染预定义的“渲染网格”序列，通常用于生成过场动画、宣传片或任何需要逐帧输出的高质量渲染任务。该插件整合了远程控制值设置、作业队列调度等功能，旨在简化复杂的渲染工作流。

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `RenderGrid` | Runtime | 提供渲染网格的核心数据结构、作业定义与序列管理逻辑。 | [RenderGrid.md](./RenderGrid.md) |
| `RenderGridDeveloper` | Runtime | 包含开发者辅助工具（如日志扩展、调试命令），便于排查渲染问题。 | [RenderGridDeveloper.md](./RenderGridDeveloper.md) |
| `RenderGridEditor` | Runtime | 提供编辑器面板与 UI 交互，允许可视化编辑渲染网格、预览作业并触发渲染。 | [RenderGridEditor.md](./RenderGridEditor.md) |

## 使用场景

- **批量渲染电影级过场动画**：在关卡中预先设定多个摄像机位置/序列，通过 Render Grid 一次性渲染输出。
- **自动化渲染流水线**：结合远程控制（Remote Control）动态修改场景参数，实现无需手动干预的批量渲染。
- **快速预览与迭代**：在编辑器中创建渲染任务，立即看到单个帧的输出效果，调整后再提交完整作业。
- **多作业管理与排队**：同时定义多个渲染作业，按优先级或顺序执行，适合团队协作或连续交付。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid)
- 各模块详细文档请参见上表链接。