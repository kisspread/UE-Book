# DMX Control Console

> Console that can be patched from DMX Libraries and sends DMX to Output Ports（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | DMX控制台 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXControlConsole` (Runtime), `DMXControlConsoleEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole) | |

## 用途
该插件在编辑器内提供了一个可视化的DMX控制台界面。它允许用户从项目中的DMX库（DMX Libraries）加载通道信息，并像操作真实物理灯光控制台一样，直观地设置和输出DMX数据。其核心目的是为虚拟制片（Virtual Production）中的灯光师提供一个在编辑器环境中进行快速测试、调试和预览DMX灯光效果的工具，而无需连接实际的硬件控制台或进入播放模式。

## 使用场景
- 在虚拟制片的场景搭建阶段，需要快速测试DMX灯光通道的编组、亮度、颜色等参数。
- 为小型或临时性项目提供一个轻量级的DMX控制界面，无需配置复杂的外部设备。
- 在开发DMX相关功能或插件时，用于验证DMX库的解析与数据输出是否正确。

## 模块列表
| 模块 | 说明 |
|---|---|
| **DMXControlConsole** | 运行时核心模块，提供DMX控制台的数据模型、信号处理和输出功能。 |
| **DMXControlConsoleEditor** | 编辑器扩展模块，实现控制台的用户界面、资产集成和编辑器交互逻辑。 |

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole)