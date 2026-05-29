# Multicast Analytics Provider

> Forwards analytics API calls to a list of analytics providers to log data to multiple services at once

| 属性 | 值 |
|---|---|
| 中文名 | 多播分析 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnalyticsMulticast` (Runtime), `AnalyticsMulticastEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-21 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast) | |

## 用途

AnalyticsMulticast 是一个**分析数据多路分发器**，它不直接收集或存储数据，而是作为一个"中继站"，将分析 API 调用**同时转发**到所有已注册的分析提供商。

核心价值：当你需要同时将数据发送到多个分析服务（如 Firebase + GameAnalytics + 自定义后端）时，只需配置一次多播提供商，所有子提供商都会自动收到数据，无需在业务代码中重复调用各服务的 API。

## 使用场景

- 你的项目需要同时向**多个分析服务**上报数据 → 用 AnalyticsMulticast 作为统一入口
- 你正在**迁移分析服务商**，需要新旧服务并行运行一段时间 → 用多播实现双写
- 你需要在**运行时动态添加/移除**分析提供商，而不是硬编码 → 多播支持动态管理

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `AnalyticsMulticast` | Runtime | 核心多播分析提供商实现，转发 API 调用到已注册的子提供商列表 |
| `AnalyticsMulticastEditor` | Editor | 编辑器支持模块，提供 UI 配置界面 |

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码编译错误 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回退之前的代码变更 |
| 2024-01-31 | `6bfbcbac` | Move the initial declaration of ::BlockUntilFlushed from IAnalyticsProviderET to it's parent class I | 将 BlockUntilFlushed 声明移至父接口 |
| 2023-12-08 | `ae0e1db1` | Pushed Set/GetDefaultAttributes into IAnalyticsProvider | 将默认属性方法上推到基础接口 |

### 维护评价

这是一个**老牌但仍在维护**的插件，已存在超过 11 年。最近的更新主要是**API 跟进和编译修复**（日志迁移、代码清理），而非功能性增强。该插件功能简洁稳定，作为基础设施组件无需频繁更新。

✅ **推荐使用**：如果你需要多分析服务并行上报，这是官方提供的标准方案。注意 `EnabledByDefault=false`，需要手动在项目设置中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)