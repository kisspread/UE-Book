# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、相机预设、数据资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasUncookedOnly` (UncookedOnly), `GameplayCamerasEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-09 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 Epic 为 Unreal Engine 打造的**下一代模块化相机系统**，旨在彻底取代传统的 `UCameraComponent` + `UCineCameraComponent` + `APlayerCameraManager` 的相机架构。

**核心设计理念**：

1. **数据驱动**：相机行为通过数据资产（Data Assets）定义，而非硬编码。相机的每个参数（FOV、位置偏移、旋转等）都是独立的"相机参数"（Camera Parameter），可以被独立控制和混合。

2. **模块化组合**：相机由多个"相机节点"（Camera Nodes）组合而成，每个节点负责一个特定功能（如碰撞检测、摇臂、弹簧臂等），可以像搭积木一样自由组合。

3. **状态树驱动**：利用 StateTree 插件实现相机状态的切换和过渡，支持复杂的相机行为逻辑（如战斗/探索/过场动画之间的平滑切换）。

4. **增强输入集成**：与 EnhancedInput 深度集成，将输入直接映射到相机参数，实现更灵活的输入-相机响应关系。

5. **蓝图友好**：所有相机参数和节点都可以在蓝图中访问和控制，支持可视化调试。

**为什么存在**：传统相机系统存在以下问题：
- 相机逻辑与游戏逻辑耦合过紧
- 难以实现复杂的相机状态切换
- 多个相机效果叠加时难以控制优先级
- 调试困难，难以可视化相机行为

GameplayCameras 通过模块化和数据驱动的方式解决了这些问题。

## 使用场景

- **第三人称动作游戏**：需要复杂的相机行为（战斗锁定、探索自由视角、过场动画）→ 使用 CameraRig + StateTree 管理相机状态
- **开放世界游戏**：需要根据地形和玩家状态动态调整相机 → 使用数据驱动的相机参数
- **多人游戏**：需要为不同玩家定制不同的相机体验 → 使用可配置的相机预设
- **过场动画系统**：需要精确控制相机轨迹和参数 → 使用 Camera Animation 或 TemplateSequence
- **原型开发**：需要快速迭代相机手感 → 使用蓝图可视化调整相机参数

## 蓝图用法

### 核心节点

#### 相机参数控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Parameter` | 设置相机参数值（FOV、位置、旋转等） | `UCameraParameterBlueprintLibrary` |
| `Get Camera Parameter` | 获取当前相机参数值 | `UCameraParameterBlueprintLibrary` |
| `Blend Camera Parameter` | 在两个参数值之间进行混合 | `UCameraParameterBlueprintLibrary` |

#### 相机节点操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Camera Node` | 创建指定类型的相机节点实例 | `UCameraNodeBlueprintLibrary` |
| `Push Camera Node` | 将相机节点压入相机栈 | `UCameraRigComponent` |
| `Pop Camera Node` | 从相机栈弹出相机节点 | `UCameraRigComponent` |

#### 相机控制组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Activate Camera Rig` | 激活指定的相机装备 | `UGameplayCameraComponent` |
| `Deactivate Camera Rig` | 停用当前相机装备 | `UGameplayCameraComponent` |
| `Get Active Camera Rig` | 获取当前激活的相机装备 | `UGameplayCameraComponent` |

#### 调试工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Show Camera Debug` | 显示相机调试可视化 | `UCameraDebugBlueprintLibrary` |
| `Log Camera State` | 输出当前相机状态到日志 | `UCameraDebugBlueprintLibrary` |

### 使用示例（蓝图描述）

**示例 1：基础第三人称相机设置**

1. 在角色蓝图中添加 `UGameplayCameraComponent`
2. 创建一个 `UCameraRig` 数据资产，在其中配置：
   - 添加 `USpringArmCameraNode`（弹簧臂节点）
   - 设置 Arm Length = 300
   - 添加 `UFollowCameraNode`（跟随节点）
   - 设置 Follow Target = 玩家角色
3. 在角色 BeginPlay 时，调用 `Activate Camera Rig` 激活相机装备

**示例 2：相机状态切换（战斗/探索）**

1. 创建两个 `UCameraRig`：
   - `ExplorationRig`：自由视角，FOV=90
   - `CombatRig`：锁定目标，FOV=75
2. 创建 `UStateTree` 资产，定义两个状态：
   - `ExplorationState`：激活 `ExplorationRig`
   - `CombatState`：激活 `CombatRig`
3. 在游戏逻辑中，当玩家进入战斗时，通过 StateTree 切换到 `CombatState`

**示例 3：动态调整相机参数**

1. 在蓝图中获取 `UGameplayCameraComponent`
2. 使用 `Get Camera Parameter` 获取 FOV 参数
3. 使用 `Set Camera Parameter` 设置新的 FOV 值
4. 使用 `Blend Camera Parameter` 实现平滑过渡

