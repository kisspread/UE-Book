# IK Rig

> （Description 字段为空，以下基于源码分析）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Slate 图标/样式资源） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (UncookedOnly), `IKRigEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig) | |

---

## 用途

IKRig 是 UE5 的核心动画插件，提供两大系统：

1. **IK Rig（逆运动学绑定）**：允许在骨骼网格体上定义 IK 目标（Goals）、求解器（Solvers）和骨骼约束，用于运行时程序化骨骼调整（如脚部放置、手部抓取、身体姿态修正）。支持多种求解器类型：Full Body IK、Limb Solver、Pole Solver、Body Mover、Set Transform、Stretch Limb。

2. **IK Retargeter（IK 重定向）**：在不同骨骼结构的角色之间转移动画。通过 IK Rig 定义作为桥梁，将源骨骼链映射到目标骨骼链，解决不同比例/骨骼层级之间的动画复用问题。支持批量重定向、重定向姿态编辑、姿态导入导出。

该插件依赖 ControlRig 和 FullBodyIK 插件，构建在 UE 的动画蓝图系统之上。

## 使用场景

- 你需要为角色实现程序化 IK（脚部放置、手部触碰）→ 用 **IKRig** 定义 IK 目标和求解器
- 你有多个不同体型/骨骼结构的角色，需要共享动画 → 用 **IKRetargeter** 建立骨骼映射
- 你需要批量将一批动画资产从一个骨架重定向到另一个骨架 → 用 **IKRetargeter** 的批量导出功能
- 你在做角色自定义系统（不同身高/体型），需要动画自动适配 → 用 **IKRetargeter**
- 你需要快速为标准人形角色设置 Full Body IK → 用 **Auto Setup FBIK** 自动配置

## 蓝图用法

### 核心动画节点

IKRig 的运行时功能主要通过动画蓝图节点暴露：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AnimNode_IKRig` | 在动画蓝图中应用 IK Rig 处理，驱动程序化骨骼调整 | `FAnimNode_IKRig` |
| `AnimNode_RetargetPoseFromMesh` | 从源骨骼网格体重定向动画到目标网格体 | `FAnimNode_RetargetPoseFromMesh` |

### 资产创建

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create New IK Rig Asset` | 在指定路径创建新的 IK Rig 资产 | `UIKRigDefinitionFactory` |

### 使用示例（蓝图描述）

**IK Rig 动画蓝图用法**：
1. 打开角色的动画蓝图
2. 在 AnimGraph 中添加 `IK Rig` 节点
3. 指定 `IKRigDefinition` 资产
4. 将该节点串联到动画图表的输出之前
5. 运行时自动应用 IK 求解

**IK Retargeter 用法**：
1. 创建 `IKRetargeter` 资产，指定源和目标 `IKRigDefinition`
2. 在动画蓝图中添加 `Retarget Pose From Mesh` 节点
3. 指定源骨骼网格体组件和 Retargeter 资产
4. 源角色的动画将自动重定向到目标角色

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "Rig/IKRigDefinition.h"
#include "Rig/IKRigController.h"
#include "Rig/IKRigProcessor.h"
#include "Retargeter/IKRetargeter.h"
#include "AnimNodes/AnimNode_IKRig.h"
#include "AnimNodes/AnimNode_RetargetPoseFromMesh.h"

// Editor 模块（仅编辑器环境）
#include "RigEditor/IKRigDefinitionFactory.h"
```

### 基本用法 — 创建 IK Rig 资产

从 `UIKRigDefinitionFactory` 提取的 API：

```cpp
#include "RigEditor/IKRigDefinitionFactory.h"

// 在指定路径创建新的 IK Rig 资产
UIKRigDefinition* NewRig = UIKRigDefinitionFactory::CreateNewIKRigAsset(
    TEXT("/Game/MyIKRigs/"),   // 包路径
    TEXT("IK_MyCharacter")     // 资产名称
);
```

### 基本用法 — 动画节点配置

