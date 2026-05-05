# ContextualAnimation — Runtime 模块

Runtime 模块包含上下文动画系统的所有核心运行时功能，包括场景资产定义、角色绑定、动画选择、Motion Warping 对齐和网络同步。

## 模块信息

- **模块名**: `ContextualAnimation`
- **类型**: Runtime
- **Build.cs**: `Source/ContextualAnimation/ContextualAnimation.Build.cs`

## 源码文件结构

### Public Headers

| 文件 | 核心类型 | 说明 |
|---|---|---|
| `ContextualAnimation.h` | `FContextualAnimationModule` | 模块入口（IModuleInterface） |
| `ContextualAnimTypes.h` | 多种核心类型 | 系统的所有基础数据类型定义 |
| `ContextualAnimSceneAsset.h` | `UContextualAnimSceneAsset`, `UContextualAnimRolesAsset` | 场景资产和角色资产定义 |
| `ContextualAnimSceneActorComponent.h` | `UContextualAnimSceneActorComponent` | 挂载在参与交互的 Actor 上的组件 |
| `ContextualAnimUtilities.h` | `UContextualAnimUtilities` | 蓝图函数库，提供工具函数 |
| `ContextualAnimSelectionCriterion.h` | `UContextualAnimSelectionCriterion` 及子类 | 选择标准基类和内置标准 |
| `ContextualAnimActorInterface.h` | `IContextualAnimActorInterface` | Actor 接口（提供 GetMesh） |
| `AnimNotifyState_EarlyOutContextualAnimWindow.h` | `UAnimNotifyState_EarlyOutContextualAnimWindow` | 允许提前退出的动画通知 |
| `AnimNotifyState_IKWindow.h` | `UAnimNotifyState_IKWindow` | 控制 IK 启用区间的动画通知 |

## 核心类型详解（ContextualAnimTypes.h）

这是系统中最重要的头文件，定义了所有基础数据结构：

### FContextualAnimRoleDefinition

角色定义，描述参与交互的角色类型：

```cpp
struct FContextualAnimRoleDefinition
{
    FName Name;                    // 角色名称（如 "Attacker"、"Victim"）
    bool bIsCharacter;             // 是否为角色（影响预览 Capsule 显示）
    float PreviewCapsuleHalfHeight;// 预览用 Capsule 半高
    float PreviewCapsuleRadius;    // 预览用 Capsule 半径
    FTransform MeshToComponent;    // Mesh 到 Component 的变换偏移
};
```

### FContextualAnimTrack

动画轨道，描述一个角色在某个 AnimSet 中的动画数据：

```cpp
struct FContextualAnimTrack
{
    UAnimSequenceBase* Animation;     // 动画资产（通常是 UAnimMontage）
    float AnimMaxStartTime;           // 动画最大开始时间（用于延迟开始）
    bool bChangeMovementMode;         // 是否在播放期间切换移动模式
    EMovementMode MovementMode;       // 切换到的移动模式
    bool bControlCharacterRotation;   // 是否控制角色旋转（禁用自动朝向）
    bool bOptional;                   // 该角色是否可选
    FName Role;                       // 角色名称
    int32 SectionIdx;                 // 所属区段索引
    int32 AnimSetIdx;                 // 所属动画集合索引
    int32 AnimTrackIdx;               // 在 AnimSet 中的轨道索引
    FTransform MeshToScene;           // Mesh 到场景空间的变换
    TArray<UContextualAnimSelectionCriterion*> SelectionCriteria; // 选择标准
    FContextualAnimAlignmentTrackContainer AlignmentData;        // 对齐数据（预计算）
    FContextualAnimAlignmentTrackContainer IKTargetData;         // IK 目标数据（预计算）
};
```

### FContextualAnimSceneBindingContext

绑定上下文，封装一个 Actor 参与交互时需要的所有信息：

```cpp
struct FContextualAnimSceneBindingContext
{
    AActor* Actor;                           // 参与的 Actor
    TOptional<FTransform> ExternalTransform; // 外部变换覆盖
    TOptional<FVector> ExternalVelocity;     // 外部速度覆盖
    FGameplayTagContainer ExternalGameplayTags; // 外部 Gameplay Tags
    
    // 缓存的组件引用
    UAnimInstance* GetAnimInstance() const;
    USkeletalMeshComponent* GetSkeletalMeshComponent() const;
    UContextualAnimSceneActorComponent* GetSceneActorComponent() const;
    UCharacterMovementComponent* GetCharacterMovementComponent() const;
    UMotionWarpingComponent* GetMotionWarpingComponent() const;
};
```

### FContextualAnimSceneBinding

将一个 Actor（通过 BindingContext）绑定到一个 AnimTrack：

