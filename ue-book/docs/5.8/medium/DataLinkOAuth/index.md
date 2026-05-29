# Motion Design Data Link OAuth

> Motion Design Data Link functionality for OAuth 2.0

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 OAuth |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（OAuth 认证相关资产） |
| 模块 | `DataLinkOAuth` (Runtime), `DataLinkOAuthEditor` (Editor) |
| 实验性 | ⚠️ 是（Beta） |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLinkOAuth) | |

## 用途

为 Motion Design（动态设计）系统的 **Data Link** 功能提供 **OAuth 2.0 认证支持**。Data Link 负责从外部数据源拉取实时数据，而本插件为其增加了基于标准 OAuth 2.0 协议的授权能力，使 Motion Design 能够安全地对接需要身份认证的第三方 API（如社交媒体数据、云服务等）。

该插件从 Experimental 阶段迁移到 VirtualProduction 分类，目前处于 **Beta** 状态（`Installed: false`，需手动启用）。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [DataLinkOAuth](DataLinkOAuth.md) | Runtime | OAuth 2.0 核心认证逻辑，令牌获取、刷新与管理 |
| [DataLinkOAuthEditor](DataLinkOAuthEditor.md) | Editor | 编辑器中的 OAuth 配置界面与授权流程集成 |

## 使用场景

- 你在 Motion Design 中配置 Data Link 连接外部 API，且该 API 要求 OAuth 2.0 认证 → 使用本插件
- 你需要在编辑器中完成 OAuth 授权流程（浏览器跳转、回调处理） → `DataLinkOAuthEditor` 提供相关 UI 支持
- 你在打包后的运行时需要维持 OAuth 令牌有效性（自动刷新） → `DataLinkOAuth` Runtime 模块负责处理

## 模块依赖

本插件依赖 DataLink 插件，无其他特殊依赖。

| 模块 | 用途 |
|---|---|
| `DataLink` | 基础数据链接框架，本插件为其提供 OAuth 认证能力 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 修复非 Unity 编译模式下的头文件缺失问题 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将插件标记为 Beta 状态 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 从 Experimental 迁移到 VirtualProduction 分类 |

### 维护评价

该插件创建于 2025 年 8 月，不足一年，属于 **新建插件**。自创建以来有少量维护性更新（编译修复、日志迁移），但无功能性变更。目前仍处于 **Beta** 状态且 `Installed: false`，表明尚在早期开发阶段。

⚠️ **Beta 状态提示**：API 可能在后续版本中发生变更，不建议在生产环境中强依赖此插件。适合在 Motion Design 相关的开发和测试中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLinkOAuth)
- [DataLink 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)（前置依赖）