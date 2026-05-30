# SVG Importer

> Importing and handling SVG files（照抄自 .uplugin Description）

| 属性 | 值 |
|---|---|
| 中文名 | SVG 导入器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（SVG 相关资产与模板） |
| 模块 | `SVGImporter` (Runtime), `SVGImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SVGImporter) | |

---

## 用途

SVGImporter 解决了 Unreal Engine 中 SVG 矢量图形的导入与处理问题。该插件能够解析标准 SVG 文件，将其转换为 UE 内部可使用的几何体数据，主要面向虚拟制作（Virtual Production）场景中的 Motion Design 工作流。

核心能力：
- 将 SVG 文件解析为可编辑的 UE 资产
- 利用 Geometry Scripting 将矢量路径转换为网格体
- 支持几何遮罩（GeometryMask）集成，用于材质和渲染效果

该插件最初位于 Experimental 目录，后迁移至 VirtualProduction 目录并标记为 Beta 状态，表明 Epic 将其定位为虚拟制作流程的重要工具。

---

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [SVGImporter](SVGImporter.md) | Runtime | SVG 解析引擎，负责文件读取、路径解析与几何体生成 |
| [SVGImporterEditor](SVGImporterEditor.md) | Editor | 编辑器集成，提供 SVG 文件导入 UI、资产编辑器与工作流支持 |

---

## 使用场景

- **Motion Design / 广播图形**：在虚拟制作中导入品牌 Logo、图标等矢量图形，保持缩放无损质量
- **UI 原型设计**：将设计工具（Figma、Illustrator）导出的 SVG 直接导入引擎进行预览
- **材质与遮罩效果**：利用 SVG 形状生成几何遮罩，用于材质特效或屏幕空间效果
- **动态内容生成**：运行时解析 SVG 文件，生成程序化网格体（依赖 GeometryScripting）

---

## 模块依赖

该插件的使用者需要关注以下外部依赖（摘自 .uplugin Plugins 字段）：

| 模块/插件 | 用途 |
|---|---|
| GeometryScripting | SVG 路径转换为网格体几何体 |
| GeometryMask | 几何遮罩功能，用于材质/渲染集成 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新 API |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复批量替换错误后的重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退有问题的改动 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托的注册问题 |
| 2025-09-04 | `69830deb` | MotionDesign : SVGImporter - Moving SVGImporter plugin outside of Experimental and into VirtualProduction | 插件从 Experimental 迁移至 VirtualProduction 目录 |

### 维护评价

- **创建时间**：2025 年 9 月，不足 1 年，属于较新的插件
- **维护状态**：**活跃维护中** — 最近一次更新在 2026 年 4 月，且 2026 年 2 月有多次修复提交
- **当前标记**：Beta + Experimental 分类，功能可能尚未完全稳定
- **潜在风险**：API 可能随版本迭代发生变化；依赖 GeometryScripting 插件
- **推荐使用**：适合 Motion Design / 虚拟制作用户探索使用；生产环境需谨慎评估稳定性

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SVGImporter)
- [SVGImporter 模块文档](SVGImporter.md)
- [SVGImporterEditor 模块文档](SVGImporterEditor.md)