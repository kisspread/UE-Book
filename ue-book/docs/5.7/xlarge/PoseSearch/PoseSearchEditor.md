# Pose Search

> Framework for indexing and searching pose features. Used in techniques such as Motion Matching.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、蓝图资产） |
| 模块 | `PoseSearch` (Runtime), `PoseSearchEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-16 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch) | |

## 用途

PoseSearch 是 UE5 的 **Motion Matching（运动匹配）** 核心框架。它解决的核心问题是：**如何从大量动画片段中，实时找到与当前角色状态最匹配的动画姿态**。

传统动画系统需要手动设置状态机和过渡条件，而 Motion Matching 通过以下方式自动化这个过程：

1. **特征索引**：将动画数据库中的每一帧姿态提取为特征向量（骨骼位置、速度、轨迹等）
2. **高效搜索**：使用 KD-Tree 和 PCA 降维等技术，在运行时快速找到最匹配的姿态
3. **无缝过渡**：通过 BlendStack 系统实现平滑的动画混合过渡

该插件还支持**多角色交互动画**（Experimental），可以同步搜索多个角色的匹配姿态。

## 使用场景

- 你在做一个动作游戏，需要角色根据移动方向和速度自动选择最合适的跑步/转向动画 → 用 Motion Matching
- 你有大量 Motion Capture 数据，想要自动选择最佳动画片段而非手动制作状态机 → 用 PoseSearch Database
- 你需要角色在不同地形（上坡、下坡、台阶）自动切换动画 → 配置 PoseSearch Schema 的特征通道
- 你需要两个角色进行同步交互动画（如握手、格斗） → 用 MotionMatchingInteraction（实验性功能）

## 蓝图用法

### 动画图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Motion Matching` | 核心运动匹配节点，从数据库中搜索最佳匹配姿态 | `UAnimGraphNode_MotionMatching` |
| `Motion Matching Interaction` | 多角色交互运动匹配（实验性） | `UAnimGraphNode_MotionMatchingInteraction` |
| `Pose Search History Collector` | 收集姿态搜索历史数据 | `UAnimGraphNode_PoseSearchHistoryCollector` |
| `Pose Search Component Space History Collector` | 组件空间的姿态搜索历史收集器 | `UAnimGraphNode_PoseSearchComponentSpaceHistoryCollector` |

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UPoseSearchSchema` | 定义姿态特征的提取规则（哪些骨骼、哪些特征通道） |
| `UPoseSearchDatabase` | 包含动画序列集合和预计算的搜索索引 |
| `UPoseSearchNormalizationSet` | 特征归一化配置，用于平衡不同特征的权重 |
| `UPoseSearchInteractionAsset` | 多角色交互动画资产（实验性） |

### 使用示例（蓝图描述）

**基本 Motion Matching 设置流程：**

1. **创建 Schema**：右键 Content Browser → Animation → Pose Search Schema，选择目标骨骼，配置特征通道（如骨骼位置、速度、轨迹）
2. **创建 Database**：右键 Content Browser → Animation → Pose Search Database，选择刚创建的 Schema，添加动画序列
3. **构建索引**：在 Database 编辑器中点击 Build 按钮，预计算搜索索引
4. **添加到动画蓝图**：在 AnimGraph 中添加 Motion Matching 节点，连接 Database 资产

**Motion Matching 节点配置：**
- `Database`：指向 PoseSearchDatabase 资产
- `BlendTime`：动画过渡时间
- `PoseJumpThresholdTime`：防止频繁跳转的阈值
- `OnMotionMatchingStateUpdatedFunction`：状态更新时的回调函数

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "PoseSearch/AnimNode_MotionMatching.h"
#include "PoseSearch/PoseSearchRole.h"
#include "PoseSearch/PoseSearchAssetSampler.h"

// Editor 模块
#include "PoseSearchDatabaseEditor.h"
#include "PoseSearchDatabaseViewModel.h"
```

### 基本用法

**创建和配置 PoseSearch Schema：**

```cpp
// 创建 Schema 资产
UPoseSearchSchema* Schema = NewObject<UPoseSearchSchema>(GetTransientPackage(), "MySchema");
Schema->Skeleton = MySkeleton;

// 添加特征通道（骨骼位置、速度等）
// Schema 定义了从动画中提取哪些特征用于搜索
```

**使用 Database ViewModel 进行预览：**

```cpp
// 来源: PoseSearchDatabaseViewModel.h
// FDatabaseViewModel 管理数据库编辑器的预览和交互

TSharedRef<FDatabaseViewModel> ViewModel = MakeShared<FDatabaseViewModel>();
ViewModel->Initialize(PoseSearchDatabase, PreviewScene, DataDetailsWidget);

// 预览控制
ViewModel->PreviewForward();
ViewModel->PreviewBackward();
ViewModel->PreviewPause();

// 构建搜索索引
ViewModel->BuildSearchIndex();

// 获取预览 Actor 信息
const TArray<TArray<FDatabasePreviewActor>>& PreviewActors = ViewModel->GetPreviewActors();
```

**使用 AnimationAssetSampler 采样动画：**

```cpp
// 来源: PoseSearchAssetSampler.h
// FAnimationAssetSampler 用于在特定时间点采样动画姿态

FAnimationAssetSampler Sampler;
// Sampler 可以获取动画在任意时间点的姿态数据
// 用于预览和调试
```

### 进阶用法

**自定义 Database 编辑器扩展：**

```cpp
// 来源: PoseSearchDatabaseEditor.h
// FDatabaseEditor 提供完整的数据库编辑功能

class FMyCustomDatabaseEditor : public FDatabaseEditor
{
    // 可以扩展编辑器功能
    // 添加自定义 Tab、工具栏按钮等
};

// 编辑器支持的 Tab 类型
// - Viewport: 3D 预览视口
// - AssetDetails: 资产属性面板
// - AssetTreeView: 动画资产树形视图
// - DataDetails: 数据详情（特征通道统计）
// - StatisticsOverview: 数据库统计信息
// - AssetBrowser: 资产浏览器
```

**使用 DatabaseEdMode 进行交互式编辑：**

```cpp
// 来源: PoseSearchDatabaseEdMode.h
// FDatabaseEdMode 提供自定义编辑模式

const FEditorModeID FDatabaseEdMode::EdModeId = "PoseSearchDatabaseEdMode";

// 编辑模式支持：
// - 自定义渲染（Render）
// - 点击处理（HandleClick）
// - 拖拽输入（InputDelta）
// - 键盘输入（InputKey）
// - Widget 显示和移动
```

**多角色交互动画（实验性）：**

```cpp
// 来源: PoseSearchInteractionAssetEditor.h
// FInteractionAssetViewModel 管理交互动画预览

TSharedRef<FInteractionAssetViewModel> InteractionViewModel = MakeShared<FInteractionAssetViewModel>();
InteractionViewModel->Initialize(InteractionAsset, PreviewScene);

// 预览控制
InteractionViewModel->PreviewForward();
InteractionViewModel->SetPlayTime(1.5f, true);

// 获取预览 Actor
TConstArrayView<FInteractionAssetPreviewActor> Actors = InteractionViewModel->GetPreviewActors();
for (const FInteractionAssetPreviewActor& Actor : Actors)
{
    const FRole& Role = Actor.GetRole();
    // 每个 Actor 有不同的角色标识
}
```

## Demo 示例

### 基本 Motion Matching 设置

```cpp
// MyMotionMatchingComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyMotionMatchingComponent.generated.h"

class UPoseSearchDatabase;
class UPoseSearchSchema;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyMotionMatchingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMotionMatchingComponent();

    // 指向 PoseSearch Database 资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Matching")
    TObjectPtr<UPoseSearchDatabase> MotionDatabase;

    // 当前最佳匹配的动画时间
    UPROPERTY(BlueprintReadOnly, Category = "Motion Matching")
    float CurrentMatchTime = 0.0f;

    // 是否正在播放匹配的动画
    UPROPERTY(BlueprintReadOnly, Category = "Motion Matching")
    bool bIsMatching = false;

    // 手动触发搜索（用于调试）
    UFUNCTION(BlueprintCallable, Category = "Motion Matching")
    void TriggerSearch();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    // 内部搜索状态
    int32 LastBestPoseIndex = INDEX_NONE;
};
```

```cpp
// MyMotionMatchingComponent.cpp
#include "MyMotionMatchingComponent.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"

UMyMotionMatchingComponent::UMyMotionMatchingComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyMotionMatchingComponent::BeginPlay()
{
    Super::BeginPlay();

    if (!MotionDatabase)
    {
        UE_LOG(LogTemp, Warning, TEXT("MotionMatchingComponent: No database assigned!"));
        return;
    }

    // 验证数据库是否已构建索引
    if (!MotionDatabase->IsSearchIndexValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("MotionMatchingComponent: Database index not built. Please build in editor."));
    }
}

void UMyMotionMatchingComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!MotionDatabase || !MotionDatabase->IsSearchIndexValid())
    {
        return;
    }

    // 在实际项目中，Motion Matching 通常通过动画蓝图的 AnimNode_MotionMatching 节点处理
    // 这里展示的是底层 API 的使用方式
}

void UMyMotionMatchingComponent::TriggerSearch()
{
    if (!MotionDatabase)
    {
        return;
    }

    // 获取数据库中的动画序列数量
    int32 NumAssets = MotionDatabase->GetNumAssets();
    UE_LOG(LogTemp, Log, TEXT("Database contains %d animation assets"), NumAssets);

    bIsMatching = true;
}
```

