# Spatially Aware Retarget Ops

> A collection of Retarget Ops for preserving spatial relationships on retargeted animations

| 属性 | 值 |
|---|---|
| 中文名 | 空间感知重定向操作 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（重定向操作、调试资产） |
| 模块 | `BodyIntersectIKOp` (Runtime), `PreviewPropOp` (Runtime), `RelativeBodyAnimInfo` (Runtime), `RelativeBodyAnimUtils` (Runtime), `RelativeIKOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

这个插件提供了一套用于动画重定向（Retargeting）的“操作”（Retarget Ops），其核心目标是**在将动画从一个骨骼模型重定向到另一个时，保持关键的空间关系**。

标准的动画重定向主要关注骨骼的旋转，但常常会忽略肢体末端（如手、脚）相对于场景中其他物体的空间位置。例如，当一个角色将手放在桌上的动画被重定向到身材不同的角色时，手可能会穿过桌面或悬空。这个插件中的操作就是为了解决这类问题：

- **IK 驱动**：使用逆向运动学（Inverse Kinematics, IK）确保末端效应器（如脚、手）在世界空间中的位置保持正确。
- **身体相交检测**：防止重定向后的动画导致身体部位（如手臂）穿过其他物体（如墙壁或身体其他部分）。
- **道具预览**：提供可视化工具，用于检查在动画播放时，角色手持的道具是否正确地附着在手骨上，并保持正确的位置和旋转。

## 使用场景

- **动画师进行风格化角色重定向**：当你需要将一个写实角色的动画重定向到一个比例完全不同的卡通风格角色（例如，头大身小），但又希望角色的手能准确地放在原动画中指定的桌面上时。
- **游戏开发中复杂交互动画**：当你的游戏包含大量角色与场景物体交互的动画（如攀爬、靠墙、使用工具）时，使用此插件可以确保重定向后的动画依然保持正确的空间交互，避免穿模。
- **动画资产转换管线**：在自动化资产转换流水线中，集成此插件的操作，可以系统性地提高动画重定向的质量，减少人工修正。

## 蓝图用法

此插件主要通过蓝图和编辑器中的 IK Retargeter 系统使用，提供了在动画蓝图和编辑器中调试预览的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取当前预览道具操作的设置（包括附着映射、道具列表等） | `UIKRetargetPreviewPropController` |
| `SetSettings` | 设置预览道具操作的各项配置 | `UIKRetargetPreviewPropController` |

### 使用示例（蓝图描述）

在动画蓝图的事件图表中，你可以通过获取 `UIKRetargetPreviewPropController` 的引用来控制道具预览。典型的用法是在动画更新时，根据运行时逻辑动态调整预览的道具（例如，根据游戏状态显示或隐藏特定道具）。

1.  在动画蓝图中，使用 `Get Controller` 节点获取 `PreviewPropOp` 的控制器。
2.  调用 `Get Settings` 获取当前设置。
3.  修改返回的 `FIKRetargetPreviewPropOpSettings` 结构体中的 `PreviewProps` 数组，添加或修改道具数据（如网格体、附着骨骼）。
4.  调用 `Set Settings` 应用修改后的设置。

## C++ 用法

此插件的 C++ API 主要用于自定义重定向操作或深度集成。

### 头文件引入

```cpp
#include "PreviewPropOp.h"
```

### 基本用法

在 C++ 中，你可以创建和操作 `FIKRetargetPreviewPropOpSettings` 结构体来配置预览道具。

```cpp
// 来源: Public/PreviewPropOp.h
FIKRetargetPreviewPropOpSettings PreviewSettings;

// 添加一个要预览的道具
FPreviewPropsData NewProp;
NewProp.PropStaticMeshAsset = MySwordStaticMesh; // 设置静态网格体道具
NewProp.SourceAttachBone = FBoneReference(TEXT("hand_r")); // 设置附着到右手骨骼
NewProp.AttachTransform = FTransform(FRotator(0, 90, 0), FVector(0, 5, 0)); // 设置相对于附着骨骼的偏移和旋转
NewProp.ShowProp = true;

PreviewSettings.PreviewProps.Add(NewProp);

// 设置源骨骼到目标骨骼的附着映射（名称映射）
PreviewSettings.AttachMapping.Add(FName(TEXT("hand_r")), FName(TEXT("hand_r")));
PreviewSettings.AttachMapping.Add(FName(TEXT("hand_l")), FName(TEXT("hand_l")));
```

### 进阶用法

你可以通过 `UIKRetargetPreviewPropController` 在运行时动态控制设置。

```cpp
// 假设你已经获取了控制器指针
UIKRetargetPreviewPropController* Controller = GetPreviewPropController();

