# Composite

> Modern system for real-time compositing. This plugin succeeds legacy Composure and extends CompositeCore.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 现代合成系统 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（合成蓝图资产、材质、Pass 模板） |
| 模块 | `Composite` (Runtime), `CompositeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite) | |

## 用途

这是一个用于 Unreal Engine 的现代实时合成框架，作为旧版 Composure 插件的继任者和替代品。它提供了一套更现代、更强大的工具，用于在运行时进行多层合成、视觉特效和后处理效果。插件扩展了 `CompositeCore` 模块，提供了更丰富的合成 Pass 类型、更灵活的合成流程控制以及更完善的编辑器集成。核心目标是为虚拟制片、动态媒体和实时渲染管线提供高性能、可扩展的实时合成解决方案。

## 使用场景

- **虚拟制片 / LED Volume 拍摄**：在 LED 屏幕上实时合成 CG 背景、前景元素和视觉特效。
- **动态媒体生成**：在运行时动态创建视频合成或视觉特效序列。
- **高级后处理管线**：实现复杂的多通道合成、抠像、色彩校正和混合。
- **创建自定义渲染 Pass**：构建包含抠像、合成、模糊、色调映射等自定义操作的完整合成流程。

## 模块列表

| 模块 | 用途 |
|---|---|
| `Composite` | 提供运行时合成框架的核心类、合成 Pass、合成元素和底层渲染功能。 |
| `CompositeEditor` | 提供编辑器内创建、编辑和预览合成蓝图、材质及 Pass 的界面和工具。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite)
- [官方文档]() (待补充)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `0d66152d` | Compositing: Add ChromaShift property to compensate for potential chroma subsampling offsets during | 新增 ChromaShift 属性，用于补偿色度子采样偏移。 |
| 2026-05-22 | `90b2a9d0` | Composure: Default bRemoveOverscan to false on Transform2D pass. | 将 Transform2D Pass 的 bRemoveOverscan 属性默认值改为 false。 |
| 2026-05-21 | `e1f95393` | Composure: Release r.Translucency.AutoBeforeDOF / r.Translucency.Holdout.Location override when the | 修复了透明物体渲染顺序相关的设置覆盖问题。 |
| 2026-05-20 | `4d6f2665` | Composure: Fixed custom pass pass details view so Interp properties show the keyframe button. | 修复了自定义 Pass 细节面板中可插值属性的关键帧按钮显示问题。 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | 新增合成 Actor、图层和 Pass 的最终图标，并微调了菜单内容。 |

### 维护评价

- **活跃维护**：插件创建于 2025 年 9 月，历史不足一年，属于全新插件。
- **开发状态**：近期（2026年5月）有密集的功能更新和 Bug 修复，表明处于**活跃开发阶段**。
- **重要提示**：该插件在 `.uplugin` 中标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明其为**实验性功能**，API 和功能可能在未来版本中发生破坏性变更。目前不建议在追求稳定性的正式生产项目中依赖此插件。
- **推荐**：**仅推荐**用于技术预研、原型开发或对 UE 最新合成功能感兴趣的开发者。对于生产项目，建议继续使用旧版 `Composure` 插件或等待此插件脱离 Beta 状态。