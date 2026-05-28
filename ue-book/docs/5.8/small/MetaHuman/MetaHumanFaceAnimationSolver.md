# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanFaceAnimationSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 工具套件核心，旨在将真实世界的面部表演数据（例如来自 iPhone 或专业头盔的捕捉数据）转换为可用于驱动高保真 MetaHuman 角色的动画数据。`MetaHumanFaceAnimationSolver` 模块是此工作流的关键一环，它是一个**面部动画求解器**，负责存储和管理将面部追踪数据（如追踪点、深度图）映射到 MetaHuman 面部骨骼/控制点动画所需的全部配置和参数。简单来说，它的作用是将“原始捕捉数据”翻译成“有意义的角色动画”。

## 使用场景

-   **数字人表演动画制作**：你使用 iPhone 的 TrueDepth 相机或专业头戴式捕捉设备录制了一段演员的面部表演，需要将其转换为高质量的 MetaHuman 动画用于电影或游戏过场动画。
-   **AI 驱动虚拟角色**：通过 AI 模型（如语音转面部）生成的原始面部数据，需要经过求解器优化和适配，才能自然地驱动一个 MetaHuman 角色。
-   **批量处理与自动化**：需要对大量面部捕捉数据进行统一的求解器配置，以确保生成动画的风格一致性。
-   **动画优化与调整**：在初步求解后，通过调整求解器参数（如平滑度、牙齿模式）来优化动画细节，改善眼球转动的自然度或牙齿的表现。

## 蓝图用法

`UMetaHumanFaceAnimationSolver` 的属性主要在编辑器中进行配置，其核心函数（如 `GetSolverConfigData`）主要被内部系统或编辑器工具调用，而非直接作为蓝图节点使用。然而，它的属性（如 `bOverrideDeviceConfig`, `DepthMapInfluence` 等）在蓝图编辑器中是**可编辑**的。

### 核心属性（蓝图可编辑）

| 属性 | 说明 | 类型 |
|---|---|---|
| `bOverrideDeviceConfig` | 是否覆盖全局设备配置 | `bool` |
| `DeviceConfig` | 指定用于此求解器的 MetaHuman 设备配置资产 | `UMetaHumanConfig*` |
| `bOverrideDepthMapInfluence` | 是否覆盖深度图影响设置 | `bool` |
| `DepthMapInfluence` | 深度图对求解结果的影响程度（无、低、高） | `EDepthMapInfluenceValue` |
| `bOverrideEyeSolveSmoothness` | 是否覆盖眼球求解平滑度 | `bool` |
| `EyeSolveSmoothness` | 眼球控制结果的平滑度（0-1） | `float` |
| `bOverrideTeethMode` | 是否覆盖牙齿模式 | `bool` |
| `TeethMode` | 牙齿数据是使用追踪点还是估算值 | `ETeethMode` |

### 使用示例（蓝图描述）

在编辑器中，你可以通过以下方式使用此求解器：
1.  创建一个 `UMetaHumanFaceAnimationSolver` 类型的资产（通常是 `MetaHumanFaceAnimationSolver` 蓝图类）。
2.  在该资产的**细节面板**中，勾选你想要自定义的参数（例如 `bOverrideDepthMapInfluence`），然后调整其值（例如将 `DepthMapInfluence` 设置为 `High`）。
3.  将这个配置好的求解器资产指定给 MetaHuman Pipeline 或 MetaHuman Performance 处理节点，作为其面部动画求解的核心配置。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

创建求解器实例并获取其用于配置的数据（通常用于与底层技术库交互）。
*来源文件：`Source/MetaHumanFaceAnimationSolver/MetaHumanFaceAnimationSolver.h`*

```cpp
// 假设已有一个 UCaptureData* 捕获数据对象 InCaptureData
UMetaHumanFaceAnimationSolver* FaceSolver = NewObject<UMetaHumanFaceAnimationSolver>();

// 检查求解器是否就绪（依赖于配置）
if (FaceSolver->CanProcess())
{
    // 获取用于配置求解器的 JSON 字符串数据
    FString SolverConfigJson = FaceSolver->GetSolverConfigData(InCaptureData);
    
    // 将此配置数据传递给底层的求解算法（例如 MetaHumanCoreTechLib）
    // SolverCore->Configure(SolverConfigJson);
}

// 监听求解器内部变化（例如，当用户在编辑器中修改参数后）
FaceSolver->OnInternalsChanged().AddLambda([]() {
    UE_LOG(LogTemp, Log, TEXT("Face Animation Solver configuration changed!"));
    // 这里可以触发重新求解或更新预览
});
```