从 `FIKRigAnimInstanceProxy` 和 `IKRigAnimInstance.h` 提取的用法：

```cpp
#include "RigEditor/IKRigAnimInstance.h"

// 在自定义 AnimInstance 中设置 IK Rig 资产
UIKRigAnimInstance* AnimInstance = Cast<UIKRigAnimInstance>(MeshComponent->GetAnimInstance());
if (AnimInstance)
{
    AnimInstance->SetIKRigAsset(MyIKRigDefinition);
    AnimInstance->SetProcessorNeedsInitialized();
    
    // 获取当前运行的处理器
    FIKRigProcessor* Processor = AnimInstance->GetCurrentlyRunningProcessor();
}
```

### 进阶用法 — IK Retargeter 配置

从 `IKRetargetAnimInstance.h` 和 `IKRetargetAnimInstanceProxy.h` 提取：

```cpp
#include "RetargetEditor/IKRetargetAnimInstance.h"

// 配置重定向动画实例
UIKRetargetAnimInstance* RetargetInstance = Cast<UIKRetargetAnimInstance>(TargetMeshComponent->GetAnimInstance());
if (RetargetInstance)
{
    // 配置源/目标和重定向资产
    RetargetInstance->ConfigureAnimInstance(
        ERetargetSourceOrTarget::Target,  // 当前实例是目标
        MyIKRetargeterAsset,               // 重定向资产
        SourceMeshComponent                // 源骨骼网格体组件
    );
    
    // 设置输出模式
    RetargetInstance->SetRetargetMode(ERetargeterOutputMode::RetargetPose);
    
    // 混合重定向姿态
    RetargetInstance->SetRetargetPoseBlend(1.0f);
    
    // 强制初始化处理器
    RetargetInstance->ForceInitializeProcessor(TargetMeshComponent);
    
    // 获取重定向处理器
    FIKRetargetProcessor* Processor = RetargetInstance->GetRetargetProcessor();
}
```

### 进阶用法 — 求解器类型

从 `IKRigStructWrappers.h` 提取的可用求解器：

| 求解器 | 设置结构体 | 用途 |
|---|---|---|
| Body Mover | `FIKRigBodyMoverSettings` | 移动身体根骨骼 |
| Full Body IK | `FIKRigFBIKSettings` | 全身逆运动学 |
| Limb Solver | `FIKRigLimbSolverSettings` | 肢体链求解（手臂/腿部） |
| Pole Solver | `FIKRigPoleSolverSettings` | 极向量约束 |
| Set Transform | `FIKRigSetTransformSettings` | 直接设置骨骼变换 |
| Stretch Limb | `FIKRigStretchLimbSettings` | 可拉伸肢体 |

## Demo 示例

### 最小 IK Rig 使用示例

