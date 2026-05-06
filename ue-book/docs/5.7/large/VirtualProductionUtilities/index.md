# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作实用工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产、蓝图、编辑器工具） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

## 总体用途

VirtualProductionUtilities 是一套为虚拟制作工作流提供的工具集合。它包含：

- **书签系统**（VPBookmark）：在场景中标记和快速定位关键位置、摄像机视角等信息，便于在拍摄或布景时切换视角。
- **通用工具函数**（VPUtilities）：提供 OSC（Open Sound Control）通信、视口交互辅助、全屏媒体小部件等实用功能，简化虚拟制作中的设备控制与 UI 操作。
- **编辑器扩展**（VPBookmarkEditor、VPUtilitiesEditor）：在 Unreal Editor 中为书签和工具提供可视化操作面板、工具栏按钮及交互模式，提升编辑效率。

该插件旨在帮助虚拟制作团队快速搭建拍摄环境，减少重复劳动，并作为其他虚拟制作解决方案的基础库。

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| `VPBookmark` | Runtime | 提供虚拟制作书签的核心数据结构和保存/加载逻辑 | [VPBookmark.md](./VPBookmark.md) |
| `VPBookmarkEditor` | Runtime | 在编辑器中为书签提供 UI 交互（创建、编辑、切换）与视口绘制 | [VPBookmarkEditor.md](./VPBookmarkEditor.md) |
| `VPUtilities` | Runtime | 通用工具类，包括 OSC 服务器、全屏媒体输出、视口交互辅助等 | [VPUtilities.md](./VPUtilities.md) |
| `VPUtilitiesEditor` | Runtime | 编辑器工具扩展，如 OSC 服务器配置面板、视口交互模式开关 | [VPUtilitiesEditor.md](./VPUtilitiesEditor.md) |

## 使用场景

- **虚拟制片棚搭建**：需要在场景中标记多个摄像机位置，并快速切换视角 → 使用 VPBookmark 创建书签，配合 VPBookmarkEditor 在编辑器中可视化管理。
- **外部设备控制**：需要从灯光控制台、调音台等通过 OSC 协议与 UE 通信 → 使用 VPUtilities 中的 OSC 服务器组件，并可在编辑器中通过 VPUtilitiesEditor 进行配置。
- **多屏输出与导播**：需要将渲染画面输出到外部显示器或投影仪，并支持全屏切换 → 使用 VPUtilities 中的媒体输出小工具。
- **视口交互模式**：在虚拟制作过程中需要临时启用/禁用 UE 的视口交互（如避免意外移动摄像机）→ 使用 VPUtilities 中的视口锁定或交互模式功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [VPBookmark 模块文档](./VPBookmark.md)
- [VPBookmarkEditor 模块文档](./VPBookmarkEditor.md)
- [VPUtilities 模块文档](./VPUtilities.md)
- [VPUtilitiesEditor 模块文档](./VPUtilitiesEditor.md)

## 维护状态

### 近期更新

- 2025-10-03 `e6b66964` 修复媒体输出提供者的全屏小部件问题
- 2025-09-25 `4b556c0e` VPUtilities OSC 服务器 – 允许指定服务器地址的覆盖值
- 2025-09-23 `66f6004f` ViewportInteraction：弃用 ViewportInteraction 模块（随 VR Editor 弃用）
- 2025-09-10 `cb5faa0b` VR Editor：弃用 VR Editor 模式及大部分关联类
- 2025-08-27 `551d3a5b` 修复 BugHawk 和 CIS 弃用警告

### 维护评价

该插件创建于 2025-08-27，属于较新插件。近 1 个月内有功能性更新（OSC 地址覆盖）和 bug 修复，维护较为活跃。注意：部分外围模块（ViewportInteraction、VR Editor）已被标记为弃用，但 VirtualProductionUtilities 核心功能未受影响，且后续可能继续与新的虚拟制作工具集成。推荐在虚拟制作项目中使用，但需留意实验性标签，生产环境建议充分测试。