```markdown
# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、形状库） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-14 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是 UE5 的核心动画绑定框架，提供了一个完整的、基于节点图（RigVM）的程序化动画系统。它解决的核心问题是：**在运行时或编辑器中，通过可交互的控制点（Controls）驱动骨骼、变换和动画数据**。

与传统的关键帧动画不同，ControlRig 允许动画师创建逻辑驱动的动画系统——包括 IK/FK 求解器、物理模拟、程序化运动等——并通过直观的控制柄（Gizmo）在视口中实时交互。

ControlRig 同时支持**独立绑定（Standalone Rig）**、**模块化绑定（Modular Rig）** 和**绑定模块（Rig Module）**三种模式。模块化绑定系统允许将一个完整的绑定拆分为多个可复用的模块（如臂、腿、脊柱），通过连接器（Connector）拼接组合，极大提升了大型角色绑定的复用性和维护效率。

此外，ControlRig 深度集成于 Sequencer，支持在动画序列中对控制参数进行关键帧动画，是 UE5 动画层（Animation Layer）工作流的基础。

## 使用场景

- 你需要为角色创建 IK/FK 切换的手臂绑定 → 使用 ControlRig 的 IK 求解器节点
- 你需要程序化动画（如呼吸、尾巴摆动） → 在 ControlRig 节点图中组合数学和层级节点
- 你需要一个可复用的模块化骨架系统 → 使用 Modular Rig 将绑定拆分为臂/腿/脊柱等模块
- 你需要在 Sequencer 中对绑定控制参数做关键帧 → 使用 ControlRigComponent 或 ControlRig 动画层
- 你需要运行时动态修改角色姿态 → 通过 ControlRigComponent 在游戏线程中驱动绑定
- 你需要将绑定动画输出应用到非骨骼组件 → 使用 ControlRigComponent 的映射系统

## 蓝图用法

### 核心节点 — 控制值读写

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Control Float` | 获取 Float 类型控制的当前值、最小值、最大值 | `FRigUnit_GetControlFloat` |
| `Get Control Transform` | 获取 Transform 类型控制的变换（支持局部/全局空间） | `FRigUnit_GetControlTransform` |
| `Get Control Vector` | 获取 Vector 类型控制的值（用于 Position/Scale 控制） | `FRigUnit_GetControlVector` |
| `Get Control Rotator` | 获取 Rotator 类型控制的旋转值 | `FRigUnit_GetControlRotator` |
| `Get Control Bool` | 获取 Bool 类型控制的值 | `FRigUnit_GetControlBool` |
| `Get Control Integer` | 获取 Integer/Enum 类型控制的值 | `FRigUnit_GetControlInteger` |
| `Set Control Float` | 设置 Float 类型控制的值，支持权重混合 | `FRigUnit_SetControlFloat` |
| `Set Control Transform` | 设置 Transform 类型控制的值 | `FRigUnit_SetControlTransform` |
| `Set Control Vector` | 设置 Vector 类型控制的值 | `FRigUnit_SetControlVector` |
| `Set Control Rotator` | 设置 Rotator 类型控制的值 | `FRigUnit_SetControlRotator` |
| `Set Multiple Controls Float` | 批量设置多个 Float 控制 | `FRigUnit_SetMultiControlFloat` |

### 核心节点 — 层级操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Parent` | 获取元素的父级 | `FRigUnit_HierarchyGetParent` |
| `Get Parents` | 获取元素的所有父级链 | `FRigUnit_HierarchyGetParentsItemArray` |
| `Get Children` | 获取元素的子元素列表 | `FRigUnit_HierarchyGetChildrenItemArray` |
| `Get Transform` | 获取元素的局部/全局变换 | `FRigUnit_HierarchyGetTransform` |
| `Set Transform` | 设置元素的变换 | `FRigUnit_HierarchySetTransform` |
| `Pose Cache` / `Use Pose Cache` | 保存和恢复骨架姿态缓存 | `FRigUnit_HierarchyCreatePoseItemArray` |

### 核心节点 — 动态层级（Construction Event）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Null` | 在 Construction Event 中创建 Null 元素 | `FRigUnit_HierarchyAddNull` |
| `Spawn Control` | 在 Construction Event 中创建控制 | `FRigUnit_HierarchyAddControl*` |
| `Spawn Socket` | 在 Construction Event 中创建 Socket | `FRigUnit_HierarchyAddSocket` |
| `Create Parent Relationship` | 动态添加父子关系 | `FRigUnit_AddParent` |
| `Switch Parent` | 切换元素的父级（空间切换） | `FRigUnit_SwitchParent` |

