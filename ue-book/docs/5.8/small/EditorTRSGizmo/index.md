# 5.8 Gizmo Testing

> A temporary plugin for New TRS Gizmo work

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `EditorTRSGizmo` (Runtime), `EditorTRSGizmoSettings` (Runtime), `EditorTRSGizmoTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorTRSGizmo) | |

## 用途

这是一个用于开发和测试 Unreal Engine 5.8 中新的变换 Gizmo（平移、旋转、缩放）功能的**实验性临时插件**。它并非面向最终用户的功能插件，而是作为新 Gizmo 系统的开发沙盒和测试环境。插件的核心目的是隔离新 Gizmo 的实现代码，便于开发者进行迭代、测试和验证，而不会影响引擎主分支的稳定性。

## 使用场景

- **引擎开发者**：正在开发或测试 UE 5.8 的新变换 Gizmo 功能，需要一个独立的环境来运行和调试相关代码。
- **功能验证**：需要验证新 Gizmo 的交互逻辑、渲染表现或性能是否符合预期。
- **自动化测试**：运行针对新 Gizmo 功能的自动化测试用例。

## 蓝图用法

无（实验性测试插件，无公开蓝图API）

## C++ 用法

无（实验性测试插件，主要提供测试用例）

## Demo 示例

无（实验性测试插件，无独立使用示例）

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `EditorTRSGizmo` | Runtime | 新 TRS Gizmo 的核心实现模块。 |
| `EditorTRSGizmoSettings` | Runtime | 新 TRS Gizmo 的配置与设置模块。 |
| `EditorTRSGizmoTests` | Runtime | 包含针对新 TRS Gizmo 功能的自动化测试用例。 |

## 维护状态

### 近期更新

（注：由于插件创建时间非常近，且为实验性临时插件，暂无历史提交记录可供分析。）

### 维护评价

- **性质**：这是一个**实验性、临时性**的开发测试插件。
- **状态**：作为新功能的开发沙盒，其维护状态与新 Gizmo 功能的开发进度直接绑定。
- **风险**：此插件**不保证长期存在**。一旦新 Gizmo 功能开发完成并集成到引擎主分支，此插件可能会被移除或废弃。
- **建议**：**不推荐**普通项目依赖此插件。仅建议引擎开发者或需要深度参与新 Gizmo 功能测试的团队使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorTRSGizmo)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorTRSGizmo/Source/EditorTRSGizmoTests)