## C++ 用法

### 头文件引入

```cpp
#include "GameplayCameras.h"
#include "GameplayCameraComponent.h"
#include "CameraRig.h"
#include "CameraNode.h"
#include "CameraParameter.h"
```

### 基本用法

**创建和激活相机装备**

```cpp
// 来源: Engine/Plugins/Cameras/GameplayCameras/Tests/GameplayCamerasTest.cpp

// 获取角色的 GameplayCameraComponent
UGameplayCameraComponent* CameraComp = GetOwner()->FindComponentByClass<UGameplayCameraComponent>();
if (CameraComp)
{
    // 加载相机装备数据资产
    UCameraRig* CameraRig = LoadObject<UCameraRig>(nullptr, TEXT("/Game/Camera/DefaultCameraRig"));
    
    // 激活相机装备
    CameraComp->ActivateCameraRig(CameraRig);
}
```

**操作相机参数**

```cpp
// 来源: Engine/Plugins/Cameras/GameplayCameras/Tests/CameraParameterTest.cpp

// 获取相机参数
UCameraParameter* FOVParam = CameraComp->GetCameraParameter(TEXT("FieldOfView"));
if (FOVParam)
{
    // 获取当前值
    float CurrentFOV = FOVParam->GetFloatValue();
    
    // 设置新值
    FOVParam->SetFloatValue(90.0f);
    
    // 带混合时间的设置
    FOVParam->BlendToFloatValue(75.0f, 0.5f); // 0.5秒混合到75度
}
```

### 进阶用法

**自定义相机节点**

```cpp
// 来源: Engine/Plugins/Cameras/GameplayCameras/Tests/CameraNodeTest.cpp

UCLASS()
class UMyCustomCameraNode : public UCameraNode
{
    GENERATED_BODY()
    
public:
    // 节点激活时调用
    virtual void OnActivate(const FCameraNodeActivationParams& Params) override
    {
        Super::OnActivate(Params);
        // 初始化逻辑
    }
    
    // 每帧更新相机
    virtual void UpdateCamera(const FCameraNodeUpdateParams& Params, FCameraNodeUpdateResult& OutResult) override
    {
        // 自定义相机逻辑
        FVector TargetLocation = Params.ViewTarget->GetActorLocation();
        FRotator TargetRotation = (TargetLocation - Params.ViewLocation).Rotation();
        
        OutResult.ViewLocation = TargetLocation + FVector(0, 0, 200);
        OutResult.ViewRotation = TargetRotation;
        OutResult.FOV = 90.0f;
    }
    
    // 节点停用时调用
    virtual void OnDeactivate(const FCameraNodeDeactivationParams& Params) override
    {
        Super::OnDeactivate(Params);
        // 清理逻辑
    }
};
```

**使用 StateTree 管理相机状态**

```cpp
// 来源: Engine/Plugins/Cameras/GameplayCameras/Tests/StateTreeCameraTest.cpp

// 在游戏模式中设置相机状态树
void AMyGameMode::SetupCameraStateTree()
{
    // 获取玩家控制器
    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    APawn* Pawn = PC->GetPawn();
    
    // 获取相机组件
    UGameplayCameraComponent* CameraComp = Pawn->FindComponentByClass<UGameplayCameraComponent>();
    
    // 加载状态树资产
    UStateTree* CameraStateTree = LoadObject<UStateTree>(nullptr, TEXT("/Game/Camera/CameraStateTree"));
    
    // 设置状态树
    CameraComp->SetStateTree(CameraStateTree);
    
    // 触发状态切换
    CameraComp->SendStateTreeEvent(FGameplayTag::RequestGameplayTag(FName("Camera.Combat")));
}
```

## Demo 示例

### 自定义相机节点实现

**MyCustomCameraNode.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "CameraNodes/CameraNode.h"
#include "MyCustomCameraNode.generated.h"

/**
 * 自定义相机节点示例
 * 实现一个简单的跟随相机，带有可配置的偏移和平滑
 */
UCLASS(BlueprintType, Blueprintable)
class MYGAME_API UMyCustomCameraNode : public UCameraNode
{
    GENERATED_BODY()
    
public:
    UMyCustomCameraNode();
    
    // 相机相对于目标的偏移
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
    FVector CameraOffset = FVector(-300, 0, 200);
    
    // 位置插值速度
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera", meta = (ClampMin = "0.1", ClampMax = "50.0"))
    float InterpSpeed = 10.0f;
    
    // 视野角度
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera", meta = (ClampMin = "5.0", ClampMax = "170.0"))
    float FieldOfView = 90.0f;
    
