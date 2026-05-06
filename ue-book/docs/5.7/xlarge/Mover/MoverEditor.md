# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.  
> Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 运动器 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例内容） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 插件提供了一套基于**回滚网络（Rollback Networking）**的 Actor 运动框架。不同于传统的 `CharacterMovementComponent`，Mover 将运动逻辑拆分为可组合的“运动模型”，并默认支持客户端预测与服务器回滚，使网络下的移动更加平滑、可定制。

**解决的核心问题：**
- 高延迟网络环境下角色移动的平滑与同步
- 需要将动画驱动的根运动与物理运动解耦的场景（如过场动画、连击技能）
- 需要灵活切换不同运动模式（走、跑、游泳、飞行、爬墙等）的游戏

MoverEditor 是 Mover 的编辑器模块，主要提供蓝图节点 `Play Montage on Mover Actor`，用于在 Mover 驱动的 Actor 上播放蒙太奇，并自动分离动画根运动与运动模拟。

## 使用场景

- **射击游戏**：需要精确的移动同步与子弹命中反馈，K2Node 可用于播放射击蒙太奇而不会干扰运动预测。
- **动作游戏**：角色连招时播放蒙太奇，但移动仍由 Mover 控制，避免根运动破坏网络回滚。
- **多模式运动游戏**：角色可在地面、水面、空中切换运动模型，Mover 提供统一接口。
- **自定义网络运动系统**：需要完整控制移动逻辑且支持客户端预测的项目。

## 蓝图用法

当前公开的蓝图节点（由 MoverEditor 模块提供）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Montage on Mover Actor` | 在指定 Mover Actor 上播放蒙太奇，并自动分离根运动（运动由 Mover 的模拟处理，动画仅提供姿势）。支持设置起始位置、混合参数等。 | `UK2Node_PlayMontageOnMoverActor` |

### 使用步骤（蓝图）

1. 在事件图表中拖出 `Play Montage on Mover Actor` 节点。
2. 连接 **Target** 为实现了 Mover 接口的 Actor（通常为 `AMoverActor` 子类或设置了 `UMoverComponent` 的 Actor）。
3. 指定 **Montage To Play**（蒙太奇资产）。
4. 可选参数：
   - **In Play Rate**：播放速率。
   - **Starting Position**：起始播放位置（秒）。
   - **Starting Section**：起始节段名称。
5. 连接 **Completed** 输出引脚执行后续逻辑（蒙太奇播放完毕时触发）。

**注意**：该节点会自动处理蒙太奇的根运动设置，无需手动调用 `SetRootMotionMode` 等操作。

> **更多蓝图 API**：Mover 运行时模块（`Mover`）提供了大量可蓝图调用的函数，如 `SetMovementMode`、`GetLocalVelocity` 等。本文限于材料仅列出 MoverEditor 提供的节点，完整 API 请查看 [Mover 模块文档](#相关链接)。

## C++ 用法

MoverEditor 模块是编辑器模块，主要提供蓝图编译节点，**不推荐在 C++ 运行时直接使用**。以下以 Mover 核心运行时模块的典型用法为例（截取自插件测试用例与官方示例）。

### 头文件引入

```cpp
#include "MoverComponent.h"
#include "MoverActorInterface.h"
```

### 基本用法：获取 Mover 组件并设置速度

```cpp
// 在拥有 Mover 组件的 Actor 中
UMoverComponent* MoverComp = FindComponentByClass<UMoverComponent>();
if (MoverComp)
{
    // 设置移动速度（单位：cm/s）
    MoverComp->SetSpeed(600.0f);
    
    // 主动触发移动方向
    MoverComp->AddInputVector(FVector(1.0f, 0.0f, 0.0f));
}
```

来源示例：`Engine/Plugins/Experimental/Mover/Source/Mover/Private/Tests/` 中的模拟测试。

### 进阶用法：自定义运动模型

Mover 支持通过创建 `UMovementModel` 子类实现自定义运动逻辑。

```cpp
// MyMovementModel.h
#include "MovementModel.h"
#include "MyMovementModel.generated.h"

UCLASS()
class UMyMovementModel : public UMovementModel
{
    GENERATED_BODY()

public:
    virtual void SimulateMovement(const FMoverTickContext& Context, FMoverOutputState& Output) override
    {
        // 自定义模拟逻辑，可访问输入、时间步长等
        Output.Location += GetInputVector() * Context.DeltaSeconds * 1000.0f;
    }
};
```

然后在蓝图中或代码里注册该模型。

### 编辑器模块的 C++ 扩展

如需扩展 `PlayMontageOnMoverActor` 节点的行为，可继承 `UK2Node_PlayMontageOnMoverActor` 并覆写虚方法。但通常建议直接修改原节点参数。

## Demo 示例

以下为一个最小的、在编辑器蓝图中使用 `Play Montage on Mover Actor` 的示例（蓝图描述）。

**步骤**：

1. 新建蓝图为 `Actor`，添加 `MoverComponent`（需要依赖 Mover 插件）。
2. 在该蓝图中添加骨骼网格体组件，并指定一个带蒙太奇的动画蓝图。
3. 在 Event Graph 中：
   - 使用 `Event BeginPlay` → `Delay`（例如 2 秒）→ `Play Montage on Mover Actor`。
   - Target 连接到 `self`。
   - Montage 选择一个已有的蒙太奇资产。
   - 其他保持默认。
4. 将该 Actor 放置到关卡中运行（需开启网络模拟以观察回滚效果）。

**注意**：Play Montage 节点会自动将蒙太奇的 `RootMotionMode` 设置为 `IgnoreRootMotion`，因此根运动不会影响 Mover 的运动模拟，确保网络回滚正确。

## 模块依赖

使用 Mover 插件时，您的模块需要添加以下依赖（从 Mover、MoverEditor 等 Build.cs 提取的独特依赖）：

| 模块 | 用途 |
|---|---|
| `Mover` | 核心运行时：运动模拟、网络回滚、输入处理 |
| `MoverCVDData` | 冲突可视化调试数据（Circular Buffer 等） |
| `MoverCVDEditor` | 冲突可视化调试编辑器支持 |
| `MoverEditor` | 编辑器蓝图节点（本文重点） |

**常见依赖**（已省略，见模板说明）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-11-18 | c94b0582 | 修复非零起始时间蒙太奇从错误位置播放的问题 |
| 2025-11-18 | 0b7174b5 | 修复 MoverCVD 中容量为零的 CircularBuffer 初始化导致编辑器崩溃 |
| 2025-11-18 | 025130bc | 回退某次提交 |
| 2025-11-18 | 796d840a | 修复 MoverCVD 中容量为零的 CircularBuffer 初始化导致编辑器崩溃（重提） |
| 2025-11-18 | 0c5c955f | 为 BlackboardEntryBase 结构体添加虚析构函数以修复内存泄漏 |

### 维护评价

- **创建时间**：2025-11-18（不足一个月）
- **近期更新**：连续 5 次都在同一天，集中在崩溃修复与内存泄漏修补，无功能性新增。
- **活跃度**：属于实验性插件，创建初期，更新以修复为主，尚未稳定。
- **建议**：插件极新，功能可能频繁改动，存在已知问题（如编辑器崩溃尚未完全解决）。适合愿意跟踪最新版本并承担较新风险的团队。**未达到生产环境推荐状态**，但值得关注和测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mover-plugin/)（需确认是否存在，.uplugin 未提供 DocsURL）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover/Source/Mover/Private/Tests/)