if (Controller)
{
    // 获取当前设置
    FIKRetargetPreviewPropOpSettings CurrentSettings = Controller->GetSettings();

    // 动态添加一个新的骨骼网格体道具
    FPreviewPropsData SkeletalProp;
    SkeletalProp.PropSkeletalMeshAsset = MyCharacterPropMesh;
    SkeletalProp.PropAnimSequence = MyPropIdleAnimation; // 为道具播放动画
    SkeletalProp.SourceAttachBone = FBoneReference(TEXT("spine_02"));
    CurrentSettings.PreviewProps.Add(SkeletalProp);

    // 应用修改后的设置
    Controller->SetSettings(CurrentSettings);
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个自定义的预览道具控制器。

```cpp
// MyPreviewPropController.h
#pragma once

#include "CoreMinimal.h"
#include "PreviewPropOp.h" // 引入预览道具模块的头文件
#include "MyPreviewPropController.generated.h"

UCLASS()
class UMyPreviewPropController : public UIKRetargetPreviewPropController
{
    GENERATED_BODY()

public:
    // 一个自定义的函数，用于在游戏开始时初始化一个默认的武器预览
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void InitializeDefaultWeaponPreview(UStaticMesh* WeaponMesh);
};

// MyPreviewPropController.cpp
#include "MyPreviewPropController.h"

void UMyPreviewPropController::InitializeDefaultWeaponPreview(UStaticMesh* WeaponMesh)
{
    if (!WeaponMesh) return;

    // 获取当前设置
    FIKRetargetPreviewPropOpSettings Settings = GetSettings();

    // 清空现有预览
    Settings.PreviewProps.Empty();

    // 创建新的武器预览配置
    FPreviewPropsData WeaponProp;
    WeaponProp.PropStaticMeshAsset = WeaponMesh;
    WeaponProp.SourceAttachBone = FBoneReference(TEXT("hand_r"));
    WeaponProp.AttachTransform = FTransform(FRotator(0, 0, -90), FVector(0, 5, -5)); // 根据武器模型调整旋转和位移
    WeaponProp.ShowProp = true;
    WeaponProp.DebugMaterial = nullptr; // 使用默认材质

    Settings.PreviewProps.Add(WeaponProp);

    // 应用设置
    SetSettings(Settings);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `IKRetargeter` | 核心的 IK 重定向框架，此插件的所有重定向操作都基于此模块构建 |
| `IKRig` | 提供 IK 骨架和求解器功能 |
| `MeshDescription` | 用于从静态或骨骼网格体中提取顶点和三角形数据，以便进行调试绘制 |
| `AnimationBlueprintLibrary` | 可能在动画预览和播放头获取相关功能中被间接使用 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `b70e3bb0` | [IK Retargeter] Add NotOverrideable meta to scalar TArrays in RelativeIK plugin retarget ops | 为标量TArray属性添加了不可覆盖的元数据，可能用于防止在蓝图中意外修改 |
| 2026-04-14 | `66a98b79` | Migrate UE_LOG to UE_LOGF. | 将传统的UE_LOG日志宏迁移到UE_LOGF宏 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 同上，另一个模块的日志宏迁移 |
| 2026-04-14 | `701659c5` | RIK: Prop Intersection Pushout fix | 修复了道具相交推出功能的错误 |
| 2026-04-08 | `23ef9e5c` | RelativeIK: Prop push out | 添加了道具相交时的推出逻辑 |

### 维护评价

- **活跃维护**：插件创建于2025年7月，至今约1年。从近期提交历史看，在2026年4月有**非常活跃的更新**，包括功能添加（NotOverrideable元数据）、代码现代化（日志宏迁移）和Bug修复（相交推出逻辑）。
- **实验性状态**：插件被明确标记为实验性（IsExperimentalVersion=true）且默认不启用（Installed=false），这意味着它可能还不稳定或API可能会发生变化。
- **局限性**：作为实验性功能，其性能和在复杂场景下的稳定性需要进一步验证。文档和示例可能不足。
- **推荐**：**推荐在开发或原型阶段尝试使用**，尤其是当你在动画重定向过程中遇到严重的空间关系问题时。但不建议直接用于生产环境的核心功能。建议密切关注其API变化和更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Animation/RelativeIKOpTests) (推断路径，需验证)