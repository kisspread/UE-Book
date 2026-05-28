# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 中文名 | 变形图编辑器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `OptimusCore` (Runtime), `OptimusDeveloper` (Runtime), `OptimusEditor` (Runtime), `OptimusSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

DeformerGraph 是一个基于节点图的 GPU 网格变形编辑器（前身为实验性插件 "Optimus"）。它解决的核心问题是：**如何让美术和技术美术无需手写 Compute Shader，就能创建复杂的自定义 GPU 蒙皮变形管线**。

通过可视化的节点编辑器，用户可以：
- 组合预置的数据接口（骨骼、网格顶点、自定义属性等）
- 连接数学、逻辑、采样等运算节点
- 编译生成对应的 Compute Shader 并在运行时高效执行

该插件填补了引擎内置骨骼蒙皮和完全手写 Compute Shader 之间的空白，特别适合需要在 GPU 上做大规模网格变形的场景。

## 使用场景

- 你需要对角色布料、毛发、肌肉进行自定义 GPU 驱动变形 → 用 DeformerGraph
- 你需要在不修改引擎源码的前提下扩展自定义蒙皮管线 → 用 DeformerGraph
- 技术美术需要可视化地构建 GPU 变形逻辑并实时预览 → 用 DeformerGraph
- 你需要对大量顶点做程序化位移（地形侵蚀、建筑形变等）→ 用 DeformerGraph

## 子模块列表

| 模块 | 类型 | 职责 |
|---|---|---|
| [OptimusCore](OptimusCore.md) | Runtime | 核心运行时：节点图模型、数据接口、着色器编译、GPU 调度 |
| [OptimusDeveloper](OptimusDeveloper.md) | Runtime | 开发者工具：调试、性能分析等辅助功能 |
| [OptimusEditor](OptimusEditor.md) | Runtime | 编辑器 UI：节点图编辑器、资产浏览器、属性面板 |
| [OptimusSettings](OptimusSettings.md) | Runtime | 项目设置：全局配置项（调试开关、默认行为等） |

> 详细 API 和代码示例请参阅各子模块文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph)
- 官方文档：暂无（DocsURL 为空）