# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个功能全面的面部动画制作工具包，其核心目的是将真实世界的面部表演数据（来自 iPhone 的 Live Link Face 应用、其他深度摄像头或视频片段）转换为驱动 MetaHuman 角色的高质量动画数据。它不仅仅是一个简单的导入工具，而是一个完整的处理管线，涵盖了从原始数据导入、面部特征点追踪与编辑、深度图生成、面部动画求解到最终在 Sequencer 中驱动角色的全流程。该插件解决了从视频或深度数据创建逼真、可编辑的面部动画这一复杂问题，是 MetaHuman 生态系统中实现“表演捕捉”到“数字角色动画”转换的关键桥梁。

## 使用场景

-   **游戏过场动画制作**：使用 iPhone 捕捉演员的面部表演，快速生成用于游戏过场动画的面部动画序列。
-   **虚拟主播/VTuber**：实时或离线处理面部捕捉数据，驱动虚拟形象进行直播或内容创作。
-   **影视与广告制作**：为数字替身或虚拟角色创建基于真实表演的细腻面部动画。
-   **快速原型与预览**：在正式进行昂贵的专业动捕之前，使用消费级设备快速预览面部动画效果。
-   **批量处理**：利用 `MetaHumanBatchProcessor` 模块对大量表演数据进行自动化处理。

## 蓝图用法

该插件的核心功能主要通过 C++ 模块提供，但部分数据结构和控制器提供了蓝图接口。以下是从 `MetaHumanCore` 模块头文件中提取的关键蓝图可用类和函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetContourDataForDrawing` | 设置用于视口绘制的轮廓数据（简化曲线） | `UMetaHumanContourData` |
| `SetFullCurveContourDataForDrawing` | 设置用于视口绘制的完整轮廓数据 | `UMetaHumanContourData` |
| `ClearGeneratedDrawData` | 清除生成的绘制数据和控制顶点 | `UMetaHumanContourData` |
| `GetControlVertexPositions` | 获取指定曲线的控制顶点位置（不含端点） | `UMetaHumanContourData` |
| `GetSelectedCurves` | 获取当前被选中的曲线名称集合 | `UMetaHumanContourData` |
| `GetStartEndNamesForCurve` | 获取指定曲线的起始点和结束点名称 | `UMetaHumanContourData` |
| `InitializeContoursFromConfig` | 从配置初始化轮廓列表和默认显示数据 | `FMetaHumanCurveDataController` |
| `UpdateFromContourData` | 根据追踪数据更新轮廓和显示数据 | `FMetaHumanCurveDataController` |
| `OffsetSelectedPoints` | 按偏移量移动所有选中的控制点 | `FMetaHumanCurveDataController` |
| `MoveSelectedPoint` | 将单个控制点移动到图像空间的新位置 | `FMetaHumanCurveDataController` |
| `SetCurveSelection` | 设置曲线的选择状态 | `FMetaHumanCurveDataController` |
| `AddRemoveKey` | 在指定曲线上添加或移除一个关键点（控制顶点） | `FMetaHumanCurveDataController` |

### 使用示例（蓝图描述）

1.  **初始化轮廓数据**：首先，你需要一个 `UMetaHumanContourData` 对象。通常，这个对象由 `MetaHumanIdentity` 或 `MetaHumanPerformance` 资产创建并管理。在蓝图中，你可以获取到这个对象的引用。
2.  **创建控制器**：使用 `FMetaHumanCurveDataController` 的构造函数节点，传入 `UMetaHumanContourData` 对象和显示模式（`Editing` 或 `Visualization`）。
3.  **加载配置**：调用 `InitializeContoursFromConfig` 节点，传入从配置文件加载的默认追踪数据（`FFrameTrackingContourData`）和配置版本字符串。这将设置好所有可编辑的曲线。
4.  **更新与编辑**：当有新的追踪数据时，调用 `UpdateFromContourData`。在编辑模式下，你可以使用 `MoveSelectedPoint` 或 `OffsetSelectedPoints` 来调整控制点位置，使用 `AddRemoveKey` 来增删关键点。
5.  **获取结果**：使用 `GetControlVertexPositions` 或 `GetDensePointsForVisibleCurves` 等节点获取编辑后的曲线数据，用于后续的动画求解或可视化。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanContourData.h"
#include "MetaHumanCurveDataController.h"
#include "MetaHumanViewportSettings.h"
#include "DNAUtilities.h"
```

### 基本用法

以下示例展示了如何创建和操作轮廓数据控制器，这是编辑面部轮廓的核心。

```cpp
// 假设你已经有了一个 UMetaHumanContourData 对象，例如从资产中加载
UMetaHumanContourData* MyContourData = ...;

// 1. 创建一个控制器，用于编辑轮廓
FMetaHumanCurveDataController ContourController(MyContourData, ECurveDisplayMode::Editing);

// 2. 从配置初始化（通常在资产加载后调用）
FFrameTrackingContourData DefaultData; // 从配置文件加载
FString ConfigVersion = TEXT("1.0");
ContourController.InitializeContoursFromConfig(DefaultData, ConfigVersion);

// 3. 模拟接收到新的追踪数据并更新
FFrameTrackingContourData NewTrackingData = ...; // 从追踪器获取
ContourController.UpdateFromContourData(NewTrackingData, true);

// 4. 编辑一个控制点
int32 PointIdToMove = 42;
FVector2D NewPosition(100.0f, 200.0f);
ContourController.MoveSelectedPoint(NewPosition, PointIdToMove);

// 5. 获取编辑后的曲线数据用于求解
TMap<FString, TArray<FVector2D>> EditedCurves = ContourController.GetDensePointsForVisibleCurves();
```