```cpp
struct FContextualAnimSceneBinding
{
    FContextualAnimSceneBindingContext Context; // Actor 上下文
    int32 AnimTrackIdx;                        // 绑定的动画轨道索引
    
    // 便捷访问
    AActor* GetActor() const;
    FTransform GetTransform() const;
    float GetAnimMontageTime() const;
    FName GetCurrentSection() const;
    FAnimMontageInstance* GetAnimMontageInstance() const;
};
```

### FContextualAnimSceneBindings

一次交互的所有绑定集合，核心运行时结构：

```cpp
struct FContextualAnimSceneBindings
{
    const UContextualAnimSceneAsset* SceneAsset;
    int32 SectionIdx;
    int32 AnimSetIdx;
    TArray<FContextualAnimSceneBinding> Data;
    
    // 静态工厂方法
    static bool TryCreateBindings(/* 多种重载 */);
    static int32 FindAnimSet(/* 查找最佳 AnimSet */);
    
    // 运行时操作
    bool BindActorToRole(AActor& Actor, FName Role);
    void CalculateWarpPoints(TArray<FContextualAnimWarpPoint>& OutWarpPoints) const;
    bool SetRoleWarpTarget(FName Role, FName WarpTargetName, const FTransform& Transform);
    bool RemoveActor(AActor& Actor);
    void TransitionTo(int32 NewSectionIdx, int32 NewAnimSetIdx);
    
    // 查询
    const FContextualAnimSceneBinding* FindBindingByActor(const AActor* Actor) const;
    const FContextualAnimSceneBinding* FindBindingByRole(const FName& Role) const;
    const FContextualAnimSceneBinding* GetPrimaryBinding() const;
    const FContextualAnimSceneBinding* GetSyncLeader() const;
    bool ShouldSyncAnimation() const;
};
```

### Warp Point 类型

```cpp
enum class EContextualAnimWarpPointDefinitionMode : uint8
{
    PrimaryActor, // 使用主角色的变换
    Socket,       // 使用主角色某个 Socket 的变换
    Custom        // 基于自定义规则计算
};

struct FContextualAnimWarpPointDefinition
{
    FName WarpTargetName;           // 对应的 Warping Window 名称
    EContextualAnimWarpPointDefinitionMode Mode;
    FName SocketName;               // Socket 模式下使用
    FContextualAnimWarpPointCustomParams Params; // Custom 模式下使用
};
```

### IK Target 类型

```cpp
// IK 目标提供方式
enum class EContextualAnimIKTargetProvider : uint8
{
    Autogenerated, // 从动画自动生成
    Bone,          // 由动画中的骨骼/Socket 定义
};

// IK Alpha 控制方式
enum class EContextualAnimIKTargetAlphaProvider : uint8
{
    AnimNotifyState, // 由 IK Window 通知控制
    Curve,           // 由动画曲线控制
    None,            // 始终为 1
};

struct FContextualAnimIKTarget
{
    FName GoalName;    // IK 目标名称
    FName BoneName;    // 关联骨骼
    float Alpha;       // 混合权重
    FTransform Transform; // 世界空间变换
};
```

## SceneAsset（ContextualAnimSceneAsset.h）

### 层级结构

```
UContextualAnimSceneAsset
├── RolesAsset: UContextualAnimRolesAsset
│   └── Roles: TArray<FContextualAnimRoleDefinition>
├── PrimaryRole: FName                    // 主角色名称
├── Sections: TArray<FContextualAnimSceneSection>
│   ├── Section[0]
│   │   ├── Name: FName
│   │   ├── bSyncAnimations: bool
│   │   ├── WarpPointDefinitions: TArray<FContextualAnimWarpPointDefinition>
│   │   └── AnimSets: TArray<FContextualAnimSet>
│   │       ├── AnimSet[0]
│   │       │   ├── Tracks: TArray<FContextualAnimTrack>
│   │       │   ├── WarpPoints: TMap<FName, FTransform>
│   │       │   ├── Name: FName
│   │       │   └── RandomWeight: float
│   │       └── AnimSet[1] ...
│   └── Section[1] ...
├── Radius: float                         // 交互半径
├── CollisionBehavior: EContextualAnimCollisionBehavior
├── AttachmentParams: TArray<FContextualAnimAttachmentParams>
├── IKTargetParams: FContextualAnimIKTargetParams
├── bPrecomputeAlignmentTracks: bool      // 是否预计算对齐轨道
├── SampleRate: int32                     // 采样率（默认 15 fps）
└── bIgnoreClientMovementErrorChecksAndCorrection: bool
```

### 关键函数

