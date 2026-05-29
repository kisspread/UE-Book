# OpenCV

> Plugin initializing OpenCV library to be used in engine.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | OpenCV初始化 |
| 分类 | Computer Vision |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python依赖包） |
| 模块 | `OpenCVHelper` (Runtime), `OpenCV` (External) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2021-11-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV) | |

## 用途

该插件的核心功能是**将 OpenCV 计算机视觉库集成到虚幻引擎中**。它负责配置和初始化 OpenCV 的运行环境，使得其他 UE5 功能或插件能够依赖并使用 OpenCV 强大的图像处理和分析能力。它本身不包含具体的业务逻辑，而是作为基础层，为例如 ML Deformer 等需要视频处理的功能提供支持。

## 使用场景

- 你需要在 Unreal Engine 项目中使用 OpenCV 库进行图像分析、目标检测、图像滤波等计算机视觉任务。
- 你正在使用或开发依赖于 OpenCV 的 Unreal Engine 功能，例如 `ML Deformer` 需要处理视频文件时，该插件是运行时的先决条件。
- 你的项目需要跨平台（Windows/Linux/macOS）支持 OpenCV 功能。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `OpenCVHelper` | Runtime | 核心运行时模块，负责加载 OpenCV 库并提供 C++ 帮助函数与辅助类。 |
| `OpenCV` | External | 外部模块，负责处理第三方 OpenCV 库的构建和链接配置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 UE_LOG 日志宏迁移至新的 UE_LOGF 宏。 |
| 2026-04-13 | `a0b7804f` | [OpenCV] Add OpenCV library for macOS | 新增了对 macOS 平台的 OpenCV 库支持。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了编辑器中更改纹理属性的代码，按要求将其包装在 PreEditChange/PostEditChange 中。 |
| 2025-11-10 | `e0906b79` | Fix for crash when OpenCV fails to load | 修复了当 OpenCV 库加载失败时可能导致引擎崩溃的问题。 |

### 维护评价

该插件自 2021 年底创建以来持续维护，近期（2026年5月）仍有活跃更新，包含功能增强（新增 macOS 支持）、代码现代化迁移以及关键问题修复（崩溃修复）。这表明它是一个**处于积极维护状态**的实验性插件。鉴于其作为底层基础设施的定位和近期的更新频率，可以放心在项目中使用，但需注意其“实验性”状态（BetaVersion = true）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV)