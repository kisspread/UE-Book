# ArchVis Character

> A controllable character tuned for architectural applications

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | ArchVisCharacter (Runtime) |
| 创建时间 | 2015-07-10 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ArchVisCharacter) | |

## 用途

ArchVisCharacter 是一个专为**建筑可视化 (Architectural Visualization)** 场景设计的角色插件。它提供了一种不同于默认 `ACharacter` 的第一人称漫游体验：

- **旋转输入采用物理惯性模型**：鼠标或手柄的转动输入不直接驱动角色旋转，而是通过加速/减速/最大速度的物理模型来实现平滑的惯性转动，模拟真实摄像机的操控感。
- **俯仰角限制**：默认限制在 -85° ~ 85°，避免出现不自然的翻转视角。
- **移动速度随俯仰角自适应**：越往上看/下看，行走速度越慢（类似余弦缩放），模拟真实的第一人称观察行为。
- **将 Yaw（水平旋转）交给角色体，Pitch（垂直旋转）交给控制器**：通过 `GetViewRotation()` 的分离处理，实现更自然的第一人称摄像机行为。

简而言之：这个插件存在的目的是让你在 UE 中快速获得一个"建筑漫游"的第一人称体验，不需要自己从零搭建移动和视角系统。

## 使用场景

- 你正在制作建筑可视化项目（如房产展示、室内设计预览）→ 用 ArchVisCharacter 作为默认的漫游角色
- 你需要一种带有惯性、不会过于灵敏的第一人称操控体验 → 比默认 `ACharacter` 更适合"走走看看"的场景
- 你需要一个快速可用的 Blueprintable 角色，可以自定义输入轴名称和灵敏度 → 在蓝图中直接设置属性即可

## 蓝图用法

ArchVisCharacter 是 `Blueprintable` 的，可以直接作为蓝图父类使用。所有属性都是 `EditDefaultsOnly, BlueprintReadOnly`，适合在蓝图的 Class Defaults 中配置。

### 核心属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `TurnAxisName` | 水平旋转的输入轴名称（直接输入，如鼠标），默认 `"Turn"` | `AArchVisCharacter` |
| `TurnAtRateAxisName` | 水平旋转的输入轴名称（速率输入，如摇杆），默认 `"TurnRate"` | `AArchVisCharacter` |
| `LookUpAxisName` | 垂直旋转的输入轴名称（直接输入），默认 `"LookUp"` | `AArchVisCharacter` |
| `LookUpAtRateAxisName` | 垂直旋转的输入轴名称（速率输入），默认 `"LookUpRate"` | `AArchVisCharacter` |
| `MoveForwardAxisName` | 前后移动的输入轴名称，默认 `"MoveForward"` | `AArchVisCharacter` |
| `MoveRightAxisName` | 左右移动的输入轴名称，默认 `"MoveRight"` | `AArchVisCharacter` |
| `MouseSensitivityScale_Pitch` | 鼠标垂直灵敏度，默认 `0.025` | `AArchVisCharacter` |
| `MouseSensitivityScale_Yaw` | 鼠标水平灵敏度，默认 `0.025` | `AArchVisCharacter` |

| 属性 | 说明 | 所在类 |
|---|---|---|
| `RotationalAcceleration` | 旋转加速度 (Pitch, Yaw, Roll)，默认 `(300, 300, 0)` | `UArchVisCharMovementComponent` |
| `RotationalDeceleration` | 旋转减速度，松开输入后的减速速率，默认 `(300, 300, 0)` | `UArchVisCharMovementComponent` |
| `MaxRotationalVelocity` | 最大旋转速度，默认 `(80, 100, 0)` 度/秒 | `UArchVisCharMovementComponent` |
| `MinPitch` | 最低俯仰角，默认 `-85` | `UArchVisCharMovementComponent` |
| `MaxPitch` | 最高俯仰角，默认 `85` | `UArchVisCharMovementComponent` |
| `WalkingFriction` | 行走摩擦力，默认 `4.0` | `UArchVisCharMovementComponent` |
| `WalkingSpeed` | 行走速度，默认 `165` | `UArchVisCharMovementComponent` |
| `WalkingAcceleration` | 行走加速度，默认 `500` | `UArchVisCharMovementComponent` |

### 使用示例（蓝图描述）

1. **创建蓝图子类**：在 Content Browser 中右键 → Blueprint Class → 选择 `ArchVisCharacter` 作为父类。
2. **配置输入**：在 Project Settings → Input 中创建对应的 Axis 映射（如 `Turn`、`LookUp`、`MoveForward`、`MoveRight` 等），然后在蓝图的 Class Defaults 中将轴名称指向你创建的映射。
3. **放置到关卡**：将蓝图拖入关卡，确保 GameMode 的 Default Pawn Class 设置为你的 ArchVisCharacter 蓝图。
4. **调整灵敏度**：根据需要调整 `MouseSensitivityScale_Pitch/Yaw`，以及 `RotationalAcceleration`、`MaxRotationalVelocity` 等旋转参数。

