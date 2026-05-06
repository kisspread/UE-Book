# Remote Control Components

> （描述为空，从源码推断：为 Motion Design 工作流提供基于组件的远程控制功能，允许在运行时通过外部控制面板操控 Actor 属性。）

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制组件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlComponents` (Runtime), `RemoteControlComponentsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents) | |

## 总体用途

该插件为 Motion Design 场景提供一组 Actor Component，用于将 Actor 的属性暴露给远程控制系统（如 Web 控制面板）。它实现了属性的自动跟踪与批量更新，无需手动编写绑定代码。开发者可通过组件直接指定要远程控制的属性路径，系统自动注册到 Remote Control 协议中。适用于需要在运行时动态调整场景元素参数的影视、虚拟制片或交互式演示项目。

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `RemoteControlComponents` | Runtime | 核心运行时组件，提供基础属性跟踪与远程控制注册逻辑 | [模块文档](./RemoteControlComponents.md) |
| `RemoteControlComponentsEditor` | Runtime | 编辑器扩展，提供组件细节面板中的属性选择 UI 和配置辅助 | [模块文档](./RemoteControlComponentsEditor.md) |

## 使用场景

- **虚拟制片**：导演或美术在片场通过平板实时调整灯光强度、相机焦距、道具位置等参数。
- **交互式展览**：运营人员通过外部控制界面管理多个终端的场景元素状态。
- **影视预演**：动画师遥控角色骨骼控制器或材质参数，边预览边调整。
- **自动化测试**：通过脚本远程控制多个 actor 属性，验证场景响应。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents)