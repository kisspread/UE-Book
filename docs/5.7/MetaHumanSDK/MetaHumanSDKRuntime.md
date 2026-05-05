# MetaHuman SDK Runtime

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、本地化资源） |
| 模块 | `MetaHumanSDKRuntime` (Runtime), `MetaHumanSDKEditor` (Editor), `InterchangeDNA` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK) | |

## 用途

MetaHumanSDKRuntime 是 MetaHuman SDK 插件的运行时模块，负责在运行时驱动 MetaHuman 角色的身体和面部动画。核心功能是通过 `UMetaHumanComponentUE` 组件自动配置 MetaHuman 角色的骨骼网格体组件——包括设置后处理动画蓝图（Post-Process AnimBP）、Control Rig、物理资产以及 LOD 阈值。

该模块解决的核心问题：MetaHuman 角色由多个骨骼网格体组成（Face、Body、Torso、Legs、Feet），每个部分需要独立的动画处理管道（Rig Logic 面部动画、身体 Control Rig、物理模拟等）。手动配置这些组件非常繁琐且容易出错。MetaHumanSDKRuntime 通过一个组件自动完成所有配置，确保面部动画（Rig Logic）、身体校正（Body Correctives）、颈部校正（Neck Correctives）、Control Rig 和物理模拟在正确的 LOD 级别上正确运行。

## 使用场景

- 你导入了一个 MetaHuman 角色并希望在运行时正确驱动其面部和身体动画 → 在 Actor 上添加 `UMetaHumanComponentUE` 组件
- 你需要为 MetaHuman 的身体部位（Torso/Legs/Feet）配置自定义 Control Rig 或物理资产 → 通过组件的 BodyParts 属性配置
- 你需要根据 LOD 级别优化 MetaHuman 的动画性能 → 通过组件的 LOD Threshold 属性控制各部分的 LOD 剔除

## 蓝图用法

`UMetaHumanComponentUE` 标记为 `BlueprintSpawnableComponent`，可在蓝图中作为组件添加到任何 Actor。

### 核心配置属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `BodyComponentName` | 身体骨骼网格体组件的名称（默认 "Body"） | `UMetaHumanComponentBase` |
| `FaceComponentName` | 面部骨骼网格体组件的名称（默认 "Face"） | `UMetaHumanComponentBase` |
| `BodyType` | MetaHuman 身体类型枚举 | `UMetaHumanComponentBase` |
| `bEnableBodyCorrectives` | 启用身体程序化 Control Rig 和姿态驱动器 | `UMetaHumanComponentBase` |
| `RigLogicLODThreshold` | Rig Logic 面部动画的 LOD 阈值（-1 为始终评估） | `UMetaHumanComponentBase` |
| `bEnableNeckCorrectives` | 启用颈部校正 | `UMetaHumanComponentBase` |
| `NeckCorrectivesLODThreshold` | 颈部校正的 LOD 阈值 | `UMetaHumanComponentBase` |
| `bEnableNeckProcControlRig` | 启用颈部程序化 Control Rig | `UMetaHumanComponentBase` |
| `NeckProcControlRigLODThreshold` | 颈部程序化 Control Rig 的 LOD 阈值 | `UMetaHumanComponentBase` |
| `Torso` / `Legs` / `Feet` | 身体部位的可自定义配置（Control Rig + 物理资产 + LOD 阈值） | `UMetaHumanComponentBase` |
| `PostProcessAnimBP` | 身体部位的后处理动画蓝图（如 ABP_Clothing_PostProcess） | `UMetaHumanComponentUE` |

### 使用示例（蓝图描述）

