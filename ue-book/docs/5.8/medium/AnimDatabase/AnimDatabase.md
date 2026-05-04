# AnimDatabase

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `AnimDatabase` (Runtime), `AnimDatabaseEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimDatabase) | |

## 用途

AnimDatabase 是一个用于构建和查询**动画数据库**的实验性插件，核心目标是将动画数据（姿态、帧范围、属性）以结构化、可索引的方式存储，并支持在运行时高效查询。它与 UE 的 Learning 框架深度集成，将动画数据转换为**向量化的平面表示**，适用于机器学习驱动的动画系统。

该插件解决的核心问题：
- **动画数据的结构化存储**：将 UAnimSequence 中的帧数据提取为 Frames、FrameRanges、FrameAttribute 三种基本结构
- **运行时动画查询**：通过索引系统（UAnimDatabaseIndex）快速查找满足特定属性条件的动画帧
- **ML 动画管线支持**：提供姿态数据的向量化表示（FPoseData），配合 LearningCore 插件用于神经网络动画推理
- **RigVM 集成**：提供 RigVM 节点，可在动画蓝图中直接操作帧属性和帧范围
- **动画混合辅助**：内置惯性化匹配距离计算、弹簧外推、死混合等数学工具

## 使用场景

- 你在构建基于机器学习的动画系统，需要将大量动画数据预处理为可查询的数据库 → 用 AnimDatabase
- 你需要在运行时根据角色状态（速度、位置、事件）查找最匹配的动画帧 → 用 AnimDatabase 的 FrameAttribute 查询
- 你在使用 Control Rig 进行动画驱动，需要在 RigVM 图中操作帧范围和属性 → 用 AnimDatabase 的 RigVM 节点
- 你需要实现惯性化过渡或弹簧式动画混合，且需要精确的数学工具 → 用 AnimDatabaseMath

## 蓝图用法

### 核心数据类型

AnimDatabase 提供三个核心蓝图结构体：

| 结构体 | 说明 |
|---|---|
| `FAnimDatabaseFrames` | 表示动画数据库中的一组帧，内部封装 `UE::Learning::FFrameSet` |
| `FAnimDatabaseFrameRanges` | 表示一组帧范围，内部封装 `UE::Learning::FFrameRangeSet` |
| `FAnimDatabaseFrameAttribute` | 表示与帧范围关联的属性（布尔、浮点、位置、旋转、速度等） |

### FrameAttribute 类型

`EAnimDatabaseAttributeType` 枚举定义了所有支持的属性类型：

| 类型 | 说明 |
|---|---|
| `Bool` | 布尔值 |
| `Float` | 浮点数 |
| `Location` | 位置 (FVector3f) |
| `Rotation` | 旋转 (FQuat4f) |
| `Scale` | 缩放 (FVector3f) |
| `LinearVelocity` | 线速度 |
| `AngularVelocity` | 角速度 |
| `ScalarVelocity` | 标量速度 |
| `Direction` | 方向 |
| `Transform` | 完整变换 |
| `Event` | 事件（含时间直到事件发生） |
| `Angle` | 角度 |

### FrameAttribute 数据访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAsBool` | 获取指定帧的布尔属性值 | `FAnimDatabaseFrameAttribute` |
| `GetAsFloat` | 获取指定帧的浮点属性值 | `FAnimDatabaseFrameAttribute` |
| `GetAsLocation` | 获取指定帧的位置属性 | `FAnimDatabaseFrameAttribute` |
| `GetAsRotation` | 获取指定帧的旋转属性 | `FAnimDatabaseFrameAttribute` |
| `GetAsScale` | 获取指定帧的缩放属性 | `FAnimDatabaseFrameAttribute` |
| `GetAsVelocity` | 获取指定帧的速度属性 | `FAnimDatabaseFrameAttribute` |
| `GetAsDirection` | 获取指定帧的方向属性 | `FAnimDatabaseFrameAttribute` |
| `GetAsTransform` | 获取指定帧的完整变换 | `FAnimDatabaseFrameAttribute` |
| `GetAsEvent` | 获取指定帧的事件信息（含时间直到事件） | `FAnimDatabaseFrameAttribute` |
| `IsValid` | 检查 FrameAttribute 是否有效 | `FAnimDatabaseFrameAttribute` |

### RigVM 节点

