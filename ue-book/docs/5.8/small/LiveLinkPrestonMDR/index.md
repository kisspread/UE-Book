# Live Link Preston MDR

> Live Link support for the Preston MDR-3 Motor Driver

| 属性 | 值 |
|---|---|
| 中文名 | Preston MDR 传动链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `LiveLinkPrestonMDR` (Runtime), `LiveLinkPrestonMDREditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR) | |

## 用途

为 Preston MDR-3 电动镜头驱动器提供 Unreal Live Link 集成支持。在影视虚拟制片场景中，摄影组使用 Preston MDR-3 控制镜头的焦距、光圈和变焦等参数；本插件通过 Live Link 框架将这些实时物理镜头数据接入引擎，使虚拟摄影机能够同步响应真实镜头操作，实现精确的镜头匹配。

## 使用场景

- 你使用 Preston MDR-3 控制镜头并在虚拟制片中同步虚拟摄影机参数
- 需要将现场拍摄的镜头焦点/光圈数据实时传递给 UE5 中的虚拟摄影机
- 使用 Live Link 架构统一管理多个硬件数据源时，需要接入 Preston MDR

## 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| `LiveLinkPrestonMDR` | Runtime | 核心运行时模块，实现 Preston MDR-3 的串口通信、Live Link 镜头数据源（Provider）以及主题（Subject）数据定义 |
| `LiveLinkPrestonMDREditor` | Editor | 编辑器扩展模块，提供 MDR 设备配置 UI、连接设置面板和编辑器内的设备管理功能 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR)
- [模块文档：LiveLinkPrestonMDR](LiveLinkPrestonMDR.md)
- [模块文档：LiveLinkPrestonMDREditor](LiveLinkPrestonMDREditor.md)