1. 在 MetaHuman Actor 上添加 `MetaHuman Component`（即 `UMetaHumanComponentUE`）
2. 在 Details 面板中，Face 分类下设置 `Facial Animation LOD Threshold`（如设为 2 表示 LOD 0-2 评估 Rig Logic）
3. 在 Body 分类下可启用/禁用 `Body Correctives`
4. 在 BodyParts 分类下，为 Torso/Legs/Feet 分别指定自定义 Control Rig 类和物理资产
5. 指定 `PostProcessAnimBP` 为 MetaHuman 附带的 `ABP_Clothing_PostProcess`

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanComponentUE.h"
#include "MetaHumanComponentBase.h"
#include "MetaHumanBodyType.h"
#include "MetaHumanTypes.h"
```

### 基本用法

Runtime 模块主要通过组件驱动，C++ 中直接使用较少。以下展示如何在 C++ 中访问组件属性：

```cpp
// 获取 Actor 上的 MetaHuman 组件
UMetaHumanComponentUE* MetaHumanComp = MyActor->FindComponentByClass<UMetaHumanComponentUE>();
if (MetaHumanComp)
{
    // 组件在 BeginPlay 时自动配置所有身体部位
    // 无需手动调用，组件会自动：
    // 1. 为 Torso/Legs/Feet 设置后处理 AnimBP 或 Leader-Follower 姿态
    // 2. 将 LOD 阈值和 Control Rig 配置注入到 AnimBP 变量中
    // 3. 为面部设置 Rig Logic LOD 阈值和颈部校正参数
}
```

### 进阶用法

`UMetaHumanComponentBase` 提供了受保护的工具方法，可用于派生自定义组件：

```cpp
// 自定义 MetaHuman 组件（继承 UMetaHumanComponentBase）
class UMyMetaHumanComponent : public UMetaHumanComponentBase
{
    GENERATED_BODY()

protected:
    virtual void PostInitAnimBP(USkeletalMeshComponent* SkelMeshComponent, 
                                 UAnimInstance* AnimInstance) const override
    {
        Super::PostInitAnimBP(SkelMeshComponent, AnimInstance);
        
        // 自定义 AnimBP 变量注入
        MetaHumanComponentHelpers::ConnectVariable<FIntProperty, int32>(
            AnimInstance, TEXT("MyCustomVariable"), 42);
    }
};
```

`MetaHumanComponentHelpers` 命名空间提供两个工具模板函数：
- `ConnectVariable<PropertyBPType, PropertyVarType>()` — 通过反射将值注入 AnimBP 的蓝图属性
- `GetPropertyValue<T>()` — 通过反射从 UObject 上按名称读取属性值

## Demo 示例

### 最小可编译示例

```cpp
// MyMetaHumanActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMetaHumanActor.generated.h"

class UMetaHumanComponentUE;
class USkeletalMeshComponent;

UCLASS()
class AMyMetaHumanActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanActor();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> BodyComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> FaceComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UMetaHumanComponentUE> MetaHumanComponent;
};
```

```cpp
// MyMetaHumanActor.cpp
#include "MyMetaHumanActor.h"
#include "MetaHumanComponentUE.h"
#include "Components/SkeletalMeshComponent.h"

AMyMetaHumanActor::AMyMetaHumanActor()
{
    BodyComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Body"));
    RootComponent = BodyComponent;

    FaceComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Face"));
    FaceComponent->SetupAttachment(BodyComponent);

    MetaHumanComponent = CreateDefaultSubobject<UMetaHumanComponentUE>(TEXT("MetaHumanComponent"));
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "MetaHumanSDKRuntime" });
```

## 模块依赖

MetaHumanSDKRuntime 的 Build.cs 依赖如下：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库（公共依赖） |
| `CoreUObject` | UObject 反射系统 |
| `Engine` | 引擎核心（SkeletalMesh、AnimInstance 等） |
| `Slate` / `SlateCore` | UI 框架（可能用于编辑器预览相关） |
| `AnimationCore` | 动画核心数学和工具 |
| `AnimGraphRuntime` | 动画图运行时（AnimBP 执行） |
| `ControlRig` | Control Rig 框架（程序化动画） |
| `RigVM` | Control Rig 的虚拟机 |

**插件级依赖**（来自 .uplugin）：ControlRig、RigLogic、HairStrands

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-10 | `9585d26c` | Add warnings when verifying MetaHuman packages that contain VT textures or Substrate materials | 为包含虚拟纹理或 Substrate 材质的 MetaHuman 包添加验证警告 |
| 2025-10-03 | `15c2d59e` | Detect engine feature usage that may not be compatible with end-user project settings | 检测与用户项目设置不兼容的引擎特性（Substrate 材质、VT 纹理） |
| 2025-10-01 | `b35afec6` | Fix for Arabic localization issues | 修复阿拉伯语本地化问题 |

### 维护评价

- **创建时间**：2025-04-22，是一个较新的模块（约 1 年）
- **最近更新**：2025 年 10 月有活跃更新，主要集中在编辑器侧的验证和兼容性检测
- **维护状态**：活跃维护中
- **实验性**：非实验性，默认启用
- **推荐使用**：✅ 如果你在项目中使用 MetaHuman 角色，这是必需的运行时组件。模块代码量小（9 个文件），职责清晰，专注于运行时动画驱动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK)
- [官方文档]()（未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKEditor/Private/Tests)（测试位于 Editor 模块中）