### 进阶用法

结合 `MetaHumanConfig` 和其他模块，动态调整求解参数。
*综合自：`MetaHumanFaceAnimationSolver.h` 和 `MetaHumanConfig` 的典型用法*

```cpp
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanConfig.h"

// ... 在某个管理类中 ...

// 1. 加载一个特定的设备配置（例如，针对 iPhone 14 的优化配置）
UMetaHumanConfig* iPhoneConfig = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Path/To/Your/iPhone14_Config"));

// 2. 应用配置到求解器
UMetaHumanFaceAnimationSolver* MySolver = NewObject<UMetaHumanFaceAnimationSolver>();
MySolver->bOverrideDeviceConfig = true;
MySolver->DeviceConfig = iPhoneConfig;

// 3. 根据需要调整其他参数
MySolver->bOverrideEyeSolveSmoothness = true;
MySolver->EyeSolveSmoothness = 0.25f; // 设置一个较高的平滑度以减少抖动

// 4. 当设置改变后，求解器会广播通知，我们可以响应
MySolver->OnInternalsChanged().AddUObject(this, &UMyAnimationManager::OnSolverSettingsChanged);

// 5. 最终，将配置好的求解器用于实际的数据处理流程
// ProcessCaptureData(InCaptureData, MySolver);
```

## Demo 示例

一个最小的、创建并配置求解器的 C++ 类示例。
*注意：此示例仅演示对象创建和属性设置，实际集成需要更复杂的工作流。*

**MyFaceSolverUser.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyFaceSolverUser.generated.h"

UCLASS()
class MYPROJECT_API AMyFaceSolverUser : public AActor
{
    GENERATED_BODY()
    
public:
    AMyFaceSolverUser();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<class UMetaHumanFaceAnimationSolver> FaceAnimationSolver;
};
```

**MyFaceSolverUser.cpp**
```cpp
#include "MyFaceSolverUser.h"
#include "MetaHumanFaceAnimationSolver.h"

AMyFaceSolverUser::AMyFaceSolverUser()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyFaceSolverUser::BeginPlay()
{
    Super::BeginPlay();

    // 创建求解器实例
    FaceAnimationSolver = NewObject<UMetaHumanFaceAnimationSolver>();

    // 配置求解器参数
    if (FaceAnimationSolver)
    {
        // 使用自定义配置覆盖
        FaceAnimationSolver->bOverrideDeviceConfig = true;
        // FaceAnimationSolver->DeviceConfig = LoadObject<UMetaHumanConfig>(...); // 设置具体配置

        // 调整牙齿求解模式
        FaceAnimationSolver->bOverrideTeethMode = true;
        FaceAnimationSolver->TeethMode = ETeethMode::Estimated;

        // 注册变更回调
        FaceAnimationSolver->OnInternalsChanged().AddLambda([this]() {
            UE_LOG(LogTemp, Warning, TEXT("Solver config changed on %s"), *GetName());
        });

        UE_LOG(LogTemp, Log, TEXT("FaceAnimationSolver created and configured."));
    }
}
```

## 模块依赖

`MetaHumanFaceAnimationSolver` 模块依赖于 MetaHuman 工具链的核心库，以完成实际的动画求解计算。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供底层的面部动画求解算法和技术支持 |
| `MetaHumanConfig` | 提供设备和求解流程的配置管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当身体追踪时，过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHuman Animator 及其子模块（包括 `MetaHumanFaceAnimationSolver`）正处于**活跃维护**状态。从最近的提交历史看（2026年5月），团队在持续进行功能完善（如身体追踪集成、序列导出）和重要缺陷修复（渲染、缓存问题）。该插件是 Epic 官方核心产品的一部分，拥有长期的维护承诺。虽然 `MetaHumanFaceAnimationSolver` 本身主要是配置和数据接口层，但其稳定性和更新直接反映了整个 MetaHuman 工具链的健康度。**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/animation-and-animations-in-unreal-engine/) (通用动画文档，MetaHuman 部分请参考 Epic 官方门户)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver) (模块自身目录下通常包含测试代码)