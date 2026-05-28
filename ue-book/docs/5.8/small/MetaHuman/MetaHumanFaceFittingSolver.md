# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数字人资产、配置、编辑器工具） |
| 模块 | `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanToolkit` (Runtime) (共 28 个模块，此处列举示例) |
| 实验性 | 否 |
| 创建时间 | 2023-02-16 (估算) |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
MetaHuman Animator 是 Epic Games 官方提供的一套完整工具，用于从面部捕捉数据（如 iPhone 深度摄像头视频或专业动捕设备数据）创建并驱动高保真、可动画的 MetaHuman 数字人。它不仅仅是导入资产，而是一个完整的流水线，涵盖了从原始视频/数据摄入、面部身份创建、表情求解器训练，到最终在引擎中实时驱动动画输出的全过程。该插件的目标是简化创建与真实演员表演绑定的高质量数字人角色的复杂流程。

## 使用场景
- 你有一段演员的面部表演视频，想将其驱动一个已有的 MetaHuman 角色，实现精准的口型同步和表情动画。
- 你需要为游戏或影视项目创建一个全新的、基于真实演员面部数据的定制化 MetaHuman 角色。
- 你在开发一个需要批量处理面部捕捉数据并生成动画序列的 pipeline 工具。
- 你正在使用 Live Link 或其他实时捕捉设备，希望在引擎中实时预览演员的面部表演驱动 MetaHuman。

## 蓝图用法
由于插件包含大量模块和编辑器集成，其 API 主要集中在 C++ 和编辑器工具界面。蓝图层面的公开 API 相对有限，通常用于控制 pipeline 流程或查询状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Face Fitting Solvers` | 加载用于面部拟合的求解器配置 | `UMetaHumanFaceFittingSolver` |
| `Can Process` | 检查当前配置是否准备好进行处理 | `UMetaHumanFaceFittingSolver` |
| `Get Fitting Template Data` | 获取面部拟合的模板数据（JSON 格式） | `UMetaHumanFaceFittingSolver` |
| `Get Fitting Config Data` | 获取面部拟合的配置数据（JSON 格式） | `UMetaHumanFaceFittingSolver` |
| `On Internals Changed` | 当求解器内部数据改变时广播的多播委托 | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）
在蓝图中，你可能会在一个自定义的批处理 Actor 或 Widget 中，获取一个 `UMetaHumanFaceFittingSolver` 对象的引用。首先调用 `LoadFaceFittingSolvers` 节点来初始化求解器。然后，通过 `GetFittingConfigData` 节点获取配置的 JSON 字符串，用于调试或传递给其他系统。最后，你可以绑定到 `OnInternalsChanged` 事件，以便在求解器配置发生变化时更新 UI 或重新触发处理流程。

## C++ 用法
插件的核心逻辑和复杂的数据处理均在 C++ 中实现。开发者通常需要与数据资产、求解器和 Pipeline 模块交互。

### 头文件引入
```cpp
#include "MetaHumanFaceFittingSolver.h" // 面部拟合求解器
#include "MetaHumanFaceAnimationSolver.h" // 面部动画求解器
#include "MetaHumanIdentity.h" // 数字人身份资产
```

### 基本用法
以下是一个简化的示例，展示如何检查面部拟解器的状态并获取其数据。**注意**：实际使用中，`UMetaHumanFaceFittingSolver` 对象通常作为资产的一部分被管理。
```cpp
// 假设 UMetaHumanFaceFittingSolver* Solver 已有效引用
if (Solver && Solver->CanProcess())
{
    // 加载必要的求解器数据
    Solver->LoadFaceFittingSolvers();
    
    // 获取拟合配置的 JSON 字符串，可用于调试或序列化
    FString ConfigJson = Solver->GetFittingConfigData();
    UE_LOG(LogTemp, Log, TEXT("Fitting Config: %s"), *ConfigJson);
}
```
*（代码逻辑基于 `Public/MetaHumanFaceFittingSolver.h` 头文件中的公开接口推导）*

### 进阶用法
进阶用法涉及组合多个模块。例如，你可能需要将 `UCaptureData`（捕捉数据）与 `UMetaHumanIdentity`（身份资产）关联，然后使用 `UMetaHumanFaceAnimationSolver` 来生成最终的动画序列。这通常通过 `MetaHumanPipeline` 模块来编排。处理流程大致如下：
1.  创建或获取一个 `UMetaHumanIdentity` 对象。
2.  关联 `UCaptureData`。
3.  利用 `MetaHumanFaceContourTracker` 和 `MetaHumanFaceFittingSolver` 对数据进行拟合和优化。
4.  使用训练好的 `MetaHumanFaceAnimationSolver` 驱动面部 Control Rig。
5.  通过 `MetaHumanSequencer` 将动画输出到关卡序列或资产。

## Demo 示例
由于插件高度集成且依赖特定资产（MetaHuman、CaptureData等），一个最小可运行的示例需要先在编辑器中完成身份创建工作。以下代码展示了如何以编程方式检查一个已存在的求解器对象。
```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UMetaHumanFaceFittingSolver;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();

    // 在编辑器中设置此求解器资产
    UPROPERTY(EditAnywhere, Category="MetaHuman")
    TObjectPtr<UMetaHumanFaceFittingSolver> SolverAsset;

    UFUNCTION(CallInEditor, BlueprintCallable)
    void CheckSolverStatus();
};

