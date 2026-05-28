# OpenColorIO (OCIO)

> Provides support for OpenColorIO

| 属性 | 值 |
|---|---|
| 中文名 | 开放色彩管理 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（OCIO 配置文件、材质模板、蓝图资产） |
| 模块 | `OpenColorIO` (Runtime), `OpenColorIOEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO) | |

## 用途

OpenColorIO 插件为 Unreal Engine 提供了工业标准色彩管理解决方案。它解决了在不同显示设备、渲染管线和后期制作流程之间保持色彩一致性的问题。通过集成 OCIO 库，该插件允许用户定义复杂的色彩变换规则，确保从场景渲染到最终输出（如 HDR 显示器、SDR 显示器或特定影院投影仪）的色彩准确传递。这对于影视制作、虚拟制片和需要精确色彩控制的视觉特效工作流至关重要。

## 使用场景

- **影视后期制作**：需要将 Unreal Engine 渲染的素材与使用 ACES、Nuke 或 DaVinci Resolve 的其他制作环节进行色彩匹配。
- **虚拟制片**：在 LED Volume 或绿幕拍摄中，需要将实时渲染的场景与摄影机拍摄的实拍画面进行准确的色彩融合。
- **跨平台发布**：确保同一项目在 PC、游戏主机和移动设备上呈现一致的视觉效果。
- **专业显示器调色**：在 HDR 或特定色域（如 DCI-P3）显示器上进行色彩校正和评估。
- **多软件协作**：在包含 Maya、Houdini 等 DCC 工具的流水线中，统一色彩空间。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `OpenColorIO` | Runtime | OCIO 核心运行时库，提供色彩变换引擎、配置文件解析和运行时应用功能。 |
| `OpenColorIOEditor` | Editor | 编辑器集成模块，提供 OCIO 配置文件资产编辑、预览和材质节点编辑器扩展。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/open-color-io-in-unreal-engine/)（请根据实际版本更新链接）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整了虚拟制片资产分类，可能影响 OCIO 配置文件资产的存放位置。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 代码维护，将日志宏迁移到新版本。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 渲染管线相关重构，可能影响着色器编译流程。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 预处理头文件包含，为后续清理做准备。 |
| 2026-03-13 | `ac816610` | OCIO: Fix for linear floating point (SDR) backbuffer. | 修复了线性浮点（SDR）后缓冲区的色彩转换问题。 |

### 维护评价

OpenColorIO 插件自 2019 年创建以来，作为 Epic Games 官方支持的虚拟制片核心组件之一，一直处于**活跃维护**状态。尽管标记为实验性（Beta），但其在专业影视和虚拟制片领域不可或缺，因此持续获得更新和 bug 修复。近期更新集中在性能优化、代码现代化（如日志系统升级）和特定显示管线的兼容性修复上，表明该插件仍在不断改进以满足工业需求。**推荐使用**，但需注意其仍在 Beta 阶段，API 和功能可能会发生变化。建议定期查看官方更新日志和社区反馈。