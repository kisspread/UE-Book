# PSD Importer

> 导入Photoshop PSD文件，解析图层结构和图像数据，创建可编辑的UE资产。

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PSD解析SDK、编辑器导入功能） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSDImporter 是一个实验性插件，用于将 Adobe Photoshop 的 PSD 文件直接导入到 Unreal Engine 中。它解析 PSD 文件的完整图层结构、图像数据和元信息，将其转换为引擎内部可编辑的资产格式（如纹理2D、纹理立方体等）。该插件解决了传统工作流中需要先从PSD导出为其他格式（如PNG、TGA）再导入引擎的繁琐步骤，允许艺术家直接在引擎内访问和利用PSD的原始图层信息，非常适合需要频繁迭代UI或材质纹理的项目。

## 使用场景

- 你需要在UE中直接编辑Photoshop的UI设计图，并保持图层结构以便后续修改。
- 你的美术团队使用PSD进行概念设计，希望将设计直接转换为引擎可用的材质纹理。
- 你希望自动化资产导入流程，避免手动导出和转换PSD文件。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 提供几何遮罩功能，可能用于处理图层蒙版 |

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `PSDImporter` | Runtime | 核心运行时模块，提供PSD文件解析和资产转换功能 |
| `PSDImporterCore` | Runtime | 核心数据结构和解析逻辑，与平台无关的底层代码 |
| `PSDImporterEditor` | Editor | 编辑器集成模块，提供资产导入、UI和编辑器扩展功能 |
| `PsdSDK` | External | 第三方PSD解析SDK，提供底层的PSD文件格式支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志调用迁移到UE_LOGF格式化日志系统 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换操作后的第二次尝试 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了CL51314860提交的更改 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托注册问题，将静态委托改为获取函数 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 静默了不正确的V1051静态分析警告 |

### 维护评价

该插件创建于2025年4月，是一个相对较新的实验性插件。从提交历史看，它经历了从其他位置重命名并移动到Experimental目录的过程。最近6个月内有更新，主要集中在日志系统迁移、错误修复和编译警告处理上，表明项目仍在维护中。然而，由于是实验性版本且尚未标记为默认启用，它可能还不完全稳定或功能完整。该插件主要支持Win64平台。

**推荐使用**：适合需要直接PSD导入功能的项目，但应注意其实验性状态，可能在未来版本中发生变化。建议在重要项目中谨慎评估，或仅用于原型开发阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)