// MyActor.cpp
#include "MyActor.h"
#include "MetaHumanFaceFittingSolver.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::CheckSolverStatus()
{
    if (SolverAsset)
    {
        if (SolverAsset->CanProcess())
        {
            UE_LOG(LogTemp, Warning, TEXT("Solver is ready to process."));
            SolverAsset->LoadFaceFittingSolvers();
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Solver is not ready. Check its configuration."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("SolverAsset is null."));
    }
}
```
**使用步骤**：
1.  在编辑器中创建一个新的 `AActor` 子类或使用上面的代码编译一个新 Actor。
2.  将该 Actor 拖入场景。
3.  在其细节面板中，将一个已创建好的 `MetaHuman Face Fitting Solver` 资产（可在内容浏览器中创建）赋值给 `SolverAsset` 属性。
4.  点击 `CheckSolverStatus` 按钮（如果使用 `CallInEditor`）或在其他逻辑中调用该函数，即可在输出日志中看到状态信息。

## 模块依赖
MetaHuman Animator 是一个包含大量模块的插件，其内部依赖关系复杂。对于想要扩展或集成此插件的外部模块，通常需要依赖其核心数据类型和接口模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供核心数据结构和工具函数 |
| `MetaHumanCaptureDataEditor` | 编辑器内管理和操作捕捉数据 |
| `MetaHumanIdentity` | 定义数字人身份资产 (`UMetaHumanIdentity`) |
| `ControlRigDeveloper` | 与 Control Rig 系统集成，用于驱动面部动画 |
| `SkeletalMeshUtilitiesCommon` | 处理骨骼网格体相关的通用工具 |

## 维护状态
该插件由 Epic Games 官方维护，是 MetaHuman 生态系统的核心组件，更新活跃，与 UE 版本迭代同步。

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 缓存问题 |

### 维护评价
- **活跃维护**：最近提交频繁（集中在2026年5月），均为功能增强和 Bug 修复，表明该插件是官方重点维护的产品级组件。
- **持续集成**：更新内容与 MetaHuman 的核心工作流（如动画导出、身体追踪集成、渲染优化）紧密相关。
- **推荐使用**：作为创建高保真 MetaHuman 数字人的官方标准工具，**强烈推荐**给所有相关项目使用。它提供了从捕捉到动画的完整、受支持的解决方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-humans-in-unreal-engine/) (MetaHuman 整体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (示例：`MetaHumanControlsConversionTest` 模块)