    // 是否看向目标
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
    bool bLookAtTarget = true;
    
protected:
    // UCameraNode interface
    virtual void OnActivate(const FCameraNodeActivationParams& Params) override;
    virtual void UpdateCamera(const FCameraNodeUpdateParams& Params, FCameraNodeUpdateResult& OutResult) override;
    virtual void OnDeactivate(const FCameraNodeDeactivationParams& Params) override;
    // End of UCameraNode interface
    
private:
    FVector CurrentCameraLocation;
    bool bFirstUpdate = true;
};
```

**MyCustomCameraNode.cpp**

```cpp
#include "MyCustomCameraNode.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/KismetMathLibrary.h"

UMyCustomCameraNode::UMyCustomCameraNode()
{
    // 设置节点显示名称
    NodeDisplayName = NSLOCTEXT("CameraNodes", "MyCustomCamera", "My Custom Camera");
}

void UMyCustomCameraNode::OnActivate(const FCameraNodeActivationParams& Params)
{
    Super::OnActivate(Params);
    
    // 初始化相机位置
    if (Params.ViewTarget)
    {
        CurrentCameraLocation = Params.ViewTarget->GetActorLocation() + CameraOffset;
    }
    bFirstUpdate = true;
}

void UMyCustomCameraNode::UpdateCamera(const FCameraNodeUpdateParams& Params, FCameraNodeUpdateResult& OutResult)
{
    Super::UpdateCamera(Params, OutResult);
    
    if (!Params.ViewTarget)
    {
        return;
    }
    
    // 计算目标位置
    FVector TargetLocation = Params.ViewTarget->GetActorLocation();
    FVector DesiredCameraLocation = TargetLocation + CameraOffset;
    
    // 平滑插值相机位置
    if (bFirstUpdate)
    {
        CurrentCameraLocation = DesiredCameraLocation;
        bFirstUpdate = false;
    }
    else
    {
        float DeltaTime = Params.DeltaTime;
        CurrentCameraLocation = FMath::VInterpTo(
            CurrentCameraLocation, 
            DesiredCameraLocation, 
            DeltaTime, 
            InterpSpeed
        );
    }
    
    // 设置输出结果
    OutResult.ViewLocation = CurrentCameraLocation;
    OutResult.FOV = FieldOfView;
    
    // 计算旋转
    if (bLookAtTarget)
    {
        FRotator LookAtRotation = UKismetMathLibrary::FindLookAtRotation(
            CurrentCameraLocation, 
            TargetLocation
        );
        OutResult.ViewRotation = LookAtRotation;
    }
    else
    {
        OutResult.ViewRotation = Params.ViewTarget->GetActorRotation();
    }
}

void UMyCustomCameraNode::OnDeactivate(const FCameraNodeDeactivationParams& Params)
{
    Super::OnDeactivate(Params);
    
    // 清理资源
    bFirstUpdate = true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 输入系统集成，将输入映射到相机参数 |
| `StateTree` | 状态机驱动相机行为切换 |
| `TemplateSequence` | 过场动画序列支持 |
| `GameplayTags` | 游戏标签系统，用于事件和状态标识 |
| `ControlRig` | 高级骨骼控制（用于角色相机） |

## 维护状态

### 近期更新

```
- e51db9259b53 Cameras: fix crash when opening the Blueprint palette #jira UE-353208
- 2f201434ba01 Cameras: fix Blueprint breakpoints not working on GET/SET parameter nodes
- 2f814ccb5088 Cameras: fix handling of enum parameters in Blueprint setter nodes
```

### 维护评价

**综合评价：活跃开发中，但仍是实验性功能**

- **创建时间**：2020年10月，已有约5年历史
- **最近更新**：近期提交集中在 Blueprint 集成的 bug 修复，说明 Epic 正在积极完善蓝图工作流
- **维护状态**：活跃维护中，持续有功能性更新和 bug 修复
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion: true`，说明 API 可能在未来版本中发生变化
- **已知限制**：
  - 作为实验性功能，API 不稳定，升级引擎版本时可能需要重构
  - 文档相对较少，主要依赖源码和测试用例学习
  - 与传统相机系统的迁移路径不明确

**推荐使用场景**：
- ✅ 新项目，愿意接受实验性 API 的风险
- ✅ 需要高度定制化相机系统的项目
- ✅ 已经使用 StateTree 和 EnhancedInput 的项目
- ❌ 追求稳定性的商业项目（建议等待正式版）
- ❌ 需要长期维护的老项目

**建议**：如果你的项目已经在使用 EnhancedInput 和 StateTree，且愿意承担实验性 API 的风险，GameplayCameras 是一个值得尝试的现代化相机解决方案。否则，建议继续使用传统相机系统，等待 GameplayCameras 正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras/Tests)