### 核心节点 — 动画通道

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Float Channel` | 获取动画通道的值 | `FRigUnit_GetFloatAnimationChannel` |
| `Set Float Channel` | 设置动画通道的值 | `FRigUnit_SetFloatAnimationChannel` |
| `Get Transform Channel` | 获取变换类型动画通道 | `FRigUnit_GetTransformAnimationChannel` |

### 核心节点 — 模块化绑定

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Connection` | 解析连接器，获取连接的目标 | `FRigUnit_ResolveConnector` |
| `Get Module Name` | 获取当前模块实例名称 | `FRigUnit_GetModuleName` |
| `Is In Current Module` | 判断元素是否属于当前模块 | `FRigUnit_IsItemInCurrentModule` |
| `Get Items In Module` | 获取当前模块中的所有元素 | `FRigUnit_GetItemsInModule` |

### 核心节点 — 碰撞检测

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sphere Trace By Trace Channel` | 球体扫描检测（按 Trace Channel） | `FRigUnit_SphereTraceByTraceChannel` |
| `Line Trace By Trace Channel` | 射线检测（按 Trace Channel） | `FRigUnit_LineTraceByTraceChannel` |
| `Sphere Trace By Profile` | 球体扫描检测（按碰撞配置） | `FRigUnit_SphereTraceByProfile` |

### ControlRigComponent — Actor 级集成

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get ControlRig` | 获取组件托管的 ControlRig 实例 | `UControlRigComponent` |
| `Initialize` | 初始化绑定并触发 Construction Event | `UControlRigComponent` |
| `Update` | 执行一帧的绑定求解 | `UControlRigComponent` |
| `Set Mapped Elements` | 替换组件的映射元素列表 | `UControlRigComponent` |
| `Add Mapped Complete Skeletal Mesh` | 将骨骼网格的所有匹配骨骼添加为映射 | `UControlRigComponent` |

### 使用示例（蓝图描述）

**读取控制值并驱动网格变形：**
1. 创建一个 Actor，添加 `ControlRigComponent`
2. 在 `ControlRigAssetReference` 中设置你的 ControlRig 资产
3. 在 `OnPostInitialize` 事件中，使用 `Add Mapped Complete Skeletal Mesh` 将骨骼网格组件映射到绑定
4. 在 `Tick` 中调用 `Update(DeltaTime)` 驱动绑定求解
5. 组件会自动将绑定输出映射回骨骼网格组件

**在 ControlRig 节点图中创建 IK：**
1. 使用 `Get Transform` 获取手部骨骼当前变换
2. 将其连接到 Two Bone IK 求解器的 `Effector` 输入
3. 使用 `Set Transform` 将求解结果写回骨骼
4. 在 Construction Event 中使用 `Spawn Control` 创建控制柄
5. 用控制柄值驱动 IK 目标位置

## C++ 用法

### 头文件引入

```cpp
#include "ControlRig.h"
#include "ControlRigComponent.h"
#include "Rigs/RigHierarchy.h"
#include "Rigs/RigHierarchyController.h"
#include "Units/Execution/RigUnit_Hierarchy.h"
```

### 基本用法 — 运行时操控 ControlRig

```cpp
// 创建并初始化一个 ControlRig 实例（来源：ControlRig.h）
UControlRig* ControlRig = NewObject<UControlRig>(Outer, ControlRigClass);
ControlRig->Initialize();

// 执行绑定求解
ControlRig->Evaluate_AnyThread();

// 设置控制值
ControlRig->SetControlValue<float>(FName("MyFloatControl"), 0.5f);

// 读取控制值
FRigControlValue Value = ControlRig->GetControlValue(FName("MyFloatControl"));

// 获取绑定的层级结构
URigHierarchy* Hierarchy = ControlRig->GetHierarchy();
```

### 基本用法 — 层级遍历与变换操作

```cpp
// 获取元素变换（来源：RigHierarchy.h）
URigHierarchy* Hierarchy = ControlRig->GetHierarchy();
FRigElementKey BoneKey(FName("spine_01"), ERigElementType::Bone);

// 获取全局变换
FTransform GlobalTransform = Hierarchy->GetGlobalTransform(BoneKey);

// 获取局部变换
FTransform LocalTransform = Hierarchy->GetLocalTransform(BoneKey);

// 设置变换
FTransform NewTransform = FTransform(FRotator(0, 45, 0), FVector(0, 0, 100));
Hierarchy->SetGlobalTransform(BoneKey, NewTransform, /*bNotify=*/true);

// 获取元素的子元素
TArray<FRigElementKey> Children;
if (FRigBaseElement* Element = Hierarchy->Find(BoneKey))
{
    for (int32 ChildIndex : Hierarchy->GetChildren(Element))
    {
        FRigBaseElement* Child = Hierarchy->Get(ChildIndex);
        Children.Add(Child->GetKey());
    }
}
```

