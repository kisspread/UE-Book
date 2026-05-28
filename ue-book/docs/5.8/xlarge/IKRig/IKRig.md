Let me first gather the git information needed.

```bash
# Get creation time
cd /mnt/x/UnrealEngine && git log --diff-filter=A --format='%ai' -- 'Engine/Plugins/Animation/IKRig/IKRig.uplugin' | tail -1

# Get recent commits
cd /mnt/x/UnrealEngine && git log --format='%h|%ai|%s' -5 -- 'Engine/Plugins/Animation/IKRig/'
```

# IK Rig

> IK Rig, IK Retarget, and related animation runtime for Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | IK骨骼 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、动画节点、编辑器工具） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (Runtime), `IKRigEditor` (Runtime), `IKRigUAF` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig) | |

## 用途

IKRig 是 Unreal Engine 的**核心动画重定向和 IK 求解系统**。它解决两个核心问题：

1. **IK Rig（IK 求解）**：在运行时根据目标位置（Goals）驱动骨骼链完成逆运动学计算。支持多种求解器（Full Body IK、Limb IK、Body Mover、Pole Solver 等），可在动画蓝图中对输入姿态进行 IK 修改。

2. **IK Retargeter（动画重定向）**：将一个骨骼网格体的动画传输到另一个不同比例、不同骨架结构的骨骼网格体上。采用可插拔的"Op 栈"架构，通过组合不同的重定向操作（FK Chain、IK Goals、Pelvis Motion、Speed Planting、Stride Warping 等）来精细控制重定向行为。

这个系统的设计理念是将 IK 求解和动画重定向统一在一个框架下。IK Retargeter 内部使用 IK Rig 来定义骨骼链和求解逻辑，而 IK Rig 本身也可以独立用于运行时 IK 修正（如手持武器、脚部贴地等）。

## 使用场景

- 你需要将角色 A 的动画应用到体型完全不同的角色 B 上 → 使用 **IK Retargeter**
- 你需要让角色的脚在斜坡上保持贴地 → 使用 Floor Constraint Op + IK Rig
- 你需要在动画蓝图中实时驱动角色的手/脚到特定位置 → 使用 **AnimNode_IKRig**
- 你需要从另一个角色网格体获取动画数据并重定向 → 使用 **AnimNode_RetargetPoseFromMesh**
- 你需要精细控制重定向过程中的步幅拉伸（stride warping） → 使用 Stride Warping Op
- 你需要将武器/持握骨骼从一个骨架映射到另一个 → 使用 Weapon Goals Op
- 你需要自定义 IK 求解器（如机器人手臂、特殊约束） → 继承 `FIKRigSolverBase`

## 文档结构

由于本插件包含 243 个源文件，属于大型插件，文档按子模块拆分：

| 文档 | 内容 |
|---|---|
| [index.md](index.md)（本页） | 用途总览、模块列表、维护状态 |
| [IKRig-Core.md](IKRig-Core.md) | IK Rig 求解核心：Processor、Solver、Goal、Skeleton |
| [IKRig-Solvers.md](IKRig-Solvers.md) | 内置求解器：FBIK、Limb、BodyMover、Pole、SetTransform、StretchLimb |
| [IKRetargeter-Core.md](IKRetargeter-Core.md) | IK Retargeter 核心：Asset、Processor、Profile、Override |
| [IKRetargeter-Ops.md](IKRetargeter-Ops.md) | 重定向 Op 栈：FK/IK Chain、Pelvis、Speed Planting、Stride Warping 等 |
| [AnimNodes.md](AnimNodes.md) | 动画蓝图节点：IKRig、RetargetPoseFromMesh |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | IK Rig 依赖 ControlRig 基础设施 |
| `FullBodyIK` | 提供物理骨骼 IK (PBIK) 求解算法 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d96c8edf` | Fix root motion trajectory visualization in IK Retarget editor | 修复 IK 重定向编辑器中根运动轨迹可视化问题 |
| 2026-05-12 | `b9da6b61` | [IK Retargeter] Fix curve-bound override values having no effect on exported batch retarget animatio | 修复曲线绑定覆盖值在批量导出重定向动画时无效的问题 |
| 2026-05-12 | `553f4a7e` | [IK Retargeter] Fix pre-5.6 RTG assets having all ops enabled in 5.8: narrow PostLoad version guard | 修复 5.6 之前的重定向资产在 5.8 中所有 Op 被意外启用的问题 |
| 2026-05-12 | `0171c6fd` | [IK Retargeter] Fix null deref crashes in GenerateAssetLists: guard GC'd weak ptrs, uncompiled bluep | 修复 GenerateAssetLists 中空指针崩溃问题 |
| 2026-05-12 | `f8c7fc88` | [IK Retargeter] Fix active-by-default Override Sets not applied when exporting animations through th | 修复默认激活的覆盖集在通过重定向器导出动画时未被应用的问题 |

### 维护评价

**🟢 活跃维护中**。IKRig 是 Epic Games 核心动画系统的关键组件，持续受到活跃开发和维护：

- 2026 年 5 月仍有功能性 Bug 修复和兼容性改进
- 5.6 版本经历了重大架构重构（从 UObject 到 UStruct），5.7/5.8 持续修补迁移兼容性
- 代码中大量 `_DEPRECATED` 属性展示了完善的向后兼容策略
- 作为默认启用的核心插件，有持续的用户反馈驱动改进
- **强烈推荐使用**，是 UE5 动画重定向和 IK 求解的标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig)
- [IKRig 核心文档](IKRig-Core.md)
- [IKRig 求解器文档](IKRig-Solvers.md)
- [IKRetargeter 核心文档](IKRetargeter-Core.md)
- [IKRetargeter Ops 文档](IKRetargeter-Ops.md)
- [动画节点文档](AnimNodes.md)