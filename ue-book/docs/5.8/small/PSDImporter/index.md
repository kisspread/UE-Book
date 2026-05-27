# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PSD 相关资产） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 是一个用于将 Adobe Photoshop 的 PSD 文件导入 Unreal Engine 5 的实验性插件。它能够解析 PSD 文件中的各个图层，将其转换为引擎可用的纹理和资产。该插件依赖 GeometryMask 插件来处理图层的可见性和遮罩信息。

## 使用场景

- 将 Photoshop 设计的 UI 界面分层导入 UE5，各图层独立可用
- 从 PSD 文件中提取特定图层作为游戏纹理或材质
- 需要保留 PSD 文件的图层结构和遮罩信息的工作流
- 美术团队使用 Photoshop 制作资源，需要批量导入到引擎中

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [PsdSDK](PsdSDK.md) | External | 第三方 PSD 文件解析库，负责底层 PSD 格式读取 |
| [PSDImporterCore](PSDImporterCore.md) | Runtime | 核心导入逻辑，定义 PSD 数据结构和转换流程 |
| [PSDImporter](PSDImporter.md) | Runtime | 运行时模块，管理已导入的 PSD 内容 |
| [PSDImporterEditor](PSDImporterEditor.md) | Editor | 编辑器集成模块，提供 Content Browser 中的 PSD 文件导入功能 |

## 相关依赖

该插件需要启用以下插件：

| 插件 | 用途 |
|---|---|
| GeometryMask | 处理 PSD 图层的遮罩和可见性信息 |

## 平台支持

⚠️ 当前仅支持 **Win64** 平台。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前的错误查找替换，重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退 CL51314860 的改动 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 迁移引擎初始化委托调用方式，修复注册缺失问题 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制不正确的 V1051 编译警告 |

### 维护评价

- 该插件创建于 2025 年 4 月，是一个较新的实验性插件
- 首次提交显示它从其他位置重命名并移至 Experimental 目录（可能来自非实验性文件夹）
- 近期（2026 年 2 月和 4 月）仍有更新，主要涉及日志迁移和引擎委托 API 适配
- 作为实验性插件，API 可能会发生变化
- **推荐度**：可关注但生产环境慎用，适合提前了解 PSD 导入功能

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [子模块文档 - PsdSDK](PsdSDK.md)
- [子模块文档 - PSDImporterCore](PSDImporterCore.md)
- [子模块文档 - PSDImporter](PSDImporter.md)
- [子模块文档 - PSDImporterEditor](PSDImporterEditor.md)