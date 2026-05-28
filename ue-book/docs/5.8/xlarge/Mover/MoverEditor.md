# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking. Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 移动组件 |
| 分类 | Gameplay |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 是一个支持**回滚网络（Rollback Networking）**的 Actor 移动系统。它解决的核心问题是：在网络多人游戏中，如何让客户端实现流畅的移动预测与服务器校验，同时保持代码的模块化和可扩展性。

传统 CharacterMovementComponent 将移动逻辑紧密耦合在单一类中，难以扩展和复用。Mover 采用了**模式（Mode）+ 移动方式（Movement Style）+ 修改器（Modifier）**的分层架构，将移动行为拆解为独立、可组合的模块，使得：
- 可以灵活切换不同移动模式（如行走、飞行、攀爬等）
- 每种移动方式可独立实现和测试
- 支持网络回滚：客户端预测移动后，可以安全回滚并重新模拟
- 动画根运动（Root Motion）与移动逻辑解耦

该插件包含四个模块：
- **Mover**：核心运行时，包含移动模拟、模式管理、网络同步等
- **MoverCVDData**：控制台变量调试器（CVD）数据，用于运行时可视化调试
- **MoverCVDEditor**：CVD 编辑器端支持
- **MoverEditor**：编辑器工具，提供蓝图 K2 节点等

## 使用场景

- 你需要为多人在线游戏构建自定义移动系统，且需要客户端预测与回滚 → 用 Mover
- 你需要高度模块化的移动架构，方便扩展飞行、攀爬、载具等多种移动方式 → 用 Mover
- CharacterMovementComponent 的设计无法满足你的移动需求（如非胶囊体碰撞、复杂运动状态机） → 用 Mover
- 你需要在动画蒙太奇播放时正确处理根运动对移动的影响 → 用 Mover

## 蓝图用法

### 核心节点

MoverEditor 模块提供了一个异步蓝图节点，用于在 Mover Actor 上播放动画蒙太奇：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Montage on Mover Actor` | 在 Mover 控制的 Actor 上异步播放动画蒙太奇，支持完成/中断等回调 | `UK2Node_PlayMontageOnMoverActor` |

### 使用示例（蓝图描述）

1. 在蓝图中搜索 **"Play Montage on Mover Actor"** 节点
2. 连接目标 Actor（必须是 Mover 控制的 Actor）
3. 选择要播放的 AnimMontage 资产
4. 连接异步输出引脚：
   - **On Completed**：蒙太奇正常播放完成时触发
   - **On Interrupted**：蒙太奇被中断时触发
   - **On Cancelled**：蒙太奇被取消时触发
5. 该节点会自动处理根运动与 Mover 移动模拟的协调

## C++ 用法

### 头文件引入

```cpp
#include "MoverComponent.h"
#include "MoverSimulationTypes.h"
#include "DefaultMovementSet/Modes/WalkingMode.h"
#include "DefaultMovementSet/Modes/FallingMode.h"
```

### 基本用法

Mover 的核心组件是 `UMoverComponent`，需要挂载到 Actor 上并配置移动模式和方式。

```cpp
// MoverComponent 通常作为 Actor 的组件使用
// 配置移动模式（Walking、Falling、Flying 等）
// 配置移动方式（Movement Styles），决定具体的移动实现逻辑

// 获取 Mover 组件
UMoverComponent* MoverComp = MyActor->FindComponentByClass<UMoverComponent>();
if (MoverComp)
{
    // 查询当前移动模式
    FGameplayTag CurrentMode = MoverComp->GetCurrentMode();
    
    // 强制切换模式
    MoverComp->SetMode(FGameplayTag::RequestGameplayTag(TEXT("Mover.Walking")));
}
```

### 进阶用法

Mover 系统的回滚网络支持使得客户端可以预测移动并在服务器校正后重新模拟。自定义移动方式（Movement Style）需要实现特定接口来参与模拟过程。

```cpp
// 自定义移动方式需要实现 IMovementModeTransitionInterface 或类似接口
// 每个 Simulation Tick 时，Mover 会按以下顺序处理：
// 1. 收集输入（Input）
// 2. 应用修改器（Modifiers）
// 3. 执行移动模拟（通过当前 Mode 和 Styles）
// 4. 生成移动结果（Sync State）

// 动画根运动通过专门的通道注入 Mover 模拟
// UK2Node_PlayMontageOnMoverActor 节点封装了此交互
```

## 模块依赖

从各模块 Build.cs 提取的依赖关系：

| 模块 | 用途 |
|---|---|
| `MoverCVDData` | Mover 主模块依赖，提供控制台变量调试器的可视化数据 |
| `GameplayTags` | Mover 使用 GameplayTag 标识移动模式和状态 |
| `PhysicsCore` / `Chaos` | 物理模拟集成，支持物理驱动的移动和回滚 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6ef46a3c` | Mover: update README for next release | 更新 README 文档，为下个版本发布做准备 |
| 2026-05-22 | `4ea45e21` | Mover: fix bug where skipping vertical anim root motion was not being respected in all montage cases | 修复跳过垂直动画根运动在部分蒙太奇场景下未生效的 bug |
| 2026-05-20 | `dd78e781` | Mover: fix for inconsistent behavior of mode-changed events (kinematic / NPP cases) resulting in que | 修复运动学/NPP 模式切换事件不一致导致的队列问题 |
| 2026-05-14 | `801be5dc` | Mover/ChaosMover: Just like moves, move instances are now using a pull mechanism so they can work in | MoveInstance 改为拉取机制以兼容新架构 |
| 2026-05-14 | `d040bc9f` | Mover: adding simulation that's specific to kinematically-moved Actors | 新增针对运动学驱动 Actor 的专用模拟支持 |

### 维护评价

Mover 插件处于**活跃维护**状态。2026 年 5 月有密集的更新，涵盖 bug 修复（根运动、模式切换）、架构改进（拉取机制）和新功能（运动学 Actor 模拟）。作为实验性插件（约 2 年历史），它正在积极迭代和完善。

**注意事项**：
- 位于 `Experimental` 目录下，API 可能会发生变化
- 推荐用于新项目尝试，不建议在已发布项目中替换现有 CMC
- 建议关注 README 文档中记录的已知问题

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
- [官方文档]()（暂无独立文档，请参考插件内 README）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover/Source/MoverTests)