## C++ 用法

### 头文件引入

```cpp
#include "ArchVisCharacter.h"
#include "ArchVisCharMovementComponent.h"
```

### 基本用法

创建一个继承自 `AArchVisCharacter` 的子类，然后在构造函数中自定义输入轴和灵敏度：

```cpp
// MyArchVisCharacter.h
#pragma once
#include "ArchVisCharacter.h"
#include "MyArchVisCharacter.generated.h"

UCLASS()
class AMyArchVisCharacter : public AArchVisCharacter
{
    GENERATED_BODY()

public:
    AMyArchVisCharacter(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        // 自定义灵敏度
        MouseSensitivityScale_Pitch = 0.05f;
        MouseSensitivityScale_Yaw = 0.05f;

        // 自定义输入轴名称（如果你使用 Enhanced Input 或自定义映射）
        MoveForwardAxisName = TEXT("Forward");
        MoveRightAxisName = TEXT("Right");
    }
};
```

### 进阶用法

如果需要微调移动组件的物理参数，可以通过 `GetArchVisCharMoveComponent()` 获取自定义的移动组件：

```cpp
void AMyArchVisCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (UArchVisCharMovementComponent* MoveComp = GetArchVisCharMoveComponent())
    {
        // 调整旋转惯性感
        MoveComp->RotationalAcceleration = FRotator(200.f, 200.f, 0.f);
        MoveComp->RotationalDeceleration = FRotator(150.f, 150.f, 0.f);
        MoveComp->MaxRotationalVelocity = FRotator(60.f, 80.f, 0.f);

        // 放宽俯仰限制
        MoveComp->MinPitch = -90.f;
        MoveComp->MaxPitch = 90.f;

        // 更慢的行走速度，适合建筑漫游
        MoveComp->WalkingSpeed = 120.f;
    }
}
```

也可以继承 `UArchVisCharMovementComponent` 来进一步自定义物理行为，例如重写 `PhysWalking` 来添加自定义的移动逻辑。

## Demo 示例

一个完整的最小 ArchVisCharacter 子类，可直接编译使用：

```cpp
// MinArchVisChar.h
#pragma once
#include "ArchVisCharacter.h"
#include "MinArchVisChar.generated.h"

UCLASS()
class AMinArchVisChar : public AArchVisCharacter
{
    GENERATED_BODY()
public:
    AMinArchVisChar(const FObjectInitializer& OI) : Super(OI)
    {
        // 增大灵敏度，建筑漫游场景下更舒适
        MouseSensitivityScale_Pitch = 0.04f;
        MouseSensitivityScale_Yaw = 0.04f;
    }
};
```

```cpp
// MinArchVisChar.cpp
#include "MinArchVisChar.h"
// 构造函数已在头文件中内联定义，此文件可留空
```

**Build.cs 依赖**：如果你的项目模块要使用 ArchVisCharacter，需要在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ArchVisCharacter"
});
```

## 模块依赖

ArchVisCharacter 自身依赖以下模块（从 `Build.cs` 提取）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能（Character、MovementComponent 等） |

如果你要使用此插件，你的模块需要额外依赖 `ArchVisCharacter` 模块本身。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 编译优化，将 .gen.cpp 文件内联，减少编译时间。非功能性改动。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to convert all files to have dllstorage on methods/staticvar | DLL 导出符号标准化重构。非功能性改动。 |
| 2024-11-28 | `be437642` | Created missing Get/Set functions for member variables on ACharacter/APawn | 引擎级重构，为 ACharacter/APawn 的成员变量添加缺失的 getter/setter。非 ArchVisCharacter 特定的改动。 |

### 维护评价

- **创建时间**：2015-07-10，距今超过 10 年，属于 UE4 早期的插件
- **最后实质性功能更新**：源码中所有实质性的功能代码自创建以来基本没有变化，最近的 3 次提交均为引擎级的批量重构/编译修复，并非针对此插件的功能迭代
- **维护状态**：**维护不活跃** — 此插件处于"写完即放"的状态，Epic 没有对它进行持续的功能开发
- **稳定性**：由于代码量小且逻辑简单，多年来运行稳定，没有已知问题
- **推荐使用**：对于建筑可视化项目来说仍然可用且有效。但如果你需要更现代的输入方式（如 Enhanced Input System），需要自行替换输入绑定逻辑。插件本身功能完备，适合快速原型搭建

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ArchVisCharacter)
- 官方文档：无（.uplugin 中 DocsURL 为空）
