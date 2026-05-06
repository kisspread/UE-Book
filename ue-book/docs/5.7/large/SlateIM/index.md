# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.

| 属性 | 值 |
|---|---|
| 中文名 | SlateIM |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMInGame` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM) | |

## 总体用途

SlateIM 提供了一套**立即模式（Immediate Mode）** 的 UI 封装层，用于快速搭建调试工具。它允许开发者以声明式、每帧刷新的方式绘制界面，无需维护复杂的 Widget 树和数据绑定，特别适合开发性能分析面板、内存监视器、游戏内控制台、场景调试叠加层等场景。

插件由两个运行时模块组成：
- **SlateIM 核心模块**：实现立即模式 API，包括基础控件（窗口、按钮、文本、图像等）和布局系统。
- **SlateIMInGame 扩展模块**：将立即模式 UI 渲染到游戏世界或屏幕空间（如 HUD 或 3D Actor），支持服务器/客户端调试。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `SlateIM` | Runtime | 核心立即模式 UI 框架，提供 `Window`、`Button`、`Text`、`Image` 等控件 API。 | [SlateIM.md](SlateIM.md) |
| `SlateIMInGame` | Runtime | 在游戏内显示调试界面的支撑模块，包含世界 Actor 和 HUD 集成。 | [SlateIMInGame.md](SlateIMInGame.md) |

## 使用场景

- **构建轻量级性能/内存/网络调试面板**：无需创建 UMG Widget 蓝图，用几行 C++ 就能生成实时更新数据的 UI。
- **游戏内编辑器/控制台**：在运行时弹出命令面板、日志过滤器或材质调试窗口。
- **服务器/客户端交互调试**：利用 `SlateIMInGame` 的世界 Actor 在多玩家环境下可视化服务器状态。
- **实验性原型开发**：快速迭代 UI 布局和交互逻辑，待稳定后再迁移到传统保留模式 Widget。

## 维护状态

### 近期更新

- 2025-09-09 `accbcce5` Fixup API macros（API 宏修复）
- 2025-09-03 `3b7603db` Fixes for SlateIMInGame widgets（游戏内控件修复）
- 2025-09-03 `40963b9c` SlateIM InGame widget actor for server/client debugging（新增服务端/客户端调试用 Actor）
- 2025-08-28 `ea3f5ec2` Add an overload of `SlateIM::Image` that takes just a color（Image API 重载）
- 2025-07-28 `9469fd08` Fix example window text not readjusting after window resize（示例窗口文本适配修复）

### 维护评价

- **创建时间**：2025 年 7 月，距今不到 3 个月。
- **更新频率**：高（近 2 个月内有多次实质性提交），含功能增加（新 Actor、API 重载）和 bug 修复。
- **活跃度**：**活跃维护**，开发团队仍在积极增加特性和修复问题。
- **限制**：目前标注为“实验性”，API 可能变动；模块数量少（2 个），功能尚在扩展期。
- **推荐**：适合有 C++ 开发经验、需要快速构建调试工具的团队尝试；生产环境前需关注未来 API 稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM/Tests)（若有）