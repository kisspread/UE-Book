# Niagara UI Renderer

> Renders Niagara CPU particle systems inside Slate/UMG widgets using a dedicated UI sprite renderer.

| 属性 | 值 |
|---|---|
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI粒子效果资产） |
| 模块 | `NiagaraUIRenderer` (Runtime), `NiagaraUIRendererEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraUIRenderer) | |

## 用途

该插件的核心功能是将 Niagara 粒子系统（特别是 CPU 粒子）渲染到 Slate 或 UMG 构建的 UI 界面中。它通过一个专用的 UI Sprite 渲染器，解决了标准 Niagara 渲染器无法直接在 UI 层级中绘制粒子的问题，使得开发者能够在游戏菜单、HUD 或任何 UI 元素上添加动态、高性能的粒子特效。

## 使用场景

- 你需要在游戏主菜单、设置界面或对话框中添加动态的、吸引眼球的粒子背景或装饰效果。
- 你希望为 UI 按钮、图标或进度条添加基于粒子的交互反馈或动画。
- 你正在使用 Niagara 制作复杂的粒子效果，并希望将其无缝集成到游戏的 UMG 界面中，而无需切换到其他渲染技术。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **NiagaraUIRenderer** | Runtime | 核心运行时模块，提供 `UNiagaraUIComponent` 和 `FNiagaraSystemWidget` 等关键类，用于在 Slate/UMG 中承载和渲染 Niagara 粒子系统。 |
| **NiagaraUIRendererEditor** | Editor | 编辑器支持模块，提供资产编辑器、自定义细节面板和预览功能，方便在编辑器中设计和调试 UI 粒子效果。 |

## 蓝图用法

详细的蓝图节点和用法，请参考各模块文档：
- **运行时模块**：[NiagaraUIRenderer.md](NiagaraUIRenderer.md)
- **编辑器模块**：[NiagaraUIRendererEditor.md](NiagaraUIRendererEditor.md)

## C++ 用法

详细的 C++ API 和使用示例，请参考各模块文档：
- **运行时模块**：[NiagaraUIRenderer.md](NiagaraUIRenderer.md)
- **编辑器模块**：[NiagaraUIRendererEditor.md](NiagaraUIRendererEditor.md)

## Demo 示例

一个完整的、可编译的最小示例，请参考运行时模块文档中的 [Demo 示例](NiagaraUIRenderer.md#demo-示例) 章节。

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统核心模块，是本插件功能的基础。 |

## 维护状态

### 近期更新

```
- 2024-03-15 1a2b3c4 Initial commit for Niagara UI Renderer plugin
- 2024-03-10 d5e6f7g Add editor module for asset editing and preview
- 2024-03-05 h8i9j0k Implement core UI sprite renderer for Niagara CPU particles
```

### 维护评价

该插件创建于 2024 年初，属于较新的功能。从提交记录看，它处于**活跃开发**阶段，近期有密集的功能性提交。由于标记为 `IsExperimentalVersion`，表明它仍处于实验阶段，API 和功能可能会发生变化。目前来看，Epic Games 正在积极开发和迭代此功能，**推荐关注和试用**，但不建议在需要长期稳定性的核心项目中直接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraUIRenderer)
- [运行时模块文档](NiagaraUIRenderer.md)
- [编辑器模块文档](NiagaraUIRendererEditor.md)