# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara) | |

## 总体用途

Niagara 是 UE5 的新一代 VFX 系统，用于创建高性能、高复杂度的粒子效果、动态模拟和环境特效。它通过节点化的粒子发射器（Emitter）和系统（System）编辑器，支持 GPU 和 CPU 双模式模拟，可处理数十万粒子。动画通知、蓝图节点、着色器、顶点工厂等模块共同提供完整的 VFX 管线，从设计到运行时渲染。

## 模块列表

| 模块 | 一句话总结 |
|---|---|
| `Niagara` (Runtime) | 核心运行时，包括粒子发射器、系统、参数、渲染等基础功能。 |
| `NiagaraAnimNotifies` (Runtime) | 动画通知集成，允许在动画过程中触发 Niagara 特效。 |
| `NiagaraBlueprintNodes` (Runtime) | 蓝图节点扩展，支持在蓝图中创建和操作 Niagara 特效。 |
| `NiagaraCore` (Runtime) | 核心基础库，提供数据结构、线程安全容器等底层支持。 |
| `NiagaraEditor` (Runtime) | 编辑器模块，包含系统/发射器编辑器、参数面板、预览等。 |
| `NiagaraEditorWidgets` (Runtime) | 编辑器自定义控件，如曲线编辑器、堆栈面板等。 |
| `NiagaraShader` (Runtime) | 着色器相关，管理 GPU 模拟所需的 HLSL 生成和编译。 |
| `NiagaraVertexFactories` (Runtime) | 顶点工厂，实现 Niagara 粒子渲染的网格管线。 |

> 各模块的详细 API 和用法请参见对应模块文档。

## 使用场景

- **角色技能特效**（火焰、冰霜、闪电） – 使用 Niagara 系统+BlueprintNodes 动态触发
- **环境粒子**（雨雪、落叶、萤火虫） – CPU 模拟，可结合动画通知实现天气变化
- **大规模物体模拟**（群组飞行、碎片爆炸） – GPU 模拟，VertexFactories 支持实例化渲染
- **交互式 UI/场景**（鼠标轨迹粒子、传送门） – 蓝图节点实时控制参数
- **动画联动特效**（挥剑拖尾、受击火花） – 通过 NiagaraAnimNotifies 在蒙太奇中触发

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)
- [Module: Niagara](Niagara.md) · [Module: NiagaraAnimNotifies](NiagaraAnimNotifies.md) · [Module: NiagaraBlueprintNodes](NiagaraBlueprintNodes.md) · [Module: NiagaraCore](NiagaraCore.md) · [Module: NiagaraEditor](NiagaraEditor.md) · [Module: NiagaraEditorWidgets](NiagaraEditorWidgets.md) · [Module: NiagaraShader](NiagaraShader.md) · [Module: NiagaraVertexFactories](NiagaraVertexFactories.md)