```cpp
// MyIKRigCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyIKRigCharacter.generated.h"

class UIKRigDefinition;
class UIKRetargeter;

UCLASS()
class AMyIKRigCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyIKRigCharacter();

    // 在编辑器中指定 IK Rig 资产
    UPROPERTY(EditAnywhere, Category = "IK Rig")
    TObjectPtr<UIKRigDefinition> IKRigAsset;

    // 重定向资产（用于动画转移）
    UPROPERTY(EditAnywhere, Category = "IK Retarget")
    TObjectPtr<UIKRetargeter> RetargeterAsset;

    // 源角色的骨骼网格体组件（用于重定向）
    UPROPERTY(EditAnywhere, Category = "IK Retarget")
    TWeakObjectPtr<USkeletalMeshComponent> SourceMeshComponent;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyIKRigCharacter.cpp
#include "MyIKRigCharacter.h"
#include "Rig/IKRigDefinition.h"
#include "Retargeter/IKRetargeter.h"

AMyIKRigCharacter::AMyIKRigCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyIKRigCharacter::BeginPlay()
{
    Super::BeginPlay();

    // IK Rig 资产通常在动画蓝图中通过 AnimNode_IKRig 节点使用
    // 这里仅验证资产是否已正确分配
    if (IKRigAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("IK Rig Asset loaded: %s"), *IKRigAsset->GetName());
    }

    if (RetargeterAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("IK Retargeter Asset loaded: %s"), *RetargeterAsset->GetName());
    }
}
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ControlRig` | 底层骨骼控制系统，IKRig 构建于其上 |
| `FullBodyIK` | 全身逆运动学求解器实现 |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Persona` | 编辑器预览场景和动画编辑框架 |
| `SkeletonEditor` | 骨骼编辑器集成 |
| `ContentBrowser` | 资产浏览器集成 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 子模块概览

本插件包含 3 个模块，按功能划分：

| 模块 | 类型 | 职责 |
|---|---|---|
| **IKRig** | Runtime | 核心运行时：IK Rig 定义、处理器、求解器、重定向器、动画节点 |
| **IKRigDeveloper** | UncookedOnly | 开发者工具：仅在未打包编辑器中可用的开发辅助功能 |
| **IKRigEditor** | Editor | 编辑器工具：IK Rig 编辑器、IK Retarget 编辑器、资产工厂、缩略图渲染、细节面板自定义、批量操作 |

### IKRigEditor 模块关键组件

| 组件 | 说明 |
|---|---|
| `FIKRigEditorToolkit` | IK Rig 资产编辑器主框架 |
| `FIKRetargetEditor` | IK Retargeter 资产编辑器主框架 |
| `FIKRigEditorController` | IK Rig 编辑器控制器（管理选择、交互） |
| `FIKRetargetEditorController` | IK Retarget 编辑器控制器 |
| `FAutoFBIKCreator` | 自动 Full Body IK 设置生成器 |
| `FIKRetargetPoseExporter` | 重定向姿态导入/导出（支持 Pose Asset 和动画序列） |
| `UIKRigThumbnailRenderer` | IK Rig 资产缩略图渲染 |
| `UIKRetargeterThumbnailRenderer` | IK Retargeter 资产缩略图渲染（显示源/目标双骨骼） |
| `FIKRigGenericDetailCustomization` | 骨骼和目标的细节面板自定义 |

### 编辑器标签页

**IK Rig 编辑器**包含以下标签页：

| 标签页 | 说明 |
|---|---|
| Skeleton | 骨骼层级视图，用于选择骨骼、创建目标、配置求解器 |
| Solver Stack | 求解器堆栈，管理求解器的添加/排序/配置 |
| Retarget Chains | 重定向链配置 |
| Output Log | 输出日志 |
| Asset Browser | 资产浏览器 |

**IK Retarget 编辑器**包含以下标签页：

| 标签页 | 说明 |
|---|---|
| Hierarchy | 源/目标骨骼层级对比视图 |
| Op Stack | 重定向操作堆栈 |
| Output Log | 输出日志 |
| Asset Browser | 动画资产浏览器（含批量导出） |

## 维护状态

### 近期更新

```
- ee5d553fbb23 [IK Retarget] Exposed "bOverwriteExistingFiles" to batch retarget operation.
- 26b963f00200 [IK Retarget] Allow displaying retarget chains column while pose editing.
- 6a6e8621e17d [IK Retarget] Removed broken old dropdown menu in retarget editor toolbar.
```

近期三次提交均围绕 IK Retarget 系统的改进：批量操作参数暴露、编辑器 UI 优化、损坏菜单修复。

### 维护评价

- **活跃维护**：由 Epic Games 官方维护，近期有持续的功能更新和 bug 修复
- **核心动画插件**：作为 UE5 动画系统的关键组件，与 ControlRig 深度集成
- **稳定成熟**：创建于 2020 年，经过 5 年迭代，IK Rig 核心已趋于稳定
- **持续演进**：IK Retarget 系统仍在积极开发中，近期提交集中在重定向功能增强
- **推荐使用**：✅ 强烈推荐。这是 UE5 官方推荐的 IK 和动画重定向方案，替代了旧版 UE4 的重定向系统

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig)
- 官方文档（.uplugin 中未提供 DocsURL）