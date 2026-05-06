# Color Correction Regions (CCR)

> Color correction/shading constrained to regions/volumes

| 属性 | 值 |
|---|---|
| 中文名 | 颜色校正区域 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（场景资产、材质、蓝图） |
| 模块 | `ColorCorrectRegions` (Runtime), `ColorCorrectRegionsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions) | |

## 总体用途

Color Correct Regions (CCR) 插件允许用户在场景中定义三维区域或体积，并在这些区域内叠加局部的颜色校正（如色温、色调、饱和度等）。它解决了传统全局后处理无法灵活控制特定区域的问题，特别适用于虚拟制片、nDisplay 多屏拼接、以及需要精细调整局部的影视级实时渲染场景。

核心特性：
- 支持球形、盒体、圆柱体等形状的区域
- 通过优先级和混合模式控制多个区域叠加效果
- 可与 nDisplay 配合，实现多通道的局部颜色匹配
- 提供编辑器内实时预览和 Actor 拖放操作

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `ColorCorrectRegions` | Runtime | 运行时核心模块，负责颜色校正区域的计算、渲染与数据管理。 | [ColorCorrectRegions.md](ColorCorrectRegions.md) |
| `ColorCorrectRegionsEditor` | Editor | 编辑器模块，提供 Actor 创建、组件编辑、UI 面板及 nDisplay/ObjectMixer 集成。 | [ColorCorrectRegionsEditor.md](ColorCorrectRegionsEditor.md) |

## 使用场景

- **虚拟制片 (Virtual Production)**：在绿幕前对角色或道具进行局部颜色匹配，或按场景区域调整色温。
- **nDisplay 多屏拼接**：对不同显示墙上的画面进行一致性校正，消除因显示器差异导致的颜色偏差。
- **影视级实时渲染**：在 Sequencer 中为特定物体或区域叠加风格化颜色 Look，而不影响全局。
- **交互式安装/舞台灯光**：通过蓝图动态控制区域颜色，实现灯光跟随角色移动。

## 相关链接

- [源码仓库](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions)
- [模块文档 - ColorCorrectRegions](ColorCorrectRegions.md)
- [模块文档 - ColorCorrectRegionsEditor](ColorCorrectRegionsEditor.md)