```cpp
// 查询动画
UAnimSequenceBase* BP_FindAnimationForRole(int32 SectionIdx, int32 AnimSetIdx, FName Role) const;
const FContextualAnimTrack* FindAnimTrackByAnimation(const UAnimSequenceBase* Animation) const;

// 获取对齐变换
FTransform GetAlignmentTransform(int32 SectionIdx, int32 AnimSetIdx, int32 AnimTrackIdx, 
    const FName& WarpPointName, float Time) const;
FTransform GetAlignmentTransformForRoleRelativeToOtherRole(int32 SectionIdx, int32 AnimSetIdx,
    FName Role, FName OtherRole, float Time) const;

// 获取对齐点
void GetAlignmentPointsForSecondaryRole(EContextualAnimPointType Type, int32 SectionIdx,
    const FContextualAnimSceneBindingContext& Primary, TArray<FContextualAnimPoint>& OutResult) const;

// 查找最佳动画
const FContextualAnimTrack* FindAnimTrackForRoleWithClosestEntryLocation(int32 SectionIdx,
    const FName& Role, const FContextualAnimSceneBindingContext& Primary, const FVector& TestLocation) const;

// 预计算
void PrecomputeData(); // 生成对齐轨道和 IK 目标轨道
```

## SceneActorComponent（ContextualAnimSceneActorComponent.h）

### 组件职责

`UContextualAnimSceneActorComponent` 是挂载在每个参与交互的 Actor 上的组件，负责：

1. **动画播放**：管理 Montage 的播放、混合和同步
2. **Motion Warping**：设置/更新 Warp Targets 以实现位移对齐
3. **IK 目标**：每帧更新 IK 目标并通过 `IIKGoalCreatorInterface` 提供给 IKRig
4. **碰撞管理**：交互期间禁用参与者之间的碰撞
5. **移动模式管理**：交互期间控制角色移动模式和旋转
6. **网络同步**：通过 Replicated 属性在多人游戏中同步交互状态

### 网络同步结构

```cpp
struct FContextualAnimRepBindingsData : FContextualAnimRepData
{
    FContextualAnimSceneBindings Bindings;
    TArray<FContextualAnimWarpPoint> WarpPoints;
    TArray<FContextualAnimWarpTarget> ExternalWarpTargets;
};

struct FContextualAnimRepLateJoinData : FContextualAnimRepData
{
    TWeakObjectPtr<AActor> Actor;
    FName Role;
    TArray<FContextualAnimWarpPoint> WarpPoints;
    TArray<FContextualAnimWarpTarget> ExternalWarpTargets;
};

struct FContextualAnimRepTransitionData : FContextualAnimRepData
{
    uint8 Id;
    uint8 SectionIdx;
    uint8 AnimSetIdx;
    bool bStopEveryone;
    TArray<FContextualAnimWarpPoint> WarpPoints;
    TArray<FContextualAnimWarpTarget> ExternalWarpTargets;
};
```

### 调试

```cpp
// 控制台变量（仅非 Shipping/Test 构建）
a.ContextualAnim.IK.Debug          // 0/1 - 绘制 IK 目标调试信息
a.ContextualAnim.IK.DrawDebugLifetime // 调试绘制持续时间
```

## SelectionCriterion（ContextualAnimSelectionCriterion.h）

### 内置标准详解

**UContextualAnimSelectionCriterion_Cone（锥形标准）**

基于角度和方向的判断：

```cpp
enum class EContextualAnimCriterionConeMode : uint8
{
    ToPrimary,    // 从 Querier 到 Primary 的方向 vs Querier 的前方
    FromPrimary   // 从 Primary 到 Querier 的方向 vs Primary 的前方
};

// 参数
float Distance = 200.f;  // 最大距离
float HalfAngle = 45.f;  // 半角（0-180）
float Offset = 0.f;      // 角度偏移（-180 到 180）
```

**UContextualAnimSelectionCriterion_Distance（距离标准）**

```cpp
enum class EContextualAnimCriterionDistanceMode : uint8
{
    Distance_3D, // 3D 距离
    Distance_2D  // 2D 距离（忽略 Z 轴）
};

float MinDistance = 0.f;
float MaxDistance = 0.f;
```

**UContextualAnimSelectionCriterion_TriggerArea（触发区域标准）**

```cpp
TArray<FVector> PolygonPoints; // 多边形顶点
float Height = 100.f;          // 区域高度
```

**UContextualAnimSelectionCriterion_Blueprint（蓝图标准）**

蓝图可实现的自定义标准，通过 `BP_DoesQuerierPassCondition` 事件实现判断逻辑。

## AnimNotifyState

### UAnimNotifyState_IKWindow

在动画时间轴上定义 IK 启用区间：

- **GoalName**: IK 目标名称（与 FContextualAnimIKTargetDefinition 中的 GoalName 对应）
- **BlendIn**: 混合进入参数（FAlphaBlend）
- **BlendOut**: 混合退出参数（FAlphaBlend）
- **GetIKAlphaValue** (static): 在给定时间获取 IK Alpha 值

### UAnimNotifyState_EarlyOutContextualAnimWindow

在动画末尾定义提前退出窗口：

- **bStopEveryone**: 是否强制所有参与者都退出交互
- 通常放在动画末尾，提升玩家操作的响应性
