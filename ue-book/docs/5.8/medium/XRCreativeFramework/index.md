# XR Creative Framework

> *(无描述)*

| 属性 | 值 |
|---|---|
| 中文名 | XR 创意框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRCreative` (Runtime), `XRCreativeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/XRCreativeFramework) | |

## 用途

XR Creative Framework 是一个面向虚拟制片（Virtual Production）的 XR 工作流框架。它为在 VR 环境中进行创意工作——如场景搭建、Actor 放置与操纵（通过 VR Gizmo 移动/选择对象）——提供运行时基础支持。该插件默认关闭且标记为 Beta，目前仅支持 Win64 平台，属于 Epic 内部从 sandbox 迁移出的实验性功能。

## 使用场景

- 你在做虚拟制片项目，需要在 VR 中直接操纵场景中的 Actor → 用 XRCreativeFramework
- 你需要 VR Gizmo 工具来移动、选择和编辑放置在场景中的对象 → 用 XRCreativeFramework

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `XRCreative` | Runtime | 核心运行时模块，提供 XR 创意工作流的基础框架与 VR Gizmo 等交互功能 |
| `XRCreativeEditor` | Runtime | 编辑器侧支持模块，为 XR 创意工作流提供编辑器集成能力 |

详见各子模块文档：

- [XRCreative.md](XRCreative.md) — 核心运行时模块
- [XRCreativeEditor.md](XRCreativeEditor.md) — 编辑器支持模块

## 启用方式

该插件**默认关闭且为 Beta 状态**，需手动启用：

1. 在编辑器中通过 **Edit → Plugins** 搜索 "XR Creative Framework" 并启用
2. 或在项目配置中添加启用声明

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `998bea39` | [XR Creative] - Fix regression where actors moved with the VR Gizmo then can't be selected because t | 修复 VR Gizmo 移动 Actor 后无法选中的回归 Bug |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 新宏 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 移除已废弃的 5.4 兼容 include 保护 |
| 2026-02-06 | `119111a0` | Complete refactor in 50451248 and deprecate old methods | 完成重构并废弃旧方法 |

### 维护评价

该插件自 2023 年创建以来**持续活跃维护**——近 3 个月内有多次实质性提交，涵盖 Bug 修复、API 重构和引擎兼容性更新。作为 Beta 状态的实验性插件，API 尚不稳定（近期有完整重构和方法废弃），建议在生产环境中谨慎使用。目前仅支持 Win64 平台。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/XRCreativeFramework)
- [官方文档]()（暂无）