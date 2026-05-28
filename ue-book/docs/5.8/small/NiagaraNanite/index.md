# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 粒子渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

NiagaraNanite 是一个 Niagara 粒子渲染器扩展插件，允许将 Nanite 虚拟几何体系统用于粒子渲染。它为 Niagara 添加了专用的 Nanite 渲染器类型，使得海量粒子可以直接使用 Nanite 的高效几何管线进行渲染，从而突破传统粒子数量限制。

该插件解决的核心问题是：**如何在粒子系统中利用 Nanite 的几何体渲染能力**。传统粒子通常通过 GPU 粒子模拟 + Billboard/Mesh 渲染，而本插件允许粒子输出 Nanite 兼容的网格数据，利用 Nanite 的硬件加速光栅化和 LOD 管线来渲染极大规模的粒子几何体。

## 使用场景

- 需要渲染数百万级粒子且每个粒子有复杂网格形状 → 用 Niagara Nanite 渲染器
- 粒子需要支持 Nanite 的自动 LOD 和虚拟几何体特性 → 用 Niagara Nanite 渲染器
- 环境特效（如碎片、植被飞散、建筑崩塌）需要与 Nanite 场景无缝融合 → 用 Niagara Nanite 渲染器

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `NiagaraNanite` | Runtime | 核心运行时模块，实现 Nanite 粒子渲染器的数据接口、网格构建逻辑和运行时行为 |
| `NiagaraNaniteEditor` | Editor | 编辑器模块，提供 Nanite 渲染器的编辑器界面和自定义属性面板支持 |
| `NiagaraNaniteShader` | Runtime (PostConfigInit) | 着色器模块，包含 Nanite 粒子渲染所需的 Shader 定义和 ShaderParameter 绑定 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 粒子系统框架，本插件作为 Niagara 的渲染器扩展 |
| `UnrealEd` | 编辑器支持（NiagaraNanite 模块依赖） |

> 本插件默认未启用（`EnabledByDefault: false`），属于**实验性**插件。使用前需在 Edit → Plugins 中手动启用，并确保已启用 Niagara 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite)
- 子模块文档：
  - [NiagaraNanite](NiagaraNanite.md) — 核心运行时渲染器实现
  - [NiagaraNaniteEditor](NiagaraNaniteEditor.md) — 编辑器集成
  - [NiagaraNaniteShader](NiagaraNaniteShader.md) — Shader 定义

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-03 | `a811ae50` | Refactor UseGPUScene to only require EShaderPlatform argument, remove the FeatureLevel argument | 重构 GPU Scene 参数，简化着色器平台调用接口 |
| 2026-02-02 | `eaa0098d` | Include all bound variables in parameter view model RW counts | 修复参数视图中绑定变量的读写计数遗漏问题 |
| 2026-01-08 | `6297259f` | Fix shutdown crash. The UObject destruction order is not deterministic on shutdown. | 修复引擎关闭时 UObject 销毁顺序不确定导致的崩溃 |
| 2025-10-22 | `297b8f95` | Added renderer mesh info to niagara BP function library | 在 Niagara 蓝图函数库中添加渲染器网格信息查询接口 |
| 2025-10-15 | `d7179c85` | Fix crash when adding additional meshes to Nanite renderer | 修复向 Nanite 渲染器添加额外网格时的崩溃问题 |

### 维护评价

**活跃维护中**。该插件于 2025 年 6 月创建，至今约 9 个月，最近一次更新在 2026 年 3 月，更新频率稳定（约每月 1-2 次）。更新内容包括：
- 持续的功能完善（新增蓝图接口、着色器重构）
- 稳定性修复（崩溃修复）

作为实验性插件，目前仍在积极开发和打磨中。由于 `EnabledByDefault: false` 且标记为实验性，建议在**非生产环境**或**原型验证**中使用，暂不推荐用于正式发布项目。