# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 中文名 | 克隆器与效果器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Niagara 系统资产、蓝图资产） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是 Motion Design（运动设计）工具链的核心组件之一，基于 Niagara 粒子系统构建了一套高性能的克隆与效果控制系统。

- **克隆器（Cloner）**：支持多种布局方式，将单个 Actor 或网格体按规则复制为大量实例（如线性排列、网格排列、球形分布等），用于快速生成密集的视觉元素阵列
- **效果器（Effector）**：对克隆出的每个实例施加空间化的影响效果（位移、旋转、缩放、材质参数等），实现波浪、衰减、随机扰动等动态视觉效果
- **网格体构建器（MeshBuilder）**：负责将克隆数据高效转换为可渲染的网格体，优化大量实例的渲染性能

该插件专为虚拟制片中的实时运动设计场景打造，常见于演播室背景动画、舞台视觉特效、数据可视化等需要程序化生成大量动态对象的场景。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ClonerEffector` | Runtime | 核心运行时模块，实现克隆器/效果器的布局算法、实例管理和 Niagara 集成 |
| `ClonerEffectorEditor` | Runtime | 编辑器支持，提供克隆器/效果器的自定义 UI、资产编辑和可视化调试 |
| `ClonerEffectorMeshBuilder` | Runtime | 网格体构建模块，负责将克隆数据烘焙为优化的渲染网格体 |

## 使用场景

- **演播室虚拟背景**：需要数百个几何元素按规律排列并实时响应动画参数
- **舞台视觉设计**：创建粒子化、矩阵式的动态视觉效果
- **数据可视化**：将数据点映射为空间中的克隆实例阵列
- **Motion Design 工作流**：配合 Motion Design 插件完成完整的运动设计管线

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector)
- 关联插件：Motion Design, ActorModifier, PropertyAnimator, GeometryMask（同属 Motion Design 工具链）