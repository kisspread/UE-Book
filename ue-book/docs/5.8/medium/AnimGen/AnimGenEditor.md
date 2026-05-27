# AnimGen

> 基于神经网络的动画压缩、重建与控制器生成系统。

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画图节点） |
| 模块 | `AnimGen` (Runtime), `AnimGenEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimGen) | |

## 用途

AnimGen 是一个实验性的动画插件，其核心功能是利用机器学习（特别是自编码器 AutoEncoder 和主成分分析 PCA）来压缩、分析和重建动画数据。它旨在解决以下问题：

1.  **动画数据压缩**：将高维的动画姿态数据（如骨骼变换）编码到低维的潜在空间中，从而大幅减少存储和传输开销。
2.  **动画分析与可视化**：通过 PCA 等技术对动画数据库进行降维分析，帮助开发者理解动画数据的分布和特征。
3.  **动画控制器生成**：训练神经网络控制器，使其能够根据简单的输入（如目标轨迹、控制参数）生成复杂的动画输出，实现程序化的动画驱动或风格迁移。

该插件提供了一套完整的编辑器工具链，用于训练自编码器、管理动画数据库、可视化潜在空间以及测试控制器。

## 使用场景

-   你正在开发一个拥有海量动画资源的大型开放世界游戏，需要优化动画资产的内存占用和加载速度 → 使用 AnimGen 的自编码器压缩动画。
-   你需要分析一个庞大的动画库，找出相似或重复的动画片段 → 使用 AnimGen 的 PCA 可视化工具在编辑器中查看动画的分布。
-   你希望实现一个程序化的角色动画系统，让角色能够根据环境或游戏逻辑平滑地过渡和混合动画 → 训练并使用 AnimGen 的控制器。
-   你需要将一种动画风格（如写实）迁移到另一种风格（如卡通）→ 通过训练自编码器学习两种风格的潜在表示，并在它们之间进行插值或转换。

## 蓝图用法

该插件主要提供了一个动画蓝图节点，用于在动画蓝图中集成 AnimGen 控制器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AnimGen Controller` | 在动画蓝图中使用训练好的 AnimGen 控制器来驱动角色动画。 | `UAnimGraphNode_AnimGenController` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键，选择 `Animation > AnimGen Controller` 来创建一个新的控制器资产。
2.  **训练控制器**：双击打开资产，在编辑器工具中配置动画数据库、训练参数，然后启动训练过程。
3.  **在动画蓝图中使用**：
    -   打开你的角色动画蓝图。
    -   在动画图表中右键，搜索并添加 `AnimGen Controller` 节点。
    -   在节点的细节面板中，指定你训练好的 `UAnimGenController` 资产。
    -   将该节点的输出姿势连接到动画蓝图的最终输出姿势。
    -   运行时，该节点将根据控制器内部逻辑和可能的输入参数（如目标速度、方向）生成动画姿势。

## C++ 用法

### 头文件引入

```cpp
#include "AnimGenControl.h" // 核心控制逻辑
#include "AnimDatabase.h"   // 动画数据库相关
```

### 基本用法

由于该插件为实验性且主要提供编辑器工具，其运行时 C++ API 相对有限。主要的交互是通过动画蓝图节点完成的。以下是一个概念性的示例，展示如何在 C++ 中引用相关的数据类型。

```cpp
// 引用动画数据库中的姿态状态
FAnimDatabasePoseState CurrentPose;
// ... 从某处获取或计算姿态数据

// 引用控制器（通常通过资产引用）
UAnimGenController* MyController = LoadObject<UAnimGenController>(nullptr, TEXT("/Game/Path/To/MyController"));
if (MyController)
{
    // 控制器的使用通常封装在动画节点内部，直接调用较少见。
    // 主要工作流是通过编辑器训练，然后在动画蓝图中使用节点。
}
```

### 进阶用法

进阶用法涉及直接操作动画数据库和训练流程，这通常发生在插件的编辑器模块内部。对于插件使用者，更常见的“进阶”用法是通过编辑器工具链进行复杂的训练配置和可视化分析。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个使用 `AnimGenController` 动画节点的动画实例。这需要在你的动画蓝图 C++ 类或相关逻辑中实现。

**AnimGenDemoCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "AnimGenDemoCharacter.generated.h"

UCLASS()
class AAnimGenDemoCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AAnimGenDemoCharacter();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // 用于在蓝图或C++中设置控制器资产的引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    UAnimGenController* AnimGenControllerAsset;
};
```

**AnimGenDemoCharacter.cpp**
```cpp
#include "AnimGenDemoCharacter.h"
#include "AnimGenControl.h" // 确保包含控制器头文件

AAnimGenDemoCharacter::AAnimGenDemoCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AAnimGenDemoCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 在此处可以添加初始化逻辑，例如验证控制器资产是否有效
    if (AnimGenControllerAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("AnimGen Controller Asset loaded: %s"), *AnimGenControllerAsset->GetName());
    }
}

void AAnimGenDemoCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 实际的动画驱动由动画蓝图中的 AnimGen Controller 节点处理。
    // 此处可以添加其他游戏逻辑。
}
```

**使用说明**：
1.  创建一个继承自 `AAnimGenDemoCharacter` 的蓝图类。
2.  在蓝图类的默认值中，为 `AnimGenControllerAsset` 属性指定一个在编辑器中训练好的控制器资产。
3.  为该角色创建一个动画蓝图，在动画图表中使用 `AnimGen Controller` 节点，并引用同一个控制器资产。
4.  将此动画蓝图分配给角色的骨骼网格体组件。

## 模块依赖

从模块名称和头文件包含关系推断，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `Learning` | 提供神经网络推理、PCA 编码等机器学习基础功能。 |
| `AnimDatabase` | 提供动画数据库的存储、查询和帧属性管理。 |
| `AnimDatabaseEditor` | 提供动画数据库的编辑器工具，如预览场景、时间轴。 |

## 维护状态

### 近期更新

- 2026-04-24 `05f62ee5` AnimGen: Added support for debug drawing on the canvas
- 2026-04-22 `2fc4ab35` AnimGen: No longer auto-refresh when changing frame ranges or frame attributes on the various editor
- 2026-04-21 `f3505bce` AnimGen: Exposed seed as parameter
- 2026-04-21 `0e8451f1` AnimGen: Various small fixes
- 2026-04-20 `4955ba48` AnimGen: Added support for multiple progress bars to make training Controller status more clear.

### 维护评价

-   **状态**：**实验性**。插件明确标记为实验性版本，默认未启用。
-   **活跃度**：**未知**。缺乏 git 历史数据，无法判断近期更新频率。作为 Epic 官方实验性项目，其维护状态取决于内部研发进度。
-   **推荐度**：**谨慎使用**。适合用于技术预研、原型开发或内部工具链。不建议直接用于需要长期稳定维护的商业项目核心功能，因为其 API 可能在未来版本中发生重大变更或被移除。
-   **已知限制**：作为实验性功能，可能存在性能、稳定性或功能完整性方面的问题。文档和社区支持可能有限。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimGen)
-   官方文档：暂无
-   测试用例：未在提供的路径中发现标准测试文件。