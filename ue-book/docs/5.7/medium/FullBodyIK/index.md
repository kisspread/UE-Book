# Full Body IK

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 全身 IK |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容插件，可能包含求解器资源与测试数据） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-07-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK) | |

## 总体用途

Full Body IK 插件提供了两种高效的全身逆运动学（Inverse Kinematics）求解器，主要用于角色动画中的姿态调整与绑定控制。它依托于 ControlRig 框架，允许用户在动画蓝图或控制绑定中直接求解全身骨骼链的 IK 目标。

- **FBIK（Full Body IK）**：一种迭代式的全身 IK 求解器，能够处理复杂的多分支骨骼链，支持中间效应器、根补偿等高级功能。
- **PBIK（Position Based IK）**：一种基于位置的快速 IK 求解器，更适用于四肢或局部链的求解，计算开销较低。

这两个模块相互独立，但可以协同使用，满足不同精度的 IK 需求。

## 模块列表

| 模块名称 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `FullBodyIK` | Runtime | 提供 FBIK 求解器，支持全身约束与迭代解算 | [FullBodyIK.md](./FullBodyIK.md) |
| `PBIK` | Runtime | 提供 PBIK 求解器，基于位置的快速局部 IK | [PBIK.md](./PBIK.md) |

## 使用场景

- 制作程序化角色动画（如手部抓取、脚部接触地面调整）
- 在 ControlRig 中实现精准的姿态修正（如角色从坐姿站起时的全身平衡）
- 需要高实时性的局部 IK（例如手指、肢体末端）用 PBIK，全身协调用 FBIK
- 与游戏玩法结合，动态影响角色骨骼（如推墙、攀爬时的肢体适配）

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK)
- [FullBodyIK 模块文档](./FullBodyIK.md)
- [PBIK 模块文档](./PBIK.md)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK/Tests)（若存在）