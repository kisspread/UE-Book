# MoverTests

> Series of test content for the Mover system.

| 属性 | 值 |
|---|---|
| 中文名 | Mover 测试套件 |
| 分类 | Gameplay |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试地图） |
| 模块 | `MoverTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverTests) | |

## 用途

MoverTests 是 Mover 系统的测试内容插件，主要提供**自定义分层移动（Layered Move）**的参考实现。它解决了以下问题：

- 如何继承 `FLayeredMoveBase` 并实现自定义移动逻辑（如 Launch）
- 如何在 Mover 系统中注册、克隆、网络序列化分层移动
- 如何将自定义分层移动与 Mover 组件和黑名单系统集成，用于自动化测试或示例参考

该插件不提供运行时功能，而是作为**测试和示例框架**，帮助开发者快速验证自己的分层移动实现。

## 使用场景

- 你想为 Mover 角色添加自定义冲刺、击退、弹射等效果 → 参考 `FTestCustomLayeredMove`
- 你需要为 Mover 分层移动编写自动化测试 → 将此插件作为测试容器，在其中添加你的测试用例
- 你正在学习 Mover 2.0 的分层移动系统 → 直接阅读此插件的源码和蓝图资产，理解接口实现

## 蓝图用法

当前版本仅公开一个 `FTestCustomLayeredMove` 结构体（`BlueprintType`），可通过蓝图构造并应用到 Mover 组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FTestCustomLayeredMove`（构造节点） | 创建自定义分层移动实例，可设置 `LaunchVelocity` 和 `ForceMovementMode` | `FTestCustomLayeredMove` |
| `LaunchVelocity`（属性） | 施加的初始速度（cm/s），可叠加或覆盖 | `FTestCustomLayeredMove` |
| `ForceMovementMode`（属性） | 应用前强制切换到的移动模式名称 | `FTestCustomLayeredMove` |

### 使用示例（蓝图描述）

1. **在蓝图中**，通过「Construct Custom Layered Move」节点（实际由 `Make TestCustomLayeredMove` 提供）创建实例。
2. 设置 `LaunchVelocity` 和可选的 `ForceMovementMode`。
3. 调用 `Mover Component` 的 `AddLayeredMove` 节点，输入该实例。
4. 移动过程中该 Move 会自动执行，直到结束或被移除。

> 注意：`FTestCustomLayeredMove` 内部逻辑与 Launch 分层移动相同，仅用于测试自定义实现。生产环境建议直接使用 Mover 内置的 Launch 移动。

## C++ 用法

### 头文件引入

```cpp
#include "TestCustomLayeredMoves.h"
```

### 基本用法

继承 `FTestCustomLayeredMove` 或直接实例化它，用于测试或扩展。

```cpp
// 创建自定义分层移动
FTestCustomLayeredMove MyMove;
MyMove.LaunchVelocity = FVector(0, 0, 800.f);
MyMove.ForceMovementMode = FName("Jumping");
MyMove.MixMode = EMoveMixMode::OverrideAll;

// 通过 MoverComponent 添加
UMoverComponent* MoverComp = GetComponentByClass<UMoverComponent>();
if (MoverComp)
{
    MoverComp->AddLayeredMove(&MyMove);
}
```

来源文件：`Engine/Plugins/Experimental/MoverTests/Source/MoverTests/Public/TestCustomLayeredMoves.h`（及对应 .cpp）

### 进阶用法

自定义分层移动需要重写以下虚函数以实现完整功能：

