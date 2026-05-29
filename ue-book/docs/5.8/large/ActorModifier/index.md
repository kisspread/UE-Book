# Actor Modifier

> Actual implementation of modifiers for actors based on ActorModifierCore plugin

| 属性 | 值 |
|---|---|
| 中文名 | Actor 修改器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ActorModifier` (Runtime), `ActorModifierEditor` (Runtime), `ActorModifierLayout` (Runtime), `ActorModifierRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier) | |

## 用途

ActorModifier 是虚幻引擎 Motion Design 工作流中的核心修改器系统实现层，基于 ActorModifierCore 插件提供的抽象框架，为 Actor 提供具体的修改器实现。

该插件解决的核心问题是：**如何对场景中的 Actor 施加非破坏性的程序化修改**（如布局变换、渲染属性调整等），使 Motion Design 用户能够在不直接修改 Actor 原始属性的情况下，通过修改器栈（Modifier Stack）对 Actor 进行动态的、可叠加的变换操作。

它将修改器实现拆分为三个维度——**编辑器交互**（Editor）、**布局变换**（Layout）、**渲染属性**（Rendering），形成清晰的关注点分离。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ActorModifier`](ActorModifier.md) | Runtime | 修改器核心运行时逻辑，管理修改器栈的生命周期与执行流程 |
| [`ActorModifierEditor`](ActorModifierEditor.md) | Runtime | 编辑器集成，提供修改器的 UI 面板与交互操作 |
| [`ActorModifierLayout`](ActorModifierLayout.md) | Runtime | 布局类修改器实现（位移、旋转、缩放等空间变换） |
| [`ActorModifierRendering`](ActorModifierRendering.md) | Runtime | 渲染类修改器实现（材质、可见性、渲染状态等属性修改） |

## 使用场景

- 你正在使用 **Motion Design** 工作流进行虚拟制片的场景搭建 → 用 ActorModifier 对 Actor 施加程序化布局和渲染修改
- 你需要对一组 Actor 进行**非破坏性的批量空间变换**（如阵列排列、随机分布）→ 通过 Layout 修改器实现
- 你需要动态控制 Actor 的**渲染属性**（如材质覆盖、可见性切换）而不想直接修改原始资产 → 通过 Rendering 修改器实现
- 你需要构建**可叠加、可排序的修改器栈**，让多个修改器按优先级依次生效 → 使用核心栈管理逻辑

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier)
- [ActorModifierCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore)（底层抽象框架）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causi | 修复渲染状态标记机制，改进 Text3D 更新触发逻辑 |
| 2026-04-08 | `5c28c1d0` | Motion Design: added render state dirty reason scope for the modifier system to have a better idea o | 为修改器系统添加渲染状态脏标记原因追踪，便于调试 |
| 2026-03-13 | `ab2df2c3` | Motion Design: moved usage of core ticker to custom ts ticker instance to better control timing. | 将核心 Ticker 替换为自定义实例，提升时序控制精度 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范化 |
| 2025-09-23 | `cabb6e4f` | MotionDesign : ActorModifier | ActorModifier 插件初始提交 |

### 维护评价

**✅ 活跃维护中**

该插件于 2025 年 5 月从 Experimental 目录迁移至 VirtualProduction，是 Motion Design 工具链的正式组成部分。近 3 个月内持续有功能性更新（渲染状态优化、时序控制改进），表明 Epic Games 内部团队正在积极使用和迭代此插件。

作为 Motion Design 生态的一部分，该插件跟随整体 Motion Design 工具链同步维护，预计会持续获得更新。建议在 Motion Design 工作流中放心使用，但注意依赖底层的 ActorModifierCore 插件版本需保持一致。