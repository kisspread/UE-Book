# XR Creative Framework

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | XR创意框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRCreative` (Runtime), `XRCreativeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/XRCreativeFramework) | |

## 总体用途

XR Creative Framework 是面向虚拟制作场景的 XR（扩展现实）创作工具集。它提供在引擎内直接操作虚拟场景、管理 XR 设备及交互的运行时组件，并配套编辑器扩展以优化工作流。插件目前处于 Beta 阶段，主要用于 VR 编辑器相关功能的修复与增强（如 WidgetComponent 退出逻辑、PostProcess 参数校验等）。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `XRCreative` | Runtime | 核心运行时模块，封装 XR 场景管理、设备交互与验证逻辑 |
| `XRCreativeEditor` | Runtime | 编辑器扩展模块，提供 XR 创作相关的 UI、工具栏与设置面板 |

> 详细 API 请参阅各模块文档：[XRCreative](XRCreative.md) | [XRCreativeEditor](XRCreativeEditor.md)

## 使用场景

- **虚拟制作**：在绿幕摄影棚或 LED 舞台中，需要实时合成虚拟场景与真实拍摄内容时，使用此框架管理 XR 设备校准、相机跟踪与场景呈现。
- **VR 编辑器工作流**：开发者在 VR 模式下进行关卡编辑、蓝图调试或资产摆放时，利用该框架提供的交互工具与 UX 优化。
- **自定义 XR 交互**：需要为特定 XR 硬件（如头显、控制器）编写扩展交互逻辑，可基于运行时模块的抽象接口快速集成。

## 相关链接

- [源码仓库 (5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/XRCreativeFramework)
- [XRCreative 模块文档](XRCreative.md)
- [XRCreativeEditor 模块文档](XRCreativeEditor.md)