### 进阶用法

结合视口设置和DNA工具，实现更完整的动画流程。

```cpp
// 1. 检查DNA兼容性（在混合不同来源的动画数据前）
IDNAReader* SourceDNA = ...;
IDNAReader* TargetDNA = ...;
FString CompatibilityMessage;
bool bIsCompatible = FDNAUtilities::CheckCompatibility(
    SourceDNA, 
    TargetDNA, 
    EDNARigCompatiblityFlags::All, 
    CompatibilityMessage
);

if (!bIsCompatible)
{
    UE_LOG(LogTemp, Warning, TEXT("DNA不兼容: %s"), *CompatibilityMessage);
}

// 2. 配置视口显示状态
UMetaHumanViewportSettings* ViewportSettings = NewObject<UMetaHumanViewportSettings>();
FMetaHumanViewportState& ViewState = ViewportSettings->GetViewportState();
ViewState.bShowCurves = true;
ViewState.bShowControlVertices = true;
ViewState.bShowFootage = true;
ViewState.ViewModeIndex = VMI_Lit;

// 3. 使用轮廓数据控制器的委托来响应选择变化
ContourController.GetCurvesSelectedDelegate().AddLambda([](bool bClearPointSelection)
{
    // 当曲线选择状态改变时，更新UI或执行其他逻辑
    UE_LOG(LogTemp, Log, TEXT("曲线选择已更新，清除点选择: %s"), bClearPointSelection ? TEXT("是") : TEXT("否"));
});
```

## Demo 示例

一个最小化的示例，演示如何初始化轮廓数据控制器并执行基本操作。

**MyMetaHumanAnimActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanContourData.h"
#include "MetaHumanCurveDataController.h"
#include "MyMetaHumanAnimActor.generated.h"

UCLASS()
class AMyMetaHumanAnimActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanAnimActor();

protected:
    virtual void BeginPlay() override;

public:
    // 轮廓数据资产（可在编辑器中指定）
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    TObjectPtr<UMetaHumanContourData> ContourDataAsset;

private:
    // 轮廓控制器
    TUniquePtr<FMetaHumanCurveDataController> ContourController;

    // 模拟初始化配置数据
    FFrameTrackingContourData CreateDefaultContourData();
};
```

**MyMetaHumanAnimActor.cpp**
```cpp
#include "MyMetaHumanAnimActor.h"
#include "MetaHumanContourData.h"

AMyMetaHumanAnimActor::AMyMetaHumanAnimActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanAnimActor::BeginPlay()
{
    Super::BeginPlay();

    if (ContourDataAsset)
    {
        // 创建控制器
        ContourController = MakeUnique<FMetaHumanCurveDataController>(ContourDataAsset, ECurveDisplayMode::Editing);

        // 初始化
        FFrameTrackingContourData DefaultData = CreateDefaultContourData();
        ContourController->InitializeContoursFromConfig(DefaultData, TEXT("1.0"));

        UE_LOG(LogTemp, Log, TEXT("MetaHuman 轮廓控制器已初始化。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("未指定 ContourDataAsset。"));
    }
}

FFrameTrackingContourData AMyMetaHumanAnimActor::CreateDefaultContourData()
{
    // 这里应该从配置文件或资产中加载真实的默认数据
    // 为示例创建一个空的结构
    FFrameTrackingContourData Data;
    // ... 填充数据 ...
    return Data;
}
```

## 模块依赖

该插件模块众多，依赖关系复杂。`MetaHumanCore` 模块依赖 `UnrealEd`，但这属于编辑器插件的常见依赖。其他模块间的依赖（如 `MetaHumanIdentity` 依赖 `MetaHumanCaptureDataEditor` 和 `MetaHumanSDKEditor`）是插件内部的实现细节。

对于**使用者**（即希望在自己的模块中调用 MetaHuman Animator 功能的开发者），通常只需要依赖你直接使用的具体模块（如 `MetaHumanCore`, `MetaHumanIdentity`）。这些模块的公共依赖已经包含了必要的底层模块。

**无特殊依赖（仅标准 Core/Engine/Slate 等）**。使用时请根据你引用的具体模块，在你的 `.Build.cs` 文件中添加对应的 `PublicDependencyModuleNames`。

## 维护状态

### 近期更新

-   2025-10-03 9803c443cfab 为包含对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏。
-   2025-10-03 865186bfe3c7 重构相机速度，使其基于一个在最小值和最大值范围内的单一浮点值。
-   2025-10-03 52e3dac151e1 使用 UnrealCodeFixup 更新了头文件，确保 dllstorage 位于方法/静态变量上而不是类型上。

### 维护评价

MetaHuman Animator 是一个相对较新的插件（创建于 2024 年初），但作为 Epic Games 官方 MetaHuman 工具链的核心部分，它得到了**积极维护**。从最近的提交记录看，更新集中在代码质量改进（如内联宏、头文件规范化）和功能优化（如相机速度控制重构）上，表明该插件处于活跃的开发和完善阶段。由于其官方地位和重要性，可以预期它会随着 Unreal Engine 和 MetaHuman 技术的演进持续更新。**推荐使用**，它是实现高质量 MetaHuman 面部动画的官方且功能完备的解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档]()（暂无）
-   [测试用例]()（路径待确认，通常位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests/` 或 `Engine/Tests/` 下）