### 基本用法 — 控制器创建元素

```cpp
// 使用层级控制器动态创建元素（来源：RigHierarchyController.h）
URigHierarchyController* Controller = NewObject<URigHierarchyController>();
Controller->SetHierarchy(Hierarchy);

// 添加骨骼
FRigElementKey BoneKey = Controller->AddBone(
    FName("new_bone"),                       // 名称
    FRigElementKey(FName("root"), ERigElementType::Bone), // 父级
    FTransform(FVector(0, 0, 100)),          // 变换
    true,                                    // 全局空间
    ERigBoneType::User,                      // 用户定义骨骼
    true                                     // 记录撤销
);

// 添加 Null
FRigElementKey NullKey = Controller->AddNull(
    FName("my_null"),
    BoneKey,
    FTransform::Identity,
    true
);

// 添加控制（需要完整的控制设置）
FRigControlSettings Settings;
Settings.ControlType = ERigControlType::Float;
Settings.AnimationType = ERigControlAnimationType::AnimationControl;
Settings.bAnimatable = true;

FRigControlValue DefaultValue;
DefaultValue.Set<float>(0.5f);

FRigElementKey ControlKey = Controller->AddControl(
    FName("my_float_control"),
    BoneKey,
    Settings,
    DefaultValue
);

// 选择元素
Controller->SelectElement(ControlKey, true, false, true);
```

### 进阶用法 — ControlRigComponent 运行时映射

```cpp
// 设置 ControlRigComponent 的映射（来源：ControlRigComponent.h）
void SetupControlRigMappings(UControlRigComponent* CRComp, USkeletalMeshComponent* SkelMesh)
{
    // 添加完整的骨骼网格映射（输出方向：绑定 → 骨骼网格）
    CRComp->AddMappedCompleteSkeletalMesh(
        SkelMesh,
        EControlRigComponentMapDirection::Output
    );

    // 或者手动添加单个映射元素
    FControlRigComponentMappedElement MappedElement;
    MappedElement.ComponentReference = FSoftComponentReference(SkelMesh);
    MappedElement.TransformName = FName("spine_01");
    MappedElement.ElementType = ERigElementType::Bone;
    MappedElement.ElementName = FName("spine_01");
    MappedElement.Direction = EControlRigComponentMapDirection::Output;
    MappedElement.Space = EControlRigComponentSpace::WorldSpace;
    MappedElement.Weight = 1.0f;
    
    TArray<FControlRigComponentMappedElement> Elements;
    Elements.Add(MappedElement);
    CRComp->SetMappedElements(Elements);
}

// 绑定生命周期事件
void BindEvents(UControlRigComponent* CRComp)
{
    CRComp->OnPostInitializeDelegate.AddDynamic(this, &AMyActor::OnRigInitialized);
    CRComp->OnPostForwardsSolveDelegate.AddDynamic(this, &AMyActor::OnRigSolved);
}

// 每帧驱动
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    ControlRigComponent->Update(DeltaTime);
}
```

### 进阶用法 — ModularRig 模块化绑定操作

```cpp
// 操作模块化绑定（来源：ModularRig.h, ModularRigController.h）
UModularRig* ModularRig = Cast<UModularRig>(ControlRig);
if (ModularRig)
{
    // 获取所有模块名称
    TArray<FName> ModuleNames = ModularRig->GetModuleNames();
    
    // 获取指定模块的 ControlRig 实例
    UControlRig* ModuleRig = ModularRig->GetModuleRigByName(FName("Arm_L"));
    
    // 获取模块的父模块名称
    FName ParentName = ModularRig->GetParentModuleName(FName("Arm_L"));
    
    // 在所有模块上执行事件
    TArray<FName> ExecutedModules = ModularRig->ExecuteEventOnAllModules(FName("ForwardsSolve"));
    
    // 遍历所有模块
    ModularRig->ForEachModule([](FRigModuleInstance* Module) -> bool
    {
        UControlRig* Rig = Module->GetRig();
        if (Rig)
        {
            // 处理每个模块的 Rig
        }
        return true; // 继续遍历
    });
}
```

## Demo 示例

### 运行时创建并驱动 ControlRig 的最小示例

```cpp
// MyRigActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyRigActor.generated.h"

class UControlRigComponent;
class USkeletalMeshComponent;

UCLASS()
class AMyRigActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRigActor();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> MeshComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UControlRigComponent> ControlRigComponent;

    UPROPERTY(EditAnywhere, Category = "Rig")
    float SpinSpeed = 30.0f;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UFUNCTION()
    void OnRigPostInitialize(UControlRigComponent* Component);

    UFUNCTION()
    void OnRigPostForwardsSolve(UControlRigComponent* Component);

private:
    float CurrentAngle = 0.0f;
};
```