### 自定义 Database 编辑器扩展

```cpp
// MyDatabaseEditorExtension.h
#pragma once

#include "CoreMinimal.h"
#include "PoseSearchDatabaseEditor.h"

namespace UE::PoseSearch
{
    class FMyDatabaseEditorExtension
    {
    public:
        // 扩展数据库编辑器的工具栏
        static void ExtendToolbar(FToolBarBuilder& ToolbarBuilder, TSharedRef<FDatabaseEditor> Editor);

        // 自定义统计信息显示
        static void AddCustomStatistics(TSharedRef<FDatabaseViewModel> ViewModel);
    };
}
```

```cpp
// MyDatabaseEditorExtension.cpp
#include "MyDatabaseEditorExtension.h"
#include "PoseSearchDatabaseViewModel.h"
#include "PoseSearch/PoseSearchDatabase.h"

namespace UE::PoseSearch
{
    void FMyDatabaseEditorExtension::ExtendToolbar(FToolBarBuilder& ToolbarBuilder, TSharedRef<FDatabaseEditor> Editor)
    {
        // 添加自定义工具栏按钮
        ToolbarBuilder.AddToolBarButton(
            FUIAction(),
            NAME_None,
            LOCTEXT("MyCustomAction", "Custom Action"),
            LOCTEXT("MyCustomActionTooltip", "Perform custom action on database"),
            FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.GameSettings")
        );
    }

    void FMyDatabaseEditorExtension::AddCustomStatistics(TSharedRef<FDatabaseViewModel> ViewModel)
    {
        const UPoseSearchDatabase* Database = ViewModel->GetPoseSearchDatabase();
        if (!Database)
        {
            return;
        }

        // 获取数据库统计信息
        int32 NumSequences = Database->GetNumAssets();
        UE_LOG(LogTemp, Log, TEXT("Database has %d sequences"), NumSequences);

        // 获取预览 Actor 信息
        const TArray<TArray<FDatabasePreviewActor>>& PreviewActors = ViewModel->GetPreviewActors();
        UE_LOG(LogTemp, Log, TEXT("Preview actors: %d groups"), PreviewActors.Num());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationWarping` | 动画变形功能，用于根运动和 IK 调整 |
| `BlendStack` | 动画混合栈系统，Motion Matching 的过渡动画依赖此模块 |
| `Chooser` | 选择器系统，用于条件化动画选择 |
| `GameplayInsights` | 游戏洞察工具（仅编辑器），用于调试和可视化 |

## 维护状态

### 近期更新

```
- 7ff009b49aca Chooser - PoseSearchColumn initial support for fallback row
- ee9751c9f006 PoseSearch - avoid opening the schema asset selector window for every row in the chooser table
- 9168c9ee7cb9 PoseSearch - fix for SDatabaseAssetListItem potentially referencing a deleted asset
```

**解读：**
- 最新提交增加了 Chooser 集成的 fallback row 支持，表明 PoseSearch 正在与 Chooser 系统深度整合
- 修复了 Schema 选择器窗口重复弹出的 UX 问题
- 修复了资产引用可能失效的 bug

### 维护评价

**活跃维护中** ✅

- **创建时间**：2020 年，已有 5 年历史，是 UE5 Motion Matching 的核心实现
- **更新频率**：持续有功能性更新和 bug 修复，最近的提交集中在 Chooser 集成
- **实验性功能**：部分功能标记为 Experimental（如 InteractionAsset、MotionMatchingInteraction），可能在未通知的情况下移除
- **依赖关系**：依赖 BlendStack、Chooser 等活跃维护的模块
- **推荐使用**：✅ 推荐用于需要 Motion Matching 的项目，但需注意实验性功能的稳定性

**注意事项**：
- `EnabledByDefault: false`，需要在项目设置中手动启用
- 多角色交互功能（InteractionAsset）仍为实验性，生产环境慎用
- 需要配合 BlendStack 插件使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch/Tests)（如果存在）