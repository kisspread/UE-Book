# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.  
> Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 运动网络回滚 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资源、示例） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover) | |

## 总体用途

Mover 是专门为**多人网络游戏**设计的运动系统插件，核心能力是提供**带回滚（rollback）的角色运动模拟**。它允许服务器和客户端对同一段运动历史进行回滚、验证和修正，从而解决传统运动预测中的不同步问题，尤其适用于竞技射击、动作游戏等高精度回放需求。

与 UE 原生 `CharacterMovementComponent` 不同，Mover 采用**模块化运动管线**，将运动逻辑拆分为多个可组合的“动作”（Motions），并结合**压缩可变增量数据（CVD）** 技术降低网络带宽消耗。插件同时提供编辑器工具用于调试和可视化运动数据。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `Mover` | Runtime | 核心运动运行时，包含仿射运动解算器、动作管线、网络回滚与状态同步逻辑。 |
| `MoverCVDData` | Runtime | 压缩可变增量数据（CVD）的数据结构定义与序列化逻辑，负责高效传输运动状态变化。 |
| `MoverCVDEditor` | Runtime | 编辑器模块，提供 CVD 数据的可视化查看与调试工具。 |
| `MoverEditor` | Runtime | 运动编辑器扩展，包含蓝图节点、自定义属性编辑器和设置面板。 |

## 使用场景

- **竞技射击游戏**（如即时枪战、战术竞技）：需要精确的玩家位置回放与击杀判定，Mover 的回滚网络可大幅减少因网络延迟导致的“回头杀”问题。
- **高同步要求的多人在线动作游戏**（如平台跳跃、格斗）：角色移动轨迹的精确回滚保障公平性，避免因轻微卡顿导致的位置突变。
- **需要灵活定制运动逻辑的项目**：Mover 的运动管线允许开发者通过自定义 Motion、AnimGraph 节点和数据集来替换或扩展运动行为，而无需重写整个运动系统。
- **对带宽敏感的项目**：通过 CVD 压缩技巧，仅发送运动状态的增量变化，降低每帧网络数据量。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover)
- [Mover 模块文档](Mover.md)
- [MoverCVDData 模块文档](MoverCVDData.md)
- [MoverCVDEditor 模块文档](MoverCVDEditor.md)
- [MoverEditor 模块文档](MoverEditor.md)