AnimDatabase 提供以下 RigVM 节点，可在 Control Rig 蓝图中使用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Intersection` | 计算 FrameAttribute 与 FrameRanges 的交集 | `FRigVMFunction_FrameAttributeIntersection` |
| `Add (Frame Attribute)` | 合并两个 FrameAttribute | `FRigVMFunction_FrameAttributeAdd` |
| `Inertialization Matching Distance` | 基于位置和速度属性计算惯性化匹配距离 | `FRigVMFunction_FrameAttributeInertializationMatchingDistance` |

### 使用示例（蓝图描述）

**查询动画帧属性**：
1. 获取一个 `UAnimDatabase` 资产引用
2. 通过 `UAnimDatabaseIndex` 获取预构建的 `FAnimDatabaseFrameAttribute`（如速度、位置等）
3. 使用 `GetAsFloat` / `GetAsLocation` 等节点，传入帧索引获取具体数值
4. 根据查询结果驱动角色动画状态

**在 Control Rig 中使用**：
1. 在 Control Rig 图中添加 `Intersection` 节点
2. 将一个 FrameAttribute（如"正在移动"属性）连接到输入 A
3. 将 FrameRanges（如"行走动画帧范围"）连接到输入 B
4. 输出 Result 即为同时满足两个条件的帧集合

## C++ 用法

### 头文件引入

```cpp
#include "AnimDatabase.h"
#include "AnimDatabaseFrameAttribute.h"
#include "AnimDatabaseFrameRanges.h"
#include "AnimDatabaseIndex.h"
#include "AnimDatabasePose.h"
#include "AnimDatabaseMath.h"
```

### 基本用法 — FrameAttribute 数据访问

```cpp
// 假设已有一个 FAnimDatabaseFrameAttribute 实例
FAnimDatabaseFrameAttribute VelocityAttribute;

if (VelocityAttribute.IsValid())
{
    // 获取第 10 帧的速度
    FVector3f Velocity = VelocityAttribute.GetAsVelocity(10);
    
    // 获取第 10 帧的浮点属性
    float Speed = VelocityAttribute.GetAsFloat(10);
    
    // 获取事件信息
    bool bTimeUntilEventKnown;
    float TimeUntilEvent;
    VelocityAttribute.GetAsEvent(bTimeUntilEventKnown, TimeUntilEvent, 10);
}
```

### 基本用法 — FrameRanges 操作

```cpp
// FAnimDatabaseFrames 和 FAnimDatabaseFrameRanges 是对 Learning 库数据结构的薄包装
FAnimDatabaseFrames Frames;
FAnimDatabaseFrameRanges FrameRanges;

if (Frames.IsValid() && FrameRanges.IsValid())
{
    // 底层数据结构可直接访问
    // TSharedPtr<UE::Learning::FFrameSet, ESPMode::ThreadSafe> FrameSet = Frames.FrameSet;
    // TSharedPtr<UE::Learning::FFrameRangeSet, ESPMode::ThreadSafe> FrameRangeSet = FrameRanges.FrameRangeSet;
}
```

### 进阶用法 — 姿态数据操作

```cpp
#include "AnimDatabasePose.h"

using namespace UE::AnimDatabase;

// 创建姿态数据
FPoseRootData RootData;
RootData.Resize(60); // 60 帧

// 获取可写视图
FPoseRootDataView RootView = RootData.View();

// 访问根骨骼位置和旋转
for (int32 i = 0; i < 60; ++i)
{
    FVector& Location = RootView.RootLocations[i];
    FQuat4f& Rotation = RootView.RootRotations[i];
    FVector3f& LinearVel = RootView.RootLinearVelocities[i];
    // ... 设置或读取数据
}

// 切片操作 - 获取子范围
FPoseRootDataView SubView = RootView.Slice(10, 20); // 第 10-29 帧
```

### 进阶用法 — 数学工具

```cpp
#include "AnimDatabaseMath.h"

using namespace UE::AnimDatabase::Math;

// 弹簧式动画混合 - 使用半衰期控制衰减
FVector CurrentPosition = FVector::ZeroVector;
FVector CurrentVelocity = FVector::ZeroVector;
FVector DesiredPosition = FVector(100, 0, 0);
float HalfLife = 0.1f; // 100ms 半衰期
float DeltaTime = 0.016f;

