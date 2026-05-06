# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara Nanite |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Niagara 资源） |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite) | |

## 总体用途

本插件为 Niagara 粒子系统添加了一个新的渲染器，使其能够渲染 Nanite 几何体。通过利用 Nanite 的虚拟几何体系统，可以在大规模粒子场景中高效渲染数百万个实例化网格，同时保持极低的渲染开销。适用于需要大量静态网格体实例的粒子效果，如碎石、瓦砾、树叶、人群等。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [NiagaraNanite](./NiagaraNanite.md) | Runtime | 运行时核心模块，提供 Nanite 渲染器实现及数据处理 |
| [NiagaraNaniteEditor](./NiagaraNaniteEditor.md) | Editor | 编辑器模块，提供 Nanite 渲染器的 UI 支持和资产创建 |
| [NiagaraNaniteShader](./NiagaraNaniteShader.md) | Runtime | 着色器模块，负责 Nanite 渲染所需的 GPU 着色器编译及管线 |

## 使用场景

- **大量静态网格体粒子**：例如在开放世界中生成碎石、瓦砾、碎片等粒子，需要同时渲染数千甚至数万个独立实例。
- **植被或人群模拟**：使用 Niagara 分布大量树木、花草或角色，借助 Nanite 实现高密度 LOD 自动管理。
- **程序化生成场景**：与 Niagara 的 CPU/GPU 生成结合，快速创建复杂几何体集合，同时保持性能。
- **替换传统 Instanced Static Mesh**：传统 Instanced Static Mesh 存在实例数上限和管理复杂度，Nanite 渲染器可突破这些限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite)
- [Niagara 官方文档](https://docs.unrealengine.com/5.7/en-US/niagara-effects-in-unreal-engine/)
- [Nanite 官方文档](https://docs.unrealengine.com/5.7/en-US/nanite-virtualized-geometry-in-unreal-engine/)

## 维护状态

### 近期更新
- 2025-10-15 2673f68 — Fix crash when adding additional meshes to Nanite renderer
- 2025-08-25 a0f5c68 — Fix bug where nanite niagara shader can stomp the instance data in GPUScene.
- 2025-08-18 c111785 — - Fix for previous transforms being incorrect on CPU
- 2025-08-13 c7595da — - Fix naming of material override struct
- 2025-08-11 8c7d488 — Fix for niagara nanite renderer thumbnail crash

### 维护评价
该插件创建于 2025 年 8 月，属于 UE 5.7 的新插件，年龄约 2 个月。近期更新活跃（最近一次 2025-10-15），主要集中于 Bug 修复和稳定性改进。目前仍标记为实验性，但已具备基本功能。由于是全新插件，尚未有重大功能迭代，建议在非生产项目中使用，并密切关注更新。总体上值得关注，但需注意可能存在的兼容性问题。