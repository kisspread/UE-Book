# Color Correction Regions (CCR)

> Color correction/shading constrained to regions/volumes

| 属性 | 值 |
|---|---|
| 中文名 | 区域色彩校正 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、蓝图资产） |
| 模块 | `ColorCorrectRegions` (Runtime), `ColorCorrectRegionsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ColorCorrectRegions) | |

## 用途

该插件解决了在场景中对特定体积或区域应用局部色彩校正和着色调整的问题。它允许美术师在关卡中放置几何体，定义受色彩校正影响的范围，而不是对整个场景应用全局效果。这对于创建局部视觉效果（如在不同区域使用不同色调的夜晚场景、在特定地方突出显示的区域效果）非常有用，尤其在需要精细视觉控制的大型开放世界项目中。

## 使用场景

- 你在制作一个夜晚的城市环境，希望某些区域（如霓虹灯牌周围）有独特的色彩分级
- 你需要在游戏关卡的不同区域应用不同的视觉风格（例如：绿色森林、蓝色水下、红色危险区）
- 在建筑可视化中，希望为特定房间或区域创建不同的光照氛围
- 使用 nDisplay 进行多屏渲染时，需要对不同屏幕区域应用独立的色彩校正

## 模块概览

- **ColorCorrectRegions** (Runtime)：运行时模块，包含色彩校正区域的核心实现、渲染管线集成和蓝图接口
- **ColorCorrectRegionsEditor** (Editor)：编辑器模块，提供用于放置和编辑色彩校正区域的工具、自定义资产类型和编辑器UI

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ColorCorrectRegions)
- [子模块文档](ColorCorrectRegions.md) - 运行时模块的API和使用详情
- [子模块文档](ColorCorrectRegionsEditor.md) - 编辑器模块的工具和工作流

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告 |
| 2026-05-12 | `5c7314c3` | Fix Color Correct Regions render rect being truncated when dynamic resolution scales below 1.0. | 修复动态分辨率低于1.0时色彩校正区域渲染矩形被截断的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移到UE_LOGF |
| 2026-04-06 | `a7ea00e7` | ColorCorrectActors: Promote CustomDepth/SceneDepth from half to float to preserve precision | 色彩校正Actor：将CustomDepth/SceneDepth从半精度提升为单精度以保持精度 |
| 2026-04-01 | `12ae598f` | Color Correction Actors Multi-User: fixed an issue where stencil id's assignment on some actors were | 多用户色彩校正Actor：修复某些Actor模板ID分配的问题 |

### 维护评价

**活跃维护**。插件创建于2020年，最近一次更新在2026年5月，持续有功能性更新和bug修复。尽管位于Experimental目录下，但仍在持续开发和改进中。插件解决了真实的制作需求（局部色彩校正），并已与UE5的现代特性（动态分辨率、多用户编辑）集成。推荐在需要局部色彩校正的项目中使用，但需注意其在Experimental目录下，可能在未来的引擎版本中发生变化。