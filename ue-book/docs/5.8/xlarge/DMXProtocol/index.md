# DMX Protocol

> DMX Protocols implementation

| 属性 | 值 |
|---|---|
| 中文名 | DMX 协议 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 插件为 Unreal Engine 提供了完整的 DMX（数字多路复用）通信框架，实现了舞台灯光、特效设备等行业标准控制协议的支持。

DMX512 是娱乐演出和建筑照明领域的标准信号协议。该插件解决的核心问题是：在虚拟制片和实时灯光控制场景中，UE 需要与外部 DMX 设备进行双向通信。插件提供了协议抽象层和两种主流实现（Art-Net 和 sACN/E1.31），使开发者无需关心底层网络传输细节即可收发 DMX 数据。

## 模块一览

| 模块 | 类型 | 说明 |
|---|---|---|
| [DMXProtocol](DMXProtocol.md) | Runtime | 核心协议框架，定义 DMX 传输、端口、信号管理等基础设施 |
| [DMXProtocolArtNet](DMXProtocolArtNet.md) | Runtime | Art-Net 协议实现，通过 UDP 广播收发 DMX 数据 |
| [DMXProtocolSACN](DMXProtocolsACN.md) | Runtime | sACN (E1.31) 协议实现，基于 ACN 框架的 DMX over Ethernet |
| [DMXProtocolEditor](DMXProtocolEditor.md) | Editor | 编辑器工具，提供协议配置 UI 和端口管理面板 |
| [DMXProtocolBlueprintGraph](DMXProtocolBlueprintGraph.md) | UncookedOnly | 蓝图自定义节点，用于在蓝图中发送和接收 DMX 信号 |

## 使用场景

- 你在做虚拟制片（Virtual Production），需要将灯光控制台的 DMX 数据同步到 UE 内的灯光 Actor → 使用 DMXProtocol + Art-Net/sACN
- 你需要通过 UE 控制实体 LED 灯墙或舞台效果设备 → 配置 DMX 端口映射，绑定蓝图节点发送 DMX 信号
- 你要构建一个完整的演出灯光预览系统 → 使用 DMXProtocolEditor 在编辑器中配置多端口、多协议并行工作
- 你需要在蓝图中根据外部 DMX 输入控制游戏逻辑 → 使用 DMXProtocolBlueprintGraph 提供的接收节点

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 所有协议实现的基础框架，Art-Net 和 sACN 均依赖它 |
| `Sockets`, `Networking` | UDP 网络通信（Art-Net 和 sACN 模块依赖） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 新日志宏 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复不可达代码编译警告 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前批量替换导致的错误 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退有问题的提交 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配引擎委托 API 变更，修复注册遗漏 |

### 维护评价

该插件创建于 2020 年 9 月，至今约 6 年。近期（2026 年 4 月）仍有持续更新，主要集中在编译兼容性维护（日志宏迁移、编译警告修复、API 适配）。虽然近几次提交以维护性修复为主，没有新功能添加，但代码仍在跟随引擎版本迭代，**属于活跃维护状态**。

作为 Epic 官方维护的 Virtual Production 核心组件，该插件在虚拟制片领域具有不可替代的地位。**推荐在需要 DMX 灯光控制的项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [DMXProtocol 模块文档](DMXProtocol.md)
- [DMXProtocolArtNet 模块文档](DMXProtocolArtNet.md)
- [DMXProtocolSACN 模块文档](DMXProtocolsACN.md)
- [DMXProtocolEditor 模块文档](DMXProtocolEditor.md)
- [DMXProtocolBlueprintGraph 模块文档](DMXProtocolBlueprintGraph.md)