```cpp
class FMyCustomLayeredMove : public FLayeredMoveBase
{
    // 移动开始时回调
    virtual void OnStart(const UMoverComponent* MoverComp, UMoverBlackboard* SimBlackboard) override;
    
    // 移动结束时回调
    virtual void OnEnd(const UMoverComponent* MoverComp, UMoverBlackboard* SimBlackboard, double CurrentSimTimeMs) override;
    
    // 每帧生成提议移动
    virtual bool GenerateMove(const FMoverTickStartData& StartState, const FMoverTimeStep& TimeStep,
                              const UMoverComponent* MoverComp, UMoverBlackboard* SimBlackboard, FProposedMove& OutProposedMove) override;
    
    // 克隆自身（用于网络复制）
    virtual FLayeredMoveBase* Clone() const override;
    
    // 网络序列化
    virtual void NetSerialize(FArchive& Ar) override;
    
    // 返回脚本结构
    virtual UScriptStruct* GetScriptStruct() const override;
    
    // 调试输出
    virtual FString ToSimpleString() const override;
    
    // 引用收集
    virtual void AddReferencedObjects(class FReferenceCollector& Collector) override;
};
```

参考 `FTestCustomLayeredMove` 的实现（位于 `.cpp` 文件）来了解每个函数的具体写法。

## Demo 示例

以下是一个最小 C++ 测试模块，在基于 Mover 的角色上应用自定义分层移动。

**MyCustomMove.h**

```cpp
#pragma once
#include "LayeredMove.h"
#include "MyCustomMove.generated.h"

USTRUCT(BlueprintType)
struct FMyCustomMove : public FLayeredMoveBase
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FVector Velocity = FVector::ZeroVector;

    virtual void OnStart(const UMoverComponent*, UMoverBlackboard*) override {}
    virtual void OnEnd(const UMoverComponent*, UMoverBlackboard*, double) override {}
    
    virtual bool GenerateMove(const FMoverTickStartData& StartState, const FMoverTimeStep& TimeStep,
                              const UMoverComponent* MoverComp, UMoverBlackboard* SimBlackboard, FProposedMove& OutProposedMove) override
    {
        OutProposedMove.LinearVelocity = Velocity;
        return true;
    }
    
    virtual FLayeredMoveBase* Clone() const override { return new FMyCustomMove(*this); }
    virtual void NetSerialize(FArchive& Ar) override { Ar << Velocity; }
    virtual UScriptStruct* GetScriptStruct() const override { return FMyCustomMove::StaticStruct(); }
    virtual FString ToSimpleString() const override { return TEXT("MyCustomMove"); }
    virtual void AddReferencedObjects(FReferenceCollector&) override {}
};
```

**AMyTestCharacter.cpp**

```cpp
#include "MyCustomMove.h"
#include "MoverComponent.h"

void AMyTestCharacter::ApplyCustomMove()
{
    if (UMoverComponent* Mover = FindComponentByClass<UMoverComponent>())
    {
        FMyCustomMove MyMove;
        MyMove.Velocity = FVector(500.f, 0, 200.f);
        Mover->AddLayeredMove(&MyMove);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mover` | 运行时 Mover 系统核心模块 |
| `MoverExamples` | 包含官方示例资源，用于测试集成 |

（其余标准依赖如 Core、Engine 等已省略）

## 维护状态

### 近期更新

```
- 2025-06-27 a55f7404 Mover: fix layered move timestamp conversions, including fix for broken multi-jump due to rounding
- 2024-06-13 269e9d03 Mover 2.0 Tests: Adding a new test layered move that acts the same as Launch. Used for testing implementation
- 2024-02-27 5fcc42d9 Mover 2.0 tests: Updating plugin to have proper dependencies
- 2024-02-02 1f1f5871 Moving Mover, MoverExamples, MoverTests out of Restricted engine folder
```

### 维护评价

- **创建时间**：2024-02-02，诞生约 1.5 年。
- **近期更新**：2025-06-27 有功能性修复，涉及分层移动时间戳和跳跃修复，维护较为活跃。
- **内容充实度**：插件仅包含一个测试分层移动类，功能简单但作为测试框架足够。
- **推荐使用**：✅ 推荐用于学习 Mover 分层移动实现或编写自定义移动测试。对于生产环境，建议直接使用 Mover 内置移动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverTests)
- [Mover 系统官方文档](https://docs.unrealengine.com/5.3/en-US/mover-plugin-in-unreal-engine/)（UE 5.3+）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverTests)（与源码同目录，包含蓝图测试资产）