CriticalSpringUpdate(CurrentPosition, CurrentVelocity, DesiredPosition, HalfLife, DeltaTime);

// 半衰期与阻尼系数转换
float Damping = HalfLifeToDamping(0.1f);
float BackToHalfLife = DampingToHalfLife(Damping);

// 位置外推（带衰减）
FVector3f OutTranslation, OutVelocity;
FVector3f InTranslation = FVector3f(10, 0, 0);
FVector3f InVelocity = FVector3f(100, 0, 0);
FVector3f DecayHalflife = FVector3f(0.1f, 0.1f, 0.1f);

ExtrapolateTranslation(OutTranslation, OutVelocity, InTranslation, InVelocity, 0.05f, DecayHalflife);
```

## Demo 示例

### AnimDatabaseIndex 自定义索引构建

```cpp
// MyAnimIndexFunction.h
#pragma once

#include "AnimDatabaseIndex.h"
#include "MyAnimIndexFunction.generated.h"

UCLASS(meta = (DisplayName = "Speed Based Index"))
class UMyAnimIndexFunction : public UAnimDatabaseIndexFunction
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Settings")
    float SpeedThreshold = 100.0f;

#if WITH_EDITOR
    virtual void BuildIndex_Implementation(
        TMap<FName, FAnimDatabaseFrames>& OutIndexFrames,
        TMap<FName, FAnimDatabaseFrameRanges>& OutIndexFrameRanges,
        TMap<FName, FAnimDatabaseFrameAttribute>& OutIndexFrameAttributes,
        UAnimDatabase* InDatabase,
        const FAnimDatabaseFrameRanges& InFrameRanges) override;
#endif
};
```

```cpp
// MyAnimIndexFunction.cpp
#include "MyAnimIndexFunction.h"

#if WITH_EDITOR
void UMyAnimIndexFunction::BuildIndex_Implementation(
    TMap<FName, FAnimDatabaseFrames>& OutIndexFrames,
    TMap<FName, FAnimDatabaseFrameRanges>& OutIndexFrameRanges,
    TMap<FName, FAnimDatabaseFrameAttribute>& OutIndexFrameAttributes,
    UAnimDatabase* InDatabase,
    const FAnimDatabaseFrameRanges& InFrameRanges)
{
    // 在此处从数据库中提取帧范围和属性
    // 例如：根据速度阈值将帧分为"行走"和"跑步"两组
    // OutIndexFrameRanges.Add("Walking", WalkingFrameRanges);
    // OutIndexFrameRanges.Add("Running", RunningFrameRanges);
    // OutIndexFrameAttributes.Add("Speed", SpeedAttribute);
}
#endif
```

## 模块依赖

AnimDatabase 依赖以下插件（来自 .uplugin 的 Plugins 字段）：

| 插件 | 用途 |
|---|---|
| `AnimationWarping` | 动画变形/扭曲支持 |
| `LearningCore` | 机器学习核心库，提供向量化数据结构（FFrameSet、FFrameRangeSet 等） |
| `DrawDebugLibrary` | 调试绘制工具 |

模块级依赖（从 Build.cs 提取）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能（注意：AnimDatabase Runtime 模块也依赖此模块，可能用于编辑器内数据构建） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2026-04-24 `05f62ee5` AnimGen: Added support for debug drawing on the canvas
- 2026-04-22 `2fc4ab35` AnimGen: No longer auto-refresh when changing frame ranges or frame attributes on the various editor
- 2026-04-22 `e4a63951` AnimDatabase: Added a couple more frame attribute functions
- 2026-04-10 `4f791a26` AnimDatabase: Adjusted how bone weights are computed to improve autoencoder accuracy on foot joints
- 2026-04-10 `3f7370fe` AnimGen: Added attribute smoothing to help reduce the noise

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **依赖 LearningCore**：与 UE 的机器学习框架深度绑定，表明这是 ML 动画管线的一部分
- **Runtime 模块依赖 UnrealEd**：这是一个不寻常的模式，可能意味着该模块在打包后不可用，或存在架构问题
- **版本号 0.1**：处于早期开发阶段
- **建议**：仅用于实验和原型开发，不建议在生产环境中使用。关注 Epic 的 ML 动画相关更新以获取该插件的后续发展

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimDatabase)
- 官方文档：无
- 测试用例：未在插件目录内发现测试文件