# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、节点模板、摄像机导演蓝图） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

---

## 用途

GameplayCameras 是 Epic 为 UE5 构建的全新、模块化、数据驱动的摄像机系统。它从根本上重新设计了 UE 中摄像机行为的定义、评估和混合方式。

**解决的核心问题：**

1. **传统摄像机系统碎片化**：UE4 时代的摄像机行为散落在 `CameraComponent`、`CameraShake`、`PlayerCameraManager` 等各处，难以组合和复用
2. **缺乏数据驱动**：摄像机行为难以用资产形式定义和共享，修改需要改代码
3. **混合能力有限**：多摄像机 rig 之间的过渡/混合机制不完善，难以实现电影级的摄像机切换

**架构设计思想：**

- **Camera Node 树**：摄像机行为通过类似材质编辑器的节点图定义，每个节点负责一个特定功能（取景、碰撞避让、抖动等）
- **Camera Rig Asset**：可复用的摄像机行为单元，封装了一棵节点树和可暴露的参数接口
- **Camera Asset**：更高层的资产，包含摄像机导演（Director）和多个 Camera Rig
- **Blend Stack**：支持多种混合模式（隔离瞬态、叠加持久），用于管理多个活跃 Camera Rig 之间的过渡
- **评估上下文（Evaluation Context）**：将摄像机的运行与特定玩家、世界关联起来

## 相关文档

| 文档 | 说明 |
|---|---|
| [核心架构](Core.md) | 评估流水线、变量表、上下文数据表、Camera Pose |
| [Game Framework 集成](GameFramework.md) | GameplayCameraComponent、PlayerCameraManager 替代方案 |
| [Camera Nodes](CameraNodes.md) | 内置摄像机节点（取景、碰撞、蓝图节点等） |
| [Camera Rig & Asset](CameraRigAsset.md) | CameraRigAsset、CameraAsset、参数接口、引用与覆盖 |
| [Actions & Directors](ActionsDirectors.md) | 摄像机动作、瞄准动作、蓝图摄像机导演 |
| [混合系统](BlendSystem.md) | Blend Stack、Blend Nodes、过渡机制 |
| [蓝图 API 参考](BlueprintAPI.md) | 蓝图可调用函数完整列表 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 中摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double→float 截断警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 补充 trace channel 描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 常规更新（提交信息为插件名） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |

### 维护评价

- **创建时间**：2020-10-10，约 6 年历史
- **维护状态**：**活跃维护中**。最近一次更新距今不到 1 个月（2026-05-26），且更新频率稳定（每月多次提交）
- **代码质量**：持续有 bug 修复和代码清理工作（如 UE_LOG→UE_LOGF 迁移、编译警告修复）
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，说明 Epic 仍将此系统视为实验性功能。API 可能在未来版本中发生变化
- **启用状态**：`EnabledByDefault=true`，默认随引擎启用，方便测试
- **推荐使用**：✅ 推荐用于新项目的摄像机系统开发。它代表了 Epic 对 UE 摄像机系统的未来方向。但需注意实验性标签意味着 API 稳定性不能完全保证

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]() （暂无公开文档 URL）