```cpp
// MyRigActor.cpp
#include "MyRigActor.h"
#include "ControlRigComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "ControlRig.h"
#include "Rigs/RigHierarchy.h"

AMyRigActor::AMyRigActor()
{
    PrimaryActorTick.bCanEverTick = true;

    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    ControlRigComponent = CreateDefaultSubobject<UControlRigComponent>(TEXT("ControlRig"));
    ControlRigComponent->SetupAttachment(RootComponent);
}

void AMyRigActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定生命周期事件
    ControlRigComponent->OnPostInitializeDelegate.AddDynamic(
        this, &AMyRigActor::OnRigPostInitialize);
    ControlRigComponent->OnPostForwardsSolveDelegate.AddDynamic(
        this, &AMyRigActor::OnRigPostForwardsSolve);

    // 添加骨骼网格映射（绑定输出驱动骨骼网格）
    if (MeshComponent && MeshComponent->GetSkeletalMeshAsset())
    {
        ControlRigComponent->AddMappedCompleteSkeletalMesh(
            MeshComponent,
            EControlRigComponentMapDirection::Output);
    }
}

void AMyRigActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 累积角度
    CurrentAngle += SpinSpeed * DeltaTime;

    // 更新 ControlRig 组件（触发求解）
    ControlRigComponent->Update(DeltaTime);
}

void AMyRigActor::OnRigPostInitialize(UControlRigComponent* Component)
{
    // 绑定初始化后，可以安全访问 ControlRig
    if (UControlRig* Rig = Component->GetControlRig())
    {
        UE_LOG(LogTemp, Log, TEXT("ControlRig initialized: %s"),
            *Rig->GetName());
    }
}

void AMyRigActor::OnRigPostForwardsSolve(UControlRigComponent* Component)
{
    // 每次求解完成后，可以读取结果
    if (UControlRig* Rig = Component->GetControlRig())
    {
        URigHierarchy* Hierarchy = Rig->GetHierarchy();
        if (Hierarchy)
        {
            // 示例：读取根骨骼的全局变换
            FRigElementKey RootKey(FName("root"), ERigElementType::Bone);
            if (Hierarchy->Find(RootKey))
            {
                FTransform RootTransform = Hierarchy->GetGlobalTransform(RootKey);
                // 可在此对变换结果做额外处理
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigVM` | ControlRig 底层虚拟机，执行节点图逻辑 |
| `LevelSequence` | Sequencer 集成，支持在动画序列中关键帧化控制参数 |
| `Constraints` | 约束系统集成，用于创建可变换的控制柄句柄 |
| `AnimationCore` | 动画核心库（IK/FK 等算法基础） |
| `AnimationBlueprintLibrary` | 动画蓝图工具库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7fc008ea` | AutoBake: Fix crash with using Shim track editor, need to get real one in order to cast to shared po | 修复 AutoBake 使用 Shim 轨道编辑器时的崩溃问题 |
| 2026-05-26 | `0f35dc86` | Animating in Engine: Marquee selection in Animation Mode picks controls by pivot in addition to mesh | 动画模式下框选控制时，除网格体外还通过枢轴点拾取控制 |
| 2026-05-22 | `c09576c8` | Control Rig: Fix older rigs not creating gizmos when controls are selected | 修复旧版绑定在选择控制时不创建 Gizmo 的问题 |
| 2026-05-22 | `4eed6d63` | Control Rig: Guard against invalid instance proxy. | 增加对无效实例代理的防护检查 |
| 2026-05-20 | `818e65b0` | Control Rig Nullptr check for static analyzer | 为静态分析器添加空指针检查 |

### 维护评价

**活跃维护。** ControlRig 是 Epic 的旗舰动画系统之一，持续获得高频更新。最近的提交（2026年5月）涵盖了 bug 修复、编辑器交互改进和健壮性增强。

- **年龄**：约 4 年（从实验性迁移到正式目录），但其前身在 Experimental 中存在更久
- **更新频率**：极高，几乎每周都有提交
- **活跃度**：Epic 核心开发团队持续维护，是 UE5 动画管线的关键组件
- **稳定性**：作为默认启用的正式插件，已达到生产级稳定
- **推荐度**：⭐⭐⭐⭐⭐ 强烈推荐。这是 UE5 中创建程序化动画和运行时绑定系统的标准方案，深度集成于 Sequencer、动画蓝图和动画层工作流中

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-in-unreal-engine)
```